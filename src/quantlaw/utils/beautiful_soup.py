import os

from bs4 import BeautifulSoup


def create_soup(path):
    """
    Reads a file and returns a lxml-xml BeautifulSoup object.
    """
    with open(path, encoding="utf8") as f:
        return BeautifulSoup(f.read(), "lxml-xml")


def save_soup(soup: BeautifulSoup, path: str):
    """
    Writes an BeautifulSoup object to a file at a given path.
    """
    try:
        with open(path, "w", encoding="utf8") as f:
            f.write(str(soup))
    except Exception:  # Clean file if error
        if os.path.exists(path):
            os.remove(path)
        raise


def find_parent_with_name(tag: str, name: str):
    """
    Args:
        tag: A tag of a BeautifulSoup
        name: name to search in parents
    Returns: the nearest ancestor with the name
    """
    if tag.name == name:
        return tag
    else:
        return find_parent_with_name(tag.parent, name)
