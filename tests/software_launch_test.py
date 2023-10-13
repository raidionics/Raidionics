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
            time.sleep(10)
            stdout = proc.stdout
            stderr = proc.stderr
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            proc.kill()
        else:
            proc = subprocess.Popen([os.path.join(build_executable_path, 'Raidionics')], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, preexec_fn=os.setsid)
            time.sleep(10)
            stdout = proc.stdout
            stderr = proc.stderr
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

        # Parsing the content of stderr to identify any potential issue or problem!
        error_msg = stderr.read().decode("utf-8")
        print("Collected stdout: {}\n".format(stdout.read().decode("utf-8")))
        print("Collected stderr: {}\n".format(error_msg))
        if error_msg is not None:
            if 'error' in error_msg.lower() or 'failed' in error_msg.lower():
                raise ValueError("Error during software launch unit test.\n")
    except Exception as e:
        logging.error("Error during software launch unit test with: \n {}.\n".format(traceback.format_exc()))
        raise ValueError("Error during software launch unit test with.\n")

    logging.info("Software launch unit test succeeded.\n")


software_launch_test()
