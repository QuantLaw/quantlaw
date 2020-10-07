import os


def ensure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def list_dir(path, type):
    return [f for f in os.listdir(path) if f.endswith(type)]
