import os
from unittest import TestCase

from quantlaw.utils.beautiful_soup import create_soup, find_parent_with_name, save_soup


class UtilsBeautifulSoupTestCase(TestCase):
    def setUp(self):
        self.text = """
        <law heading="ALPHA">
        <book heading="X">
        <section heading="A">
        </section>
        <section heading="B">
        </section>
        </book>
        <book heading="Y">
        <section heading="A">
        </section>
        <section heading="B">
        </section>
        </book>
        </law>
        """
        self.source_filename = "temp.txt"
        self.xml_filename = "temp.xml"
        with open(self.source_filename, "w") as f:
            f.write(self.text)

    def test_create_soup(self):
        soup = create_soup(self.source_filename)
        self.assertEqual(soup.book.attrs["heading"], "X")

    def test_save_soup(self):
        soup = create_soup(self.source_filename)
        save_soup(soup, self.xml_filename)
        soup = create_soup(self.xml_filename)
        self.assertEqual(soup.book.attrs["heading"], "X")
        with self.assertRaises(OSError):
            save_soup(soup, 100)

    def test_save_soup_failed(self):
        class TestException(Exception):
            pass

        class FailingTestObj:
            def __str__(self):
                raise TestException()

        with self.assertRaises(TestException):
            save_soup(FailingTestObj(), "temp2.xml")

        self.assertFalse(os.path.exists("temp2.xml"))

    def test_find_parent_with_name(self):
        soup = create_soup(self.source_filename)
        base_tag = soup.find("section")
        parent_with_name = find_parent_with_name(base_tag, "law")
        self.assertEqual(parent_with_name.attrs["heading"], "ALPHA")
        parent_with_name = find_parent_with_name(soup.find("law"), "law")
        self.assertEqual(parent_with_name.attrs["heading"], "ALPHA")

    def tearDown(self):
        if os.path.exists(self.source_filename):
            os.remove(self.source_filename)
        if os.path.exists(self.xml_filename):
            os.remove(self.xml_filename)
