import os


def ensure_exists(path: str):
    """
    Creates a folder if it does not exists yet.
    Returns: In any case the input path is returned
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def list_dir(path: str, type: str):
    """
    List files in a folder given by the path filtered by type.
    """
    return sorted(f for f in os.listdir(path) if f.endswith(type))
