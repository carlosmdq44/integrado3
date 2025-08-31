import sys
from pathlib import Path
from utils import RAW_DIR, copy_with_date, logging

def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/extract.py /ruta/a/AB_NYC.csv")
        sys.exit(1)

    src = Path(sys.argv[1]).resolve()
    if not src.exists():
        print(f"Archivo no encontrado: {src}")
        sys.exit(1)

    dest = copy_with_date(src, RAW_DIR, prefix="ab_nyc")
    logging.info(f"EXTRACT: copiado {src} -> {dest}")
    print(f"OK EXTRACT → {dest}")

if __name__ == "__main__":
    main()
