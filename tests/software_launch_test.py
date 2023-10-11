import os
import shutil
import logging
import sys
import subprocess
import traceback
import platform


def software_launch_test():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Running software launch unit test.\n")

    try:
        build_executable_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'dist', 'Raidionics')
        logging.info("Running executable from: {}.\n".format(build_executable_path))
        if platform.system() == 'Windows':
            subprocess.check_call([os.path.join(build_executable_path, 'Raidionics')], shell=True)
        else:
            subprocess.check_call([os.path.join(build_executable_path, 'Raidionics')])
    except Exception as e:
        logging.error("Error during software launch unit test with: \n {}.\n".format(traceback.format_exc()))
        raise ValueError("Error during software launch unit test with.\n")

    logging.info("Software launch unit test succeeded.\n")


software_launch_test()
