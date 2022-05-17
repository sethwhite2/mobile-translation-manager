
import os
from re import compile
from strings.strings import StringFile, StringItem

re_translation = compile(r'^"(.+)" = "(.+)";$')
re_comment_single = compile(r'^/\*.*\*/$')
re_comment_start = compile(r'^/\*.*$')
re_comment_end = compile(r'^.*\*/$')


class iOSStringFile(StringFile):
    
    @property
    def header(self):
        return ""

    @property
    def body(self):
        return ""

    @property
    def footer(self):
        return ""

    def parse(self):
        string_items = []
        with open(self.filepath, 'r') as f:
            line = f.readline()
            while line:
                comments = [line]
                if not re_comment_single.match(line):
                    while line and not re_comment_end.match(line):
                        line = f.readline()
                        comments.append(line)
                
                line = f.readline()
                if line and re_translation.match(line):
                    translation = line
                else:
                    continue
                
                line = f.readline()
                while line and line == u'\n':
                    line = f.readline()

                key, value = re_translation.match(translation).groups()
                string_items.append(
                    StringItem(
                        key,
                        StringItem.STRING_TYPE,
                        value=value,
                        comments=comments
                    )
                )

        return string_items

    @staticmethod
    def get_string_files(config):
        # can do away with module map
        string_files = []
        for module in config.modules:
            for language in config.languages:
                if config.has_module_map:
                    path = os.path.normpath(f'{config.project_dir}/{module.name}/{module.strings_dir}/{language}.lproj/{config.strings_filename}')
                else:
                    path = os.path.normpath(f'{config.project_dir}/{module}/{config.strings_dir}/{language}.lproj/{config.strings_filename}')
                string_files.append(iOSStringFile(path, language, default=language == config.default_language))
        return string_files
