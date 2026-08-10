"""Transform data between workflow steps using a restricted Python expression."""

import ast
from typing import Final


_ALLOWED_NODES: Final = (
    ast.Expression,
    ast.Dict,
    ast.Constant,
    ast.Name,
    ast.Subscript,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.IfExp,
    ast.Load,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.UAdd,
    ast.USub,
    ast.Not,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
    ast.Index,
)


def _validate_expression(expression: str) -> ast.Expression:
    """Parse and validate the expression before passing it to ``eval``."""
    parsed = ast.parse(expression, mode="eval")

    for node in ast.walk(parsed):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(
                f"Unsupported expression construct: {type(node).__name__}"
            )
        if isinstance(node, ast.Name) and node.id != "input_data":
            raise ValueError("Only the name 'input_data' may be referenced")
        if isinstance(node, ast.Dict) and any(key is None for key in node.keys):
            raise ValueError("Dictionary unpacking is not supported")

    return parsed


def transform_step_data(transform_map_expr: str, input_data: dict) -> dict:
    """Evaluate a dictionary expression against the previous step's output.

    The expression may reference the input only as ``input_data`` and supports
    dictionary literals, indexing, arithmetic, comparisons, and boolean logic.
    Python builtins and attribute access/calls are deliberately unavailable.
    """
    expression = _validate_expression(transform_map_expr)
    result = eval(
        compile(expression, "<workflow_transform>", "eval"),
        {"__builtins__": {}},
        {"input_data": input_data},
    )

    if not isinstance(result, dict):
        raise TypeError("transform_map_expr must evaluate to a dictionary")
    return result
