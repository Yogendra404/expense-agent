"""Three distinct tools: policy retrieval, currency conversion, safe calculator."""
import ast, json, operator, re
from pathlib import Path
from langchain_core.tools import tool

POLICIES = json.loads((Path(__file__).parent.parent / "data" / "policies.json").read_text())
FX_TO_USD = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27, "INR": 0.012, "JPY": 0.0067}

SYNONYMS = {
    "ground": {"cab", "uber", "ola", "lyft", "ride", "transport", "transportation", "taxi"},
    "lodging": {"hotel", "accommodation", "stay", "night"},
    "meals": {"meal", "food", "dinner", "lunch", "breakfast", "restaurant"},
    "mileage": {"drive", "drove", "car", "mile", "driving"},
    "internet": {"wifi", "broadband", "remote"},
    "alcohol": {"wine", "beer", "liquor", "drink"},
    "airfare": {"flight", "fly", "airline", "plane", "business"},
    "receipts": {"receipt", "invoice"},
    "deadline": {"late", "submit", "submission", "expired", "old"},
}

GENERIC = {"domestic", "international", "policy", "expense", "reimbursable", "travel"}


def _tokens(s: str) -> set:
    words = re.findall(r"[a-z]+", s.lower())
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words}


@tool
def search_policy(query: str) -> str:
    """Search the company expense policy. Input: a short keyword query such as
    'lodging international' or 'alcohol'. Returns the top matching policy rules,
    or 'NO MATCHING POLICY' if nothing relevant exists."""
    q = _tokens(query) - GENERIC
    scored = []
    for p in POLICIES:
        words = _tokens(p["title"] + " " + p["text"]) | SYNONYMS.get(p["id"], set())
        score = len(q & words)
        if score:
            scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return "NO MATCHING POLICY"
    return "\n".join(f"[{p['title']}] {p['text']}" for _, p in scored[:3])


@tool
def convert_currency(amount: float, currency: str) -> str:
    """Convert an amount in EUR, GBP, INR, JPY or USD to USD using fixed rates.
    Returns the USD amount."""
    cur = currency.upper().strip()
    if cur not in FX_TO_USD:
        return f"ERROR: unsupported currency '{currency}'. Supported: {list(FX_TO_USD)}"
    return f"{amount} {cur} = {round(amount * FX_TO_USD[cur], 2)} USD (rate {FX_TO_USD[cur]})"


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg, ast.Pow: operator.pow}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


@tool
def calculate(expression: str) -> str:
    """Evaluate an arithmetic expression using only numbers, + - * / ** and
    parentheses, e.g. '4 * 180'. Functions like min() are not supported."""
    try:
        return str(round(_eval(ast.parse(expression, mode="eval").body), 2))
    except Exception as e:
        return f"ERROR: {e}"


TOOLS = [search_policy, convert_currency, calculate]