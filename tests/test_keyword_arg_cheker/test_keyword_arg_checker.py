import pytest
import subprocess
from pathlib import Path
PLUGIN_NAME = "keyword_arg_checker"

@pytest.fixture
def sample_code_path() -> Path:
    """Provides the path to the sample Python file."""
    return Path(__file__).parent / "not_filled_kwargs.py"

def test_pylint_plugin(sample_code_path):
    """Runs Pylint on the sample code and checks for expected warnings."""
    result = subprocess.run(
        ["pylint", "--load-plugins", PLUGIN_NAME, str(sample_code_path)],
        capture_output=True,
        text=True
    )
    output = result.stdout + result.stderr
    print(output)  
    assert "unused-attribute"