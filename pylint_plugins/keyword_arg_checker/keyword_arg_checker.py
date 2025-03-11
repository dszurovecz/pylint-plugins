from typing import TYPE_CHECKING
import astroid
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter

if TYPE_CHECKING:
    from pylint.reporters import BaseReporter

EXCLUDED_MODULES = {"time", "logging", "math", "os", "sys", "pytest"}
BUILTINS = [
    "str",
    "list",
    "dict",
    "tuple",
    "set",
    "frozenset",
    "int",
    "float",
    "complex",
    "bool",
]


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
        self.registered_node_ids = set()

    def is_new_node_id(self, node: astroid.Call) -> bool:
        """Ensure that each node is checked only once."""
        node_id = id(node)
        if node_id not in self.registered_node_ids:
            self.registered_node_ids.add(node_id)
            return True
        return False

    def visit_call(self, node: astroid.Call) -> None:
        """Checks if keyword arguments are used in a function call."""
        if isinstance(node.func, astroid.Attribute):
            base_expr = node.func.expr
            if hasattr(base_expr, "name"):
                if base_expr.name in BUILTINS:
                    return

            while isinstance(base_expr, astroid.Attribute):
                base_expr = base_expr.expr

            if (
                isinstance(base_expr, astroid.Name)
                and base_expr.name in EXCLUDED_MODULES
            ):
                return

        func = node.func.infer()
        if not isinstance(func, (astroid.BoundMethod, astroid.ClassDef)):
            call_site = astroid.arguments.CallSite.from_call(node)
            keyword_arguments = call_site.keyword_arguments

            if not keyword_arguments and self.is_new_node_id(node):
                self.add_message("E9001", node=node)


def register(linter: PyLinter) -> None:
    """Register the checker in Pylint."""
    linter.register_checker(KeywordArgEnforcerChecker(linter))
