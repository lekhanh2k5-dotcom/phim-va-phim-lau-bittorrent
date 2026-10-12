"""
Phong cách biểu đồ dùng chung cho toàn dự án (import từ các script 2x/3x/4x).

Bảng màu = bảng tham chiếu của skill dataviz, đã chạy scripts/validate_palette.js (light):
8 màu phân loại PASS theo cặp kề nhau; 3 màu sáng (aqua, vàng, hồng) < 3:1 trên nền ->
luôn có chú thích/nhãn trực tiếp. Biểu đồ dạng scatter/bản đồ (mọi cặp màu đều kề nhau):
chỉ dùng tối đa 3 màu đầu, phần còn lại gộp "Khác".

Quy ước: nền sáng, chữ không mang màu dữ liệu, lưới mảnh liền (không nét đứt), đường 2px,
điểm >= 8px có viền màu nền, tiêu đề + phụ đề căn trái ở mức figure.
"""

import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT  = Path(__file__).resolve().parent.parent
DC    = ROOT / "data_clean"
PLOTS = ROOT / "plots"

SURFACE = "#fcfcfb"
INK     = "#0b0b0b"   # chữ chính
INK2    = "#52514e"   # chữ phụ
MUTED   = "#898781"   # nhãn trục
GRID    = "#e1e0d9"
AXIS    = "#c3c2b7"
OTHER   = "#b5b3ab"   # "Khác" (xám, không phải màu phân loại)

# Thứ tự cố định — không bao giờ xoay vòng; màu thứ 9 trở đi -> gộp "Khác"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
BLUE, ORANGE, AQUA = CAT[0], CAT[1], CAT[2]

# Tuần tự: một sắc xanh, nhạt -> đậm
SEQ_STEPS = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
SEQ = LinearSegmentedColormap.from_list("seq_blue", [SURFACE] + SEQ_STEPS)
# Phân kỳ: xanh <-> đỏ, giữa xám trung tính
DIV = LinearSegmentedColormap.from_list(
    "div_blue_red", ["#184f95", "#6da7ec", "#f0efec", "#ec8a89", "#b52d2d"])


def setup():
    mpl.rcParams.update({
        "font.family": ["Segoe UI", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 11,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK2,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "lines.linewidth": 2,
        "lines.solid_capstyle": "round",
        "legend.frameon": False,
        "legend.labelcolor": INK2,
        "legend.fontsize": 9,
    })


def style_axes(ax, grid="y", keep_left=False):
    """Bỏ khung thừa, lưới mảnh liền theo trục chọn ('x', 'y', 'both', None)."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(keep_left)
    ax.spines["bottom"].set_color(AXIS)
    if grid:
        ax.grid(axis=grid, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def titles(fig, title, subtitle=None, extra=0.0):
    """Tiêu đề + phụ đề căn trái ở mức figure. Khoảng chừa tính theo inch (không phụ thuộc
    chiều cao hình); phụ đề tự xuống dòng theo bề rộng hình. `extra` = inch chừa thêm phía
    dưới phụ đề (vd. cho chú thích đặt trên trục)."""
    h, w = fig.get_figheight(), fig.get_figwidth()
    lines = textwrap.wrap(subtitle, width=int(w * 17)) if subtitle else []
    head = 0.55 + 0.19 * len(lines) + extra
    fig.tight_layout(rect=(0, 0, 1, 1 - head / h))
    fig.text(0.012, 1 - 0.16 / h, title, color=INK, fontsize=13, va="top")
    if lines:
        fig.text(0.012, 1 - 0.48 / h, "\n".join(lines), color=MUTED, fontsize=8.5, va="top",
                 linespacing=1.4)


def save(fig, folder, name):
    out = PLOTS / folder
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name}.png"
    fig.savefig(path, dpi=150)
    print(f"  wrote {path.relative_to(ROOT)}")
    return path


def fmt_int(x, _=None):
    return f"{x:,.0f}"


# Tên thể loại IMDb -> tiếng Việt (dùng chung)
GENRE_VI = {
    "Drama": "Chính kịch", "Comedy": "Hài", "Documentary": "Tài liệu", "Action": "Hành động",
    "Romance": "Lãng mạn", "Thriller": "Giật gân", "Crime": "Hình sự", "Horror": "Kinh dị",
    "Adventure": "Phiêu lưu", "Family": "Gia đình", "Mystery": "Bí ẩn", "Fantasy": "Kỳ ảo",
    "Biography": "Tiểu sử", "History": "Lịch sử", "Sci-Fi": "Viễn tưởng",
    "Animation": "Hoạt hình", "Music": "Âm nhạc", "War": "Chiến tranh", "Western": "Viễn Tây",
    "Musical": "Nhạc kịch", "Sport": "Thể thao", "Adult": "Người lớn", "Film-Noir": "Film noir",
    "News": "Tin tức", "Reality-TV": "Truyền hình thực tế", "Talk-Show": "Talk show",
    "Game-Show": "Game show",
}


# Mã nước ISO-2 -> tên tiếng Việt (dùng chung)
COUNTRY_VI = {
    "US": "Mỹ", "IN": "Ấn Độ", "GB": "Anh", "FR": "Pháp", "JP": "Nhật", "DE": "Đức", "CA": "Canada",
    "ES": "Tây Ban Nha", "IT": "Ý", "KR": "Hàn Quốc", "CN": "Trung Quốc", "RU": "Nga", "BR": "Brazil",
    "MX": "Mexico", "TR": "Thổ Nhĩ Kỳ", "PH": "Philippines", "AU": "Úc", "HK": "Hồng Kông",
    "AR": "Argentina", "SE": "Thụy Điển", "NG": "Nigeria", "ID": "Indonesia", "TH": "Thái Lan",
    "NZ": "New Zealand", "AT": "Áo", "BE": "Bỉ", "IE": "Ireland", "FI": "Phần Lan", "GG": "Guernsey",
    "CH": "Thụy Sĩ", "NO": "Na Uy", "DK": "Đan Mạch", "NL": "Hà Lan", "PL": "Ba Lan", "PT": "Bồ Đào Nha",
    "VN": "Việt Nam", "TW": "Đài Loan", "SG": "Singapore", "MY": "Malaysia", "ZA": "Nam Phi", "EG": "Ai Cập",
}
