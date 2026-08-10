"""Utilities for transforming data between workflow steps."""


def transform_step_data(transform_map_expr: str, input_data: dict) -> dict:
    """Evaluate a dictionary expression using ``input_data`` as its context.

    The expression may use normal Python expression syntax, including
    dictionary literals and arithmetic, comparison, and logical operators.
    Builtins are not exposed to the expression; the workflow input is made
    available under the documented name ``input_data``.
    """
    result = eval(
        transform_map_expr,
        {"__builtins__": {}},
        {"input_data": input_data},
    )
    return result
