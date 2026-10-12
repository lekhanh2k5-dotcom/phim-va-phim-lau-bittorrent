import sys; sys.path.insert(0, r"D:\dulieulon\notebooks\_src")
from build_nb import build
INTRO = ("# Phần 3.2 — Phim nào bị chia sẻ lậu, khi nào, và vì sao\n\n"
 "Dùng bảng đã tích hợp ở phần 3.1 (`torrents_clean`, `movie_analysis`): mỗi torrent đã được gắn với một phim IMDb, kèm thông tin TMDb "
 "(ngày ra rạp, ngày ra bản online/Digital theo từng nước). Mọi phân tích theo thời gian chỉ dùng **giai đoạn crawler ổn định 04/2021 – 09/2024** (phần 1.4).\n\n"
 "**Thước đo:** *số torrent khác nhau* của mỗi phim = **nguồn cung** bản lậu (bao nhiêu bản được đăng), **không phải** số người tải "
 "(MagnetDB không có dữ liệu seeder/leecher). Không phân tích sâu bản quay lén CAM/TS vì nhãn ngắn, dễ nhận nhầm. "
 "Biểu đồ lưu vào `plots/7_piracy_movies/`.")
MD = {
 "01": ("## 1. Phim nào bị chia sẻ lậu nhiều nhất?",
        "**Nhận xét.** Top 20 toàn là **bom tấn Hollywood 2021–2023**: *Avatar: The Way of Water* dẫn đầu (~1.250 bản), rồi *Spider-Man: No Way Home*, "
        "*Black Widow*, *Dune*, *The Batman*. Nhiều phim trong top (Black Widow, Dune, Matrix Resurrections, Mortal Kombat, Godzilla vs. Kong) "
        "từng **phát hành online cùng ngày ra rạp** năm 2021 (HBO Max, Disney+ Premier Access)."),
 "02": ("## 2. Phim nổi tiếng hơn có bị lậu nhiều hơn không?",
        "**Nhận xét.** Có: quan hệ log-log khá chặt (**R² ≈ 0,39**), số vote ×10 thì số torrent ×~3,6. Phim nằm **xa phía trên đường** bị chia sẻ lậu nhiều hơn "
        "mức nổi tiếng — chủ yếu phim hành động thương mại (*Transformers: Rise of the Beasts, Snake Eyes, The Expendables 4, Infinite*). "
        "Các điểm **xa phía dưới** cần thận trọng: nhiều ca là **lỗi đo** — vd. *Pinocchio (2022)* có hai phim trùng tên cùng năm nên bị loại khi ghép."),
 "03": ("## 3. Thể loại nào bị lậu nhiều hơn mức nổi tiếng của nó?",
        "**Nhận xét.** Sau khi trừ đi ảnh hưởng của độ nổi tiếng, **phiêu lưu (×1,85), hành động (×1,75), viễn tưởng, hoạt hình** bị chia sẻ lậu nhiều hơn dự đoán; "
        "**tài liệu (×0,64), âm nhạc, tiểu sử** ít hơn. Phim \"xem vì hiệu ứng hình ảnh\" là loại được săn bản lậu chất lượng cao nhiều nhất."),
 "04": ("## 4. Phim nói tiếng gì bị lậu nhiều so với độ nổi tiếng?",
        "**Nhận xét.** Phim tiếng **Nga (×2,1), Trung (×2,0), Ba Lan (×1,9)** bị chia sẻ gấp đôi mức nổi tiếng — khớp với phần 1.4: cộng đồng Kirin và Hán rất đông trên DHT, "
        "Ba Lan có văn hóa lồng tiếng (*lektor*) riêng. Ngược lại phim **Hindi, Thổ Nhĩ Kỳ, Ả Rập, Bengal** ít hơn nhiều: khán giả các nước này "
        "có thể xem lậu qua kênh khác (web xem trực tuyến, Telegram) mà MagnetDB không ghi nhận. Lưu ý: số vote IMDb nghiêng về khán giả phương Tây."),
 "05": ("## 5. Bản lậu mới thuộc phim mới hay phim cũ?",
        "**Nhận xét.** Chỉ khoảng **40–48%** bản lậu mới là phim của thập niên 2020; **~1/3 là phim sản xuất trước 2010**, ~10% là phim trước 1980. "
        "Phim kinh điển liên tục được đăng lại dưới dạng remaster, Blu-ray 4K, bản lồng tiếng mới — **phim cũ không bao giờ \"chết\"** trên mạng chia sẻ."),
 "06": ("## 6. Điều gì xảy ra khi phim ra bản xem hợp pháp online?",
        "**Nhận xét.** Kết quả **ngược với giả thuyết tiện lợi** (\"có cách xem hợp pháp thì bớt lậu\"): số bản lậu mới **tăng ~20 lần đúng tuần phim ra bản online**, "
        "gần hết là bản WEB. Lý do: **bản online hợp pháp chính là nguyên liệu** để làm bản lậu chất lượng cao. Vì dữ liệu chỉ đo nguồn cung (số bản được đăng), "
        "ta **không kết luận được** về số người tải — người xem có thể vẫn giảm tải lậu dù số bản được đăng tăng."),
 "07": ("## 7. Bản lậu chất lượng cao xuất hiện nhanh đến mức nào?",
        "**Nhận xét.** Rất nhanh: **trung vị 0 ngày** — với ~46% phim, bản WEB lậu xuất hiện ngay trong ngày 0–1 sau khi phim ra bản online ở Mỹ. "
        "Nhóm \"≤ −7 ngày\" phần lớn là phim đã ra online ở nước khác trước Mỹ (82%). Thời gian \"bảo vệ\" của bản online gần như bằng 0."),
 "08": ("## 8. Ra bản online sớm có làm tăng tổng lượng bản lậu không?",
        "**Nhận xét.** So sánh tổng bản lậu **trong năm đầu** (đủ dài để mọi nhóm đều đã có bản online), có tính đến độ nổi tiếng, năm, thể loại: "
        "phát hành rạp + online **cùng ngày** cao hơn **+14% nhưng chưa có ý nghĩa thống kê** (p = 0,08); chiếu rạp 46–90 ngày không khác; "
        "> 90 ngày thấp hơn 29% (p = 0,03, chỉ 60 phim). → Thời điểm ra bản online chủ yếu quyết định bản lậu **xuất hiện khi nào**, chưa thấy thay đổi rõ **tổng lượng**."),
}
SUMMARY = ("## Tóm tắt phần 3.2\n\n| Câu hỏi | Trả lời |\n|---|---|\n"
 "| Phim nào bị lậu nhiều? | Bom tấn 2021–2023; tỷ lệ thuận với độ nổi tiếng (R² ≈ 0,39) |\n"
 "| Thể loại | Phiêu lưu, hành động, viễn tưởng bị lậu vượt mức nổi tiếng |\n"
 "| Ngôn ngữ | Phim tiếng Nga, Trung, Ba Lan bị lậu gấp đôi mức nổi tiếng |\n"
 "| Phim cũ | ~1/3 bản lậu mới là phim trước 2010 |\n"
 "| Bản online hợp pháp | Làm bản lậu tăng vọt (là nguồn rip); bản WEB lậu xuất hiện trong ngày |\n"
 "| Chiến lược phát hành | Ảnh hưởng thời điểm, chưa thấy ảnh hưởng rõ tổng lượng |\n\n"
 "**Giới hạn:** thước đo là nguồn cung (số bản đăng), không phải số người tải; tương quan, không phải nhân quả.")
build(r"D:\dulieulon\notebooks\_src\07_piracy_movies.py", r"D:\dulieulon\notebooks\07_piracy_movies.ipynb", INTRO, MD, SUMMARY)
