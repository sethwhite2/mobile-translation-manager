from email import header
from email.quoprimime import body_check
import os
from bs4 import BeautifulSoup
import traceback

from utilities.utilities import remove_files


class StringItem:
    STRING_TYPE = 'string'
    PLURAL_TYPE = 'plural'
    
    def __init__(self, key, type, translatable, value=None, plural_items=None):
        self.key = key
        self.value = value
        self.plural_items = plural_items
        self.type = type
        self.translatable = translatable
        self.translated = False


class PluralItem:
    def __init__(self, quantity, quantity_value):
        self.quantity = quantity
        self.quantity_value = quantity_value


class StringFile:

    def __init__(self, filepath, language):
        self.language = language
        self.values = []
        self.filepath = filepath
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


class AndroidStringFile(StringFile):
    
    @property
    def header(self):
        return "{}{}".format(
            '<?xml version="1.0" encoding="utf-8"?>\n',
            '<resources xmlns:tools="http://schemas.android.com/tools"{}>\n'.format(' tools:ignore=\"MissingTranslation\"' if self.language != 'default' else '')
        )

    @property
    def body(self):
        body_string = ""
        sorted_values = sorted(self.values, key=lambda x: x.key)
        for value in sorted_values:
            value_type = value.type
            if value_type == StringItem.STRING_TYPE:
                body_string += f'    <string name="{value.key}">{value.value}</string>\n'
            elif value_type == StringItem.PLURAL_TYPE:
                body_string += f'    <plurals name="{value.key}" tools:ignore="UnusedQuantity">\n'
                for plural_item in value.plural_items:
                    body_string += f'        <item quantity="{plural_item.quantity}">{plural_item.quantity_value}</item>\n'
                body_string += f'    </plurals>\n'
            else:
                raise Exception("Invalid value type.")
        return body_string

    @property
    def footer(self):
        return "{}".format(
            '</resources>\n'
        )

    def parse(self):
        def get_plural_items(items):
            plural_items = []
            for item in items:
                plural_items.append(
                    PluralItem(
                        item['quantity'],
                        item.text
                    )
                )
            return plural_items

        xml = open(self.filepath).read().encode('utf-8')
        soup = BeautifulSoup(xml, features='xml')
        string_items = []
        for xml_string in soup.findAll('string'):
            string_items.append(
                StringItem(
                    xml_string['name'],
                    StringItem.STRING_TYPE,
                    xml_string.get('translatable', None) != 'false',
                    value=xml_string.text,
                )
            )

        for plurals in soup.findAll('plurals'):
            items = plurals.findAll('item')
            string_items.append(
                StringItem(
                    plurals['name'],
                    StringItem.PLURAL_TYPE,
                    plurals.get('translatable', None) != 'false',
                    plural_items=get_plural_items(items)
                )
            )
        return string_items

class iOSStringFile(StringFile):
    oink = None
