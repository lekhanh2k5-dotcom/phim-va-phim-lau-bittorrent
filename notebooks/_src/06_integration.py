"""
PHẦN 3.1 — Ghép torrent với phim: phương pháp và chất lượng tích hợp.
"""

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

import viz_style as V

V.setup()
FOLDER = "6_integration"
SRC = "Nguồn: MagnetDB, IMDb, TMDb; xử lý của nhóm."
P = lambda name: (V.DC / name).as_posix()
con = duckdb.connect()
log = pd.read_csv(V.DC / "cleaning_log.csv")
tor = duckdb.sql(f"SELECT torrent_id, imdb_id, source, discovered_at_utc, implausible, in_stable_window "
                 f"FROM read_parquet('{P('torrents_clean.parquet')}')").df()
ok = tor[~tor["implausible"]]
print(f"{len(ok):,} cặp torrent–phim sạch; {ok['torrent_id'].nunique():,} torrent; {ok['imdb_id'].nunique():,} phim")

# ---- 01. Phễu làm sạch: từ dữ liệu thô đến dữ liệu tin được -------------------------------------------------------
LABELS = {
    "0. slice 2019-04 -> 2024-09 (mọi loại)": "Torrent có file khớp IMDb (2019-04 → 2024-09)",
    "A. chỉ PHIM (titleType=movie)": "A. Chỉ giữ phim lẻ",
    "B. bỏ file có số mùa/tập": "B. Bỏ tập phim bộ (S01E02…)",
    f"C. bỏ file < 100MB": "C. Bỏ file < 100 MB (trailer, clip)",
    "D. năm trong tên file khớp năm phim (±1)": "D. Năm trong tên khớp năm phim",
    "E. tên file giống tên phim >= 60": "E. Tên file giống tên phim",
    "E2. số phần phim khớp (Part 2 ≠ Part 1)": "E2. Đúng phần phim (Part 2 ≠ Part 1)",
    "0. ghép được (tên + năm khớp IMDb)": "Tên torrent khớp tên + năm phim IMDb",
    "bỏ ca mơ hồ (>1 phim trùng tên ±1 năm)": "Bỏ ca mơ hồ (trùng tên ±1 năm)",
    "hợp hai nguồn": "Hợp hai nguồn",
    "F. không xuất hiện trước ra mắt > 60 ngày": "F. Không xuất hiện trước khi phim ra mắt",
    "G. bỏ torrent hai nguồn mâu thuẫn": "G. Bỏ torrent hai nguồn mâu thuẫn",
    "H. bỏ tên torrent có từ khóa phim bộ": "H. Bỏ tên có từ khóa phim bộ",
    "I. năm trên tên torrent khớp năm phim (trừ gói)": "I. Năm trên tên torrent khớp",
    "J. bỏ torrent không hợp lý (bản nét trước ngày phát hành)": "J. Bỏ torrent giả",
}
log = log[log["step"].isin(LABELS)].drop_duplicates("step")
panels = [("magnetdb", "① Mã IMDb có sẵn của MagnetDB", V.BLUE),
          ("name_match", "② Tự ghép tên torrent", V.ORANGE),
          ("combined", "③ Gộp hai nguồn + lọc chung", V.AQUA)]
fig, axes = plt.subplots(1, 3, figsize=(13, 5.6), gridspec_kw=dict(width_ratios=[7, 2.4, 5]))
for ax, (src, name, color) in zip(axes, panels):
    d = log[log["source"] == src].reset_index(drop=True)
    y = np.arange(len(d))[::-1]
    base = d["torrents"].iloc[0]
    ax.barh(y, d["torrents"], color=color, height=0.62)
    for yi, v, step in zip(y, d["torrents"], d["step"]):
        ax.text(v * 1.02 + base * 0.01, yi, f"{v / 1e3:,.0f}k", va="center", color=V.INK2, fontsize=8.5)
        ax.text(0, yi + 0.42, LABELS[step], va="bottom", color=V.INK2, fontsize=8.5)
    ax.set_xlim(0, base * 1.35)
    ax.set_ylim(len(d) - 7.6, len(d) - 0.1)          # cùng số "khe" ở mọi bảng -> thanh dày như nhau
    ax.set_yticks([])
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(name, loc="left", color=V.INK, fontsize=10.5, pad=12)
V.titles(fig, "Từ 517 nghìn torrent \"có mã phim\" của MagnetDB đến 2,1 triệu cặp torrent–phim tin được",
         f"Số torrent còn lại sau mỗi bước làm sạch (cleaning_log.csv). Nguồn ① lọc mạnh vì mã ghép sẵn nhiều lỗi; nguồn ② "
         f"(tự ghép) chiếm phần lớn dữ liệu cuối. {SRC}")
