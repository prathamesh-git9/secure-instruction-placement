"""Safely evaluate workflow data transformation expressions."""

from __future__ import annotations

import ast
from typing import Final


_ALLOWED_NODES: Final = (
    ast.Expression,
    ast.Dict,
    ast.List,
    ast.Tuple,
    ast.Subscript,
    ast.Slice,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.UnaryOp,
    ast.UAdd,
    ast.USub,
    ast.Not,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Compare,
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
)


def _validate_expression(tree: ast.Expression) -> None:
    """Reject syntax that could access Python execution capabilities."""

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(
                f"Unsupported expression construct: {type(node).__name__}"
            )
        if isinstance(node, ast.Name) and node.id != "input_data":
            raise ValueError("Only the 'input_data' variable is available")
        if isinstance(node, ast.Constant) and not isinstance(
            node.value, (str, int, float, bool, type(None))
        ):
            raise ValueError("Unsupported constant in transformation expression")


def transform_step_data(transform_map_expr: str, input_data: dict) -> dict:
    """Transform one workflow step's output into the next step's input.

    Expressions use ``input_data`` to refer to the previous step's result.  The
    expression is parsed and restricted before being passed to ``eval`` so
    callers can use data-oriented expressions without access to imports,
    function calls, attributes, or Python builtins.
    """

    if not isinstance(transform_map_expr, str):
        raise TypeError("transform_map_expr must be a string")
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")

    try:
        tree = ast.parse(transform_map_expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError("transform_map_expr is not a valid expression") from exc

    _validate_expression(tree)

    # Keep eval's global and local namespaces deliberately minimal.  AST
    # validation above prevents expressions from constructing callable objects
    # or reaching attributes in the first place.
    transformed = eval(  # noqa: S307 - restricted by _validate_expression
        compile(tree, "<workflow transformation>", "eval"),
        {"__builtins__": {}},
        {"input_data": input_data},
    )

    if not isinstance(transformed, dict):
        raise ValueError("The transformation expression must return a dictionary")
    return transformed
