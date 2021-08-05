import getopt, traceback
# macOS relevant
import os
os.environ['LC_CTYPE'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"

# macOS Big Sur related: https://stackoverflow.com/questions/64818879/is-there-any-solution-regarding-to-pyqt-library-doesnt-work-in-mac-os-big-sur/64856281
os.environ['QT_MAC_WANTS_LAYER'] = '1'

# relevant for PySide, Qt stuff. See issue here: https://www.programmersought.com/article/8605863159/
import PySide2
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

import sys
from PySide2.QtWidgets import QApplication
from main_gui import MainWindow


def main(argv):
    gui_usage = 1
    input_filename = ''
    input_tumor_segmentation_filename = ''
    output_folder = ''
    gpu_id = '-1'
    try:
        opts, args = getopt.getopt(argv, "hg:i:s:o:d:", ["gui=1"])
    except getopt.GetoptError:
        print('main.py -g <use_gui> [-i <input_filename> -s <input_tumor_segmentation_filename> -o <output_folder> -d <gpu_id>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -g <use_gui> [-i <input_filename> -s <input_tumor_segmentation_filename> -o <output_folder> -d <gpu_id>]')
            sys.exit()
        elif opt in ("-g", "--use_gui"):
            gui_usage = arg
        elif opt in ("-i", "--input_filename"):
            input_filename = arg
        elif opt in ("-s", "--input_tumor_segmentation_filename"):
            input_tumor_segmentation_filename = arg
        elif opt in ("-o", "--output_folder"):
            output_folder = arg
        elif opt in ("-d", "--gpu_id"):
            gpu_id = arg
    try:
        if gui_usage == 1:
            app = QApplication(sys.argv)

            window = MainWindow(application=app)
            window.show()

            app.exec_()
        else:
            from diagnosis.main import diagnose_main
            diagnose_main(input_volume_filename=input_filename,
                          input_segmentation_filename=input_tumor_segmentation_filename,
                          output_folder=output_folder, gpu_id=gpu_id)
    except Exception as e:
        print('Process could not proceed. Caught error: {}'.format(e.args[0]))
        print('{}'.format(traceback.format_exc()))


if __name__ == "__main__":
    main(sys.argv[1:])
