import sys; sys.path.insert(0, r"D:\dulieulon\notebooks\_src")
from build_nb import build
INTRO = ("# Phần 1.2 — TMDb: kinh doanh và phát hành phim\n\n"
 "Notebook này dùng **TMDb API** (chi tiết phim + ngày phát hành theo từng nước), ghép với IMDb để lấy thể loại và số vote. "
 "Dữ liệu chuẩn bị bởi `src/06_fetch_tmdb.py` → `src/07_tmdb_to_table.py`: ~138k phim, gồm **mọi phim IMDb có ≥ 1.000 vote** "
 "(không giới hạn ở phim có trên torrent).\n\n"
 "Lưu ý dữ liệu: TMDb ghi ngân sách/doanh thu = 0 khi không rõ → coi là thiếu; chỉ ~9.300 phim có đủ cả hai (chủ yếu phim Mỹ/phim lớn). "
 "Tiền là **USD danh nghĩa**, chưa điều chỉnh lạm phát. Biểu đồ lưu vào `plots/2_tmdb/`.")
MD = {
 "01": ("## 1. Phim có thu hồi được vốn không?",
        "**Nhận xét.** Doanh thu tăng gần tỷ lệ với ngân sách, nhưng phân tán rất lớn (trục log: mỗi vạch = ×10). "
        "Chỉ **~33% phim vượt ngưỡng hòa vốn ước tính ×2,5** (ngân sách sản xuất chưa gồm quảng bá; rạp giữ ~50% doanh thu vé). "
        "Các \"cú hit\" ngân sách thấp (vd. *Lost in Thailand* ×95, *E.T.* ×76) cho thấy lợi nhuận cực lớn đến từ phim rẻ, không phải bom tấn. "
        "Thiên lệch: phim thất bại thường không công bố doanh thu → tỷ lệ thật có thể còn thấp hơn."),
 "02": ("## 2. Thể loại nào sinh lời nhất?",
        "**Nhận xét.** **Trung vị của mọi thể loại đều dưới ngưỡng hòa vốn ×2,5** — phần lớn phim không có lãi. "
        "Hoạt hình và phiêu lưu cao nhất (×1,9), kinh dị ×1,8 nhưng có **đuôi trên dài nhất** (phim kinh dị rẻ đôi khi lãi cực lớn). "
        "Lịch sử và chiến tranh thấp nhất (×0,8): ngân sách dựng cảnh lớn, khán giả hẹp."),
 "03": ("## 3. Bom tấn ra rạp vào tháng nào?",
        "**Nhận xét.** Phim nói chung ra rải rác quanh năm (mùa thu nhiều phim nhỏ), nhưng **bom tấn (≥ $300 triệu) dồn vào mùa hè (Th5–Th7) "
        "và mùa lễ cuối năm (Th11–Th12)** — đúng hai mùa nghỉ học/nghỉ lễ ở Mỹ. Tháng 1–4 và 8–10 gần như vắng bom tấn."),
 "04": ("## 4. Phim lên bản online sau bao lâu?",
        "**Nhận xét.** Trước COVID, phim ở rạp độc quyền **~76 ngày** (trung vị 2015–19) mới lên bản online. "
        "Khi rạp đóng cửa (2020–21), nhiều phim phát hành online cùng ngày hoặc ngay sau đó. "
        "Sau khi rạp mở lại, cửa sổ **không quay về mức cũ mà ổn định ở ~32 ngày** — COVID đã thay đổi vĩnh viễn mô hình phát hành."),
 "05": ("## 5. Phim được sản xuất ở đâu?",
        "**Nhận xét.** Mỹ chiếm **~38%** số phim (2000–2024) trên TMDb, **Ấn Độ ~10%** đứng thứ hai, rồi Pháp, Nhật. "
        "Lưu ý thiên lệch: TMDb do cộng đồng (chủ yếu phương Tây) đóng góp nên phim Mỹ được ghi nhận đầy đủ hơn — "
        "theo số liệu chính thức, Ấn Độ thực tế sản xuất nhiều phim hơn Mỹ mỗi năm."),
 "06": ("## 6. Phim nhượng quyền chiếm bao nhiêu doanh thu?",
        "**Nhận xét.** Phim thuộc loạt (phần tiếp theo, vũ trụ điện ảnh) chỉ chiếm **~20–30% số phim** nhưng **50–70% doanh thu**, "
        "và tỷ trọng doanh thu tăng rõ từ thập niên 2000 (kỷ nguyên Marvel, Harry Potter…). Năm 2020 giảm vì bom tấn dời lịch do COVID."),
 "07": ("## 7. Hãng nào đứng sau doanh thu lớn nhất?",
        "**Nhận xét.** Các \"Big Five\" Hollywood (Warner Bros., Universal, Columbia/Sony, Fox, Paramount) dẫn đầu về tổng doanh thu. "
        "**Marvel Studios** chỉ 38 phim nhưng đạt ~$33 tỷ — hiệu quả trên mỗi phim cao nhất; Pixar tương tự (25 phim, ~$16 tỷ). "
        "Lưu ý phim đồng sản xuất được tính cho mọi hãng, nên các cột không cộng lại được."),
}
SUMMARY = ("## Tóm tắt phần TMDb\n\n| Khía cạnh | Phát hiện chính |\n|---|---|\n"
 "| Lợi nhuận | Chỉ ~1/3 phim vượt hòa vốn; trung vị mọi thể loại đều lỗ hoặc hòa |\n"
 "| Thể loại | Hoạt hình, phiêu lưu sinh lời nhất; lịch sử, chiến tranh kém nhất |\n"
 "| Lịch phát hành | Bom tấn dồn vào hè và cuối năm |\n"
 "| Cửa sổ chiếu rạp | COVID rút từ ~76 xuống ~32 ngày và không quay lại |\n"
 "| Địa lý | Mỹ ~38%, Ấn Độ ~10% (có thiên lệch nguồn) |\n"
 "| Nhượng quyền | ~25% số phim nhưng tới ~70% doanh thu |")
build(r"D:\dulieulon\notebooks\_src\02_tmdb.py", r"D:\dulieulon\notebooks\02_tmdb.ipynb", INTRO, MD, SUMMARY)
