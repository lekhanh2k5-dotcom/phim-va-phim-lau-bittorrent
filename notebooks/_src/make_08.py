import sys; sys.path.insert(0, r"D:\dulieulon\notebooks\_src")
from build_nb import build
INTRO = ("# Phần 3.3 — Hệ sinh thái phim lậu: ai đăng, bằng công nghệ gì, cho cộng đồng nào\n\n"
 "Tên torrent không chỉ chứa tên phim mà còn \"tự khai\" rất nhiều thông tin: **nhóm/trang phát hành** (YTS, RARBG, TGx…), **codec** (x264, x265, AV1), "
 "**độ phân giải**, **dịch vụ streaming được rip** (AMZN, NF, DSNP…), **ngôn ngữ lồng tiếng** (Hindi, Dublado, Lektor PL…). Phần này tách các thông tin đó "
 "bằng biểu thức chính quy trên ~920 nghìn torrent phim (sạch) của giai đoạn ổn định 04/2021 – 09/2024.\n\n"
 "Lưu ý: nhận diện bằng từ khóa nên có sai số; nhiều torrent không ghi đủ thông tin (nhóm \"không ghi\" được giữ lại để tỷ lệ trung thực). "
 "Biểu đồ lưu vào `plots/8_piracy_ecosystem/`.")
MD = {
 "01": ("## 1. Ai là người phát hành bản lậu nhiều nhất?",
        "**Nhận xét.** Hai \"thương hiệu\" thống trị suốt giai đoạn: **RARBG** (#1 cho đến 2023) và **YTS** (bản nén nhẹ, phổ biến). "
        "Sau khi RARBG đóng cửa (31/5/2023), YTS lên #1, **GalaxyRG/TGx** và **TamilMV/TamilBlasters** (phim Ấn Độ) leo hạng. "
        "Các nhóm \"scene\" như EVO, FGT dao động ở cuối bảng."),
 "02": ("## 2. RARBG đóng cửa — ai lấp chỗ trống?",
        "**Nhận xét.** Đây là một **\"thí nghiệm tự nhiên\"**: ngày 31/5/2023 RARBG tuyên bố ngừng hoạt động. Số bản RARBG mới **sụp đổ ngay lập tức** "
        "(phần còn lại là bản cũ được người khác đăng lại). YTS và GalaxyRG/TGx tăng thị phần (YTS 5,9% → 8,4%, TGx 2,2% → 3,5%) nhưng **không bù được** phần mất của RARBG "
        "(7,5% → 2,8%) — hệ sinh thái mất đi một nguồn cung lớn, phần còn lại phân tán cho rất nhiều nhóm nhỏ."),
 "03": ("## 3. Bản lậu dùng công nghệ nén nào?",
        "**Nhận xét.** **x264/AVC** vẫn phổ biến nhất (~1/3), nhưng **x265/HEVC** (nén tốt hơn ~50%) tăng đều từ ~13% lên ~17%; **AV1** (codec mở, mới) bắt đầu xuất hiện. "
        "XviD/DivX — chuẩn của thập niên 2000 — vẫn còn ~7%, chủ yếu là phim cũ. ~40% torrent không ghi codec."),
 "04": ("## 4. Bản lậu nét đến mức nào?",
        "**Nhận xét.** **1080p là chuẩn** (~42%); **4K/2160p tăng gấp ba** (~3% → ~9%) theo sự phổ biến của TV 4K và bản WEB-DL 4K từ các dịch vụ streaming. "
        "Bản SD vẫn còn ~8% (phim cũ, máy cấu hình thấp, mạng chậm)."),
 "05": ("## 5. Bản WEB lậu được rip từ dịch vụ streaming nào?",
        "**Nhận xét.** Trong các bản WEB có ghi nguồn, **Amazon (~50%)** và **Netflix (~31%)** chiếm áp đảo, rồi Disney+, Max, Apple TV+/iTunes. "
        "Điều này khớp với phần 1.3: Prime Video và Netflix có kho phim và độ phủ toàn cầu lớn nhất — **nền tảng càng lớn càng là nguồn rip lớn**. "
        "Lưu ý chỉ ~13% bản WEB có ghi tên dịch vụ."),
 "06": ("## 6. Phim nước nào được \"bản địa hóa\" cho cộng đồng nào?",
        "**Nhận xét.** **Phim Mỹ/Anh** được lồng tiếng/phụ đề cho **mọi** cộng đồng (Trung 23%, Nga 19%, Ba Lan 12%, Tây Ban Nha 11%, Pháp, Ý ~10%). "
        "Ngược lại, phim châu Á **chủ yếu ở lại trong cộng đồng của mình**: 80% torrent phim Hindi có tag Hindi, 83% phim Nam Ấn có tag Tamil/Telugu/Malayalam, "
        "85% phim Hoa ngữ có chữ Hán. Phim Hàn, Nhật được cộng đồng Trung Quốc chia sẻ nhiều (36%, 61%) — dấu vết của làn sóng Hallyu và anime."),
 "07": ("## 7. Các trang lậu Nam Á hoạt động thế nào?",
        "**Nhận xét.** **TamilMV, TamilBlasters, MovieRulz** đăng đều đặn 200–450 torrent phim mỗi tháng suốt 3 năm dù liên tục bị chặn tên miền "
        "(tên trang trong torrent đổi đuôi: `.tc`, `.cz`, `.win`…). **TamilRockers** — từng là trang nổi tiếng nhất — gần như biến mất. "
        "Vết sụt 6/2024 là do crawler ngừng, không phải do các trang."),
 "08": ("## 8. Torrent giả trông như thế nào?",
        "**Nhận xét.** Torrent giả (2% torrent phim) nhắm vào **bom tấn đang chiếu rạp**: tự xưng \"WEB-DL\" hay \"BluRay\" khi phim **chưa có bản online** "
        "(vạch đen = ngày ra rạp; nhiều chấm còn xuất hiện cả *trước* ngày ra rạp). Nhiều phim có **cụm chấm dày** — một đợt đăng hàng loạt cùng lúc "
        "(vd. *Old*, *Fantastic Beasts*, *Sonic 2*), dấu hiệu của spam/mã độc tự động. Đây là lý do bộ lọc J được thêm vào quy trình làm sạch."),
}
SUMMARY = ("## Tóm tắt phần 3.3\n\n| Khía cạnh | Phát hiện chính |\n|---|---|\n"
 "| Nhà phát hành | RARBG, YTS thống trị; RARBG đóng cửa 5/2023 để lại khoảng trống không ai lấp hết |\n"
 "| Công nghệ | x265 tăng dần, AV1 xuất hiện; 4K tăng gấp ba, 1080p là chuẩn |\n"
 "| Nguồn rip | Amazon và Netflix chiếm ~80% bản WEB có ghi nguồn |\n"
 "| Ngôn ngữ | Phim Hollywood được bản địa hóa cho mọi cộng đồng; phim châu Á ở lại trong cộng đồng |\n"
 "| Nam Á | Các trang lậu sống dai dù bị chặn tên miền |\n"
 "| Torrent giả | ~2%, nhắm vào bom tấn đang chiếu rạp, thường đăng hàng loạt |")
build(r"D:\dulieulon\notebooks\_src\08_piracy_ecosystem.py", r"D:\dulieulon\notebooks\08_piracy_ecosystem.ipynb", INTRO, MD, SUMMARY)
