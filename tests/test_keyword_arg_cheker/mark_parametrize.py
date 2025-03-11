"""Module docstring"""

import pytest


@pytest.mark.parametrize(
    "arg1, arg2",
    [
        (
            "test1",
            "test2",
        ),
    ],
)
def test_flag_unused_argument():
    """Method docstring"""
    return True
