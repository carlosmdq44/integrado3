import argparse, yaml, traceback
from pathlib import Path
from extract_api import ApiExtractor
from extract_scrape import Scraper

def main():
    p = argparse.ArgumentParser(description="Run extract jobs from YAML config")
    p.add_argument("--config", required=True, help="Path to YAML config with jobs")
    p.add_argument("--raw-dir", default="data/raw/external", help="Where to store extracted files")
    p.add_argument("--manifest", default="data/raw/_manifest.csv", help="Path to the raw manifest CSV")
    args = p.parse_args()

    raw_dir = Path(args.raw_dir); raw_dir.mkdir(parents=True, exist_ok=True)
    manifest = Path(args.manifest)

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    api = ApiExtractor(raw_dir=raw_dir, manifest_path=manifest)
    scraper = Scraper(raw_dir=raw_dir, manifest_path=manifest)

    jobs = cfg.get("jobs", [])
    results = []

    for job in jobs:
        jtype = job.get("type")
        name = job.get("name") or "job"
        enabled = job.get("enabled", True)
        if not enabled:
            print(f"-> Skipping job (disabled): {name}")
            results.append({"name": name, "type": jtype, "status": "skipped"})
            continue

        print(f"-> Running job: {name} [{jtype}]")
        try:
            if jtype == "api":
                out = api.fetch(
                    name=name,
                    endpoint=job["endpoint"],
                    method=job.get("method", "GET"),
                    params=job.get("params"),
                    headers=job.get("headers"),
                    json_body=job.get("json")
                )
                results.append({"name": name, "type": jtype, "status": "ok", "path": str(out)})
            elif jtype == "scrape":
                out = scraper.fetch_page(
                    name=name,
                    url=job["url"],
                    headers=job.get("headers")
                )
                results.append({"name": name, "type": jtype, "status": "ok", "path": str(out)})
            else:
                msg = f"Unknown job type: {jtype}"
                print(f"!! {msg}")
                results.append({"name": name, "type": jtype, "status": "error", "error": msg})
        except Exception as e:
            print(f"!! Job failed: {name} — {e}")
            # print stack for debugging
            traceback.print_exc()
            results.append({"name": name, "type": jtype, "status": "error", "error": str(e)})

    print("\nSummary:")
    for r in results:
        line = f" - {r['name']} ({r.get('type')}) -> {r.get('status')}"
        if r.get("path"):
            line += f" | {r['path']}"
        if r.get("error"):
            line += f" | {r['error']}"
        print(line)

if __name__ == "__main__":
    main()
