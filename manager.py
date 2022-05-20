from datetime import datetime
import getopt
import os
from pathlib import Path
import shutil
import sys
import json
from sheets.sheets import fetch_from_google_sheet, upload_to_google_sheet
from strings.android import AndroidStringFile
from munch import Munch

from strings.ios import iOSStringFile
from strings.map import StringsMap, StringsMapSchema
from utilities.utilities import get_generic_language

# todo: add verbose option to log output or action
# todo: implement tqdm for progress


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


def init(config):
    if os.path.exists(config.string_index_filename):
        user_input = input(f"The string index file already exits: {config.string_index_filename}\nIf you continue, the file will be overwritten. Continue? [y/n]\t")
        if user_input == 'y':
            print(f"Overwritting {config.string_index_filename}")
        else:
            print("exiting")
            exit(2)

    string_files = get_string_files(config)
    generic_languages = get_generic_languages(config)
    map = StringsMap(string_files, generic_languages)
    map_dict = StringsMapSchema().dumps(map, indent=4, ensure_ascii=False, sort_keys=True)
    with open(config.string_index_filename, 'w') as f:
        f.write(map_dict)


def sync(config):
    # create backup
    string_index_path = f"{os.getcwd()}/{config.string_index_filename}"
    shutil.copyfile(string_index_path, f"{string_index_path}.{datetime.now().strftime('%s')}.bak")

    # get current map
    with open(config.string_index_filename, 'r') as f:
        json_data = f.read()
    map = StringsMapSchema().loads(json_data)
    
    # get strings files
    string_files = get_string_files(config)

    # update map with project values
    map.update_files(string_files)

    # update map with edited values from translator
    fetch_from_google_sheet(config.sheets_api.spreadsheet_id, map)

    # save to file
    map_dict = StringsMapSchema().dumps(map, indent=4, ensure_ascii=False, sort_keys=True)
    with open(config.string_index_filename, 'w') as f:
        f.write(map_dict)


def save(config):
    # todo: figure out how to incorperate this with the save
    # need to make sure project files have the same keys as the default files
    #populate_with_new_keys(config)
    with open(config.string_index_filename, 'r') as f:
        json_data = f.read()
    map = StringsMapSchema().loads(json_data)
    string_files = get_string_files(config)
    map.update_files(string_files)


def deploy(config):
    with open(config.string_index_filename, 'r') as f:
        json_data = f.read()
    generic_languages =  get_generic_languages(config, exclude_default=True)
    map = StringsMapSchema().loads(json_data)
    upload_to_google_sheet(config.sheets_api.spreadsheet_id, map, generic_languages)


def main(argv):
    help_message =  """
usage: manager.py [-h] -c <path to config file> [init, -s, --save, -d]

optional arguments:
        init\t\tcreate a strings index file based on the current project files
        -h, --help\t\tshow this help message and exit
        -c, --config\t\tpath to config file
        -s, --sync\t\sync the values in index file with google sheet and project files
        -d, --update\t\tdeploy index file to google sheet
        --save\t\tsave values from index file into the project files
    """
    try:
        opts, args = getopt.getopt(argv, "hc:d", ["init", "sync", "save"])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    config = None
    should_init = False
    should_save = False
    should_deploy = False
    should_sync = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_message)
            sys.exit()
        elif opt in ("-c", "--config"):
            with open(arg, 'r') as f:
                config_data = f.read()
            config = Munch.fromDict(json.loads(config_data))
        elif opt in ("--save"):
            should_save = True
        elif opt in ("-d", "--deploy"):
            should_deploy = True
        elif opt in ("--sync"):
            should_sync = True
        elif opt in ("--init"):
            should_init = True
    
    if not config:
        print(help_message)
        sys.exit(2)

    if should_init:
        init(config)
        return
    if should_sync:
        sync(config)
    if should_save:
        save(config)
    if should_deploy:
        deploy(config)


if __name__ == '__main__':
    main(sys.argv[1:])
    exit(0)
