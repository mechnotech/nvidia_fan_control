import os
from tempfile import NamedTemporaryFile

from controller import FanController

f = NamedTemporaryFile(prefix='lock_fun_controller_010_', delete=True) if not [
    f for f in os.listdir('/tmp') if f.find('lock_fun_controller_010_') != -1
] else exit('Already running!')

if __name__ == '__main__':
    FanController().run()
