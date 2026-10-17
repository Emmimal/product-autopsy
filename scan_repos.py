"""Scan real products (e.g. cloned template repos) and list findings to verify by hand.

  python scan_repos.py <folder containing one subfolder per product>

Writes real_findings.csv. Every 'fail' row must be checked by a human before
you report it: open the source file and confirm the reference is really broken.
"""
import csv
import sys
from pathlib import Path

import autopsy


def main(folder):
    rows, summary = [], []
    for root in sorted(p for p in Path(folder).iterdir() if p.is_dir()):
        f = autopsy.check_product(root)
        fails = [x for x in f if x["status"] == "fail"]
        summary.append((root.name, len(f), len(fails)))
        for x in fails:
            rows.append({"product": root.name, "category": x["category"], "id": x["id"],
                         "source_file": x["source"], "reason": x["reason"],
                         "verified_real (yes/no)": ""})
    with open("real_findings.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["product"])
        w.writeheader()
        w.writerows(rows)
    print(f"{'product':40s} checks  flagged")
    for n, c, k in summary:
        print(f"{n:40s} {c:6d}  {k:7d}")
    print(f"\n{len(rows)} flagged in total. Verify each in real_findings.csv.\n")
    for r in rows:
        print(f"  {r['product']} | {r['category']} | {r['id'].split('|', 2)[2]} | "
              f"{r['source_file']} | {r['reason']}")


if __name__ == "__main__":
    main(sys.argv[1])