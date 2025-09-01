# scripts/normalize_external.py
from pathlib import Path
import json, re, duckdb, pandas as pd

DB = "data/warehouse.duckdb"
RAW_EXT = Path("data/raw/external")

# --- A) Texto libre (semi/no estructurado) -> features tabulares ---
# Se apoya en staging.airbnb_listings_clean ya creado en avances previos.
TEXT_FEATURES = {
    "has_wifi": r"\bwifi|\bwi-fi",
    "has_pool": r"\bpool|\bpileta|\bpiscina",
    "has_garden": r"\bgarden|\bjard[ií]n",
    "is_luxury": r"\bluxury|\bluj[oa]",
    "near_subway": r"\bsubway|\bmetro|\bsubte",
}

def build_text_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["id","name"]].copy()
    name = df["name"].fillna("").str.lower()
    for col, pattern in TEXT_FEATURES.items():
        df[col] = name.str.contains(pattern, regex=True)
    return df

# --- B) Normalizar JSON de raw/external (del avance 2) ---
def normalize_httpbin_ip(obj: dict) -> pd.DataFrame:
    # {"origin": "1.2.3.4"}
    return pd.DataFrame([{"origin": obj.get("origin","")}])

def normalize_httpbin_headers(obj: dict) -> pd.DataFrame:
    # {"headers": { ... }}
    headers = obj.get("headers", {}) or {}
    rows = [{"key": k, "value": v} for k, v in headers.items()]
    return pd.DataFrame(rows)

def normalize_scrape_page(obj: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    # {"url":..., "title":..., "links":[{"text":..., "href":...},...], "length_html":...}
    meta = pd.DataFrame([{
        "url": obj.get("url",""),
        "title": obj.get("title",""),
        "length_html": obj.get("length_html", 0)
    }])
    links = pd.DataFrame(obj.get("links", []) or [])
    if not links.empty and "text" not in links.columns: links["text"] = None
    if not links.empty and "href" not in links.columns: links["href"] = None
    return meta, links

def main():
    con = duckdb.connect(DB)

    # A) texto libre -> features (se guarda en staging + core)
    stg = con.execute("SELECT id, name FROM staging.airbnb_listings_clean;").df()
    tf = build_text_features(stg)
    con.execute("CREATE SCHEMA IF NOT EXISTS staging;")
    con.execute("DROP TABLE IF EXISTS staging.listing_text_features;")
    con.register("tf", tf)
    con.execute("CREATE TABLE staging.listing_text_features AS SELECT * FROM tf;")
    con.unregister("tf")

    # B) recorrer raw/external y normalizar
    ip_rows, hdr_rows, page_rows, link_rows = [], [], [], []
    for p in RAW_EXT.glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        name = p.stem  # ejemplo: httpbin_get_ip_20250901T...
        if name.startswith("httpbin_get_ip"):
            ip_rows.append(normalize_httpbin_ip(data))
        elif name.startswith("httpbin_get_headers"):
            hdr_rows.append(normalize_httpbin_headers(data))
        elif name.startswith("python_org_home") or name.startswith("httpbin_html"):
            m, l = normalize_scrape_page(data)
            m["source_file"] = p.name
            l["source_file"] = p.name
            page_rows.append(m)
            link_rows.append(l)

    if ip_rows:
        df = pd.concat(ip_rows, ignore_index=True)
        con.execute("DROP TABLE IF EXISTS staging.external_httpbin_ip;")
        con.register("df", df); con.execute("CREATE TABLE staging.external_httpbin_ip AS SELECT * FROM df;"); con.unregister("df")
    if hdr_rows:
        df = pd.concat(hdr_rows, ignore_index=True)
        con.execute("DROP TABLE IF EXISTS staging.external_httpbin_headers;")
        con.register("df", df); con.execute("CREATE TABLE staging.external_httpbin_headers AS SELECT * FROM df;"); con.unregister("df")
    if page_rows:
        dfm = pd.concat(page_rows, ignore_index=True)
        dfl = pd.concat(link_rows, ignore_index=True) if link_rows else pd.DataFrame(columns=["text","href","source_file"])
        con.execute("DROP TABLE IF EXISTS staging.external_pages;")
        con.execute("DROP TABLE IF EXISTS staging.external_page_links;")
        con.register("dfm", dfm); con.execute("CREATE TABLE staging.external_pages AS SELECT * FROM dfm;"); con.unregister("dfm")
        con.register("dfl", dfl); con.execute("CREATE TABLE staging.external_page_links AS SELECT * FROM dfl;"); con.unregister("dfl")

    con.close()
    print("OK normalize_external ✔ (staging.listing_text_features & staging.external_*)")

if __name__ == "__main__":
    main()
