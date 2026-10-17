"""Prints the claims Gemma produced, from gemma_debug.json.

Run after: python run_all.py gemma3:1b
Then:      python show_claims.py
"""
import json

data = json.load(open("gemma_debug.json", encoding="utf-8"))

print("ACCEPTED claims (passed all validation checks)\n")
for product, d in data.items():
    for c in d["accepted"]:
        print(f"{product}\n  claim:  {c['claim_text']}\n  target: {c['target']}   value: {c['expected_value']}\n")

print("REJECTED claims (sent to human review)\n")
for product, d in data.items():
    for r in d["human_review"]:
        c = r["claim"]
        print(f"{product}\n  reason: {r['reason']}\n  claim:  {c.get('claim_text')}   value: {c.get('expected_value')}\n")
