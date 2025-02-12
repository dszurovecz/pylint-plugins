from typing import TYPE_CHECKING
import astroid
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter

if TYPE_CHECKING:
    from pylint.reporters import BaseReporter

registered_node_ids = []


class KeywordArgEnforcerChecker(BaseChecker):
    """A Pylint checker to enforce keyword arguments in function calls."""

    name = "keyword-arg-checker"
    priority = -1
    msgs = {
        "E9001": (
            "Function arguments should be passed as keyword arguments.",
            "keyword-arg-checker",
            "Ensure function calls use keyword arguments.",
        )
    }

    def __init__(self, linter: PyLinter) -> None:
        super().__init__(linter)

    def is_new_node_id(self, node: astroid.Call) -> bool:
        """Somewhy same node ids checked double times so this check is required to ensure
        report one error only one time"""
        if id(node) not in registered_node_ids:
            registered_node_ids.append(id(node))
            return True
        return False

    def visit_call(self, node: astroid.Call) -> None:
        """Checks if keyword arguments used in a function call."""
        func = astroid.util.safe_infer(node.func)
        if not isinstance(func, astroid.BoundMethod) and not isinstance(
            func, astroid.ClassDef
        ):
            call_site = astroid.arguments.CallSite.from_call(node)
            keyword_arguments = call_site.keyword_arguments
            if not keyword_arguments and self.is_new_node_id(node=node):
                print(type(func))
                self.add_message("E9001", node=node)


def register(linter: PyLinter) -> None:
    """Register the checker in Pylint."""
    linter.register_checker(KeywordArgEnforcerChecker(linter))
