import os
from unittest import TestCase

from quantlaw.utils.files import ensure_exists, list_dir


class UtilsFilesTestCase(TestCase):
    def setUp(self):
        self.directory = "./temp/test"

    def test_ensure_exists(self):
        ensure_exists(self.directory)
        ensure_exists(self.directory)
        self.assertTrue(os.path.exists(self.directory))

    def test_list_dir(self):
        ensure_exists(self.directory)
        files = [f"{self.directory}/a.xml", f"{self.directory}/b.txt"]
        for file in files:
            with open(file, "w") as f:
                f.write("")
        self.assertEqual(list_dir(self.directory, "xml"), ["a.xml"])
        for file in files:
            os.remove(file)

    def tearDown(self):
        if os.path.exists(self.directory):
            os.removedirs(self.directory)
