from pathlib import Path
import os, shutil, logging
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", ".")).resolve()
RAW_DIR = PROJECT_ROOT / os.getenv("RAW_DIR", "data/raw/airbnb")
STAGING_DIR = PROJECT_ROOT / os.getenv("STAGING_DIR", "data/staging")
CORE_DIR = PROJECT_ROOT / os.getenv("CORE_DIR", "data/core")
GOLD_DIR = PROJECT_ROOT / os.getenv("GOLD_DIR", "data/gold")
DUCKDB_PATH = PROJECT_ROOT / os.getenv("DUCKDB_PATH", "data/warehouse.duckdb")

for d in [RAW_DIR, STAGING_DIR, CORE_DIR, GOLD_DIR, PROJECT_ROOT/"logs"]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=PROJECT_ROOT/"logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def copy_with_date(src: Path, dest_dir: Path, prefix="ab_nyc"):
    from datetime import datetime
    dest_dir.mkdir(parents=True, exist_ok=True)
    date_tag = datetime.now().strftime("%Y%m%d")
    dest = dest_dir / f"{prefix}_{date_tag}.csv"
    shutil.copy(src, dest)
    return dest
