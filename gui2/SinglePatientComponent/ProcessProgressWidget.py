from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide2.QtCore import Qt, QSize, Signal

from utils.software_config import SoftwareConfigResources
from gui2.LogReaderThread import LogReaderThread


class ProcessProgressWidget(QWidget):
    """

    """

    cancel_process_triggered = Signal()  # @TODO. How to actually kill the thread, since started in a wrapper with no handle on it?

    def __init__(self, parent=None):
        super(ProcessProgressWidget, self).__init__()
        self.parent = parent
        self.widget_name = "process_progress_widget"
        self.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        self.process_monitoring_thread = LogReaderThread()
        self.processing_steps = None
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.cancel_process_pushbutton = QPushButton('Cancel...')
        self.progress_label = QLabel('Overall progress: ???')
        self.detailed_progression_label = QLabel()
        self.layout.addWidget(self.progress_label)
        self.layout.addWidget(self.detailed_progression_label)
        self.layout.addWidget(self.cancel_process_pushbutton)
        self.layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.cancel_process_pushbutton.setFixedSize(QSize(50, 25))
        self.progress_label.setFixedWidth(self.size().width())

    def __set_stylesheets(self):
        self.cancel_process_pushbutton.setStyleSheet("""QPushButton{background-color:rgb(255, 0, 0);}""")

    def __set_connections(self):
        self.process_monitoring_thread.message.connect(self.on_process_message)
        self.cancel_process_pushbutton.clicked.connect(self.cancel_process_triggered)

    def on_process_started(self):
        self.processing_steps = None
        self.progress_label.setText("")
        self.detailed_progression_label.setText("")
        self.process_monitoring_thread.start()

    def on_process_finished(self):
        self.process_monitoring_thread.stop()

    def on_process_message(self, message):
        # @TODO. Have to update both backends to provide an identifier together with the LOG message,
        # to track down the steps accordingly.
        if ':LOG:' in message:
            if not self.processing_steps:
                self.processing_steps = int(message.strip().split('/')[1].replace(')', ''))
                self.progress_label.setText("Overall progress: 1 / " + str(self.processing_steps))
            current_step = int(message.strip().split('(')[1].split('/')[0])
            self.progress_label.setText("Overall progress: " + str(current_step) + " / " + str(self.processing_steps))
            curated_message = message.split(':LOG:')[1].split('-')[0].strip()
            if 'Begin' in message:
                self.detailed_progression_label.setText(self.detailed_progression_label.text() + curated_message + '...')
            else:
                self.detailed_progression_label.setText(self.detailed_progression_label.text()[:-3] + '.\n')