V.save(fig, FOLDER, "01_cleaning_funnel")

# ---- 02. Độ phủ theo tháng và theo nguồn ----------------------------------------------------------------------------
m = ok.assign(month=ok["discovered_at_utc"].dt.to_period("M").dt.to_timestamp())
m = m.drop_duplicates(["torrent_id", "source"]).pivot_table(index="month", columns="source", values="torrent_id",
                                                              aggfunc="count", fill_value=0)
m = m[(m.index >= "2021-04-01") & (m.index < "2024-10-01")]
SRCS = [("both", "Cả hai nguồn cùng ghép", V.AQUA), ("magnetdb", "Chỉ MagnetDB", V.BLUE),
        ("name_match", "Chỉ tự ghép tên torrent", V.ORANGE)]
fig, ax = plt.subplots(figsize=(11, 5))
V.style_axes(ax)
ax.stackplot(m.index, [m[s] for s, _, _ in SRCS], colors=[c for _, _, c in SRCS], labels=[l for _, l, _ in SRCS],
             edgecolor=V.SURFACE, linewidth=1, alpha=0.9)
ratio = m.sum(axis=1).sum() / (m["both"] + m["magnetdb"]).sum()
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e3:.0f}k"))
ax.set_ylabel("Torrent phim mới / tháng")
ax.legend(loc="upper right", ncol=3)
ax.set_ylim(0, m.sum(axis=1).max() * 1.2)
V.titles(fig, f"Tự ghép tên torrent tăng lượng dữ liệu phim khoảng {ratio:.0f} lần",
         f"Số torrent phim mới mỗi tháng trong giai đoạn crawler ổn định (04/2021 – 09/2024), theo nguồn ghép, sau làm sạch. {SRC}")
V.save(fig, FOLDER, "02_coverage_by_source")

# ---- 03. MagnetDB gốc vs sau khi tự ghép: top 20 phim (dumbbell) ------------------------------------------------------
mv = duckdb.sql(f"SELECT title, start_year, n_torrents_stable, n_torrents_stable_magnetdb "
                f"FROM read_parquet('{P('movie_analysis.parquet')}') ORDER BY n_torrents_stable DESC LIMIT 20").df()[::-1]
fig, ax = plt.subplots(figsize=(10, 7))
V.style_axes(ax, grid="x")
y = np.arange(len(mv))
ax.hlines(y, mv["n_torrents_stable_magnetdb"], mv["n_torrents_stable"], color=V.GRID, linewidth=3)
ax.plot(mv["n_torrents_stable_magnetdb"], y, "o", markersize=8, color=V.BLUE, markeredgecolor=V.SURFACE,
        markeredgewidth=2, label="Chỉ dùng mã có sẵn của MagnetDB")
ax.plot(mv["n_torrents_stable"], y, "o", markersize=8, color=V.ORANGE, markeredgecolor=V.SURFACE,
        markeredgewidth=2, label="Sau khi tự ghép thêm tên torrent")
for yi, a, b in zip(y, mv["n_torrents_stable_magnetdb"], mv["n_torrents_stable"]):
    ax.annotate(f"{a:,} → {b:,}", xy=(b, yi), xytext=(8, 0), textcoords="offset points", va="center",
                color=V.INK2, fontsize=8)
ax.set_yticks(y)
ax.set_yticklabels([f"{t} ({yr})" for t, yr in zip(mv["title"], mv["start_year"])], color=V.INK2, fontsize=9)
ax.set_xlim(0, mv["n_torrents_stable"].max() * 1.22)
ax.set_xlabel("Số torrent trong giai đoạn ổn định (04/2021 – 09/2024)")
ax.legend(loc="lower right")
V.titles(fig, "Nếu chỉ dùng dữ liệu có sẵn, gần như mọi bom tấn đều \"biến mất\"",
         f"20 phim có nhiều torrent nhất sau khi tự ghép; chấm xanh = số torrent mà mã IMDb của MagnetDB tìm được. {SRC}")
V.save(fig, FOLDER, "03_top_movies_dumbbell")

