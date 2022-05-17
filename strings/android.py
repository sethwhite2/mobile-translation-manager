
import os
from bs4 import BeautifulSoup
from strings.strings import STRING_TYPE, PLURAL_TYPE, PluralItem, StringFile, StringItem


class AndroidStringFile(StringFile):
    
    @property
    def header(self):
        return "{}{}".format(
            '<?xml version="1.0" encoding="utf-8"?>\n',
            '<resources xmlns:tools="http://schemas.android.com/tools"{}>\n'.format(' tools:ignore=\"MissingTranslation\"' if self.language != '' else '')
        )

    @property
    def body(self):
        body_string = ""
        sorted_values = sorted(self.values, key=lambda x: x.key)
        for value in sorted_values:
            value_type = value.type
            if value_type == STRING_TYPE:
                body_string += f'    <string name="{value.key}">{value.value}</string>\n'
            elif value_type == PLURAL_TYPE:
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
                    STRING_TYPE,
                    translatable=xml_string.get('translatable', None) != 'false',
                    value=xml_string.text,
                )
            )

        for plurals in soup.findAll('plurals'):
            items = plurals.findAll('item')
            string_items.append(
                StringItem(
                    plurals['name'],
                    PLURAL_TYPE,
                    translatable=plurals.get('translatable', None) != 'false',
                    plural_items=get_plural_items(items)
                )
            )
        return string_items

    @staticmethod
    def get_string_files(config):
        string_files = []
        for module in config.modules:
            for language in config.languages:
                if config.has_module_map:
                    strings_dir = f'{module.strings_dir}-{language}' if language else module.strings_dir
                    path = os.path.normpath(f'{config.project_dir}/{module.name}/{strings_dir}/{config.strings_filename}')
                else:
                    strings_dir = f'{config.strings_dir}-{language}' if language else config.strings_dir
                    path = os.path.normpath(f'{config.project_dir}/{module}/{strings_dir}/{config.strings_filename}')
                string_files.append(AndroidStringFile(path, language, language == config.default_language))
        return string_files
