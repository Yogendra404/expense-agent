# ExpenseBot: a multi-step LangGraph expense-claim agent

An agent that audits employee expense claims. Given a claim in plain English it
looks up the policy, converts currencies, calculates the reimbursable amount
and drafts a decision, using multiple tools autonomously.

## Capabilities
| Tool | Purpose |
|---|---|
| `search_policy` | keyword retrieval over `data/policies.json` (fictional ACME policy) |
| `convert_currency` | EUR/GBP/INR/JPY/USD to USD (fixed rates, so results are reproducible) |
| `calculate` | safe AST-based arithmetic (no `eval`) |

Example flow: "3 nights in an international hotel at EUR 200/night"
-> `search_policy` -> `convert_currency` -> `calculate` -> structured decision.

## Customisation (AI-6): specialised persona + prompt strategy
`expense_agent/prompts.py` defines an "ExpenseBot auditor" persona, a 7-step
mandatory strategy (always retrieve policy, always use the calculator, never invent
rules, explain why before each tool call), a fixed output format and a worked
few-shot example.

## Tracing
Every run records, for each step: why (the model's stated reason), which tool,
input, and output. It is printed to the console and appended to
`logs/trace.jsonl` (or `logs/eval_trace.jsonl` during evaluation).

## Evaluation (AI-7)
`eval/cases.json` holds 12 cases covering: capping at limits (lodging, meals, taxi, internet),
mileage math, currency conversion, rule lookups (airfare, receipts, deadline), a rejection
(alcohol) and an out-of-scope question (must admit no policy exists).
A case passes if the final answer contains the expected value(s) and the required
tools were actually called.

    python eval/evaluate.py     # writes eval/results.json and eval/results.md

### Results
> Paste your pass rate here after running, e.g. **11/12 (92%)**, and link `eval/results.md`.

### Failure patterns observed
> Fill in honestly after your run.

## Setup

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env        # add ANTHROPIC_API_KEY
    python tests_offline.py     # tools sanity test, no API key needed
    python main.py "I drove 250 miles for work. What can I claim?"
    python eval/evaluate.py

Any LangChain chat model can be swapped in `expense_agent/agent.py`.

## Known limitations
- Policy search is keyword overlap, not embeddings; unusual wording may miss a rule.
- Policy and FX rates are static and fictional.
- Each claim is handled independently (no memory, no per-trip or per-month running totals).
- Eval uses substring matching, so a correct answer in an unusual format may be marked a fail.
- Does not verify receipts or dates; it trusts the user's description.

### Example trace
Every run records which tool was called, with what input, and what came back.
A raw sample is in `eval/sample_trace.txt`:

```
[paste the contents of sample_trace.txt here]
```