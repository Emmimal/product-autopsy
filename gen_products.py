"""Builds 10 sample products with 30 planted defects + 60 valid controls.

Each product gets exactly one defect per category:
  missing_file : README mentions a file that is not in the package
  broken_link  : one Markdown link that does not resolve
  spreadsheet  : the Total Revenue cell is wrong (3 sub-types)
Valid controls per product: 2 file mentions, 3 links, 1 correct total (Total Cost).

Ground truth is written to ground_truth.json, OUTSIDE samples/, so the
checker and the model never see it.
"""
import json
import random
import shutil
from pathlib import Path

from openpyxl import Workbook

HERE = Path(__file__).parent
SAMPLES = HERE / "samples"

PRODUCTS = [
    ("budget-planner", "Budget Planner", "track monthly spending"),
    ("freelance-invoice-kit", "Freelance Invoice Kit", "bill clients on time"),
    ("habit-tracker", "Habit Tracker", "build daily habits"),
    ("meal-prep-planner", "Meal Prep Planner", "plan a week of meals"),
    ("etsy-profit-sheet", "Etsy Profit Sheet", "see profit per listing"),
    ("podcast-launch-kit", "Podcast Launch Kit", "launch a podcast"),
    ("wedding-checklist", "Wedding Checklist", "keep wedding tasks on track"),
    ("fitness-log", "Fitness Log", "log workouts"),
    ("runway-model", "Startup Runway Model", "estimate cash runway"),
    ("study-planner", "Study Planner", "plan revision sessions"),
]

MISSING = [
    ("setup.xlsx", "Open `{m}` first and enter your starting balance."),
    ("templates/invoice-template.docx", "Copy `{m}` into your documents folder before you start."),
    ("sample-clients.csv", "Load `{m}` to replace the demo rows with your own."),
    ("start-here.txt", "Read {m} before you begin."),
    ("config/settings.json", "Duplicate `{m}` to change your currency."),
    ("monthly-summary.xlsx", "Open {m} for the dashboard view."),
    ("checklist.pdf", "Keep `{m}` open while you work."),
    ("LICENSE.txt", "Check `{m}` before reselling."),
    ("categories.csv", "Import `{m}` into the Categories tab."),
    ("bonus-pack.zip", "Unzip `{m}` for extra templates."),
]

BROKEN = [
    ("Refund policy", "docs/refund-policy.md", "missing_local_file"),
    ("Cover art", "../assets/cover.pdf", "escapes_package"),
    ("Quick start", "Guide.MD", "case_mismatch"),
    ("Install notes", "guide.md#installation", "missing_anchor"),
    ("FAQ", "#faq", "missing_local_anchor"),
    ("License terms", "docs/license.md", "missing_local_file"),
    ("Shared styles", "../shared/styles.css", "escapes_package"),
    ("Full guide", "Guide.md", "case_mismatch"),
    ("Getting started", "guide.md#getting-started", "missing_anchor"),
    ("Pricing", "#pricing", "missing_local_anchor"),
]


def sheet_variant(i):
    if i < 4:
        return "range_short"
    if i < 7:
        return "column_mismatch"
    return "promise_wrong_free_phrasing" if i >= 8 else "promise_wrong"


def build():
    if SAMPLES.exists():
        shutil.rmtree(SAMPLES)
    truth = []
    for i, (pid, title, tagline) in enumerate(PRODUCTS):
        root = SAMPLES / pid
        root.mkdir(parents=True)
        rng = random.Random(1000 + i)
        rev = [rng.randint(80, 220) for _ in range(10)]
        cost = [rng.randint(40, 120) for _ in range(10)]
        variant = sheet_variant(i)

        wb = Workbook()
        ws = wb.active
        ws.append(["Month", "Revenue", "Cost"])
        for m, (r, c) in enumerate(zip(rev, cost), start=1):
            ws.append([f"Month {m}", r, c])
        ws["A13"], ws["A14"] = "Total Revenue", "Total Cost"
        ws["B13"] = {"range_short": "=SUM(B2:B10)",
                     "column_mismatch": "=SUM(C2:C11)"}.get(variant, "=SUM(B2:B11)")
        ws["C14"] = "=SUM(C2:C11)"
        wb.save(root / "tracker.xlsx")

        (root / "example-data.csv").write_text(
            "month,revenue,cost\n" + "\n".join(f"{m},{r},{c}" for m, (r, c)
                                               in enumerate(zip(rev, cost), 1)))
        (root / "guide.md").write_text("# Guide\n\n## Setup\n\n## Troubleshooting\n")

        rp = sum(rev) + (50 + 10 * i if variant.startswith("promise_wrong") else 0)
        cp = sum(cost)
        if variant == "promise_wrong_free_phrasing":
            promise = (f"Paste in the sample rows and revenue comes to {rp:,} in total. "
                       f"With the included sample rows, the Total Cost cell shows {cp:,}.")
        else:
            promise = (f"With the included sample rows, the Total Revenue cell shows "
                       f"{rp:,} and the Total Cost cell shows {cp:,}.")

        mention, tmpl = MISSING[i]
        btext, btarget, bkind = BROKEN[i]
        readme = f"""# {title}

{title} helps you {tagline}. Everything lives in one workbook.

## What's included
- The workbook: `tracker.xlsx`
- Demo rows: `example-data.csv`

## Setup
{tmpl.format(m=mention)}
{promise}

## Links
- [Quick guide](guide.md)
- [Troubleshooting tips](guide.md#troubleshooting)
- [Jump to setup](#setup)
- [{btext}]({btarget})
"""
        (root / "README.md").write_text(readme)

        def unit(kind, key, cat, defective, sub):
            truth.append({"id": f"{pid}|{kind}|{key}", "product": pid, "category": cat,
                          "defective": defective, "subtype": sub})

        unit("file", "tracker.xlsx", "missing_file", False, "valid")
        unit("file", "example-data.csv", "missing_file", False, "valid")
        unit("file", mention, "missing_file", True, "absent_file")
        for t in ("guide.md", "guide.md#troubleshooting", "#setup"):
            unit("link", t, "broken_link", False, "valid")
        unit("link", btarget, "broken_link", True, bkind)
        unit("sheet", "total revenue", "spreadsheet", True, variant)
        unit("sheet", "total cost", "spreadsheet", False, "valid")

    (HERE / "ground_truth.json").write_text(json.dumps(truth, indent=1))
    d = sum(t["defective"] for t in truth)
    print(f"{len(PRODUCTS)} products, {d} planted defects, {len(truth) - d} valid controls")


if __name__ == "__main__":
    build()
