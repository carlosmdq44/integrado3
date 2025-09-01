import os, json, hashlib
from pathlib import Path
from datetime import datetime
from typing import Union

ENCODING = "utf-8"

def slugify(text: str) -> str:
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in text.strip())
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe.strip("-_").lower() or "source"

def now_tag() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def ensure_dir(p: Union[str, Path]):
    Path(p).mkdir(parents=True, exist_ok=True)

def sha256_file(path: Union[str, Path]) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def write_json_raw(base_dir: Union[str, Path], source: str, payload, pretty: bool=True) -> Path:
    ensure_dir(base_dir)
    fn = f"{slugify(source)}_{now_tag()}.json"
    out = Path(base_dir) / fn
    with open(out, "w", encoding=ENCODING, newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2 if pretty else None)
    return out

def write_text_raw(base_dir: Union[str, Path], source: str, text: str) -> Path:
    ensure_dir(base_dir)
    fn = f"{slugify(source)}_{now_tag()}.txt"
    out = Path(base_dir) / fn
    with open(out, "w", encoding=ENCODING, newline="\n") as f:
        f.write(text)
    return out

def append_manifest(manifest_csv: Union[str, Path], record: dict):
    header_needed = not Path(manifest_csv).exists()
    with open(manifest_csv, "a", encoding=ENCODING, newline="\n") as f:
        if header_needed:
            f.write(",".join(record.keys()) + "\n")
        f.write(",".join(str(record.get(k, "")) for k in record.keys()) + "\n")