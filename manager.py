import getopt
import sys
import json
from strings.android import AndroidStringFile
from munch import Munch

from strings.ios import iOSStringFile
from strings.map import StringsMap, StringsMapSchema
from utilities.utilities import get_generic_languages_from_config


def main(argv):
    help_message =  """
usage: manager.py [-h] -c <path to config file> -u

optional arguments:
        -h, --help\t\tshow this help message and exit
        -c, --config\t\tpath to config file
        -s, --save\t\tsave values from index file into the project files
        -u, --update\t\tupdate the values in index file
    """
    try:
        opts, args = getopt.getopt(argv,"hc:su",[])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    config = None
    json_data = None
    save = False
    update_index = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_message)
            sys.exit()
        elif opt in ("-c", "--config"):
            with open(arg, 'r') as f:
                config_data = f.read()
            config = Munch.fromDict(json.loads(config_data))
        elif opt in ("-u", "--update"):
            update_index = True
        elif opt in ("-s", "--save"):
            save = True
            with open("string_index.json", 'r') as f:
                json_data = f.read()
    
    if config and save or update_index:
        string_files = [
            *AndroidStringFile.get_string_files(config.android),
            *iOSStringFile.get_string_files(config.ios)
        ]
        if save and json_data:
            map = StringsMapSchema().loads(json_data)
            map.update_files(string_files)
        elif update_index:
            map = StringsMap(string_files, get_generic_languages_from_config(config))
            map_dict = StringsMapSchema().dumps(map, indent=4, ensure_ascii=False, sort_keys=True)
            with open("string_index.json", 'w') as f:
                f.write(map_dict)
    else: 
        print(help_message)
        sys.exit(2)

if __name__ == '__main__':
    main(sys.argv[1:])
