"""
Stage 2b: gọi TMDb API cho từng phim trong data_clean/movies.parquet (+ tùy chọn: mọi phim
IMDb có >= N vote, xem --catalog-min-votes), cache JSON.

Mỗi phim 2 request:
  1. /find/{imdb_id}?external_source=imdb_id                 -> tmdb_id
  2. /movie/{tmdb_id}?append_to_response=release_dates,watch/providers
     (details: budget, revenue, release_date, popularity ...
      release_dates: ngày phát hành theo nước + loại 1-6, 4 = Digital
      watch/providers: nền tảng streaming HIỆN TẠI theo nước — nguồn JustWatch)

Cache: data_raw/tmdb_cache/{imdb_id}.json — chạy lại sẽ bỏ qua phim đã có (resume được).
Thứ tự ưu tiên: phim ra mắt từ 2015, nhiều vote trước -> dừng giữa chừng vẫn có dữ liệu dùng được.

Chạy:
  python src/06_fetch_tmdb.py              # toàn bộ (~136k phim, ~10 phim/s; resume được)
  python src/06_fetch_tmdb.py --limit 200  # thử
  python src/06_fetch_tmdb.py --catalog-min-votes 1000   # + mọi phim IMDb >= 1000 vote
Cần .env có TMDB_API_KEY.
"""

import argparse
import json
import os
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import duckdb
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT      = Path(__file__).resolve().parent.parent
MOVIES    = (ROOT / "data_clean/movies.parquet").as_posix()
CATALOG   = (ROOT / "data_clean/imdb_catalog.parquet").as_posix()
CACHE_DIR = ROOT / "data_raw/tmdb_cache"
BASE      = "https://api.themoviedb.org/3"
WORKERS   = 8          # TMDb giới hạn mềm ~50 req/s/IP; 8 luồng là an toàn

load_dotenv(ROOT / ".env")
API_KEY = os.getenv("TMDB_API_KEY")
if not API_KEY:
    raise SystemExit("Thiếu TMDB_API_KEY trong .env")

ap = argparse.ArgumentParser()
ap.add_argument("--limit", type=int, help="chỉ lấy N phim đầu (theo thứ tự ưu tiên)")
ap.add_argument("--catalog-min-votes", type=int,
                help="lấy thêm mọi phim trong danh mục IMDb có >= N vote (vd. 1000)")
args = ap.parse_args()

CACHE_DIR.mkdir(parents=True, exist_ok=True)
local = threading.local()


def ensure_dns(host="api.themoviedb.org"):
    """DNS của một số nhà mạng VN trả NXDOMAIN cho TMDb. Khi đó hỏi IP qua DNS-over-HTTPS
    của Cloudflare (1.1.1.1) và chỉ ghi đè phân giải cho đúng host này. TLS vẫn xác thực
    chứng chỉ theo tên miền như bình thường."""
    try:
        socket.getaddrinfo(host, 443)
        return
    except socket.gaierror:
        pass
    answer = requests.get("https://1.1.1.1/dns-query", params={"name": host, "type": "A"},
                          headers={"accept": "application/dns-json"}, timeout=10).json()
    ips = [a["data"] for a in answer.get("Answer", []) if a.get("type") == 1]
    if not ips:
        raise SystemExit(f"Không phân giải được {host}. Hãy đổi DNS máy sang 1.1.1.1 hoặc 8.8.8.8.")
    print(f"DNS hệ thống chặn {host} -> dùng IP từ 1.1.1.1: {ips[0]}")
    original = socket.getaddrinfo

    def patched(h, *a, **kw):
        return original(ips[0] if h == host else h, *a, **kw)

    socket.getaddrinfo = patched


ensure_dns()


def session():
    if not hasattr(local, "s"):
        local.s = requests.Session()
    return local.s


def get(path, **params):
    """GET với retry: 429 -> chờ Retry-After; lỗi mạng / 5xx -> backoff."""
    params["api_key"] = API_KEY
    for attempt in range(6):
        try:
            r = session().get(f"{BASE}{path}", params=params, timeout=20)
            if r.status_code == 429:
                time.sleep(float(r.headers.get("Retry-After", 2)))
                continue
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed after retries: {path}")


def fetch(imdb_id):
    out = CACHE_DIR / f"{imdb_id}.json"
    found = get(f"/find/{imdb_id}", external_source="imdb_id") or {}
    hits = found.get("movie_results", [])
    if not hits:
        record = {"imdb_id": imdb_id, "found": False}
    else:
        details = get(f"/movie/{hits[0]['id']}",
                      append_to_response="release_dates,watch/providers")
        record = {"imdb_id": imdb_id, "found": details is not None, "details": details}
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out)  # ghi nguyên tử: dừng giữa chừng không để lại file hỏng
    return record["found"]


# Phim từ hai nguồn ghép (movies.parquet) + (tùy chọn) mọi phim IMDb đủ nhiều vote, để phân
# tích phim "bình thường" không bị giới hạn ở các phim có xuất hiện trên torrent.
extra = ""
if args.catalog_min_votes is not None:
    extra = f"""UNION SELECT tconst, start_year, num_votes FROM read_parquet('{CATALOG}')
                WHERE titleType = 'movie' AND num_votes >= {args.catalog_min_votes}"""
ids = [r[0] for r in duckdb.sql(f"""
    SELECT imdb_id FROM (
        SELECT imdb_id, start_year, num_votes FROM read_parquet('{MOVIES}') {extra}
    )
    ORDER BY (start_year >= 2015) DESC NULLS LAST, num_votes DESC NULLS LAST
""").fetchall()]
if args.limit:
    ids = ids[:args.limit]
todo = [i for i in ids if not (CACHE_DIR / f"{i}.json").exists()]
print(f"{len(ids):,} phim, đã cache {len(ids) - len(todo):,}, cần lấy {len(todo):,}")

t0, n_ok, n_miss, n_err = time.time(), 0, 0, 0
with ThreadPoolExecutor(WORKERS) as pool:
    futures = {pool.submit(fetch, i): i for i in todo}
    for k, fut in enumerate(as_completed(futures), 1):
        try:
            if fut.result():
                n_ok += 1
            else:
                n_miss += 1
        except Exception as e:
            n_err += 1
            print(f"  ERROR {futures[fut]}: {e}")
        if k % 500 == 0 or k == len(todo):
            rate = k / (time.time() - t0)
            eta = (len(todo) - k) / rate / 60 if rate else 0
            print(f"  {k:,}/{len(todo):,}  found={n_ok:,} not_found={n_miss:,} "
                  f"err={n_err}  {rate:.1f} phim/s  ETA {eta:.0f} phút", flush=True)

print(f"\nXong. found={n_ok:,}  not_found={n_miss:,}  errors={n_err} "
      f"(chạy lại để thử lại các phim lỗi)")
