import pytest
import os
import subprocess
from pathlib import Path

PLUGIN_NAME = "keyword_arg_checker"

path = Path(__file__).parent.parent.parent / "pylint_plugins" / "keyword_arg_checker"
expanded_path = os.path.expandvars(path)
print(expanded_path)


@pytest.fixture
def sample_code_path() -> Path:
    """Provides the path to the sample Python file."""
    return Path(__file__).parent / "not_filled_kwargs.py"


def test_pylint_plugin_unused_argument_find(sample_code_path):
    """Runs Pylint on the sample code and checks for expected warnings."""
    result = subprocess.run(
        ["pylint", "--load-plugins", PLUGIN_NAME, str(sample_code_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert (
        "not_filled_kwargs.py:8:0: E9001: Function arguments should be passed as keyword arguments"
        in output
    )
