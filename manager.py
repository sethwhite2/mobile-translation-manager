import getopt
import sys
import json
from sheets.sheets import upload_to_google_sheet
from strings.android import AndroidStringFile
from munch import Munch

from strings.ios import iOSStringFile
from strings.map import StringsMap, StringsMapSchema
from utilities.utilities import get_generic_language


def get_generic_languages(config, exclude_default=False):
    languages = []
    for application in config.applications:
        application_languages = application.languages
        if exclude_default:
            application_languages.remove(application.default_language)
        languages.extend(application_languages)
    languages = set(map(lambda l: get_generic_language(l), languages))
    return sorted(languages)


def get_string_files(config):
    string_files = []
    for application in config.applications:
        platform = application.platform
        if platform == "ios":
            string_files.extend(iOSStringFile.get_string_files(application))
        elif platform == "android":
            string_files.extend(AndroidStringFile.get_string_files(application))
        else:
            raise Exception(f"{platform} is not a supported platform")
    return string_files


def populate_with_new_keys(config):
    for application in config.applications:
        platform = application.platform
        if platform == "android":
            AndroidStringFile.populate_with_new_keys(application)
        elif platform == "ios":
            iOSStringFile.popuplate_with_new_keys(application)
        else:
            raise Exception(f"{platform} is not a supported platform")


def main(argv):
    help_message =  """
usage: manager.py [-h] -c <path to config file> [-u, -s, -d]

optional arguments:
        -h, --help\t\tshow this help message and exit
        -c, --config\t\tpath to config file
        -s, --save\t\tsave values from index file into the project files
        -u, --update\t\tupdate the values in index file
        -d, --update\t\tdeploy index file to google sheet
    """
    try:
        opts, args = getopt.getopt(argv,"hc:sud",[])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    config = None
    update_index = False
    save = False
    deploy = False
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
        elif opt in ("-d", "--deploy"):
            deploy = True
    
    if not config:
        print(help_message)
        sys.exit(2)

    if update_index:
        populate_with_new_keys(config)
        string_files = get_string_files(config)
        generic_languages = get_generic_languages(config)
        map = StringsMap(string_files, generic_languages)
        map_dict = StringsMapSchema().dumps(map, indent=4, ensure_ascii=False, sort_keys=True)
        with open(config.string_index_filename, 'w') as f:
            f.write(map_dict)
    if save:
        with open(config.string_index_filename, 'r') as f:
            json_data = f.read()
        map = StringsMapSchema().loads(json_data)
        string_files = get_string_files(config)
        map.update_files(string_files)
    if deploy:
        with open(config.string_index_filename, 'r') as f:
            json_data = f.read()
        generic_languages =  get_generic_languages(config, exclude_default=True)
        print(generic_languages)
        map = StringsMapSchema().loads(json_data)
        upload_to_google_sheet(config.sheets_api.spreadsheet_id, map, generic_languages)


if __name__ == '__main__':
    main(sys.argv[1:])
