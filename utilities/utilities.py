import os
import re

def remove_files(filepaths):
    for filepath in filepaths:
        if os.path.isfile(filepath):
            os.remove(filepath)


def get_generic_language(language):
    return re.sub(r'(-[r]|-)', '_', language)


def get_generic_languages_from_config(config):
    languages = [*config.android.languages, *config.ios.languages]
    return list(map(lambda l: get_generic_language(l), languages))
