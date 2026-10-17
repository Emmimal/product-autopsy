"""Runs the checker on samples/ and scores it against ground_truth.json.

  python run_benchmark.py --mode det     deterministic checks only
  python run_benchmark.py --mode gemma   + Gemma claim extraction (needs OLLAMA_MODEL)
  python run_benchmark.py --mode stub    + a fake model, to test the plumbing only
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import autopsy
import extract_claims as ec

HERE = Path(__file__).parent


def stub_model(system, user):
    """NOT Gemma. A regex stand-in that proves the pipeline wiring works."""
    claims = []
    for m in re.finditer(r"[^.]*?revenue comes to ([\d,]+) in total\.", user, re.I):
        claims.append({"claim_id": f"stub{len(claims)}", "claim_text": m.group(0).strip(),
                       "source_file": "README.md", "check_type": "spreadsheet_total",
                       "target": "Total Revenue",
                       "expected_value": int(m.group(1).replace(",", "")),
                       "required_evidence": "sheet total"})
    return json.dumps({"claims": claims})


def score(findings, truth):
    reported = {f["id"] for f in findings if f["status"] == "fail"}
    seen = {f["id"] for f in findings}
    rows = defaultdict(lambda: defaultdict(int))
    misses = []
    for t in truth:
        key = t["id"].lower() if t["category"] == "spreadsheet" else t["id"]
        hit = key in {r.lower() if "|sheet|" in r else r for r in reported}
        for bucket in (t["category"], "ALL"):
            r = rows[bucket]
            if t["defective"]:
                r["defects"] += 1
                r["tp" if hit else "fn"] += 1
            else:
                r["valid"] += 1
                r["fp" if hit else "tn"] += 1
        if t["defective"] and not hit:
            misses.append((t["id"], t["subtype"]))
    known = {t["id"].lower() for t in truth}
    spurious = [r for r in reported if r.lower() not in known]
    rows["ALL"]["fp"] += len(spurious)
    return rows, misses, spurious


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "n/a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["det", "gemma", "stub"], default="det")
    ap.add_argument("--set", choices=["main", "phrasing", "phrasing_noisy"], default="main")
    ap.add_argument("--model", help="Ollama model tag for --mode gemma, e.g. gemma3:1b")
    args = ap.parse_args()
    mode = args.mode
    samples_dir, truth_file = {
        "main": ("samples", "ground_truth.json"),
        "phrasing": ("samples_phrasing", "ground_truth_phrasing.json"),
        "phrasing_noisy": ("samples_phrasing_noisy", "ground_truth_phrasing_noisy.json"),
    }[args.set]
    truth = json.loads((HERE / truth_file).read_text())
    model_fn = None
    if mode == "stub":
        model_fn = stub_model
    elif mode == "gemma":
        model = args.model or os.environ.get("OLLAMA_MODEL")
        if not model:
            raise SystemExit("Give the model tag: python run_benchmark.py --mode gemma "
                             "--set phrasing --model gemma3:1b")
        problem = ec.preflight(model)
        if problem:
            raise SystemExit(problem)
        model_fn = lambda s, u: ec.call_ollama(model, s, u)

    findings, review_total, claims_total, debug = [], 0, 0, {}
    for root in sorted((HERE / samples_dir).iterdir()):
        claims = []
        if model_fn:
            claims, review = ec.extract(root, model_fn)
            review_total += len(review)
            debug[root.name] = {"accepted": claims, "human_review": review}
            claims_total += len(claims)
        findings += autopsy.check_product(root, claims)

    rows, misses, spurious = score(findings, truth)
    print(f"set={args.set}  mode={mode}  model claims accepted={claims_total}  "
          f"model claims rejected by validation (left for human review)={review_total}\n")
    print("| category | defects | recall | precision | false-positive rate |")
    print("|---|---|---|---|---|")
    for cat in ["missing_file", "broken_link", "spreadsheet", "ALL"]:
        r = rows[cat]
        print(f"| {cat} | {r['defects']} | {pct(r['tp'], r['defects'])} | "
              f"{pct(r['tp'], r['tp'] + r['fp'])} | {pct(r['fp'], r['valid'])} |")
    print(f"\nmissed defects ({len(misses)}):")
    for i, s in misses:
        print(f"  {i}  [{s}]")
    print(f"spurious findings (ids not in ground truth): {len(spurious)}")
    if debug:
        reasons = Counter(r["reason"] for d in debug.values() for r in d["human_review"])
        print("\nwhy claims were sent to human review:")
        for k, v in reasons.most_common():
            print(f"  {v:3d}  {k}")
        print("per product (accepted / human review):")
        for name, d in debug.items():
            print(f"  {name}: {len(d['accepted'])} / {len(d['human_review'])}")
        (HERE / "gemma_debug.json").write_text(json.dumps(debug, indent=1))
        print("full claims saved to gemma_debug.json")
    unver = [f for f in findings if f["status"] == "unverified"]
    print(f"checker findings marked unverified (unsupported spreadsheet formula): {len(unver)}")
    print("note: precision above is measured on the planted benchmark only, not on real repositories")


if __name__ == "__main__":
    main()