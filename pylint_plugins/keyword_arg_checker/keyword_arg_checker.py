import astroid
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pylint.reporters import BaseReporter

EXCLUDED_MODULES = {
    "time",
    "logging",
    "math",
    "os",
    "sys",
    "pytest",
    "logger",
    "TaskReporter",
    "calendar",
    "Config",
    "request" "ReportGenerator",
    "CMStatusCollector",
    "json",
    "open",
}
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
    "re",
]
BUILTIN_METHODS = {
    "append",
    "split",
    "extend",
    "remove",
    "pop",
    "insert",
    "sort",
    "join",
    "range",
    "choice",
}


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

        base_expr = self._get_base_expression(node=node)
        inferred_func = self._get_inferred_function(node=node)

        if self._is_builtin_function_call(node=node):
            return

        if self._is_excluded_module(base_expr=base_expr):
            return

        if not inferred_func:
            return

        if self._should_skip_function(func=inferred_func):
            return

        if self._is_bound_method(func=inferred_func) or self._is_builtin_method(
            func=inferred_func
        ):
            return

        # Check if bound method has positional args without keyword args
        if (
            self._is_bound_method(inferred_func)
            and self._has_positional_args_without_keywords(node=node)
            and self.is_new_node_id(node=node)
        ):
            self.add_message("E9001", node=node)

        # Check if keyword arguments are used
        if not self._has_keyword_arguments(node) and self.is_new_node_id(node):
            self.add_message("E9001", node=node)

    def _is_builtin_function_call(self, node: astroid.Call) -> bool:
        """Checks if the function call is to a built-in function."""
        if isinstance(node.func, astroid.Attribute):
            base_expr = node.func.expr
            if hasattr(base_expr, "name") and base_expr.name in BUILTINS:
                return True
        return False

    def _get_base_expression(self, node: astroid.Call) -> astroid.NodeNG:
        """Gets the base expression for an attribute call."""
        if isinstance(node.func, astroid.Attribute):
            base_expr = node.func.expr
            while isinstance(base_expr, astroid.Attribute):
                base_expr = base_expr.expr
            return base_expr
        elif isinstance(node.func, astroid.Name):
            return node.func  # If it's a Name, return it directly
        return node.func.expr  # In case of other types of functions (though unlikely)

    def _is_excluded_module(self, base_expr: astroid.NodeNG) -> bool:
        """Checks if the base expression is in excluded modules."""
        if isinstance(base_expr, astroid.Name) and base_expr.name in EXCLUDED_MODULES:
            return True
        return False

    def _get_inferred_function(self, node: astroid.Call) -> astroid.NodeNG:
        """Attempts to infer the function being called."""
        inferred_funcs = list(node.func.infer())
        if inferred_funcs and astroid.util.Uninferable not in inferred_funcs:
            return inferred_funcs[0]
        return None

    def _is_bound_method(self, func: astroid.NodeNG) -> bool:
        """Checks if the function is a bound method."""
        return isinstance(func, astroid.BoundMethod)

    def _is_builtin_method(self, func: astroid.BoundMethod) -> bool:
        """Checks if the bound method is a built-in method."""
        return "builtins" in str(func) or any(
            method in str(func) for method in BUILTIN_METHODS
        )

    def _has_positional_args_without_keywords(self, node: astroid.Call) -> bool:
        """Checks if there are positional arguments without keyword arguments."""
        positional_arguments = [
            arg for arg in node.args if not isinstance(arg, astroid.Keyword)
        ]
        return positional_arguments and not any(
            isinstance(arg, astroid.Keyword) for arg in node.args
        )

    def _should_skip_function(self, func: astroid.NodeNG) -> bool:
        """Checks if the function should be skipped (e.g., has no parameters or is a class constructor)."""
        if isinstance(func, astroid.FunctionDef) and not func.args.args:
            return True
        elif isinstance(func, astroid.ClassDef):
            return True
        return False

    def _has_keyword_arguments(self, node: astroid.Call) -> bool:
        """Checks if the function call contains keyword arguments."""
        call_site = astroid.arguments.CallSite.from_call(node)
        return bool(call_site.keyword_arguments)


def register(linter: PyLinter) -> None:
    """Register the checker in Pylint."""
    linter.register_checker(KeywordArgEnforcerChecker(linter))
