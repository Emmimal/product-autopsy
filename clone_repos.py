"""Clone public GitHub repos into a folder, ready for scan_repos.py.

Three ways to say which repos:

  python clone_repos.py --mine [folder]            the 30 Emmimal repos built in below
  python clone_repos.py --urls repos.txt [folder]  URLs from a text file (any separators)
  python clone_repos.py <github-username> [folder] every public non-fork repo of a user

Needs git installed. Shallow clones (--depth 1). Repos already in the folder are skipped.
Then:  python scan_repos.py <folder>
"""
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

MINE = """
codeownership agent-efficiency-benchmark claim-relationship-resolver rag-vs-agent
commitment-ledger wiki-compiler intent-continuity context-validity-benchmark
prompt-dependency-graph context-window-engine prompt-regression-suite
prompt-pruning-layer loop-engine promptctl context-compiler context-type-system
ml-production-readiness-checklist ml-technical-debt-code graph-density-engine
memory-decay-engine ab-test-ml-models inference-latency-debugger shadow-canary-router
ml-dashboard context-graph-benchmark async-router-engine ML-Model-Monitoring
vibe-scanner local-mcp-server rag-cost-control-layer
""".split()
MINE_URLS = [f"https://github.com/Emmimal/{n}" for n in MINE]

URL_RE = re.compile(r"https?://github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?(?=[\s,;)\"']|/|$)")


def urls_from_text(text):
    seen, out = set(), []
    for owner, repo in URL_RE.findall(text):
        key = (owner.lower(), repo.lower())
        if key not in seen:
            seen.add(key)
            out.append(f"https://github.com/{owner}/{repo}")
    return out


def urls_from_user(user):
    urls, page = [], 1
    while True:
        api = f"https://api.github.com/users/{user}/repos?per_page=100&page={page}"
        req = urllib.request.Request(api, headers={"User-Agent": "product-autopsy"})
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read())
        if not batch:
            return sorted(urls, key=str.lower)
        urls += [x["html_url"] for x in batch if not x["fork"] and not x["archived"]]
        page += 1


def clone_all(urls, out):
    out.mkdir(exist_ok=True)
    ok = failed = skipped = 0
    for url in urls:
        name = url.rstrip("/").split("/")[-1]
        dest = out / name
        if dest.exists():
            skipped += 1
            print(f"  skip {name} (already there)")
            continue
        p = subprocess.run(["git", "clone", "-q", "--depth", "1", url + ".git", str(dest)],
                           capture_output=True, text=True)
        if p.returncode == 0:
            ok += 1
            print(f"  ok   {name}")
        else:
            failed += 1
            print(f"  FAIL {name}: {p.stderr.strip()[:150]}")
    print(f"\n{ok} cloned, {skipped} skipped, {failed} failed -> {out}")
    print(f"Next: python scan_repos.py {out}")


def main():
    if not shutil.which("git"):
        sys.exit("git was not found. Install it from git-scm.com, reopen the terminal, "
                 "or download each repo as a ZIP from GitHub and unzip it into one folder.")
    argv = sys.argv[1:]
    if not argv:
        sys.exit(__doc__)
    if argv[0] == "--mine":
        urls, rest = MINE_URLS, argv[1:]
    elif argv[0] == "--urls":
        if len(argv) < 2:
            sys.exit("Usage: python clone_repos.py --urls repos.txt [folder]")
        urls, rest = urls_from_text(Path(argv[1]).read_text(encoding="utf-8")), argv[2:]
    else:
        try:
            urls = urls_from_user(argv[0])
        except Exception as e:
            sys.exit(f"Could not list repos from the GitHub API ({e}).\n"
                     "Use --mine or --urls repos.txt instead.")
        rest = argv[1:]
    out = Path(rest[0] if rest else "real_repos")
    print(f"{len(urls)} repos -> {out}")
    clone_all(urls, out)


if __name__ == "__main__":
    main()
