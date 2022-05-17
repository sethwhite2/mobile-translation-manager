import getopt
import sys
import json
import os
from strings.android import AndroidStringFile
from munch import Munch

from strings.ios import iOSStringFile
from strings.strings import StringsMap


def main(argv):
    help_message =  """
usage: manager.py [-h] -c <path to config file>

optional arguments:
        -h, --help\t\tshow this help message and exit
        -c, --config\t\tpath to config file
    """
    try:
        opts, args = getopt.getopt(argv,"hc:",[])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    config = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_message)
            sys.exit()
        elif opt in ("-c", "--config"):
            with open(arg, 'r') as f:
                json_data = f.read()
            config = Munch.fromDict(json.loads(json_data))
    
    if config:
        string_files = [
            *AndroidStringFile.get_string_files(config.android),
            *iOSStringFile.get_string_files(config.ios)
        ]
        StringsMap(string_files)


if __name__ == '__main__':
    main(sys.argv[1:])
