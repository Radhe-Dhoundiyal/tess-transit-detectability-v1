from __future__ import annotations
import importlib.metadata as md, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    if sys.version_info[:2] != (3,12): raise SystemExit(f"Python 3.12 required; found {sys.version.split()[0]}")
    missing=[]; mismatched=[]
    for line in (ROOT/"requirements-lock.txt").read_text().splitlines():
        if not line or line.startswith("#"): continue
        name, expected=line.split("==",1)
        try: actual=md.version(name)
        except md.PackageNotFoundError: missing.append(name); continue
        if actual != expected: mismatched.append(f"{name}: {actual} != {expected}")
    if missing or mismatched: raise SystemExit(f"missing={missing}; mismatched={mismatched}")
    print("Environment verification: PASSED")
if __name__ == "__main__": main()
