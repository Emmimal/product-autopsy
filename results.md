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
set=main  mode=det  model claims accepted=0  model claims rejected by validation (left for human review)=0

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
checker findings marked unverified (unsupported spreadsheet formula): 0
note: precision above is measured on the planted benchmark only, not on real repositories
```

## 4. Clone the 30 repos

```
30 repos -> real_own
  skip codeownership (already there)
  skip agent-efficiency-benchmark (already there)
  skip claim-relationship-resolver (already there)
  skip rag-vs-agent (already there)
  skip commitment-ledger (already there)
  skip wiki-compiler (already there)
  skip intent-continuity (already there)
  skip context-validity-benchmark (already there)
  skip prompt-dependency-graph (already there)
  skip context-window-engine (already there)
  skip prompt-regression-suite (already there)
  skip prompt-pruning-layer (already there)
  skip loop-engine (already there)
  skip promptctl (already there)
  skip context-compiler (already there)
  skip context-type-system (already there)
  skip ml-production-readiness-checklist (already there)
  skip ml-technical-debt-code (already there)
  skip graph-density-engine (already there)
  skip memory-decay-engine (already there)
  skip ab-test-ml-models (already there)
  skip inference-latency-debugger (already there)
  skip shadow-canary-router (already there)
  skip ml-dashboard (already there)
  skip context-graph-benchmark (already there)
  skip async-router-engine (already there)
  skip ML-Model-Monitoring (already there)
  skip vibe-scanner (already there)
  skip local-mcp-server (already there)
  skip rag-cost-control-layer (already there)

0 cloned, 30 skipped, 0 failed -> real_own
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
graph-density-engine                          9        1
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

14 flagged in total. Verify each in real_findings.csv.

  agent-efficiency-benchmark | missing_file | app/core.py | HELDOUT.md | referenced_file_absent
  commitment-ledger | missing_file | models/user.py | docs\archived\task-and-agent-protocol.md | referenced_file_absent
  commitment-ledger | missing_file | repository/users.py | docs\archived\task-and-agent-protocol.md | referenced_file_absent
  commitment-ledger | missing_file | middleware/auth.py | docs\archived\task-and-agent-protocol.md | referenced_file_absent
  commitment-ledger | missing_file | tests/test_auth.py | docs\archived\task-and-agent-protocol.md | referenced_file_absent
  commitment-ledger | missing_file | repository/items.py | transcripts\chat_with_ledger.txt | referenced_file_absent
  commitment-ledger | missing_file | models/item.py | transcripts\chat_with_ledger.txt | referenced_file_absent
  commitment-ledger | missing_file | tests/test_catalog.py | transcripts\chat_with_ledger.txt | referenced_file_absent
  commitment-ledger | missing_file | services/pricing.py | transcripts\chat_with_ledger.txt | referenced_file_absent
  graph-density-engine | missing_file | results.json | README.md | referenced_file_absent
  local-mcp-server | missing_file | requirements.txt | README.md | referenced_file_absent
  local-mcp-server | missing_file | Support/Claude/local_desktop_config.json | README.md | referenced_file_absent
  local-mcp-server | missing_file | src/main.py | README.md | referenced_file_absent
  vibe-scanner | missing_file | request.json | README.md | referenced_file_absent
```

## 6. Benchmark: deterministic + Gemma (gemma3:1b)

```
set=main  mode=gemma  model claims accepted=5  model claims rejected by validation (left for human review)=2

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
checker findings marked unverified (unsupported spreadsheet formula): 0
note: precision above is measured on the planted benchmark only, not on real repositories
```

## 7. Free-phrasing hold-out: generate 20 products

```
20 products, 10 wrong promises (defects), 10 correct promises (controls)
```

## 8. Free-phrasing hold-out: deterministic baseline

```
set=phrasing  mode=det  model claims accepted=0  model claims rejected by validation (left for human review)=0

| category | defects | recall | precision | false-positive rate |
|---|---|---|---|---|
| missing_file | 0 | n/a | n/a | n/a |
| broken_link | 0 | n/a | n/a | n/a |
| spreadsheet | 10 | 0% | n/a | 0% |
| ALL | 10 | 0% | n/a | 0% |

missed defects (10):
  tutor-tracker-wrong|sheet|total revenue  [free_phrasing_t0_wrong]
  candle-shop-wrong|sheet|total revenue  [free_phrasing_t1_wrong]
  photo-booking-wrong|sheet|total revenue  [free_phrasing_t2_wrong]
  bake-sale-wrong|sheet|total revenue  [free_phrasing_t3_wrong]
  plant-seller-wrong|sheet|total revenue  [free_phrasing_t4_wrong]
  print-farm-wrong|sheet|total revenue  [free_phrasing_t5_wrong]
  tour-guide-wrong|sheet|total revenue  [free_phrasing_t6_wrong]
  zine-shop-wrong|sheet|total revenue  [free_phrasing_t7_wrong]
  pottery-log-wrong|sheet|total revenue  [free_phrasing_t8_wrong]
  repair-desk-wrong|sheet|total revenue  [free_phrasing_t9_wrong]
spurious findings (ids not in ground truth): 0
checker findings marked unverified (unsupported spreadsheet formula): 0
note: precision above is measured on the planted benchmark only, not on real repositories
```

## 9. Free-phrasing hold-out: deterministic + Gemma (gemma3:1b)

```
set=phrasing  mode=gemma  model claims accepted=16  model claims rejected by validation (left for human review)=0

