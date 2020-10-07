import os

from bs4 import BeautifulSoup


def create_soup(path):
    with open(path, encoding="utf8") as f:
        return BeautifulSoup(f.read(), "lxml-xml")


def save_soup(soup, path):
    try:
        with open(path, "w", encoding="utf8") as f:
            f.write(str(soup))
    except Exception:  # Clean file if error
        if os.path.exists(path):
            os.remove(path)
        raise


def find_parent_with_name(tag, name):
    """
    :param tag: A tag of a BeautifulSoup
    :param name: name to search in parents
    :return: the nearest ancestor with the name
    """
    if tag.name == name:
        return tag
    else:
        return find_parent_with_name(tag.parent, name)
