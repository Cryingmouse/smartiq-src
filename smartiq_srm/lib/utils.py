import os


def check_file_path_exist(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File path does not exist: {file_path}.")