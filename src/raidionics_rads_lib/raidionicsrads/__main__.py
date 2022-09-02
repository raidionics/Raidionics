import argparse
import os
import sys
import traceback
import logging
from raidionicsrads.compute import run_rads


def path(string):
    if os.path.exists(string):
        return string
    else:
        sys.exit(f'File not found: {string}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', metavar='config', type=path, help='Path to the configuration file (*.ini)')
    parser.add_argument('--verbose', help="To specify the level of verbose, Default: warning", type=str,
                        choices=['debug', 'info', 'warning', 'error'], default='warning')

    argsin = sys.argv[1:]
    args = parser.parse_args(argsin)
    config_filename = args.config

    logging.basicConfig()
    logging.getLogger().setLevel(logging.WARNING)

    if args.verbose == 'debug':
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose == 'info':
        logging.getLogger().setLevel(logging.INFO)
    elif args.verbose == 'error':
        logging.getLogger().setLevel(logging.ERROR)

    try:
        run_rads(config_filename=config_filename)
    except Exception as e:
        logging.error('{}'.format(traceback.format_exc()))


if __name__ == "__main__":
    logging.info("Internal main call.\n")
    main()

