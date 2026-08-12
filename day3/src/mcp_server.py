import ast
import operator as op

from fastmcp import FastMCP

mcp = FastMCP("sara-alsalmi Tools")

_ALLOWED = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg, ast.Mod: op.mod,
}


def _safe_eval(node):
    """Evaluate an arithmetic AST - no names, no calls, never a shell."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
        return _ALLOWED[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
        return _ALLOWED[type(node.op)](_safe_eval(node.operand))
    raise ValueError("only basic arithmetic is allowed")


@mcp.tool
def calculate(expression: str) -> float:
    """Evaluate a basic arithmetic expression, e.g. '2 * (3+4) ** 2'."""
    return _safe_eval(ast.parse(expression, mode="eval").body)


@mcp.tool
def word_stats(text: str) -> dict:
    """Return word count, character count, and unique word count for a text."""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "unique_words": len(set(w.lower().strip(".,!?;:") for w in words)),
    }


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
