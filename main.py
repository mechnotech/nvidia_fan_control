import io
import time

import numpy as np

from scipy.interpolate import interp1d
import subprocess
import csv

curve_nodes = {
    0: 5,
    20: 15,
    40: 35,
    60: 75,
    80: 95,
    100: 100,
}

x = np.array(list(curve_nodes.keys()))
y = np.array(list(curve_nodes.values()))

discr = 101
new_x = np.linspace(min(x), max(x), discr)
new_y = interp1d(x, y, kind='linear')(new_x)

temp_fan = dict([(k, v) for k, v in zip(np.array(new_x).astype(int), np.array(new_y).astype(int))])
# print(temp_fan)
gpu_fan_map = {
    0: 1,
    1: 0,
}


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


def check_gpus():
    result = subprocess.run(['nvidia-smi', '-L'], capture_output=True)
    if result.stdout:
        print(result.stdout.decode())
        return result.stdout.split(b'\n')
    return False


def switch_control(gpus: list, defaults: bool = True):
    state = 0 if defaults else 1
    for num in range(len(gpus) - 1):
        subprocess.run(
            ['nvidia-settings', '-a', f'[gpu:{num}]/GPUFanControlState={state}']
        )


def set_fan_speed(gpu_num: int, speed: int):
    # print('try to set gpu', num, 'speed', speed)
    true_fan_num = gpu_fan_map[gpu_num]
    subprocess.run(
        ['nvidia-settings',
         '-a',
         f'[fan:{true_fan_num}]/GPUTargetFanSpeed={speed}'
         ],
        capture_output=False, stdout=subprocess.DEVNULL
    )


if __name__ == '__main__':
    gpus = []
    old_speed_set = dict()
    log_cnt = 1
    try:
        gpus = check_gpus()
        if not gpus:
            print('Nvidia GPUs not detected! (check nvidia-smi')
            exit()
        switch_control(gpus, defaults=False)
        while True:
            time.sleep(1)
            current_temps = get_current_temp()
            for num, t in enumerate(current_temps):
                speed = temp_fan.get(t)
                if old_speed_set.get(num):
                    if old_speed_set[num] == speed:
                        # print('skiped fan speed change')
                        continue

                old_speed_set[num] = speed
                set_fan_speed(num, speed)
            if log_cnt % 10 == 0:
                print(
                    'temperature:', *[f'gpu-{n}: {x}' for n, x in enumerate(current_temps)],
                    'fan speed:', *[f'gpu-{k}: {v}' for k, v in old_speed_set.items()]
                )
            log_cnt += 1

    finally:
        switch_control(gpus)
