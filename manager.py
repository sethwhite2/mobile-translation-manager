from strings.strings import AndroidStringFile


if __name__ == '__main__':
    path = "/Users/sethwhite/FieldAgentProjects/android-app/FieldAgentUI/src/main/res/values-en-rGB/strings.xml"
    language = "en-rGB"
    string_file = AndroidStringFile(path, language)
    string_file.update_strings_file()

    exit(0)