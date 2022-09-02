import getopt
import os
import sys
import logging
import traceback
from raidionicsrads.compute import run_rads
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def main(argv):
    config_filename = None
    try:
        logging.basicConfig(format="%(asctime)s ; %(name)s ; %(levelname)s ; %(message)s", datefmt='%d/%m/%Y %H.%M')
        logging.getLogger().setLevel(logging.WARNING)
        opts, args = getopt.getopt(argv, "h:c:v:", ["Config=", "Verbose="])
    except getopt.GetoptError:
        print('usage: main.py -c <configuration_filepath> (--Verbose <mode>)')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -c <configuration_filepath> (--Verbose <mode>)')
            sys.exit()
        elif opt in ("-c", "--Config"):
            config_filename = arg
        elif opt in ("-v", "--Verbose"):
            if arg.lower() == 'debug':
                logging.getLogger().setLevel(logging.DEBUG)
            elif arg.lower() == 'info':
                logging.getLogger().setLevel(logging.INFO)
            elif arg.lower() == 'warning':
                logging.getLogger().setLevel(logging.WARNING)
            elif arg.lower() == 'error':
                logging.getLogger().setLevel(logging.ERROR)

    if not config_filename or not os.path.exists(config_filename):
        print('usage: main.py -c <config_filepath> (--Verbose <mode>)')
        sys.exit()

    try:
        run_rads(config_filename=config_filename)
    except Exception as e:
        logging.error('{}'.format(traceback.format_exc()))


if __name__ == "__main__":
    main(sys.argv[1:])

