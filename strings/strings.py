import os
import traceback

from utilities.utilities import remove_files
from marshmallow import Schema, fields, post_load

STRING_TYPE = 'string'
PLURAL_TYPE = 'plural'


class StringItem:
    
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
        self._read_from_file()

    def _read_from_file(self):
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


class StringIndexSchema(Schema):
    value = fields.Str()
    type = fields.Str()
    translatable = fields.Bool()
    keys = fields.List(fields.Str())
    translations = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make_string_index(self, data, **__):
        return StringIndex(**data)

class StringIndex:

    def __init__(self, value, type, key=None, languages=None, translatable=True, translations=None, keys=None):
        self.value = value
        self.type = type
        self.translatable = translatable
        if translations and keys:
            self.keys = keys
            self.translations = translations
        else:
            self.keys = [key] if key else []
            self.translations = { language: "" for language in languages } if languages else {}
    

class StringsMapSchema(Schema):
    index = fields.Dict(keys=fields.Str(), values=fields.Nested(StringIndexSchema()))

    @post_load
    def make_strings_map(self, data, **__):
        return StringsMap(**data)

class StringsMap:
    # only string types supported at the moment
    
    def __init__(self, string_files=None, languages=None, index=None):
        if string_files and languages:
            self.index = {}
            self._map(string_files, languages)
        else:
            self.index = index

    def _map(self, string_files, languages):
        def find_index_by_key(key):
            for index in self.index.values():
                if key in index.keys:
                    return index

        def update_index(key, language, value):
            for index in self.index.values():
                if key in index.keys:
                    index.translations[language] = value

        default_files = list(filter(lambda d: d.default == True, string_files))
        for default_file in default_files:
            for string_item in list(filter(lambda s: s.type == STRING_TYPE and s.translatable, default_file.values)):
                if string_item.value in self.index:
                    self.index[string_item.value].keys.append(string_item.key)
                else:
                    self.index[string_item.value] = StringIndex(
                        string_item.value,
                        STRING_TYPE,
                        string_item.key,
                        languages,
                        string_item.translatable
                    )

        has_conflicts = False
        translation_files = list(filter(lambda d: d.default == False, string_files))
        for translation_file in translation_files:
            for string_item in list(filter(lambda s: s.type == STRING_TYPE and s.translatable, translation_file.values)):
                index = find_index_by_key(string_item.key)
                try:
                    raw_value = index.value
                except Exception:
                    print(f'error with value: {string_item.key} - {translation_file.language}\npath: {translation_file.filepath}')
                    exit(1)
                translated_value = index.translations.get(translation_file.language, raw_value)
                if translated_value and string_item.value != raw_value:
                    if raw_value != translated_value and translated_value != string_item.value:
                        print(f'conflicting translation for {translation_file.language}: "{raw_value}" translated to "{translated_value}" but another file has "{string_item.value}"')
                        has_conflicts = True
                    elif raw_value == translated_value and string_item.value not in [translated_value, raw_value]:
                        update_index(string_item.key, translation_file.language, string_item.value)
                elif string_item.value:
                    update_index(string_item.key, translation_file.language, string_item.value)

        if has_conflicts:
            print('Exiting due to conflicts. Please resolve the conflicts and try again.')
            exit(1)
