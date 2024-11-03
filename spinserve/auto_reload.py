import time
from subprocess import Popen

from watchdog.events import FileSystemEventHandler


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, command, debounce_delay=2):
        super().__init__()
        self.command = command
        self.process = None
        self.last_modified = 0
        self.debounce_delay = debounce_delay
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            time.sleep(0.1)
        self.process = Popen(self.command, shell=True)

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            current_time = time.time()
            if current_time - self.last_modified > self.debounce_delay:
                self.last_modified = current_time
                print(f"Изменение в файле {event.src_path}. Перезапуск...")
                self.start_process()
