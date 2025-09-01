import requests
from pathlib import Path
from typing import Optional, Dict
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from raw_utils import write_json_raw, append_manifest, sha256_file, slugify

DEFAULT_TIMEOUT = 20
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ELT-Extractor/1.0; +https://example.org)"
}

class Scraper:
    def __init__(self, raw_dir: Path, manifest_path: Path):
        self.raw_dir = Path(raw_dir)
        self.manifest_path = Path(manifest_path)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((requests.RequestException,))
    )
    def fetch_page(self, name: str, url: str,
                   headers: Optional[Dict[str, str]]=None,
                   timeout: int=DEFAULT_TIMEOUT) -> Path:
        h = {**DEFAULT_HEADERS, **(headers or {})}
        resp = requests.get(url, headers=h, timeout=timeout)
        resp.raise_for_status()
        html = resp.text

        soup = BeautifulSoup(html, "lxml")
        title = (soup.title.string.strip() if soup.title and soup.title.string else None)
        links = [{"text": (a.get_text(strip=True) or None), "href": a["href"]}
                 for a in soup.select("a[href]")]

        payload = {"url": url, "title": title, "links": links[:500], "length_html": len(html)}
        out_path = write_json_raw(self.raw_dir, source=name, payload=payload, pretty=True)
        size = Path(out_path).stat().st_size
        digest = sha256_file(out_path)
        append_manifest(self.manifest_path, {
            "source": slugify(name),
            "type": "scrape",
            "path": str(out_path).replace(",", "_"),
            "bytes": size,
            "sha256": digest
        })
        return out_path