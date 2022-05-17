import os
import traceback

from utilities.utilities import remove_files


class StringItem:
    STRING_TYPE = 'string'
    PLURAL_TYPE = 'plural'
    
    def __init__(self, key, type, translatable=True, value=None, plural_items=None, comments=None):
        self.key = key
        self.value = value
        self.plural_items = plural_items
        self.type = type
        self.translatable = translatable
        self.translated = False
        self.comments = comments


class PluralItem:
    def __init__(self, quantity, quantity_value):
        self.quantity = quantity
        self.quantity_value = quantity_value


class StringFile:

    def __init__(self, filepath, language, default=False):
        self.language = language
        self.values = []
        self.filepath = filepath
        self.default = default
        self.read_from_file()

    def read_from_file(self):
        print('>>> Reading {}\npath: {}\n'.format(self.language, self.filepath))
        directory = os.path.dirname(self.filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
            with open(self.filepath, "w") as f:
                f.write(self.empty_body)
        self.values = self.parse()
        print('parsed {} items'.format(len(self.values)))
        print('\n>>> Closing {}\n\n'.format(self.language))

    @property
    def header(self):
        raise NotImplementedError("header must be implemented")

    @property
    def body(self):
        raise NotImplementedError("body must be implemented")

    @property
    def footer(self):
        raise NotImplementedError("footer must be implemented")

    @property
    def empty_body(self):
        return f'{self.header}\n{self.footer}'

    def parse(self):
        raise NotImplementedError("parse must be implemented")

    @staticmethod
    def get_string_files(config):
        raise NotImplementedError('get_string_files must be implemented')

    def update_strings_file(self):
        try:
            original = self.filepath
            old = original + '.old'
            new = original + '.new'
            if os.path.isfile(original):
                self.save_to_file(new)
                os.rename(original, old)
                os.rename(new, original)
                remove_files([old, new])
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    def save_to_file(self, path):
        with open(path, 'w') as f:
            f.write(f'{self.header}{self.body}{self.footer}')

class Translation:

    def __init__(self, language, value):
        self.language = language
        self.value = value

class StringIndex:
    # add type
    def __init__(self, translatable=True):
        self.value = value
        self.translatable = translatable
        self.keys = []
        self.translations = []
        

class StringsMap:
    
    def __init__(self, string_files):
        self.string_files = string_files
        self.index = {}
        self.map()

    def map(self):
        def find_global_obj_by_string_key(key):
            for info in self.index.values():
                if key in info['keys']:
                    return info


        def update_global_obj_by_key(key, language, value):
            for info in self.index.values():
                if key in info['keys']:
                    info['translations'][language] = value

        default_files = list(filter(lambda d: d.default == True, self.string_files))
        for default_file in default_files:
            for string_item in list(filter(lambda s: s.type == StringItem.STRING_TYPE and s.translatable, default_file.values)):
                if string_item.value in self.index:
                    self.index[string_item.value]['keys'].append(string_item.key)
                else:
                    self.index[string_item.value] = {
                        "type": "string",
                        "value": string_item.value,
                        "translations": {},
                        'keys': [string_item.key],
                        'translatable': string_item.translatable,
                    }

        has_conflicts = False
        translation_files = list(filter(lambda d: d.default == False, self.string_files))
        for translation_file in translation_files:
            for string_item in list(filter(lambda s: s.type == StringItem.STRING_TYPE and s.translatable, translation_file.values)):
                global_obj = find_global_obj_by_string_key(string_item.key)
                try:
                    raw_value = global_obj['value']
                except TypeError:
                    print(f'error with value: {string_item.key} - {translation_file.language}')
                    exit(1)
                translated_value = global_obj['translations'].get(translation_file.language, raw_value)
                if string_item.value != raw_value:
                    if raw_value != translated_value and translated_value != string_item.value:
                        print(f'conflicting translation for {translation_file.language}: "{raw_value}" translated to "{translated_value}" but another file has "{string_item.value}"')
                        has_conflicts = True
                    elif raw_value == translated_value and string_item.value not in [translated_value, raw_value]:
                        update_global_obj_by_key(string_item.key, translation_file.language, string_item.value)

        if has_conflicts:
            print('Exiting due to conflicts. Please resolve the conflicts and try again.')
            exit(1)
