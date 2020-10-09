import os


def ensure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def list_dir(path, type):
    """
    List files in a folder given by the path filtered by type.
    """
    return [f for f in os.listdir(path) if f.endswith(type)]
