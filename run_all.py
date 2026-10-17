"""One command for the whole project.

  python run_all.py                          benchmark, deterministic only
  python run_all.py --real                   + clone your 30 repos and scan them
  python run_all.py gemma3:1b                + Gemma claim extraction (Ollama must be running)
  python run_all.py gemma3:1b --real         everything

Steps: 1 generate samples, 2 self-test, 3 benchmark (deterministic),
       4-5 real-world clone and scan (--real), 6 benchmark with Gemma (model tag given).
Everything printed is also saved to results.md.
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sections = []


def run(args):
    p = subprocess.run([sys.executable, *args], cwd=HERE, capture_output=True, text=True)
    return (p.stdout + p.stderr).strip(), p.returncode


def save():
    (HERE / "results.md").write_text("# Product Autopsy results\n\n" + "\n".join(sections),
                                     encoding="utf-8")


def step(title, args):
    print(f"\n## {title}\n", flush=True)
    out, code = run(args)
    print(out, flush=True)
    sections.append(f"## {title}\n\n```\n{out}\n```\n")
    if code != 0:
        print(f"\nStep failed: {title}")
        save()
        sys.exit(code)


def main():
    model = next((a for a in sys.argv[1:] if not a.startswith("--")), None)
    real = "--real" in sys.argv

    step("1. Generate samples and ground truth", ["gen_products.py"])
    step("2. Claim-validation self-test", ["extract_claims.py", "--selftest"])
    step("3. Benchmark: deterministic checks only", ["run_benchmark.py", "--mode", "det"])

    if real:
        step("4. Clone the 30 repos", ["clone_repos.py", "--mine", "real_own"])
        step("5. Real-world scan (verify every flagged row by hand)",
             ["scan_repos.py", "real_own"])
    else:
        print("\n(Skipping the real-world scan. Add --real to include it.)")

    if model:
        os.environ["OLLAMA_MODEL"] = model
        step(f"6. Benchmark: deterministic + Gemma ({model})",
             ["run_benchmark.py", "--mode", "gemma"])
    else:
        print("\n(Skipping Gemma. Give a model tag, e.g. python run_all.py gemma3:1b)")

    if model:
        step("7. Free-phrasing hold-out: generate 20 products",
             ["gen_phrasing.py"])
        step("8. Free-phrasing hold-out: deterministic baseline",
             ["run_benchmark.py", "--mode", "det", "--set", "phrasing"])
        step(f"9. Free-phrasing hold-out: deterministic + Gemma ({model})",
             ["run_benchmark.py", "--mode", "gemma", "--set", "phrasing"])
        step("10. Realistic-README hold-out: generate 20 products",
             ["gen_phrasing.py", "--noisy"])
        step("11. Realistic-README hold-out: deterministic baseline",
             ["run_benchmark.py", "--mode", "det", "--set", "phrasing_noisy"])
        step(f"12. Realistic-README hold-out: deterministic + Gemma ({model})",
             ["run_benchmark.py", "--mode", "gemma", "--set", "phrasing_noisy"])

    save()
    print("\nSaved to results.md. Flagged real-world rows are in real_findings.csv.")


if __name__ == "__main__":
    main()