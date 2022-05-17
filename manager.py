import getopt
import sys
import json
from strings.android import AndroidStringFile
from munch import Munch

from strings.ios import iOSStringFile
from strings.strings import StringsMap, StringsMapSchema


def main(argv):
    help_message =  """
usage: manager.py [-h] -c <path to config file>

optional arguments:
        -h, --help\t\tshow this help message and exit
        -c, --config\t\tpath to config file
        -s, --save\t\tsave values from index file into the project files
    """
    try:
        opts, args = getopt.getopt(argv,"hc:s",[])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    config = None
    json_data = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_message)
            sys.exit()
        elif opt in ("-c", "--config"):
            with open(arg, 'r') as f:
                config_data = f.read()
            config = Munch.fromDict(json.loads(config_data))
        elif opt in ("-s", "--save"):
            with open("string_index.json", 'r') as f:
                json_data = f.read()
    
    if config:
        if json_data:
            result = StringsMapSchema().loads(json_data)
            print(result.index)
        else:
            string_files = [
                *AndroidStringFile.get_string_files(config.android),
                *iOSStringFile.get_string_files(config.ios)
            ]
            map = StringsMap(string_files, [*config.android.languages, *config.ios.languages])
            map_dict = StringsMapSchema().dumps(map, indent=4, ensure_ascii=False, sort_keys=True)
            with open("string_index.json", 'w') as f:
                f.write(map_dict)

if __name__ == '__main__':
    main(sys.argv[1:])
