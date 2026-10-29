from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads((ROOT / "data/metadata/rc2_parent_hashes_v1_0_0.json").read_text())
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest().upper()
def main():
    failures=[]
    for relative, expected in EXPECTED.items():
        actual=sha(ROOT/relative)
        if actual != expected: failures.append(f"{relative}: {actual}")
    print(f"Parent hashes: {len(EXPECTED)-len(failures)}/{len(EXPECTED)} passed")
    if failures: raise SystemExit("\n".join(failures))
if __name__ == "__main__": main()
