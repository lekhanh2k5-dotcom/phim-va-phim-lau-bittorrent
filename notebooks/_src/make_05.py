import sys; sys.path.insert(0, r"D:\dulieulon\notebooks\_src")
from build_nb import build
INTRO = ("# Phần 2 — Kết hợp các nguồn\n\n"
 "Phần 1 nhìn từng nguồn riêng lẻ. Phần này **ghép các nguồn** để trả lời những câu hỏi mà không nguồn nào trả lời được một mình: "
 "chất lượng (IMDb) so với thành công thương mại (TMDb), cơ cấu sản xuất so với cơ cấu doanh thu, chất lượng kho phim của từng nền tảng streaming.\n\n"
 "Khóa nối chung là **mã phim IMDb (`tconst`)**: TMDb trả về `imdb_id` cho mỗi phim; MagnetDB không có khóa này nên phải **ghép thực thể** "
 "từ tên file/torrent (chương 3). Biểu đồ lưu vào `plots/5_combined/`.")
MD = {
 "01": ("## 1. Ba nguồn nối với nhau như thế nào?",
        "**Nhận xét.** IMDb là **trục trung tâm**: TMDb nối thẳng qua `imdb_id` (gọi API `/find`), còn MagnetDB chỉ có tên file tự do nên cần "
        "một bước **ghép thực thể** (tên + năm + tên theo từng nước trong `title.akas`). Kết quả là các bảng phân tích trong `data_clean/` — "
        "mỗi bảng ở một mức chi tiết khác nhau (phim, cặp torrent–phim, phim × nước × loại phát hành)."),
 "02": ("## 2. Phim hay có ăn khách không? (IMDb × TMDb)",
        "**Nhận xét.** Có, nhưng **yếu**: tương quan hạng Spearman chỉ **ρ ≈ 0,20**. Trung vị doanh thu tăng theo điểm, nhưng ở mọi mức điểm, doanh thu "
        "dao động hàng nghìn lần. Có những bom tấn tỷ đô bị chấm thấp (*Twilight: Breaking Dawn – Part 1* 5,0, *F9* 5,2) và những phim kinh điển "
        "điểm rất cao nhưng doanh thu phòng vé nhỏ (*The Shawshank Redemption* 9,3) — thành công thương mại phụ thuộc vào marketing, thương hiệu, lịch chiếu… nhiều hơn chất lượng."),
 "03": ("## 3. Nhiều tiền hơn có làm phim hay hơn? (IMDb × TMDb)",
        "**Nhận xét.** **Không.** Trung vị điểm gần như bằng nhau ở mọi mức ngân sách (6,4–6,6); phim kinh phí thấp còn có đuôi điểm cao dài hơn. "
        "Ngân sách lớn giúp phim **ít khi quá tệ** (đuôi dưới ngắn hơn) nhưng không đảm bảo phim hay. "
        "Biểu đồ *raincloud* kết hợp phân bố (mây), từng phim (mưa) và tóm tắt (thanh + chấm) trong một hình."),
 "04": ("## 4. Thể loại: nhiều phim có nghĩa là nhiều tiền? (IMDb × TMDb)",
        "**Nhận xét.** Hai bức tranh gần như đảo ngược: **tài liệu** chiếm 28% số phim sản xuất nhưng ~0% doanh thu; **chính kịch** 26% → 12%. "
        "Ngược lại **phiêu lưu** (2% → 18%), **hành động** (4% → 16%), **hoạt hình, viễn tưởng, kỳ ảo** (~1% → 5%) là các thể loại \"ít phim mà nhiều tiền\" — "
        "đúng là các thể loại của bom tấn Hollywood."),
 "05": ("## 5. Nền tảng nào có kho phim \"chất lượng\" nhất? (IMDb × TMDb/JustWatch)",
        "**Nhận xét.** **Criterion Channel (7,2)** và **Max (7,1)** có trung vị điểm IMDb cao nhất, rồi Apple TV+, MUBI. "
        "**Prime Video, Tubi, Pluto TV (6,0)** thấp nhất — đây là các kho **lớn** (hàng nghìn phim) nên chứa nhiều phim trung bình. "
        "Có một sự đánh đổi rõ: **kho càng lớn, điểm trung vị càng thấp**."),
 "06": ("## 6. Phim nổi tiếng và phim hay có dễ xem hợp pháp hơn? (IMDb × TMDb/JustWatch)",
        "**Nhận xét.** **Độ nổi tiếng** là yếu tố chính: phim > 300 nghìn vote có mặt trên dịch vụ thuê bao/miễn phí ở 50–76 nước, phim < 3 nghìn vote chỉ ở 2–8 nước. "
        "Bất ngờ là **ở cùng độ nổi tiếng, phim điểm cao lại có mặt ở ÍT nước hơn** (nhóm 300k–1tr vote: 6–6,5 điểm → 76 nước, ≥ 8 điểm → 50 nước) — "
        "có thể vì phim kinh điển/nghệ thuật được cấp phép hẹp và đắt hơn, còn phim giải trí đại chúng được phân phối rộng."),
}
SUMMARY = ("## Tóm tắt phần 2\n\n| Câu hỏi | Trả lời |\n|---|---|\n"
 "| Phim hay có ăn khách? | Chỉ một chút (ρ ≈ 0,20) |\n"
 "| Nhiều tiền → phim hay? | Không; ngân sách chỉ giúp tránh phim quá tệ |\n"
 "| Thể loại | Tài liệu/chính kịch: nhiều phim, ít tiền; phiêu lưu/hành động: ngược lại |\n"
 "| Chất lượng kho phim | Criterion, Max cao nhất; kho lớn (Prime, Tubi) thấp nhất |\n"
 "| Khả năng xem hợp pháp | Do độ nổi tiếng quyết định; phim điểm cao không dễ xem hơn |")
build(r"D:\dulieulon\notebooks\_src\05_combined.py", r"D:\dulieulon\notebooks\05_combined.ipynb", INTRO, MD, SUMMARY)
