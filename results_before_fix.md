# Product Autopsy results

## 1. Generate samples and ground truth

```
10 products, 30 planted defects, 60 valid controls
```

## 2. Claim-validation self-test

```
selftest passed (8 cases)
```

## 3. Benchmark: deterministic checks only

```
mode=det  model claims accepted=0  routed to human review=0

| category | defects | recall | precision | false-positive rate |
|---|---|---|---|---|
| missing_file | 10 | 100% | 100% | 0% |
| broken_link | 10 | 100% | 100% | 0% |
| spreadsheet | 10 | 80% | 100% | 0% |
| ALL | 30 | 93% | 100% | 0% |

missed defects (2):
  runway-model|sheet|total revenue  [promise_wrong_free_phrasing]
  study-planner|sheet|total revenue  [promise_wrong_free_phrasing]
spurious findings (ids not in ground truth): 0
unverified (needs human review): 0
```

## 4. Clone the 30 repos

```
30 repos -> real_own
  ok   codeownership
  ok   agent-efficiency-benchmark
  ok   claim-relationship-resolver
  ok   rag-vs-agent
  ok   commitment-ledger
  ok   wiki-compiler
  ok   intent-continuity
  ok   context-validity-benchmark
  ok   prompt-dependency-graph
  ok   context-window-engine
  ok   prompt-regression-suite
  ok   prompt-pruning-layer
  ok   loop-engine
  ok   promptctl
  ok   context-compiler
  ok   context-type-system
  ok   ml-production-readiness-checklist
  ok   ml-technical-debt-code
  ok   graph-density-engine
  ok   memory-decay-engine
  ok   ab-test-ml-models
  ok   inference-latency-debugger
  ok   shadow-canary-router
  ok   ml-dashboard
  ok   context-graph-benchmark
  ok   async-router-engine
  ok   ML-Model-Monitoring
  ok   vibe-scanner
  ok   local-mcp-server
  ok   rag-cost-control-layer

30 cloned, 0 skipped, 0 failed -> real_own
Next: python scan_repos.py real_own
```

## 5. Real-world scan (verify every flagged row by hand)

```
product                                  checks  flagged
ab-test-ml-models                             7        0
agent-efficiency-benchmark                   13        1
async-router-engine                           1        0
claim-relationship-resolver                  10        0
codeownership                                45        0
commitment-ledger                            15        8
context-compiler                              2        0
context-graph-benchmark                       1        0
context-type-system                           4        0
context-validity-benchmark                   10        0
context-window-engine                         4        0
graph-density-engine                         11        5
inference-latency-debugger                   11        0
intent-continuity                             2        0
local-mcp-server                              5        3
loop-engine                                  15        0
memory-decay-engine                           8        0
ml-dashboard                                  0        0
ML-Model-Monitoring                           0        0
ml-production-readiness-checklist             6        0
ml-technical-debt-code                        8        0
prompt-dependency-graph                       7        0
prompt-pruning-layer                          1        0
prompt-regression-suite                       6        0
promptctl                                     3        0
rag-cost-control-layer                        6        0
rag-vs-agent                                  9        0
shadow-canary-router                          3        0
vibe-scanner                                  3        1
wiki-compiler                                 0        0

18 flagged in total. Verify each in real_findings.csv.

  agent-efficiency-benchmark | missing_file | app/core.py | HELDOUT.md | referenced_file_absent
  commitment-ledger | missing_file | models/user.py | docs\archived\task-and-agent-protocol.md | referenced_file_absent
  commitment-ledger | missing_file | repository/users.py | docs\archived\task-and-agent-protocol.md | referenced_file_absent
  commitment-ledger | missing_file | middleware/auth.py | docs\archived\task-and-agent-protocol.md | referenced_file_absent
  commitment-ledger | missing_file | tests/test_auth.py | docs\archived\task-and-agent-protocol.md | referenced_file_absent
  commitment-ledger | missing_file | repository/items.py | transcripts\chat_with_ledger.txt | referenced_file_absent
  commitment-ledger | missing_file | models/item.py | transcripts\chat_with_ledger.txt | referenced_file_absent
  commitment-ledger | missing_file | tests/test_catalog.py | transcripts\chat_with_ledger.txt | referenced_file_absent
  commitment-ledger | missing_file | services/pricing.py | transcripts\chat_with_ledger.txt | referenced_file_absent
  graph-density-engine | missing_file | datasets/incident_01.json | experiment.md | referenced_file_absent
  graph-density-engine | missing_file | incident_10.json | experiment.md | referenced_file_absent
  graph-density-engine | missing_file | results.json | README.md | referenced_file_absent
  graph-density-engine | missing_file | run_experiment2.py | README.md | referenced_file_absent
  graph-density-engine | missing_file | agents/llm.py | requirements.txt | referenced_file_absent
  local-mcp-server | missing_file | requirements.txt | README.md | referenced_file_absent
  local-mcp-server | missing_file | Support/Claude/local_desktop_config.json | README.md | referenced_file_absent
  local-mcp-server | missing_file | src/main.py | README.md | referenced_file_absent
  vibe-scanner | missing_file | request.json | README.md | referenced_file_absent
```

## 6. Benchmark: deterministic + Gemma (gemma3:1b)

```
mode=gemma  model claims accepted=5  routed to human review=2

| category | defects | recall | precision | false-positive rate |
|---|---|---|---|---|
| missing_file | 10 | 100% | 100% | 0% |
| broken_link | 10 | 100% | 100% | 0% |
| spreadsheet | 10 | 80% | 100% | 0% |
| ALL | 30 | 93% | 100% | 0% |

missed defects (2):
  runway-model|sheet|total revenue  [promise_wrong_free_phrasing]
  study-planner|sheet|total revenue  [promise_wrong_free_phrasing]
spurious findings (ids not in ground truth): 0

why claims were sent to human review:
    2  value_not_in_claim_text
per product (accepted / human review):
  budget-planner: 0 / 0
  etsy-profit-sheet: 0 / 1
  fitness-log: 1 / 0
  freelance-invoice-kit: 1 / 0
  habit-tracker: 1 / 0
  meal-prep-planner: 1 / 0
  podcast-launch-kit: 1 / 0
  runway-model: 0 / 1
  study-planner: 0 / 0
  wedding-checklist: 0 / 0
full claims saved to gemma_debug.json
unverified (needs human review): 0
```
