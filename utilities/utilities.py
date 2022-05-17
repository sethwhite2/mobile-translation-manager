import os

def remove_files(filepaths):
    for filepath in filepaths:
        if os.path.isfile(filepath):
            os.remove(filepath)
