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


class StringsMap:
    
    def __init__(self, string_files):
        self.string_files = string_files
        self.map()

    def map(self):
        default_files = list(filter(lambda d: d.default == True, self.string_files))
        print(len(default_files))
