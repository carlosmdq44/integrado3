# scripts/sql_runner.py
import argparse, duckdb
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="data/warehouse.duckdb", help="Ruta al DuckDB")
    p.add_argument("sql_files", nargs="+", help="Archivos .sql a ejecutar, en orden")
    args = p.parse_args()

    con = duckdb.connect(args.db)
    for f in args.sql_files:
        path = Path(f)
        print(f"== Ejecutando: {path}")
        sql = path.read_text(encoding="utf-8")
        con.execute(sql)
    con.close()
    print("OK SQL RUNNER ✔")

if __name__ == "__main__":
    main()