"""Run all test cases; check (a) answer content and (b) required tool usage.

Usage:
  python eval/evaluate.py            full fresh run
  python eval/evaluate.py --resume   keep finished cases in results.json and
                                     re-run only cases that errored (e.g. rate limits)
"""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from expense_agent.agent import build_agent, run

HERE = Path(__file__).parent
CASES = json.loads((HERE / "cases.json").read_text())
MODEL = os.getenv("MODEL", "default")


def norm(s):
    return s.lower().replace(",", "").replace("$", "")


def check(case, out):
    ans = norm(out["answer"])
    problems = []
    for e in case.get("expected_all", []):
        if norm(e) not in ans:
            problems.append(f"missing '{e}'")
    if "expected_any" in case and not any(norm(e) in ans for e in case["expected_any"]):
        problems.append(f"none of {case['expected_any']} found")
    for t in case.get("expected_tools", []):
        if t not in out["tools_used"]:
            problems.append(f"tool not used: {t}")
    return problems


def save(results, final=False):
    results = sorted(results, key=lambda r: r["id"])
    (HERE / "results.json").write_text(json.dumps(results, indent=2))
    if final:
        passed = sum(r["passed"] for r in results)
        rate = passed / len(results) * 100
        lines = [f"# Evaluation results\n\nModel: `{MODEL}`\n\n**Pass rate: {passed}/{len(results)} ({rate:.0f}%)**\n",
                 "| # | Result | Tools used | Problems |", "|---|---|---|---|"]
        for r in results:
            lines.append(f"| {r['id']} | {'PASS' if r['passed'] else 'FAIL'} | {', '.join(r['tools_used'])} | {'; '.join(r['problems'])} |")
        (HERE / "results.md").write_text("\n".join(lines) + "\n")
        print(f"\nPass rate: {passed}/{len(results)} = {rate:.0f}%")


if __name__ == "__main__":
    results = []
    if "--resume" in sys.argv and (HERE / "results.json").exists():
        old = json.loads((HERE / "results.json").read_text())
        results = [r for r in old if not any(p.startswith("exception") for p in r["problems"])]
        print(f"Resuming: keeping {len(results)} finished cases, re-running the rest. Model: {MODEL}")
    done = {r["id"] for r in results}

    agent = build_agent()
    for c in CASES:
        if c["id"] in done:
            continue
        try:
            out = run(agent, c["input"], verbose=False, log_file="eval_trace.jsonl")
            problems = check(c, out)
        except Exception as ex:
            msg = str(ex)
            if "429" in msg or "rate_limit" in msg.lower():
                save(results)
                print(f"\nRATE LIMIT hit at case {c['id']}. Progress saved ({len(results)} cases done).")
                print("Wait for the limit to refill, then run: python eval\\evaluate.py --resume")
                sys.exit(1)
            out, problems = {"answer": "", "tools_used": []}, [f"exception: {msg[:200]}"]
        results.append({"id": c["id"], "input": c["input"], "passed": not problems, "problems": problems,
                        "tools_used": out["tools_used"], "answer": out["answer"], "model": MODEL})
        print(f"Case {c['id']:>2}: {'PASS' if not problems else 'FAIL'} {problems}")
        save(results)
        time.sleep(0.5)
    save(results, final=True)