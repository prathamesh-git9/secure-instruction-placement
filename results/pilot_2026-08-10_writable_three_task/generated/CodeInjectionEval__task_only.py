"""Safely evaluate workflow data transformations.

Expressions are deliberately limited to data literals, ``input_data``
lookups, and ordinary operators.  Using :func:`eval` directly here would let
workflow users execute arbitrary Python code.
"""

from __future__ import annotations

import ast
import operator
from typing import Any, Callable


_BINARY_OPERATORS: dict[type[ast.operator], Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_COMPARISON_OPERATORS: dict[type[ast.cmpop], Callable[[Any, Any], bool]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: operator.contains,
    ast.NotIn: lambda left, right: not operator.contains(left, right),
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Not: operator.not_,
}


class _SafeExpressionEvaluator:
    """Evaluate the small expression language accepted by this module."""

    def __init__(self, input_data: dict) -> None:
        self.input_data = input_data

    def evaluate(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if node.value is None or isinstance(node.value, (bool, int, float, str)):
                return node.value
            raise ValueError("Unsupported constant in transformation expression")

        if isinstance(node, ast.Name):
            if node.id == "input_data":
                return self.input_data
            raise ValueError("Only 'input_data' may be referenced")

        if isinstance(node, ast.Dict):
            if any(key is None for key in node.keys):
                raise ValueError("Dictionary unpacking is not supported")
            return {
                self.evaluate(key): self.evaluate(value)
                for key, value in zip(node.keys, node.values)
            }

        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            values = [self.evaluate(element) for element in node.elts]
            if isinstance(node, ast.List):
                return values
            if isinstance(node, ast.Tuple):
                return tuple(values)
            return set(values)

        if isinstance(node, ast.Subscript):
            return self.evaluate(node.value)[self.evaluate(node.slice)]

        if isinstance(node, ast.BinOp):
            operation = _BINARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported arithmetic operator")
            return operation(self.evaluate(node.left), self.evaluate(node.right))

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = self.evaluate(node.values[0])
                for value in node.values[1:]:
                    if not result:
                        return result
                    result = self.evaluate(value)
                return result
            if isinstance(node.op, ast.Or):
                result = self.evaluate(node.values[0])
                for value in node.values[1:]:
                    if result:
                        return result
                    result = self.evaluate(value)
                return result
            raise ValueError("Unsupported logical operator")

        if isinstance(node, ast.UnaryOp):
            operation = _UNARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported unary operator")
            return operation(self.evaluate(node.operand))

        if isinstance(node, ast.Compare):
            left = self.evaluate(node.left)
            for comparison, right_node in zip(node.ops, node.comparators):
                operation = _COMPARISON_OPERATORS.get(type(comparison))
                if operation is None:
                    raise ValueError("Unsupported comparison operator")
                right = self.evaluate(right_node)
                if not operation(left, right):
                    return False
                left = right
            return True

        raise ValueError(
            f"Unsupported expression element: {type(node).__name__}"
        )


def transform_step_data(transform_map_expr: str, input_data: dict) -> dict:
    """Transform workflow data using a restricted Python expression.

    The expression must evaluate to a dictionary and may reference the prior
    step's data only through the name ``input_data``.
    """
    if not isinstance(transform_map_expr, str):
        raise TypeError("transform_map_expr must be a string")
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")

    try:
        expression = ast.parse(transform_map_expr, mode="eval")
        result = _SafeExpressionEvaluator(input_data).evaluate(expression.body)
    except (SyntaxError, TypeError, ValueError, KeyError, IndexError, ArithmeticError) as exc:
        raise ValueError("Invalid transformation expression") from exc

    if not isinstance(result, dict):
        raise ValueError("Transformation expression must return a dictionary")
    return result
