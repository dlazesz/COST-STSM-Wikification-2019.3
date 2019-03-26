import os


def get_files_from_dir(directory):
    files = list()
    for path, subdirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith("xml"):
                files.append(os.path.join(path, filename))
    files.sort()

    return files
