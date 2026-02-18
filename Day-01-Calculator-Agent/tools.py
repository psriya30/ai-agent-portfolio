# tools.py
import ast
import operator as op
from smolagents import tool

# Supported operators
_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        fn = _ALLOWED_OPS.get(type(node.op))
        if not fn:
            raise ValueError("Operator not allowed")
        return fn(left, right)

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        fn = _ALLOWED_OPS.get(type(node.op))
        if not fn:
            raise ValueError("Operator not allowed")
        return fn(operand)

    raise ValueError("Only numbers and + - * / // % ** parentheses are allowed")

@tool
def calculate(expression: str) -> str:
    """
    Evaluate a math expression safely.

    Args:
        expression: The math expression to evaluate. Allowed: numbers, parentheses,
            + - * / // % **

    Returns:
        The result as a string, or an error message.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {e}"
