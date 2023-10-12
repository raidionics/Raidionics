import os
import shutil
import logging
import sys
import subprocess
import traceback
import platform
import signal
import time


def software_launch_test():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Running software launch unit test.\n")

    try:
        stdout = None
        stderr = None
        build_executable_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'dist', 'Raidionics')
        logging.info("Running executable from: {}.\n".format(build_executable_path))
        if platform.system() == 'Windows':
            proc = subprocess.Popen([os.path.join(build_executable_path, 'Raidionics')], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True,
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            stdout, stderr = proc.communicate()
            time.sleep(10)
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            proc.kill()
        else:
            proc = subprocess.Popen([os.path.join(build_executable_path, 'Raidionics')], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            # stdout, stderr = proc.communicate()
            time.sleep(10)
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

        # # @TODO. Should likely parse the stdout or stderr content to identify any potential issue!
        # if 'error' in stderr.decode("utf-8").lower() or 'failed' in stderr.decode("utf-8").lower():
        #     raise ValueError("Error during software launch unit test with.\n")
    except Exception as e:
        logging.error("Error during software launch unit test with: \n {}.\n".format(traceback.format_exc()))
        raise ValueError("Error during software launch unit test with.\n")

    logging.info("Software launch unit test succeeded.\n")


software_launch_test()
