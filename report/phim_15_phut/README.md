# Phim qua ba góc nhìn — Slide và dashboard 15 phút

Mở `slides.html` để thuyết trình; mở `dashboard.html` để khám phá dữ liệu. Dùng Chrome hoặc Edge. Hai trang hoạt động ngoại tuyến, không cần cài đặt hay chạy máy chủ. Dashboard có phần tổng quan nguồn dùng ảnh trong `assets/`; giữ nguyên thư mục này khi sao chép. Bản ZIP chứa đủ các tệp cần dùng.

## Bộ slide

15 slide: 2 slide mở đầu, 6 biểu đồ giới thiệu từng nguồn, 1 sơ đồ tích hợp, 1 biểu đồ độ phủ ghép, 3 biểu đồ phân tích chung, 1 slide hướng dẫn demo dashboard và 1 slide kết luận. Có 10 biểu đồ dữ liệu và 1 sơ đồ. Lời nói dự kiến 12 phút 40 giây, dành 2 phút 20 giây dự phòng.

| Phần | Slide | Thời gian |
|---|---|---|
| Mở đầu và giải thích nguồn | 1–2 | 1 phút 25 giây |
| IMDb | 3–4 | 1 phút 45 giây |
| TMDb / JustWatch | 5–6 | 1 phút 35 giây |
| MagnetDB | 7–8 | 1 phút 20 giây |
| Tích hợp | 9–10 | 1 phút 30 giây |
| Phân tích chung | 11–13 | 3 phút 30 giây |
| Demo dashboard | 14 | 1 phút |
| Kết luận | 15 | 35 giây |

Dùng ←/→ hoặc Space để chuyển; N mở lời dẫn; Z phóng to biểu đồ; F toàn màn hình; M mở mục lục. Nút Dashboard mở dashboard ở một tab riêng. Có bản `slides.pdf` 15 trang để chia sẻ hoặc trình bày khi cần. Lời dẫn và cách chuyển phần nằm trong `kich_ban.md` và bảng Lời dẫn của slide.

Các biểu đồ slide lấy từ dự án ba nguồn gốc; lời dẫn được viết lại theo mạch 15 phút. Các kết luận được giới hạn ở mối liên hệ quan sát. Không dùng biểu đồ “tăng 22 lần” vì bộ lọc trước Digital ảnh hưởng phân bố đó.

## Dashboard

Ba phần: **Khám phá tích hợp**, **Hiểu từng nguồn**, **Cách đọc dữ liệu**. Các bộ lọc chỉ áp dụng cho phần Khám phá; hình tổng quan nguồn giữ phạm vi gốc.

- Lọc theo khoảng năm IMDb, thể loại, bình chọn tối thiểu, tình trạng ghi nhận torrent, nơi xem streaming tại Mỹ và tên/mã phim.
- Bốn chỉ số: số phim, tổng cặp torrent–phim, tỷ lệ phim có ghi nhận torrent và tỷ lệ có hồ sơ TMDb.
- Hai hình chính ở đầu trang: cột trung vị torrent theo nhóm bình chọn và thanh ngang theo thể loại. Có thể chuyển hình thể loại giữa số phim và torrent trung vị/phim.
- So sánh trực tiếp hai thể loại bằng hai màu: số phim, bình chọn trung vị, torrent trung vị và tỷ lệ có ghi nhận. Phần so sánh giữ các bộ lọc khác, dùng hai lựa chọn thể loại riêng.
- Hình độ trễ WEB–Digital Mỹ, nơi xem và biểu đồ chấm từng phim nằm ở phía dưới.
- Bảng phim có sắp xếp, phân trang, hồ sơ từng phim và xuất CSV theo nhóm đang chọn.

Dashboard gồm **47.089 phim** không gắn cờ `is_adult`, có năm 1920–2024 và từ 1.000 lượt bình chọn. Nhóm mặc định 2021–2023 gồm **4.981 phim**, **225.770 cặp torrent–phim**, trong đó **565 phim chưa ghi nhận torrent**. Bắt đầu từ IMDb rồi ghép trái để giữ những phim này.

