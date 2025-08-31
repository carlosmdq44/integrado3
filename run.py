import subprocess, sys

def run(cmd):
    print(f"\n$ {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"ERROR en: {cmd}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    # 1) Extract (pasá la ruta a tu CSV original)
    # Ejemplo: python run.py data/AB_NYC.csv
    if len(sys.argv) < 2:
        print("Uso: python run.py /ruta/a/AB_NYC.csv")
        sys.exit(1)

    csv_path = sys.argv[1]

    run(f"python scripts/extract.py {csv_path}")
    run("python scripts/load.py")
    run("python scripts/transform_staging.py")
    run("python scripts/transform_core.py")
    run("python scripts/gold.py")
    run("python scripts/quality_checks.py")
    print("\nPipeline COMPLETO ✅")
