"""Safe local calculator plugin using Python's AST, not eval()."""
from __future__ import annotations

import ast
import math
import operator as op

PLUGIN = {
    "name": "calculator",
    "description": (
        "Evaluate arithmetic locally without web access. Use for numeric expressions, percentages, "
        "powers, roots, basic trig/log functions, and constants such as pi and e."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "expression": {"type": "STRING", "description": "Arithmetic expression, for example (18*7)+sqrt(81)."}
        },
        "required": ["expression"],
    },
}

_BIN = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow,
}
_UNARY = {ast.UAdd: op.pos, ast.USub: op.neg}
_FUNCS = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "log": math.log, "log10": math.log10, "ln": math.log,
    "abs": abs, "round": round, "ceil": math.ceil, "floor": math.floor,
}
_CONST = {"pi": math.pi, "e": math.e, "tau": math.tau}


def _calc(node):
    if isinstance(node, ast.Expression):
        return _calc(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _CONST:
        return _CONST[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        a, b = _calc(node.left), _calc(node.right)
        if isinstance(node.op, ast.Pow) and abs(float(b)) > 10000:
            raise ValueError("Exponent is too large")
        return _BIN[type(node.op)](a, b)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_calc(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        if node.keywords:
            raise ValueError("Keyword arguments are not supported")
        return _FUNCS[node.func.id](*[_calc(a) for a in node.args])
    raise ValueError("Unsupported expression")


def run(parameters: dict, player=None, session_memory=None) -> str:
    expression = str(parameters.get("expression") or "").strip().replace("^", "**")
    if not expression:
        return "Please provide an expression to calculate."
    if len(expression) > 300:
        return "That expression is too long for the local calculator."
    try:
        tree = ast.parse(expression, mode="eval")
        result = _calc(tree)
        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Result is not finite")
        text = f"{result:.12g}" if isinstance(result, float) else str(result)
        if player:
            player.write_log(f"CALC: {expression} = {text}")
        return text
    except Exception as exc:
        return f"I could not calculate that expression: {exc}"
