import sys
from expense_agent.agent import build_agent, run

if __name__ == "__main__":
    claim = " ".join(sys.argv[1:]) or "I stayed 4 nights at a domestic hotel, $210 per night. Can I be reimbursed?"
    run(build_agent(), claim)