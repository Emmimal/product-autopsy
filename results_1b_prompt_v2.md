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

## 4. Benchmark: deterministic + Gemma (gemma3:1b)

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
