"""Module docstring"""


def call_unused_argument(test1, test2, test3):
    """Dummy function to test unused argument"""
    test1 = None
    test2 = None
    test3 = None
    return test1, test2, test3


call_unused_argument(1, 2, 3)
