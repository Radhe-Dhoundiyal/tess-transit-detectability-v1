from __future__ import annotations
import csv, hashlib, json, re, zipfile
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
ZIP=ROOT/"release/TESS_Transit_Detectability_Benchmark_v1.0.0-rc.2.zip"
MANIFEST=ROOT/"release/terminal_benchmark_release_manifest_v1_0_0_rc2.csv"
def sha_bytes(data): return hashlib.sha256(data).hexdigest().upper()
def main():
    rows=list(csv.DictReader(MANIFEST.open(encoding="utf-8-sig",newline="")))
    controls={"release/terminal_benchmark_release_manifest_v1_0_0_rc2.csv","release/terminal_benchmark_release_manifest_v1_0_0_rc2.json"}
    with zipfile.ZipFile(ZIP) as archive:
        names=archive.namelist()
        assert len(names)==len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and ".." not in PurePosixPath(n).parts for n in names)
        assert set(names)=={r["rc2_relative_path"] for r in rows}|controls
        for row in rows:
            assert sha_bytes(archive.read(row["rc2_relative_path"]))==row["rc2_hash"]
        text="\n".join(archive.read(n).decode("utf-8","ignore") for n in names if not n.endswith((".png",".zip")))
        assert not re.search(r"[A-Za-z]:\\\\Users\\\\",text)
    identity=json.loads((ROOT/"data/metadata/rc2_scientific_identity_v1_0_0.json").read_text())
    assert identity["status"]=="PASSED"
    print(f"RC2 verification: PASSED ({len(names)} archive members)")
if __name__ == "__main__": main()
