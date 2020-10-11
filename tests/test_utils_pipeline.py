import unittest

from quantlaw.utils.pipeline import PipelineStep


class SampleStep(PipelineStep):
    max_number_of_processes = 2

    def get_items(self):
        return range(50)

    def execute_item(self, item, arg1):
        return f"x{item}y{arg1}z"


class PipelineTestCase(unittest.TestCase):
    def test_abstrac_class(self):
        step = PipelineStep()
        with self.assertRaises(Exception):
            step.get_items()
        with self.assertRaises(Exception):
            step.execute_item("asd")

    def test_sample_step(self):
        step = SampleStep(execute_args=["a"])
        items = step.get_items()
        result = step.execute_items(items)
        self.assertEqual([f"x{i}yaz" for i in range(50)], result)

    def test_sample_step_single_process(self):
        step = SampleStep(processes=1, execute_args=["a"])
        items = step.get_items()
        result = step.execute_items(items)
        self.assertEqual([f"x{i}yaz" for i in range(50)], result)

    def test_filter(self):
        step = SampleStep(execute_args=["a"])
        items = ["aa", "bab", "cc", "caad"]
        result = step.execute_filtered_items(items, ["aa", "cc"])
        self.assertEqual(["xaayaz", "xccyaz", "xcaadyaz"], result)
        result = step.execute_filtered_items(items)
        self.assertEqual(["xaayaz", "xbabyaz", "xccyaz", "xcaadyaz"], result)
