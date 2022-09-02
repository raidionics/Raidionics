import os
import sys
import traceback
import argparse
import logging
import platform

from raidionicsseg.fit import run_model
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def path(string):
    if os.path.exists(string):
        return string
    else:
        sys.exit(f'File not found: {string}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', metavar='config', type=path, help='Path to the configuration file (*.ini)')
    parser.add_argument('-v', '--verbose', help="To specify the level of verbose, Default: warning", type=str,
                        choices=['debug', 'info', 'warning', 'error'], default='warning')

    argsin = sys.argv[1:]
    args = parser.parse_args(argsin)

    config_filename = args.config

    logging.basicConfig(format="%(asctime)s ; %(name)s ; %(levelname)s ; %(message)s", datefmt='%d/%m/%Y %H.%M')
    logging.getLogger().setLevel(logging.DEBUG)

    if args.verbose == 'debug':
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose == 'info':
        logging.getLogger().setLevel(logging.INFO)
    elif args.verbose == 'error':
        logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Received arguments: {}".format(args))
    try:
        run_model(config_filename=config_filename)
    except Exception as e:
        print('{}'.format(traceback.format_exc()))


if __name__ == "__main__":
    if platform.system() == 'Windows':
        from multiprocessing import freeze_support
        freeze_support()

    logging.info("Internal main call.")
    main()

