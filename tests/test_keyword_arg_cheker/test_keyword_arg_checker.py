import pytest
import os
import subprocess
from pathlib import Path
from typing import Callable

PLUGIN_NAME = "keyword_arg_checker"

path = Path(__file__).parent.parent.parent / "pylint_plugins" / "keyword_arg_checker"
expanded_path = os.path.expandvars(path)


@pytest.fixture
def execute_keyword_arg_checker() -> Callable[[str], str]:
    """Fixture to run pylint with the keyword_arg_checker plugin."""

    def run_pylint(file_to_lint: str) -> str:
        try:
            result = subprocess.run(
                [
                    "pylint",
                    f"--load-plugins={PLUGIN_NAME}",
                    str(Path(__file__).parent / file_to_lint),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            return e.stdout + e.stderr

    return run_pylint


@pytest.mark.parametrize(
    "file_to_lint, expected_output, not_in_output",
    [
        (
            "not_filled_kwargs.py",
            "not_filled_kwargs.py:16:0: E9001: Function arguments should be passed as keyword arguments",
            "not_filled_kwargs.py:17:0: E9001: Function arguments should be passed as keyword arguments",
        ),
    ],
)
def test_flag_unused_argument(
    file_to_lint: str,
    expected_output: str,
    not_in_output: str,
    execute_keyword_arg_checker: Callable,
) -> None:
    output = execute_keyword_arg_checker(file_to_lint=file_to_lint)
    assert expected_output in output and not (not_in_output in output)


@pytest.mark.parametrize(
    "file_to_lint, expected_output",
    [
        ("filled_kwargs.py", "Your code has been rated at 10.00/10"),
        ("builtin_methods.py", "Your code has been rated at 10.00/10"),
        ("mark_parametrize.py", "Your code has been rated at 10.00/10"),
    ],
)
def test_not_flag_cases(
    file_to_lint: str,
    expected_output: str,
    execute_keyword_arg_checker: Callable,
) -> None:
    output = execute_keyword_arg_checker(file_to_lint=file_to_lint)
    assert expected_output in output
