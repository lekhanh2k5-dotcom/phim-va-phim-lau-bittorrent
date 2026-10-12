import sys; sys.path.insert(0, r"D:\dulieulon\notebooks\_src")
from build_nb import build
INTRO = ("# Phần 1.3 — JustWatch: thị trường streaming hợp pháp\n\n"
 "Phần này dùng mục *watch providers* trong cùng các lần gọi **TMDb API** ở phần 1.2 — TMDb lấy dữ liệu này từ **JustWatch** "
 "(theo điều khoản phải ghi nguồn JustWatch). Với mỗi phim, ở mỗi nước, "
 "phim đang có trên dịch vụ nào và theo hình thức nào (**thuê bao**, **miễn phí**, **miễn phí có quảng cáo**, **thuê lẻ**, **mua**). "
 "Bảng `data_clean/tmdb_watch_providers.parquet`: ~8,6 triệu dòng, 139 nước, ~780 dịch vụ.\n\n"
 "Lưu ý: đây là **ảnh chụp hiện tại (2026)**, không có lịch sử; chỉ tính các phim trong tập phim của dự án (~104k phim có dữ liệu). "
 "Tên dịch vụ được gộp về thương hiệu (\"Netflix Standard with Ads\" → Netflix); các \"kênh\" bán kèm qua nền tảng khác "
 "(\"... Amazon Channel\") bị bỏ để không đếm trùng. Biểu đồ lưu vào `plots/3_tmdb_streaming/`.")
MD = {
 "01": ("## 1. Ở đâu xem được nhiều phim hợp pháp nhất?",
        "**Nhận xét.** Kho phim xem qua thuê bao/miễn phí lớn nhất ở **Mỹ (~57k phim), Canada, Anh**, rồi Tây Âu và Úc. "
        "Châu Phi, Trung Đông, Đông Nam Á có kho nhỏ hơn nhiều. Trung Quốc và phần lớn Trung Á **không có dữ liệu** (JustWatch không theo dõi) — "
        "không có nghĩa là không có streaming."),
 "02": ("## 2. Nền tảng nào phủ rộng, nền tảng nào có kho phim sâu?",
        "**Nhận xét.** Chỉ **Prime Video, Netflix, Plex** có mặt ở > 120 nước. **Tubi** (miễn phí có quảng cáo) có kho phim lớn nhất "
        "nhưng chỉ ở vài nước. Disney+ và Max phủ 60–85 nước với kho nhỏ hơn. Có hai chiến lược: **phủ rộng toàn cầu** vs **kho sâu tại vài thị trường**."),
 "03": ("## 3. Người xem tiếp cận phim hợp pháp bằng cách nào?",
        "**Nhận xét.** Ở hầu hết các nước, phần lớn lượt phim vẫn là **thuê/mua lẻ** (vàng + hồng). Tây Ban Nha, Brazil, Ý có tỷ lệ thuê bao cao nhất. "
        "**Mỹ và Canada** nổi bật với nhiều phim **miễn phí / miễn phí có quảng cáo** (Tubi, Pluto TV, Plex…) — mô hình FAST đang phát triển mạnh ở Bắc Mỹ."),
 "04": ("## 4. Kho phim các nền tảng có trùng nhau không?",
        "**Nhận xét.** Gần như **không trùng**: ~96% phim chỉ có trên đúng một trong 8 nền tảng thuê bao lớn ở Mỹ. "
        "Tổ hợp nhiều nền tảng nhất (Prime Video + Peacock) chỉ ~200 phim. Muốn xem đủ phim, người xem phải đăng ký **nhiều dịch vụ cùng lúc** — "
        "đây là sự \"phân mảnh\" thường được nhắc tới như một động cơ của việc xem lậu (sẽ quay lại ở phần 3)."),
 "05": ("## 5. Mỗi nền tảng mạnh về thể loại nào?",
        "**Nhận xét.** Mỗi nền tảng có \"bản sắc\" rõ: **Disney+** áp đảo hoạt hình (23%), gia đình (35%), phiêu lưu (51%) và gần như không có kinh dị/giật gân. "
        "**Max** và **Apple TV+** mạnh phim tài liệu (24%, 22%). **Peacock** mạnh kinh dị (26%). Netflix và Prime Video cân bằng hơn — đúng vai \"siêu thị\" phim."),
 "06": ("## 6. Một phim trên Netflix có ở bao nhiêu nước?",
        "**Nhận xét.** Phân bố **hai đỉnh** rõ rệt: **38% phim chỉ có ở 1–3 nước** (bản quyền mua theo từng thị trường), "
        "trong khi **~2.700 phim có ở ≥ 100 nước** (phim Netflix sản xuất hoặc mua bản quyền toàn cầu). "
        "Cùng một thuê bao Netflix, kho phim ở mỗi nước rất khác nhau."),
}
SUMMARY = ("## Tóm tắt phần streaming (TMDb / JustWatch)\n\n| Khía cạnh | Phát hiện chính |\n|---|---|\n"
 "| Địa lý | Kho phim hợp pháp lớn nhất ở Bắc Mỹ, Tây Âu, Úc |\n"
 "| Nền tảng | Chỉ Prime Video, Netflix, Plex phủ > 120 nước |\n"
 "| Hình thức | Thuê/mua lẻ vẫn chiếm phần lớn; Bắc Mỹ nhiều phim miễn phí có quảng cáo |\n"
 "| Phân mảnh | ~96% phim chỉ có trên 1 nền tảng; kho Netflix khác nhau theo từng nước |\n"
 "| Bản sắc | Disney+ = gia đình/hoạt hình; Max, Apple TV+ = tài liệu; Peacock = kinh dị |")
build(r"D:\dulieulon\notebooks\_src\03_tmdb_streaming.py", r"D:\dulieulon\notebooks\03_tmdb_streaming.ipynb", INTRO, MD, SUMMARY)
