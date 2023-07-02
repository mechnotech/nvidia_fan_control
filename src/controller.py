import csv
import io
import json
import logging
import subprocess
import time
from pathlib import Path

import numpy as np
from scipy.interpolate import interp1d

base_dir = Path(__file__).parent.parent.absolute()
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s %(message)s")


class FanController:
    logger = logging.getLogger('fan controller')

    def __init__(self):
        self.gpu_fan_map = None
        self.temp_profile = None
        self.temp_fan = None
        self.gpu_fan_map = None
        self.profile_path = f'{base_dir}/profiles/'
        self.load_profile()
        self.calc_curve()

    def load_profile(self):
        with open(self.profile_path + 'temp_profile.json', 'r') as pf:
            profile = json.loads(pf.read())
            self.temp_profile = profile['GPUS'][0]
            self.gpu_fan_map = profile['GPU_FAN_MAP']

    def calc_curve(self):
        x = np.array([int(x) for x in self.temp_profile.keys()])
        y = np.array(list(self.temp_profile.values()))

        discr = 101
        new_x = np.linspace(min(x), max(x), discr)
        new_y = interp1d(x, y, kind='linear')(new_x)

        self.temp_fan = dict([(k, v) for k, v in zip(np.array(new_x).astype(int), np.array(new_y).astype(int))])

    @staticmethod
    def switch_control(gpus: list, defaults: bool = True):
        state = 0 if defaults else 1
        for num in range(len(gpus) - 1):
            subprocess.run(
                ['nvidia-settings', '-a', f'[gpu:{num}]/GPUFanControlState={state}']
            )

    def check_gpus(self):
        result = subprocess.run(['nvidia-smi', '-L'], check=True, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
        if result.stdout:
            self.logger.info(result.stdout.decode())
            return result.stdout.split(b'\n')
        return False

    @staticmethod
    def get_current_temp():
        result = []
        current_temps = subprocess.run(['nvidia-smi', 'stats', '-d', 'temp', '-c', '1'], capture_output=True)
        with io.StringIO() as stream:
            stream.write(current_temps.stdout.decode())
            stream.seek(0)
            temp_csv = csv.reader(stream)
            for row in temp_csv:
                result.append(int(row[-1].strip(' ')))
        return result

    def set_fan_speed(self, gpu_num: int, speed: int):
        self.logger.info(f'try to set gpu: {gpu_num}, speed: {speed}')
        true_fan_num = self.gpu_fan_map[str(gpu_num)]
        subprocess.run(
            ['nvidia-settings',
             '-a',
             f'[fan:{true_fan_num}]/GPUTargetFanSpeed={speed}'
             ],
            capture_output=False, stdout=subprocess.DEVNULL
        )

    def run(self):
        gpus = []
        old_speed_set = dict()
        log_cnt = 1
        try:
            gpus = self.check_gpus()
            if not gpus:
                self.logger.error('Nvidia GPUs not detected! (check nvidia-smi)')
                exit()
            self.switch_control(gpus, defaults=False)
            while True:
                time.sleep(1)
                current_temps = self.get_current_temp()
                for num, t in enumerate(current_temps):
                    speed = self.temp_fan.get(t)
                    if old_speed_set.get(num):
                        if old_speed_set[num] == speed:
                            continue

                    old_speed_set[num] = speed
                    self.set_fan_speed(num, speed)
                if log_cnt % 10 == 0:
                    c_temp = [f'gpu-{n}: {x}' for n, x in enumerate(current_temps)]
                    c_speed = [f'gpu-{k}: {v}' for k, v in old_speed_set.items()]
                    self.logger.info(f'temperature - {c_temp}')
                    self.logger.info(f'fan speed - {c_speed}')
                log_cnt += 1

        finally:
            self.switch_control(gpus)
