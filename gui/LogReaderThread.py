import os
import time
from PySide6.QtCore import Signal, QThread
from utils.software_config import SoftwareConfigResources


class LogReaderThread(QThread):
    message = Signal(str)

    def run(self) -> None:
        logfile = open(SoftwareConfigResources.getInstance().get_session_log_filename(), 'r')
        newlines = self.follow(logfile)
        for l in newlines:
            self.write(l)

    def write(self, text):
        self.message.emit(text)

    def stop(self):
        self.terminate()

    def follow(self, thefile):
        # seek the end of the file
        thefile.seek(0, os.SEEK_END)

        # start infinite loop
        while self.isRunning():
            # read last line of file
            line = thefile.readline()  # sleep if file hasn't been updated
            if not line:
                time.sleep(0.1)
                continue

            yield line