| category | defects | recall | precision | false-positive rate |
|---|---|---|---|---|
| missing_file | 0 | n/a | n/a | n/a |
| broken_link | 0 | n/a | n/a | n/a |
| spreadsheet | 10 | 80% | 100% | 0% |
| ALL | 10 | 80% | 100% | 0% |

missed defects (2):
  print-farm-wrong|sheet|total revenue  [free_phrasing_t5_wrong]
  tour-guide-wrong|sheet|total revenue  [free_phrasing_t6_wrong]
spurious findings (ids not in ground truth): 0

why claims were sent to human review:
per product (accepted / human review):
  bake-sale-right: 1 / 0
  bake-sale-wrong: 1 / 0
  candle-shop-right: 1 / 0
  candle-shop-wrong: 1 / 0
  photo-booking-right: 1 / 0
  photo-booking-wrong: 1 / 0
  plant-seller-right: 1 / 0
  plant-seller-wrong: 1 / 0
  pottery-log-right: 1 / 0
  pottery-log-wrong: 1 / 0
  print-farm-right: 0 / 0
  print-farm-wrong: 0 / 0
  repair-desk-right: 1 / 0
  repair-desk-wrong: 1 / 0
  tour-guide-right: 0 / 0
  tour-guide-wrong: 0 / 0
  tutor-tracker-right: 1 / 0
  tutor-tracker-wrong: 1 / 0
  zine-shop-right: 1 / 0
  zine-shop-wrong: 1 / 0
full claims saved to gemma_debug.json
checker findings marked unverified (unsupported spreadsheet formula): 0
note: precision above is measured on the planted benchmark only, not on real repositories
```

## 10. Realistic-README hold-out: generate 20 products

```
20 products, 10 wrong promises (defects), 10 correct promises (controls)
```

## 11. Realistic-README hold-out: deterministic baseline

```
set=phrasing_noisy  mode=det  model claims accepted=0  model claims rejected by validation (left for human review)=0

| category | defects | recall | precision | false-positive rate |
|---|---|---|---|---|
| missing_file | 0 | n/a | n/a | n/a |
| broken_link | 0 | n/a | n/a | n/a |
| spreadsheet | 10 | 0% | n/a | 0% |
| ALL | 10 | 0% | n/a | 0% |

missed defects (10):
  tutor-tracker-wrong|sheet|total revenue  [free_phrasing_t0_wrong]
  candle-shop-wrong|sheet|total revenue  [free_phrasing_t1_wrong]
  photo-booking-wrong|sheet|total revenue  [free_phrasing_t2_wrong]
  bake-sale-wrong|sheet|total revenue  [free_phrasing_t3_wrong]
  plant-seller-wrong|sheet|total revenue  [free_phrasing_t4_wrong]
  print-farm-wrong|sheet|total revenue  [free_phrasing_t5_wrong]
  tour-guide-wrong|sheet|total revenue  [free_phrasing_t6_wrong]
  zine-shop-wrong|sheet|total revenue  [free_phrasing_t7_wrong]
  pottery-log-wrong|sheet|total revenue  [free_phrasing_t8_wrong]
  repair-desk-wrong|sheet|total revenue  [free_phrasing_t9_wrong]
spurious findings (ids not in ground truth): 0
checker findings marked unverified (unsupported spreadsheet formula): 0
note: precision above is measured on the planted benchmark only, not on real repositories
```

## 12. Realistic-README hold-out: deterministic + Gemma (gemma3:1b)

```
set=phrasing_noisy  mode=gemma  model claims accepted=7  model claims rejected by validation (left for human review)=6

| category | defects | recall | precision | false-positive rate |
|---|---|---|---|---|
| missing_file | 0 | n/a | n/a | n/a |
| broken_link | 0 | n/a | n/a | n/a |
| spreadsheet | 10 | 40% | 100% | 0% |
| ALL | 10 | 40% | 100% | 0% |

missed defects (6):
  tutor-tracker-wrong|sheet|total revenue  [free_phrasing_t0_wrong]
  photo-booking-wrong|sheet|total revenue  [free_phrasing_t2_wrong]
  bake-sale-wrong|sheet|total revenue  [free_phrasing_t3_wrong]
  tour-guide-wrong|sheet|total revenue  [free_phrasing_t6_wrong]
  zine-shop-wrong|sheet|total revenue  [free_phrasing_t7_wrong]
  repair-desk-wrong|sheet|total revenue  [free_phrasing_t9_wrong]
spurious findings (ids not in ground truth): 0

why claims were sent to human review:
    4  no_expected_value
    2  claim_text_not_in_source
per product (accepted / human review):
  bake-sale-right: 0 / 0
  bake-sale-wrong: 0 / 0
  candle-shop-right: 0 / 0
  candle-shop-wrong: 1 / 0
  photo-booking-right: 0 / 0
  photo-booking-wrong: 0 / 0
  plant-seller-right: 1 / 0
  plant-seller-wrong: 1 / 0
  pottery-log-right: 1 / 0
  pottery-log-wrong: 1 / 0
  print-farm-right: 1 / 0
  print-farm-wrong: 1 / 0
  repair-desk-right: 0 / 0
  repair-desk-wrong: 0 / 0
  tour-guide-right: 0 / 1
  tour-guide-wrong: 0 / 1
  tutor-tracker-right: 0 / 1
  tutor-tracker-wrong: 0 / 1
  zine-shop-right: 0 / 1
  zine-shop-wrong: 0 / 1
full claims saved to gemma_debug.json
checker findings marked unverified (unsupported spreadsheet formula): 0
note: precision above is measured on the planted benchmark only, not on real repositories
```
