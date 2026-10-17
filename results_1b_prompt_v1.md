# Product Autopsy results

## 1. Generate samples and ground truth

```
10 products, 30 planted defects, 60 valid controls
```

## 2. Claim-validation self-test

```
selftest passed (7 cases)
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
mode=gemma  model claims accepted=7  routed to human review=23

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
