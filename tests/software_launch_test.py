import os
import json
import shutil
import configparser
import logging
import sys
import subprocess
import traceback
import zipfile


def software_launch_test():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Running software launch unit test.\n")

    try:

        import platform
        if platform.system() == 'Windows':
            subprocess.check_call(['./dist/Raidionics/Raidionics'], shell=True)
        else:
            subprocess.check_call(['./dist/Raidionics/Raidionics'])
    except Exception as e:
        logging.error("Error during software launch unit test with: \n {}.\n".format(traceback.format_exc()))
        raise ValueError("Error during software launch unit test with.\n")

    logging.info("Software launch unit test succeeded.\n")


software_launch_test()
