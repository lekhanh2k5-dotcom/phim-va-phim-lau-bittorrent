import sys; sys.path.insert(0, r"D:\dulieulon\notebooks\_src")
from build_nb import build
INTRO = ("# Phần 1.4 — MagnetDB: hệ sinh thái torrent trên mạng DHT\n\n"
 "**MagnetDB** (Seidenberger, Pursell & Maiti, ICWSM 2025; CC-BY 4.0) là bộ dữ liệu học thuật do một crawler \"nghe\" mạng BitTorrent DHT "
 "thu thập từ 12/2018 đến 9/2024: **28,6 triệu torrent** và **950 triệu file**. Phần này nhìn toàn bộ mạng — mọi loại nội dung, "
 "chưa lọc riêng phim.\n\n"
 "Dữ liệu chuẩn bị bởi `src/10_extract_magnetdb_overview.py`: mọi torrent (tên, dung lượng, thời điểm phát hiện), "
 "**mẫu ngẫu nhiên 1% bảng files** (9,5 triệu file) để biết định dạng, và số file của mỗi torrent.\n\n"
 "Lưu ý: dự án chỉ dùng **metadata** (tên, dung lượng, thời gian), không tải nội dung. Thời gian là lúc crawler **phát hiện** torrent, "
 "không phải lúc torrent được tạo. Biểu đồ lưu vào `plots/4_magnetdb/`.")
MD = {
 "01": ("## 1. Mạng DHT chia sẻ những gì?",
        "**Nhận xét.** Hai cách đếm cho hai bức tranh khác hẳn: **theo số file**, hình ảnh (34%, chủ yếu `.jpg`) và âm thanh (`.mp3`) chiếm nhiều nhất; "
        "**theo dung lượng**, **video chiếm ~78%** (`.mkv`, `.mp4`, `.avi`). Một bộ phim 2 GB \"nặng\" bằng hàng nghìn bức ảnh — "
        "nên mạng DHT về bản chất là mạng **phân phối video**, dù số file video không nhiều."),
 "02": ("## 2. Torrent thường nặng bao nhiêu?",
        "**Nhận xét.** Phân bố có đỉnh quanh 1 GB, nhưng nổi bật là các **gai nhọn** đúng ở **700 MB (1 đĩa CD), 1,4 GB (2 CD), 4,37 GiB (DVD-5), 7,95 GiB (DVD-9)**. "
        "Đây là \"di sản\" của thời đĩa vật lý: các nhóm phát hành vẫn nén phim cho vừa dung lượng đĩa dù ngày nay không còn ai ghi đĩa — "
        "một quy ước văn hóa còn sót lại trong dữ liệu."),
 "03": ("## 3. Crawler thu thập có đều không?",
        "**Nhận xét.** **Không.** 9/2019–3/2020 số torrent tăng vọt (crawler quét lại torrent cũ — *burn-in*), 7/2020–3/2021 gần như ngừng. "
        "Chỉ **4/2021–9/2024** là ổn định (~300–450 nghìn torrent/tháng). Mọi phân tích theo thời gian trong dự án chỉ dùng giai đoạn này; "
        "đây là bước **kiểm tra chất lượng dữ liệu** quan trọng trước khi kết luận bất cứ điều gì về xu hướng."),
 "04": ("## 4. Nhìn từng ngày thì sao?",
        "**Nhận xét.** Lịch nhiệt cho thấy nhịp khá đều trong tuần, **giảm dần từ 2022 sang 2024** (màu nhạt dần), "
        "vài ngày đột biến (đầu tháng 7/2022) và **quãng trống gần 1 tháng (6/2024)** khi crawler ngừng. "
        "Những chi tiết này không thấy được trên biểu đồ theo tháng."),
 "05": ("## 5. Giờ nào trong tuần sôi động nhất?",
        "**Nhận xét.** Cao điểm quanh **7h UTC** (14h Việt Nam, sáng châu Âu, chiều tối châu Á) và **17–18h UTC** (tối châu Âu); "
        "thấp nhất từ **tối thứ Sáu đến sáng thứ Bảy**. Chênh lệch chỉ ±15% so với trung bình — mạng toàn cầu nên \"không bao giờ ngủ\". "
        "Thận trọng: đây là giờ crawler *phát hiện*, có thể phản ánh cả lịch hoạt động của chính crawler."),
 "06": ("## 6. Tên torrent viết bằng ngôn ngữ nào?",
        "**Nhận xét.** **~79%** tên chỉ dùng chữ Latin (tiếng Anh và các ngôn ngữ châu Âu), **chữ Hán ~12%** (cộng đồng Trung Quốc rất lớn trên DHT), "
        "**chữ Kirin ~6%** (Nga, Ukraina). Hàn, Nhật (kana), Thái, Ả Rập chỉ chiếm phần nhỏ — các cộng đồng này dùng kênh chia sẻ khác."),
 "07": ("## 7. Một torrent chứa bao nhiêu file?",
        "**Nhận xét.** **40% torrent chỉ có đúng 1 file**, 26% có ≥ 10 file, nhưng đuôi kéo dài tới **hơn 10.000 file**. "
        "Đường gần thẳng trên thang log-log là dấu hiệu của **phân bố đuôi dài** (gần luật lũy thừa) — giống nhiều hệ thống do con người tạo ra "
        "(dung lượng file, lượt xem web, quy mô thành phố)."),
}
SUMMARY = ("## Tóm tắt phần MagnetDB\n\n| Khía cạnh | Phát hiện chính |\n|---|---|\n"
 "| Nội dung | Theo dung lượng, ~78% là video; theo số file, ảnh và nhạc nhiều nhất |\n"
 "| Dung lượng | Gai nhọn ở 700 MB / 1,4 GB / DVD — \"di sản\" của đĩa vật lý |\n"
 "| Chất lượng dữ liệu | Crawler không đều; chỉ 4/2021–9/2024 dùng được cho phân tích xu hướng |\n"
 "| Nhịp thời gian | Cao điểm 7h & 17–18h UTC; vắng nhất cuối tuần |\n"
 "| Ngôn ngữ | ~79% Latin, ~12% chữ Hán, ~6% Kirin |\n"
 "| Cấu trúc | 40% torrent 1 file; phân bố số file đuôi dài |")
build(r"D:\dulieulon\notebooks\_src\04_magnetdb.py", r"D:\dulieulon\notebooks\04_magnetdb.ipynb", INTRO, MD, SUMMARY)
