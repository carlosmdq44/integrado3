import argparse, json
from pathlib import Path
import pandas as pd

def is_json(path: Path) -> bool:
    return path.suffix.lower() == ".json"

def is_csv(path: Path) -> bool:
    return path.suffix.lower() == ".csv"

def validate_file(path: Path, min_bytes: int=100) -> dict:
    ok = path.exists()
    size = path.stat().st_size if ok else 0
    valid = ok and size >= min_bytes
    fmt = "json" if is_json(path) else "csv" if is_csv(path) else "other"
    detail = ""

    if fmt == "json" and valid:
        try:
            with open(path, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            valid = False; detail = f"invalid json: {e}"
    elif fmt == "csv" and valid:
        try:
            pd.read_csv(path, nrows=5)
        except Exception as e:
            valid = False; detail = f"invalid csv: {e}"

    return {"path": str(path), "bytes": size, "format": fmt, "valid": valid, "detail": detail}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/raw", help="raw directory")
    ap.add_argument("--report", default="docs/raw_validation_report.md", help="output report path")
    args = ap.parse_args()

    raw_dir = Path(args.dir)
    files = [p for p in raw_dir.rglob("*") if p.is_file() and not p.name.startswith("_")]
    results = [validate_file(p) for p in files]

    out = Path(args.report); out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Raw Validation Report\n\n")
        f.write(f"Scanned directory: `{raw_dir}`\n\n")
        f.write("| path | bytes | format | valid | detail |\n|---|---:|---|---:|---|\n")
        for r in results:
            f.write(f"| {r['path']} | {r['bytes']} | {r['format']} | {str(r['valid'])} | {r['detail']} |\n")

    print(f"Report written to {out} with {len(results)} files.")

if __name__ == "__main__":
    main()