Ví dụ 60 giây: nhấn Ví dụ thuyết trình → xem Hành động và Tài liệu cạnh nhau → đối chiếu số phim, bình chọn, torrent trung vị và tỷ lệ ghi nhận → nhấn tên một phim trong bảng để xem các nguồn đã nối → đặt lại bộ lọc. Chênh lệch thô giữa hai thể loại chưa tách riêng ảnh hưởng của các đặc điểm phim.

## Đơn vị và thời gian

- Mỗi phim: số torrent riêng biệt gắn với phim. Tổng qua phim: số cặp torrent–phim, không phải số torrent riêng biệt toàn hệ thống.
- Cửa sổ quan sát giữ đúng pipeline gốc: `2021-04-01 <= discovered_at_utc < 2024-09-29`. Ngày 29/09/2024 không được tính; khoảng quan sát vẫn có gián đoạn thu thập.
- Giá trị 0 nghĩa là chưa ghi nhận trong dữ liệu đã ghép, lọc và cửa sổ này; không chứng minh phim không được chia sẻ.
- Năm phim IMDb, ngày phát hành TMDb và ngày phát hiện torrent có ý nghĩa khác nhau.
- Bình chọn và nơi xem là ảnh chụp năm 2026 theo tài liệu dự án. Không có thời điểm thu thập chính xác của từng hồ sơ để coi các nguồn đồng bộ trong cùng một ngày.
- Streaming tại Mỹ: thuê bao, miễn phí hoặc có quảng cáo, không gồm thuê/mua. Không dùng nơi xem hiện tại để giải thích chia sẻ trong quá khứ.
- Độ trễ dashboard: WEB đầu tiên được phát hiện **trong cửa sổ quan sát**, trừ ngày Digital tại Mỹ. Chỉ phim đủ ngày mới tham gia. Ngày âm có thể liên quan tới khác mốc quốc gia; bộ lọc và biên cửa sổ ảnh hưởng kết quả.
- Slide phân tích chung dùng mẫu gốc đã ghép. Dashboard giữ cả phim chưa ghi nhận, nên số phim và đường xu hướng không nhất thiết trùng slide. Biểu đồ thể loại trên slide so với dự đoán từ bình chọn; dashboard mô tả trung vị thô.

Không có lượt tải, người xem hoặc thất thu trong dữ liệu này. Metadata chưa xác nhận nội dung và quyền phân phối của từng torrent.

## Tệp và tái tạo

- `slides.html`, `slides.pdf`: bản thuyết trình.
- `dashboard.html`, `assets/`: dashboard và các hình nguồn.
- `kich_ban.md`, `slides.json`: lời dẫn và nội dung từng trang.
- `data.json`: dữ liệu đã rút gọn, cùng dữ liệu được nhúng trong dashboard.
- `build.py`, `dashboard.template.html`, `dashboard.css`, `dashboard.explore.html`, `dashboard.charts.js`: nguồn tạo hai trang từ các parquet gốc. Chạy từ dự án: `python report/phim_15_phut/build.py`. Cần Python và DuckDB đã có trong môi trường dự án. Script chỉ đọc dữ liệu gốc, ghi vào thư mục này.
- `data_validation.json`, `reference_checks.json`, `browser_validation.json`: kiểm tra dữ liệu và giao diện. Reference được đối chiếu độc lập từ các parquet gốc. `verify.cjs` dùng Node và Chrome có sẵn để kiểm tra, chụp ảnh và xuất PDF.

Đã đối chiếu bảy nhóm lọc với SQL độc lập; kiểm tra các biểu đồ, trạng thái rỗng, khoảng năm sai, hồ sơ phim, sắp xếp, phân trang, xuất CSV, hiển thị trên laptop/điện thoại, giải mã ảnh và PDF đủ 15 trang. Không phát sinh yêu cầu mạng bên ngoài hay lỗi JavaScript trong kiểm tra.

Nguồn: IMDb Non-Commercial Datasets; TMDb API (watch providers do JustWatch cung cấp); MagnetDB và pipeline của dự án hiện tại. Tham khảo README ở gốc dự án để biết nguồn vào và điều kiện sử dụng.
