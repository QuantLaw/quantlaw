# -*- coding: utf-8 -*-

import pytest
from quantlaw.skeleton import fib

__author__ = "Janis Beckedorf"
__copyright__ = "Janis Beckedorf"
__license__ = "new-bsd"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
