import logging

from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QPixmap
import os
from utils.software_config import SoftwareConfigResources
from gui2.LogReaderThread import LogReaderThread
from gui2.UtilsWidgets.QCircularProgressBar import QCircularProgressBar

class ProcessProgressWidget(QWidget):
    """

    """

    cancel_process_triggered = Signal()  # @TODO. How to actually kill the thread, since started in a wrapper with no handle on it?

    def __init__(self, parent=None):
        super(ProcessProgressWidget, self).__init__()
        self.parent = parent
        self.widget_name = "process_progress_widget"
        self.process_stages_stack = []
        self.progress_widget = []
        self.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        self.process_monitoring_thread = LogReaderThread()
        self.processing_steps = None
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.overall_progress_layout = QHBoxLayout()
        self.progress_label = QLabel()
        self.circular_progressbar = QCircularProgressBar(self)
        self.overall_progress_layout.addStretch(1)
        self.overall_progress_layout.addWidget(self.circular_progressbar)
        # self.overall_progress_layout.addWidget(self.progress_label)
        self.overall_progress_layout.addStretch(1)
        self.detailed_progression_layout = QVBoxLayout()
        self.detailed_progression_layout.setSpacing(5)
        self.cancel_process_layout = QHBoxLayout()
        self.cancel_process_layout.setContentsMargins(0, 10, 0, 0)
        self.cancel_process_pushbutton = QPushButton('Cancel...')
        self.cancel_process_pushbutton.setEnabled(False)  # Impossible to actually kill the process thread atm.
        self.cancel_process_pushbutton.setToolTip("The process cannot be interrupted for now.")
        self.cancel_process_layout.addStretch(1)
        self.cancel_process_layout.addWidget(self.cancel_process_pushbutton)
        self.cancel_process_layout.addStretch(1)

        self.layout.addLayout(self.overall_progress_layout)
        self.layout.addLayout(self.detailed_progression_layout)
        self.layout.addLayout(self.cancel_process_layout)
        self.layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.cancel_process_pushbutton.setFixedSize(QSize(50, 25))
        self.progress_label.setFixedSize(QSize(165, 165))

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]

        self.cancel_process_pushbutton.setStyleSheet("""QPushButton{background-color:rgb(255, 0, 0);}""")

        # border-image automatically resizes to the QLabel size, while background-image keeps its original size.
        self.progress_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        font-style: bold;
        font-size: 17px;
        padding-left: 9px;
        border-image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/progress_icon_empty.png') + """)
        }""")

    def __set_connections(self):
        self.process_monitoring_thread.message.connect(self.on_process_message)
        self.cancel_process_pushbutton.clicked.connect(self.cancel_process_triggered)

    def on_process_started(self):
        self.processing_steps = None

        self.progress_label.setText("Overall progress: ")
        self.circular_progressbar.reset()
        self.process_stages_stack = []
        self.progress_widget = []
        items = (self.detailed_progression_layout.itemAt(i) for i in reversed(range(self.detailed_progression_layout.count())))
        for i in items:
            try:
                if i and i.widget():  # Current item is a QWidget that can be directly removed
                    w = i.widget()
                    w.setParent(None)
                    w.deleteLater()
            except Exception:
                pass
        self.process_monitoring_thread.start()

    def on_process_finished(self):
        self.process_monitoring_thread.stop()

    def on_process_message(self, message: str) -> None:
        """
        Collecting all messages coming from the two backend libraries, which are containing the LOG: keyword,
        indicating that the message should be processed in here.
        Each of such messages contains either a Begin, End, or Runtime statement, and if not simply indicate
        the overall start of a processing type (e.g., segmentation or reporting).
        If multiple processes are nested, only the steps for the outer process are reporting here.

        Parameters
        ----------
        message: str
            Line emitted by either processing backends (i.e., seg or rads) whenever a process is ongoing.
        """
        if 'LOG:' in message:
            if 'Begin' not in message and 'End' not in message and 'Runtime' not in message:
                task = message.strip().split('-')[0].strip()
                total_steps = int(message.strip().split('-')[1].strip().split(' ')[0].strip())
                self.process_stages_stack.append({'task': task, 'total_steps': total_steps, 'steps': {}})

                if not self.processing_steps:
                    self.processing_steps = self.process_stages_stack[0]['total_steps']
                    self.progress_label.setText("Overall progress:\n\t0 / " + str(self.processing_steps))
                    self.circular_progressbar.advance(0, self.process_stages_stack[0]['total_steps'])

            elif 'Begin' in message:
                current_task = message.strip().split('-')[1].strip()
                current_step = int(message.strip().split('(')[1].split('/')[0])
                self.process_stages_stack[-1]['steps'][current_step] = current_task
                if len(self.process_stages_stack) == 1:
                    progress_widget = ProgressItemWidget(self)
                    progress_widget.set_progress_text(current_task, status=False)
                    self.progress_widget.append(progress_widget)
                    self.detailed_progression_layout.insertWidget(self.detailed_progression_layout.count(), progress_widget)
            elif 'End' in message:
                current_task = message.strip().split('-')[1].strip()
                current_step = int(message.strip().split('(')[1].split('/')[0])
                if len(self.process_stages_stack) == 1:
                    self.progress_label.setText("Overall progress:\n\t" + str(current_step) + " / " + str(self.processing_steps))
                    self.progress_widget[-1].set_progress_text(self.process_stages_stack[-1]['runtime'], status=True)
                    self.circular_progressbar.advance(current_step, self.process_stages_stack[-1]['total_steps'])
                if current_step == self.process_stages_stack[-1]['total_steps']:
                    self.process_stages_stack.pop(-1)
            elif 'Runtime' in message:
                runtime = float(message.strip().split(':')[-1].split('seconds')[0].strip())
                self.process_stages_stack[-1]['runtime'] = '{:.2f}'.format(runtime)


class ProgressItemWidget(QWidget):
    def __init__(self, parent=None):
        super(ProgressItemWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.layout = QHBoxLayout(self)
        self.status_pushbutton = QPushButton()
        self.status_pushbutton.setCheckable(False)
        self.progress_label = QLabel()

        self.layout.addWidget(self.status_pushbutton)
        self.layout.addWidget(self.progress_label)

    def __set_layout_dimensions(self):
        self.status_pushbutton.setFixedSize(QSize(20, 20))
        self.status_pushbutton.setIconSize(QSize(20, 20))
        self.status_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/radio_round_toggle_off_icon.png')))
        self.progress_label.setFixedHeight(20)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        self.progress_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        font-size: 16px;
        }""")

        self.status_pushbutton.setStyleSheet("""
        QPushButton{
        border-style: none;
        }""")

    def __set_connections(self):
        pass

    def set_progress_text(self, text: str, status: bool) -> None:
        """
        Displays the ongoing process task when the current step is starting. Upon step completion, indicating by a True
        status, the total elapsed time for the current step is appended to the displayed text.

        Parameters
        ----------
        text: str
            Indication coming from the LOG: elements, either as the name of the ongoing step (i.e., when Begin), or the
            elapsed time (in seconds) as a string (i.e., when End).
        status: bool
            Completion status. Set to False is the step just began and to True upon step completion.
        """
        if status:
            self.status_pushbutton.setIcon(QIcon(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/radio_round_toggle_on_icon.png')))
            self.progress_label.setText(self.progress_label.text()[:-3] + ' (' + text + 's)')
        else:
            new_text = text + ' ...'
            if len(new_text) > 30:
                nb_words = len(new_text.split(' '))
                final_text = ' '.join(new_text.split(' ')[:int(nb_words / 2)]) + '\n' + ' '.join(new_text.split(' ')[int(nb_words / 2):])
                self.progress_label.setFixedHeight(40)
                self.progress_label.setText(final_text)
            else:
                self.progress_label.setText(new_text)