# ---- 04. Thuật toán ghép tên khớp với nhãn MagnetDB đến đâu? -------------------------------------------------------------
# Cùng định nghĩa với notebook 00 (Bước 8): đầu vào của src/04 (04/2019–09/2024, >= 100 MB), nhãn MagnetDB là phim lẻ IMDb.
con.execute(f"""
    CREATE OR REPLACE TEMP TABLE kiem_tra AS
    WITH dau_vao AS (SELECT torrent_id FROM read_parquet('{P('mdb_torrents_all.parquet')}')
                     WHERE discovered_at_utc >= '2019-04-01' AND discovered_at_utc < '2024-09-30' AND total_size >= 100e6),
         nhan AS (SELECT f.torrent_id, list(DISTINCT f.imdb_id) AS ma_magnetdb
                  FROM read_parquet('{P('matched_files.parquet')}') f
                  JOIN read_parquet('{P('imdb_movies_all.parquet')}') m ON m.tconst = f.imdb_id
                  WHERE f.torrent_id IN (SELECT torrent_id FROM dau_vao) GROUP BY 1)
    SELECT nhan.torrent_id, coalesce(NOT o.ambiguous, false) AS tra_loi,
           coalesce(NOT o.ambiguous AND list_contains(nhan.ma_magnetdb, o.imdb_id), false) AS trung
    FROM nhan LEFT JOIN read_parquet('{P('name_matches.parquet')}') o USING (torrent_id)""")
total, answered, agreeing = con.execute(
    "SELECT count(*), count(*) FILTER (WHERE tra_loi), count(*) FILTER (WHERE trung) FROM kiem_tra").fetchone()
agree_raw, coverage = agreeing / answered, agreeing / total
# So với MagnetDB SAU các bộ lọc A–E2 của chính nó nhưng TRƯỚC khi gộp (chưa bỏ ca mâu thuẫn)
agree_clean = con.execute(f"""
    WITH mdb AS (SELECT torrent_id, any_value(imdb_id) AS imdb_id
                 FROM read_parquet('{P('magnetdb_clean_pairs.parquet')}')
                 GROUP BY torrent_id HAVING count(DISTINCT imdb_id) = 1)
    SELECT avg((n.imdb_id = m.imdb_id)::INT), count(*)
    FROM read_parquet('{P('name_matches.parquet')}') n JOIN mdb m USING (torrent_id) WHERE NOT n.ambiguous
""").fetchone()
print(f"{total:,} torrent có nhãn MagnetDB; thuật toán trả lời {answered:,}; trùng {agreeing:,} "
      f"-> đồng thuận {agree_raw:.1%}, độ phủ {coverage:.1%}; vs MagnetDB đã làm sạch: {agree_clean[0]:.1%} ({agree_clean[1]:,})")
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw=dict(width_ratios=[2.2, 1.2]))
V.style_axes(ax, grid="x")
steps = [("Có nhãn MagnetDB (phim lẻ)", total, V.OTHER), ("Thuật toán đưa ra kết quả", answered, V.BLUE),
         ("Trùng nhãn MagnetDB", agreeing, V.ORANGE)]
for yi, (label, val, color) in enumerate(steps):
    ax.barh([yi], [val], color=color, height=0.6)
    ax.text(val + total * 0.01, yi, f"{val:,}".replace(",", "."), va="center", color=V.INK2, fontsize=10)
ax.set_yticks(range(len(steps)))
ax.set_yticklabels([s[0] for s in steps], color=V.INK2)
ax.invert_yaxis()
ax.set_xlim(0, total * 1.18)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e3:,.0f}k"))
ax.set_title(f"① Thuật toán ghép tên trên {total / 1e3:,.0f}k torrent MagnetDB đã gán phim".replace(",", "."),
             loc="left", color=V.INK, fontsize=10)
V.style_axes(ax2, grid=None)
for xi, (val, label) in enumerate([(agree_raw, f"mức đồng thuận\n(nhãn gốc)"), (coverage, "độ phủ\n(nhãn gốc)"),
                                   (agree_clean[0], "đồng thuận\n(nhãn đã làm sạch)")]):
    ax2.bar([xi], [val], width=0.6, color=V.ORANGE if xi != 1 else V.BLUE)
    ax2.text(xi, val + 0.015, f"{val:.1%}".replace(".", ","), ha="center", color=V.INK2, fontsize=10)
ax2.set_xticks([0, 1, 2])
ax2.set_xticklabels([f"mức đồng thuận\n(nhãn gốc)", "độ phủ\n(nhãn gốc)", "đồng thuận\n(nhãn đã làm sạch)"], color=V.INK2, fontsize=9)
ax2.set_ylim(0, 1.08)
ax2.set_yticks([])
ax2.set_title("② Tỷ lệ", loc="left", color=V.INK, fontsize=10)
V.titles(fig, "Khi đã trả lời, thuật toán ghép tên trùng nhãn MagnetDB trong phần lớn trường hợp",
         f"Mức đồng thuận = trùng nhãn ÷ số ca thuật toán trả lời; độ phủ = trùng nhãn ÷ mọi torrent có nhãn (thấp vì thuật toán từ chối tên "
         f"không có năm hoặc mơ hồ). Nhãn MagnetDB cũng có lỗi, nên đây là MỨC ĐỒNG THUẬN, không phải độ chính xác tuyệt đối. {SRC}")
V.save(fig, FOLDER, "04_match_agreement")
