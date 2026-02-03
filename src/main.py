import os
import psutil
from tempfile import NamedTemporaryFile
from controller import FanController
import atexit

temp_file = None
pid = os.getpid()


def cleanup():
    global temp_file
    if temp_file and os.path.exists(temp_file.name):
        try:
            os.remove(temp_file.name)
            print(f"Файл блокировки удален успешно.")
        except Exception:
            pass

def main():
    global temp_file
    prefix = 'lock_fun_controller_010_'

    # Ищем существующий временный файл с подходящим префиксом
    existing_files = [f for f in os.listdir('/tmp') if f.startswith(prefix)]

    if existing_files:
        # Проверяем, жив ли процесс, связанный с файлом
        for filename in existing_files:
            filepath = os.path.join('/tmp', filename)
            try:
                with open(filepath, 'r') as f:
                    file_pid = int(f.read().strip())
                if psutil.pid_exists(file_pid):
                    print(f"Скрипт уже запущен (PID: {file_pid}). Выход.")
                    return
                else:
                    # "Призрачный" файл - удаляем
                    os.remove(filepath)
                    print(f"Удален 'призрачный' файл: {filepath}")
            except (FileNotFoundError, ValueError, OSError) as e:
                print(f"Ошибка при проверке файла {filepath}: {e}")

    # Создаем временный файл
    temp_file = NamedTemporaryFile(prefix=prefix, delete=False)

    try:
        # Записываем PID в файл
        with open(temp_file.name, 'w') as f:
            f.write(str(pid))

        # Регистрируем функцию cleanup для удаления файла при выходе
        atexit.register(cleanup)

        # Запускаем FanController
        FanController(temp=temp_file).run()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        #  Всегда вызываем cleanup на всякий случай
        cleanup()


if __name__ == '__main__':
    main()
