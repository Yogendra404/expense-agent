# ExpenseBot: a multi-step LangGraph expense-claim agent

An agent that audits employee expense claims. Given a claim in plain English it
looks up the policy, converts currencies, calculates the reimbursable amount and
drafts a decision, using multiple tools autonomously.

## Capabilities
| Tool | Purpose |
|---|---|
| `search_policy` | keyword retrieval over `data/policies.json` (fictional ACME policy) |
| `convert_currency` | EUR/GBP/INR/JPY/USD to USD (fixed rates, so results are reproducible) |
| `calculate` | safe AST-based arithmetic (no `eval`) |

Example flow: "3 nights in an international hotel at EUR 200/night"
-> `search_policy` -> `convert_currency` -> `calculate` -> structured decision.

## Customisation (AI-6): specialised persona + prompt strategy
`expense_agent/prompts.py` defines an "ExpenseBot auditor" persona, a 7-step mandatory
strategy (always retrieve policy, always use the calculator, never invent rules), a
fixed output format and a worked few-shot example. `agent.py` also retries up to 2
times when the model returns an empty final answer.

## Tracing
Every run records, for each step: which tool was called, with what input, what came
back, and the model's stated reason when it gives one. It is printed to the console
and appended to `logs/trace.jsonl` (`logs/eval_trace.jsonl` during evaluation).
A sample trace is in [`eval/sample_trace.txt`](eval/sample_trace.txt).

## Evaluation (AI-7)
`eval/cases.json` holds 12 cases: caps at limits (lodging, meals, taxi, internet),
mileage math, currency conversion, rule lookups (airfare, receipts, deadline), a
rejection (alcohol) and an out-of-scope question (must admit no policy exists).
A case passes only if the answer contains the expected value(s) **and** the required
tools were actually called.

    python eval/evaluate.py            # full run
    python eval/evaluate.py --resume   # re-run only cases that errored (e.g. rate limits)

### Results
| Run | Model | Change | Pass rate |
|---|---|---|---|
| 1 | gpt-oss-120b | baseline keyword search | 10/12 (83%) |
| 2 | gpt-oss-120b | + synonyms, plural handling | 11/12 (92%) |
| 3 | gpt-oss-120b | + ignore generic words, top-3 results | 11/12 (92%) |
| 4 | gpt-oss-20b | + empty-answer retry, smaller model | 10/12 (83%) |
| 5 | gpt-oss-120b | final agent | cases 1-10: 10/10 passed; cases 11-12 pending (see note) |

Models were run on Groq's free tier at temperature 0. Run 5 was interrupted by Groq's
daily token limit after case 10. Those API errors are not agent failures and are not
counted. Cases 11-12 are re-run with `--resume`, using identical code, prompts and model.

### Failure patterns observed
- **Retrieval bug (case 5):** generic words like "domestic" tied with the real topic
  word, and a top-2 cutoff dropped the Taxi policy. Fixed by ignoring generic words
  and returning the top 3 results.
- **Empty final answer (case 2):** the model sometimes returned a blank message after
  the policy lookup. Mitigated with a retry that nudges it to continue.
- **Tool skipping (cases 3 and 4, gpt-oss-20b):** correct totals ($270, $648) without
  calling `calculate`. The answers were right but the process was not, so the eval
  counts them as failures.
- Results vary between runs even at temperature 0, so pass rates are approximate.

## Setup
    python -m venv .venv
    .venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    copy .env.example .env          # Mac/Linux: cp .env.example .env
    # edit .env: add GROQ_API_KEY (or set PROVIDER=anthropic and ANTHROPIC_API_KEY)
    python tests_offline.py         # tool sanity test, no API key needed
    python main.py "I drove 250 miles for work. What can I claim?"
    python eval/evaluate.py

Any LangChain chat model can be swapped in `expense_agent/agent.py`.

## Known limitations
- Policy search is keyword-based with a hand-written synonym list, not embeddings.
- Policy and FX rates are static and fictional.
- Each claim is handled independently (no memory, no running totals).
- The substring checker verifies the final number, not the quality of the reasoning.
- With these models the trace's "why" field is often empty.
- Evaluated on Groq's free tier; rate-limited runs were aborted or resumed, never
  counted as agent failures.
- Relies on a retry workaround for a model quirk (empty final answers).