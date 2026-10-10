import json, os, time
from pathlib import Path
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from .prompts import SYSTEM_PROMPT
from .tools import TOOLS

load_dotenv()
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

NUDGE = ("You have not given a final answer yet. Continue now: use the calculate tool "
         "for any arithmetic, then reply in the required Decision / Reimbursable / Reason format.")


def build_agent():
    provider = os.getenv("PROVIDER", "anthropic")
    if provider == "groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(model=os.getenv("MODEL", "openai/gpt-oss-120b"), temperature=0, max_tokens=1024)
    else:
        llm = ChatAnthropic(model=os.getenv("MODEL", "claude-sonnet-4-6"), temperature=0, max_tokens=1024)
    return create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")


def run(agent, claim: str, verbose: bool = True, log_file: str = "trace.jsonl") -> dict:
    """Run the agent; return final answer, tool names used and a step-by-step trace."""
    config = {"recursion_limit": 20}
    result = agent.invoke({"messages": [("user", claim)]}, config)

    # Some models return an empty final message after a tool call. Retry up to 2 times.
    retries = 0
    while not _text(result["messages"][-1].content).strip() and retries < 2:
        retries += 1
        result = agent.invoke({"messages": result["messages"] + [("user", NUDGE)]}, config)

    trace, step = [], 0
    for m in result["messages"]:
        if isinstance(m, AIMessage):
            for tc in m.tool_calls:
                step += 1
                trace.append({"step": step, "type": "tool_call", "why": _text(m.content).strip(),
                              "tool": tc["name"], "input": tc["args"]})
        elif isinstance(m, ToolMessage):
            trace.append({"step": step, "type": "tool_result", "tool": m.name, "output": _text(m.content)})
    answer = _text(result["messages"][-1].content)
    out = {"claim": claim, "answer": answer, "retries": retries,
           "tools_used": [t["tool"] for t in trace if t["type"] == "tool_call"], "trace": trace}
    if verbose:
        print(f"\n=== CLAIM: {claim}")
        for t in trace:
            if t["type"] == "tool_call":
                print(f"[{t['step']}] WHY: {t['why'] or '(no explanation)'}\n    CALL {t['tool']}({t['input']})")
            else:
                print(f"    -> {t['output']}")
        if retries:
            print(f"(empty answer: retried {retries}x)")
        print(f"ANSWER:\n{answer}")
    with open(LOG_DIR / log_file, "a") as f:
        f.write(json.dumps({"ts": time.time(), **out}) + "\n")
    return out