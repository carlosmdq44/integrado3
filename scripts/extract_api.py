import requests
from pathlib import Path
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from raw_utils import write_json_raw, append_manifest, sha256_file, slugify

DEFAULT_TIMEOUT = 20

class ApiExtractor:
    def __init__(self, raw_dir: Path, manifest_path: Path):
        self.raw_dir = Path(raw_dir)
        self.manifest_path = Path(manifest_path)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((requests.RequestException,))
    )
    def fetch(self, name: str, endpoint: str, method: str="GET",
              params: Optional[Dict[str, Any]]=None,
              headers: Optional[Dict[str, str]]=None,
              json_body: Optional[Dict[str, Any]]=None,
              timeout: int=DEFAULT_TIMEOUT) -> Path:
        method = (method or "GET").upper()
        func = requests.get if method == "GET" else requests.post
        resp = func(endpoint, params=params, headers=headers, json=json_body, timeout=timeout)
        resp.raise_for_status()

        try:
            payload = resp.json()
        except ValueError:
            payload = {"_raw_text": resp.text}

        out_path = write_json_raw(self.raw_dir, source=name, payload=payload, pretty=True)
        size = Path(out_path).stat().st_size
        digest = sha256_file(out_path)
        append_manifest(self.manifest_path, {
            "source": slugify(name),
            "type": "api",
            "path": str(out_path).replace(",", "_"),
            "bytes": size,
            "sha256": digest
        })
        return out_path