"""Sanity-check tools without any API key: python tests_offline.py"""
from expense_agent.tools import search_policy, convert_currency, calculate
assert "180" in search_policy.invoke({"query": "lodging domestic"})
assert search_policy.invoke({"query": "stock options"}) == "NO MATCHING POLICY"
assert "216.0" in convert_currency.invoke({"amount": 200, "currency": "EUR"})
assert calculate.invoke({"expression": "250 * 0.67"}) == "167.5"
assert calculate.invoke({"expression": "__import__('os')"}).startswith("ERROR")
print("tools OK")