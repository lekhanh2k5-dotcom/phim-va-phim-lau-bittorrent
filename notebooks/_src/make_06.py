import sys; sys.path.insert(0, r"D:\dulieulon\notebooks\_src")
from build_nb import build
INTRO = ("# Phần 3.1 — Ghép torrent với phim: phương pháp và chất lượng tích hợp\n\n"
 "Chương 3 phân tích **phim lậu**. Trước hết phải trả lời: *mỗi torrent là phim nào?* MagnetDB không có khóa phim chuẩn, nên đây là bài toán "
 "**ghép thực thể (entity matching)** — phần cốt lõi của tích hợp dữ liệu. Hai nguồn ghép được dùng song song:\n\n"
 "1. **Mã IMDb có sẵn của MagnetDB** (`movieMatchTitleId`, cấp file, chỉ các ca `matchScore > 138`) — có lỗi và phủ thấp.\n"
 "2. **Tự ghép tên torrent** (`src/04_match_torrent_names.py`): tách *tên + năm* từ tên torrent bằng biểu thức chính quy trong DuckDB, "
 "tra chính xác trong chỉ mục tên IMDb (gồm `title.akas`), bỏ các ca mơ hồ.\n\n"
 "Sau đó gộp và lọc chung (`src/09_build_tables.py`, 10 bước A–J). Biểu đồ lưu vào `plots/6_integration/`.")
MD = {
 "01": ("## 1. Mỗi bước làm sạch loại bỏ bao nhiêu?",
        "**Nhận xét.** Nguồn ① giảm mạnh từ **518k → 170k torrent**: phần lớn bị loại vì là phim bộ hoặc không phải phim (bước A), rồi các lỗi ghép "
        "(năm không khớp, tên không giống, sai phần phim). Nguồn ② tự ghép tên torrent cho **~2,25 triệu** torrent, bỏ ~8% ca mơ hồ "
        "(trùng tên nhiều phim, tên quá chung chung như \"New\", \"Cricket\"). Sau khi gộp và lọc chung (bỏ torrent xuất hiện trước khi phim tồn tại, "
        "mâu thuẫn giữa hai nguồn, torrent giả) còn **~2,07 triệu torrent sạch**."),
 "02": ("## 2. Tự ghép tên torrent thêm được bao nhiêu dữ liệu?",
        "**Nhận xét.** Phần màu cam (chỉ tự ghép mới tìm ra) chiếm gần hết: lượng torrent phim tăng **khoảng 14 lần** so với chỉ dùng mã có sẵn. "
        "Lý do: MagnetDB *tách tên đúng nhưng tra IMDb sai* rồi loại vì điểm thấp — vd. `Deadpool.2016.1080p.BluRay` bị ghép với một video ca nhạc "
        "\"Deadpool (feat. Deadpool)\" (điểm 11/138)."),
 "03": ("## 3. Điều gì xảy ra nếu chỉ dùng dữ liệu có sẵn?",
        "**Nhận xét.** Gần như **mọi bom tấn \"biến mất\"**: *Top Gun: Maverick, Dune, The Batman, Black Widow…* có 0 torrent theo mã của MagnetDB, "
        "nhưng 700–950 torrent sau khi tự ghép. Chỉ *The Matrix Resurrections* được MagnetDB ghép tốt. Mọi kết luận về phim lậu dựa trên dữ liệu gốc "
        "sẽ sai lệch nghiêm trọng — đây là đóng góp quan trọng nhất của bước tích hợp."),
 "04": ("## 4. Phép ghép đáng tin đến đâu?",
        "**Nhận xét.** ① Pipeline tách tên file (guessit + rapidfuzz) đạt **precision ~0,88** so với mã MagnetDB; recall thấp hơn (~0,63) vì cố tình bỏ phim bộ "
        "và tên Nga phiên âm Latin. ② Tự ghép tên torrent trùng **81,7%** với mã *gốc* của MagnetDB nhưng **99,4%** với mã MagnetDB *đã làm sạch* — "
        "khoảng chênh chính là các lỗi của mã gốc mà bước làm sạch đã loại. Lưu ý: đây là **mức đồng thuận** giữa hai phương pháp, không phải độ chính xác "
        "tuyệt đối; kiểm tra bằng mắt hàng trăm mẫu ngẫu nhiên cho thấy hầu hết đều đúng."),
}
SUMMARY = ("## Tóm tắt phần 3.1\n\n| Khía cạnh | Kết quả |\n|---|---|\n"
 "| Dữ liệu cuối | ~2,07 triệu torrent sạch, ~126k phim |\n"
 "| Độ phủ | Tự ghép tăng dữ liệu phim ~14 lần; bom tấn gần như không có trong dữ liệu gốc |\n"
 "| Chất lượng | Đồng thuận 99,4% với mã MagnetDB đã làm sạch |\n"
 "| Hạn chế | Cần năm trong tên torrent; bỏ phim trùng tên; ~1% có thể vẫn ghép sai |")
build(r"D:\dulieulon\notebooks\_src\06_integration.py", r"D:\dulieulon\notebooks\06_integration.ipynb", INTRO, MD, SUMMARY)
