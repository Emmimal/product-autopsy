"""Product Autopsy v1: deterministic promise-vs-package checks.

Supported: .md/.txt documents, local files and links, .xlsx SUM totals.
Everything else is out of scope and is never reported as a finding.
The checker (not the model) decides pass / fail.

Finding id formats (used by the benchmark ground truth):
  <product>|file|<mention as written>
  <product>|link|<link target as written>
  <product>|sheet|<total label, e.g. Total Revenue>
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string

EXTS = "xlsx|csv|docx|txt|md|pdf|zip|json|py"
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
URL_RE = re.compile(r"\b[a-z][a-z0-9+.-]*://\S+", re.I)
SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
FILE_RE = re.compile(r"(?<![\w/:.@-])((?:[\w.-]+/)*[\w-][\w.-]*\.(?:%s))\b" % EXTS, re.I)
PROMISE_RE = re.compile(
    r"the\s+(total [a-z ]+?)\s+cell\s+shows\s+([\d,]+(?:\.\d+)?)", re.I
)
SUM_RE = re.compile(r"=SUM\(([A-Z]+)(\d+):([A-Z]+)(\d+)\)")


def slug(heading):
    s = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return re.sub(r"\s+", "-", s)


def anchors_of(path):
    out = set()
    for line in path.read_text(errors="ignore").splitlines():
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            out.add(slug(m.group(1)))
    return out


def exists_exact(root, rel):
    """Case-sensitive existence check, so a link that only works on a
    case-insensitive laptop is still reported."""
    cur = Path(root)
    for part in Path(rel).parts:
        if not cur.is_dir() or part not in os.listdir(cur):
            return False
        cur = cur / part
    return True


SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".github"}


def walk(root, suffixes):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        out += [Path(dp) / f for f in fn if suffixes is None or Path(f).suffix.lower() in suffixes]
    return sorted(out)


def docs_in(root):
    return walk(root, (".md", ".txt"))


def check_links(root, product):
    out = []
    for doc in docs_in(root):
        text = doc.read_text(errors="ignore")
        for m in LINK_RE.finditer(text):
            raw = m.group(1)
            if SCHEME_RE.match(raw) or re.fullmatch(r"\.{3}|…", raw):
                continue  # external links and "..." placeholders are out of scope for v1
            path_part, _, frag = raw.partition("#")
            path_part = unquote(path_part.partition("?")[0])
            reason = None
            target = doc
            if path_part:
                # Do not use Path.resolve(): on Windows it rewrites the path to
                # the real on-disk case and hides case-mismatch links.
                if path_part.startswith("/"):  # repo-root-relative, as on GitHub
                    rel = os.path.normpath(path_part.lstrip("/"))
                else:
                    rel = os.path.normpath(os.path.join(doc.parent.relative_to(root), path_part))
                if rel == ".." or rel.startswith(".." + os.sep):
                    first = [x for x in Path(rel).parts if x != ".."][:1]
                    if first and first[0] in GITHUB_WEB:
                        continue  # GitHub web-relative URL such as ../../actions/...
                    reason = "escapes_package"
                elif not exists_exact(root, rel):
                    reason = "missing_or_case_mismatch"
                else:
                    target = root / rel
            if not reason and frag and target.suffix.lower() == ".md":
                if frag.lower() not in anchors_of(target):
                    reason = "missing_anchor"
            out.append({
                "id": f"{product}|link|{raw}", "category": "broken_link",
                "status": "fail" if reason else "pass",
                "reason": reason, "source": str(doc.relative_to(root)),
            })
    return out


HISTORY_NAMES = ("changelog", "release-notes", "release_notes", "history", "changes", "news")
GITHUB_WEB = {"actions", "issues", "pulls", "pull", "wiki", "releases", "discussions",
              "blob", "tree", "commits", "security", "projects"}
FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.S)


def check_mentions(root, product):
    out = []
    all_names = {p.name for p in walk(root, None)}
    for doc in docs_in(root):
        raw_text = doc.read_text(errors="ignore")
        if "{{" in raw_text or any(h in doc.stem.lower() for h in HISTORY_NAMES):
            continue  # template files and history logs mention files that are not meant to exist
        text = URL_RE.sub(" ", LINK_RE.sub(" ", FENCE_RE.sub(" ", raw_text)))
        for m in FILE_RE.finditer(text):
            mention = m.group(1)
            ok = exists_exact(root, os.path.normpath(mention))
            if not ok and "/" not in mention:
                ok = mention in all_names  # bare file name that exists somewhere in the package
            if not ok and doc.parent != root:
                rel = os.path.normpath(os.path.join(doc.parent.relative_to(root), mention))
                ok = not rel.startswith("..") and exists_exact(root, rel)
            out.append({
                "id": f"{product}|file|{mention}", "category": "missing_file",
                "status": "pass" if ok else "fail",
                "reason": None if ok else "referenced_file_absent",
                "source": str(doc.relative_to(root)),
            })
    return out


def regex_promises(root):
    promises = {}
    for doc in docs_in(root):
        for m in PROMISE_RE.finditer(doc.read_text(errors="ignore")):
            promises[m.group(1).lower()] = (float(m.group(2).replace(",", "")), "regex")
    return promises


def check_sheets(root, product, claims=None):
    promises = regex_promises(root)
    for c in claims or []:
        if c.get("check_type") != "spreadsheet_total":
            continue
        label = c["target"].strip().lower()
        label = label if label.startswith("total ") else "total " + label
        promises.setdefault(label, (float(c["expected_value"]), "model"))
    out = []
    for xlsx in walk(root, (".xlsx",)):
        ws = load_workbook(xlsx).active
        headers = {
            c: str(ws.cell(1, c).value).strip().lower()
            for c in range(1, ws.max_column + 1) if ws.cell(1, c).value
        }
        for row in range(2, ws.max_row + 1):
            label = ws.cell(row, 1).value
            if not (isinstance(label, str) and label.lower().startswith("total ")):
                continue
            formula = next(
                (ws.cell(row, c).value for c in range(2, ws.max_column + 1)
                 if isinstance(ws.cell(row, c).value, str)
                 and ws.cell(row, c).value.upper().startswith("=SUM(")), None)
            uid = f"{product}|sheet|{label}"
            m = SUM_RE.fullmatch((formula or "").upper().replace(" ", ""))
            if not m or m.group(1) != m.group(3):
                out.append({"id": uid, "category": "spreadsheet", "status": "unverified",
                            "reason": "unsupported_formula", "source": xlsx.name})
                continue
            col = column_index_from_string(m.group(1))
            r1, r2 = int(m.group(2)), int(m.group(4))
            data_rows = [r for r in range(2, row)
                         if isinstance(ws.cell(r, col).value, (int, float))]
            reasons = []
            if data_rows and (r1, r2) != (min(data_rows), max(data_rows)):
                reasons.append("range_does_not_match_data")
            suffix = label[6:].strip().lower()
            if headers.get(col) and suffix and headers[col] != suffix:
                reasons.append("sums_column_with_different_header")
            value = sum(ws.cell(r, col).value for r in range(r1, r2 + 1)
                        if isinstance(ws.cell(r, col).value, (int, float)))
            promised = promises.get(label.lower())
            if promised and abs(value - promised[0]) > 0.01:
                reasons.append(f"promise_mismatch_{promised[1]}")
            out.append({"id": uid, "category": "spreadsheet",
                        "status": "fail" if reasons else "pass",
                        "reason": ",".join(reasons) or None, "source": xlsx.name})
    return out


def check_product(root, claims=None):
    root = Path(root).resolve()
    product = root.name
    findings = check_links(root, product) + check_mentions(root, product) \
        + check_sheets(root, product, claims)
    unique = {}
    for f in findings:  # dedupe by id, a fail beats a pass
        if f["id"] not in unique or f["status"] == "fail":
            unique[f["id"]] = f
    return list(unique.values())


REASON_TEXT = {
    "referenced_file_absent": "is named in the docs but is not in the package",
    "missing_or_case_mismatch": "does not resolve (missing, or the letter case differs)",
    "escapes_package": "points outside the package",
    "missing_anchor": "points to a heading that does not exist",
    "range_does_not_match_data": "the SUM range does not match the data rows",
    "sums_column_with_different_header": "the total sums a column whose header does not match its label",
    "promise_mismatch_regex": "the result differs from the number the README promises",
    "promise_mismatch_model": "the result differs from the number the README promises",
    "unsupported_formula": "uses a formula this version cannot check",
}
KIND_TEXT = {"missing_file": "missing file", "broken_link": "broken link", "spreadsheet": "spreadsheet"}


def report(root, claims=None):
    """Plain-language audit report for a seller."""
    findings = check_product(root, claims)
    fails = [f for f in findings if f["status"] == "fail"]
    unver = [f for f in findings if f["status"] == "unverified"]
    passed = [f for f in findings if f["status"] == "pass"]
    lines = [f"Product Autopsy report: {Path(root).resolve().name}",
             f"{len(fails)} problem(s) found, {len(passed)} check(s) passed"
             + (f", {len(unver)} could not be verified" if unver else ""), ""]
    for f in fails:
        target = f["id"].split("|", 2)[2]
        why = "; ".join(REASON_TEXT.get(r, r) for r in (f["reason"] or "").split(","))
        sep = ":" if f["category"] == "spreadsheet" else ""
        lines.append(f"FAIL  {KIND_TEXT[f['category']]:13s} {f['source']}: `{target}`{sep} {why}")
    for f in unver:
        lines.append(f"?     {KIND_TEXT[f['category']]:13s} {f['source']}: "
                     f"`{f['id'].split('|', 2)[2]}` {REASON_TEXT.get(f['reason'], f['reason'])}")
    if not fails:
        lines.append("No problems found among the promises this version can check.")
    return "\n".join(lines)


if __name__ == "__main__":
    if "--report" in sys.argv:
        print(report(sys.argv[1]))
    else:
        print(json.dumps(check_product(sys.argv[1]), indent=2))