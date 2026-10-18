# Phim qua ba góc nhìn — Slide và dashboard

Mở `slides.html` để thuyết trình; mở `dashboard.html` để khám phá dữ liệu. Dùng Chrome hoặc Edge. Hai trang hoạt động ngoại tuyến, không cần cài đặt hay chạy máy chủ. Dashboard có phần tổng quan nguồn dùng ảnh trong `assets/`; giữ nguyên thư mục này khi sao chép. Bản ZIP chứa đủ các tệp cần dùng.

## Bộ slide

18 slide: 2 slide mở đầu (slide 2 gồm ba nguồn dữ liệu và 5 bước tiền xử lý), slide 3 là biểu đồ phễu làm sạch, slide 4–7 giải thích chi tiết phương pháp từ notebook `00_quy_trinh_xu_ly`, sau đó đến 6 biểu đồ giới thiệu từng nguồn, 1 sơ đồ tích hợp, 1 biểu đồ độ phủ ghép và 3 biểu đồ phân tích chung. Có 11 biểu đồ dữ liệu và 1 sơ đồ. Lời dẫn, điều rút ra và lưu ý nằm trong `kich_ban.md`; slide không hiển thị tab Lời dẫn.

| Phần | Slide |
|---|---|
| Mở đầu, ba nguồn và tiền xử lý | 1–7 |
| IMDb | 8–9 |
| TMDb / JustWatch | 10–11 |
| MagnetDB | 12–13 |
| Tích hợp | 14–15 |
| Phân tích chung | 16–18 |

Dùng ←/→ hoặc Space để chuyển; Z phóng to biểu đồ; F toàn màn hình; M mở mục lục. Nút Dashboard mở dashboard ở một tab riêng. Có bản `slides.pdf` 18 trang để chia sẻ hoặc trình bày khi cần. Lời dẫn và cách chuyển phần nằm trong `kich_ban.md`.

Bốn slide phương pháp nằm ngay sau biểu đồ tổng quan slide 3:

- **4 — Chuẩn hóa:** trích metadata từ SQLite, giữ định danh, bổ sung tên `akas`; ví dụ tên thay thế của The Big Lebowski và chỉ mục 1.875.336 tên.
- **5 — Ghép thực thể:** tra chính xác tên chuẩn hóa + năm lệch tối đa ±1; loại ca mơ hồ; ví dụ Parasite. Phân biệt pipeline chính với phép đối chiếu riêng `guessit` + `rapidfuzz` trên 20.000 tên file (precision 87,9%, recall 63,2% so với nhãn MagnetDB).
- **6 — Làm sạch A–J:** nhóm các quy tắc, ví dụ tập phim bộ, năm lệch và bản tự xưng BluRay trước khi ra rạp; giải thích nhật ký và cờ `implausible`.
- **7 — Đầu ra:** phân biệt cặp torrent–phim, torrent riêng biệt và phim. Toàn phạm vi có 2.078.927 cặp sạch, 2.066.598 torrent và 126.081 phim; trong cửa sổ quan sát còn 923.998 cặp. Phân biệt ba loại thời gian.

`methods_slides.py` đọc các bảng kết quả HTML đã lưu trong notebook 00, không chạy lại notebook hoặc tải dữ liệu thô. `methods_reference.json` lưu số liệu, ví dụ, chỉ số ô nguồn và SHA-256 notebook để đối chiếu. Phần chữ chi tiết là HTML, nên tìm kiếm và sao chép được trong bộ slide; không dùng ảnh chụp code làm nội dung chính.

Các biểu đồ slide lấy từ dự án ba nguồn gốc. Các kết luận được giới hạn ở mối liên hệ quan sát. Không dùng biểu đồ “tăng 22 lần” vì bộ lọc trước Digital ảnh hưởng phân bố đó.

## Dashboard

Ba mục chính: **Phân tích**, **Nguồn dữ liệu**, **Phương pháp**. Trong Phân tích, ba góc nhìn đi theo thứ tự:

1. **Đánh giá phim** (mở đầu, `#explore`): phân bố điểm IMDb, boxplot điểm theo thể loại, biểu đồ điểm × bình chọn và 10 phim điểm cao nhất có ngưỡng bình chọn riêng. Bốn chỉ số là số phim, điểm trung vị, bình chọn trung vị và tỷ lệ phim đạt từ 7 điểm.
2. **Phát hành & nơi xem** (`#explore-releases`): chọn thị trường và hình thức (có lựa chọn “Tất cả” = mốc sớm nhất của mỗi phim trên mọi thị trường/hình thức; mặc định vẫn là Mỹ · Chiếu rạp) để xem lịch theo năm × tháng, cửa sổ rạp–Digital, độ phủ các thị trường và nơi xem tại Mỹ. Bản đồ nhiệt gộp theo thập niên khi phạm vi ngày dài. Có các hình thức streaming (thuê bao / miễn phí / quảng cáo), thuê và mua phim. Cuối phần này có treemap nước sản xuất, biểu đồ cực mùa ra rạp của bom tấn và biểu đồ ngân sách–doanh thu.
3. **Torrent & đối chiếu** (`#explore-torrents`): cột trung vị torrent theo nhóm bình chọn, thể loại (chuyển giữa số phim và torrent trung vị), so sánh hai thể loại, độ trễ WEB–Digital Mỹ, nơi xem và biểu đồ bình chọn × torrent.

Năm IMDb, thể loại, bình chọn tối thiểu và tên/mã phim là bộ lọc chung, được giữ khi đổi góc nhìn. Hai nút chọn nhanh dùng 2021–2023 hoặc 1980–2024. Ô tìm kiếm nhận tên tiếng Anh, tên gốc, tên tiếng Việt (IMDb `title.akas`, vùng VN) hoặc mã IMDb, không phân biệt dấu; khi có từ khóa, tìm trên mọi năm và bỏ qua bộ lọc năm. Bộ lọc tình trạng torrent và streaming chỉ áp dụng trong phần Torrent; các giá trị được giữ để dùng khi quay lại. Nguồn dữ liệu và Phương pháp giữ phạm vi gốc, không chịu bộ lọc.

Bảng phim chung có sắp xếp, phân trang, hồ sơ và xuất CSV. Ở phần đánh giá, ẩn các cột torrent và nơi xem; ở phần phát hành, ẩn cột torrent. Hồ sơ mở từ bảng, bảng xếp hạng hoặc chấm trên biểu đồ điểm; trong phần phát hành có thêm lịch tại thị trường đang chọn. CSV chứa các trường gốc tại Mỹ và cột ngày phát hành của thị trường đang chọn.

Ba biểu đồ sản xuất và kinh doanh có lựa chọn **Nhóm phim đang lọc** (mặc định) hoặc **Mẫu gốc như notebook**. Chế độ mẫu gốc không chịu bộ lọc bên trái; có thông báo ngay trên ba hình. Treemap dùng **85.051 phim**, trong đó Mỹ **37,8%**, Ấn Độ **9,9%**. Biểu đồ tài chính dùng **9.324 phim**, có **3.091 phim (33,2%)** đạt doanh thu/ngân sách từ 2,5 lần. Biểu đồ cực dùng **7.909 phim** trong mẫu tài chính có ngày ra rạp Mỹ, gồm **549 bom tấn** doanh thu từ 300 triệu USD. Tỷ lệ theo tháng được tính riêng trong từng nhóm, đúng mẫu notebook. Trong nhóm mặc định 2021–2023 của dashboard, mẫu tài chính còn **618 phim**, nên số liệu khác chế độ mẫu gốc.

Các hình mới vẽ trực tiếp bằng SVG/canvas, có tooltip và đáp ứng kích thước màn hình. Nhấn chấm tài chính mở hồ sơ có ngân sách và doanh thu; phim chỉ thuộc mẫu gốc vẫn có hồ sơ kinh doanh riêng. CSV của nhóm đang lọc bổ sung nước sản xuất chính, năm TMDb, ngân sách và doanh thu.

Dashboard gồm **47.089 phim** không gắn cờ `is_adult`, có năm 1920–2024 và từ 1.000 lượt bình chọn. Nhóm mặc định 2021–2023 gồm **4.981 phim**, **225.770 cặp torrent–phim**, trong đó **565 phim chưa ghi nhận torrent**. Bắt đầu từ IMDb rồi ghép trái để giữ những phim này.

Nhóm mặc định có điểm trung vị **6,2**, bình chọn trung vị **2.937** và **1.185 phim đạt từ 7 điểm**. Tại Mỹ, **1.742 phim** có mốc ra rạp, **1.284 phim** đủ cả ngày rạp và Digital; **1.217 phim** có khoảng cách 0–365 ngày, trung vị **11 ngày**. Phép tính gộp loại rạp limited và theatrical, nên không dùng để thay thế số liệu của notebook gốc chỉ dùng theatrical.

Ví dụ 60 giây: nhấn Ví dụ thuyết trình → xem Hành động và Tài liệu cạnh nhau → đối chiếu số phim, bình chọn, torrent trung vị và tỷ lệ ghi nhận → nhấn tên một phim trong bảng để xem các nguồn đã nối → đặt lại bộ lọc. Chênh lệch thô giữa hai thể loại chưa tách riêng ảnh hưởng của các đặc điểm phim.

## Đơn vị và thời gian

- Mỗi phim: số torrent riêng biệt gắn với phim. Tổng qua phim: số cặp torrent–phim, không phải số torrent riêng biệt toàn hệ thống.
- Cửa sổ quan sát giữ đúng pipeline gốc: `2021-04-01 <= discovered_at_utc < 2024-09-29`. Ngày 29/09/2024 không được tính; khoảng quan sát vẫn có gián đoạn thu thập.
- Giá trị 0 nghĩa là chưa ghi nhận trong dữ liệu đã ghép, lọc và cửa sổ này; không chứng minh phim không được chia sẻ.
- Năm phim IMDb, ngày phát hành TMDb và ngày phát hiện torrent có ý nghĩa khác nhau.
- Phát hành: ngày sớm nhất theo phim–quốc gia–hình thức; gộp hai loại rạp limited và theatrical. Các biểu đồ lịch đầu phần Phát hành tính mốc đến **18/10/2026**, không tính lịch tương lai. Hai mốc rạp–Digital thuộc cùng quốc gia; chỉ giữ khoảng cách 0–365 ngày và ghi số giá trị âm hoặc trên 365 ngày bị loại. Đổi hình thức phát hành không đổi định nghĩa của biểu đồ cửa sổ rạp–Digital.
- Treemap: năm phát hành TMDb 2000–2024, nước đầu tiên trong `origin_country`; thiếu nước bị loại và ghi số lượng. Giữ top 14 nước, gộp phần còn lại. Mẫu tài chính: năm TMDb 1980–2024, ngân sách ≥ 1 triệu USD, doanh thu ≥ 10.000 USD; USD danh nghĩa. Đường 2,5× chỉ là ngưỡng tham khảo, không xác định lãi/lỗ thực tế. Biểu đồ cực mặc định dùng ngày rạp Mỹ trong mẫu tài chính, đúng định nghĩa gốc notebook. Khi đổi ô Thị trường phát hành, biểu đồ dùng ngày chiếu rạp sớm nhất tại thị trường đó (hoặc sớm nhất toàn cầu với “Tất cả”), không phụ thuộc ô Hình thức; hiện cảnh báo khi dưới 30% phim đủ tài chính có ngày rạp (ví dụ Việt Nam: 1.216 phim). Phim của mẫu gốc nằm ngoài danh mục dashboard không có lịch theo nước nên chỉ được tính khi chọn Mỹ.
- Bảng nơi xem chỉ xuất dữ liệu Mỹ để giữ bản HTML gọn. Chọn thị trường khác chỉ đổi lịch phát hành, không đổi phạm vi biểu đồ nền tảng. Dữ liệu gốc hiện không có bản ghi nơi xem `VN`; không coi là bằng chứng không có nơi xem hợp pháp tại Việt Nam.
- Bình chọn và nơi xem là ảnh chụp năm 2026 theo tài liệu dự án. Không có thời điểm thu thập chính xác của từng hồ sơ để coi các nguồn đồng bộ trong cùng một ngày.
- Streaming tại Mỹ: thuê bao, miễn phí hoặc có quảng cáo, không gồm thuê/mua. Không dùng nơi xem hiện tại để giải thích chia sẻ trong quá khứ.
- Độ trễ dashboard: WEB đầu tiên được phát hiện **trong cửa sổ quan sát**, trừ ngày Digital tại Mỹ. Chỉ phim đủ ngày mới tham gia. Ngày âm có thể liên quan tới khác mốc quốc gia; bộ lọc và biên cửa sổ ảnh hưởng kết quả.
- Slide phân tích chung dùng mẫu gốc đã ghép. Dashboard giữ cả phim chưa ghi nhận, nên số phim và đường xu hướng không nhất thiết trùng slide. Biểu đồ thể loại trên slide so với dự đoán từ bình chọn; dashboard mô tả trung vị thô.

Không có lượt tải, người xem hoặc thất thu trong dữ liệu này. Metadata chưa xác nhận nội dung và quyền phân phối của từng torrent.

## Tệp và tái tạo

- `slides.html`, `slides.pdf`: bản thuyết trình.
- `dashboard.html`, `assets/`: dashboard và các hình nguồn.
- `kich_ban.md`, `slides.json`: lời dẫn và nội dung từng trang.
- `data.json`: cùng dữ liệu được nhúng trong dashboard, khoảng 24 MB. Gồm danh mục phim, ngày phát hành sớm nhất được mã hóa theo ngày từ 1970 và danh sách nơi xem tại Mỹ bằng chỉ mục. Phần `business` chỉ bổ sung mẫu tài chính 9.324 phim và số đếm nước sản xuất của mẫu gốc, không nhúng toàn bộ kho TMDb. Không cần tải dữ liệu qua mạng khi mở HTML.
- `build.py`, `dashboard.template.html`, `dashboard.css`, `dashboard.explore.html`, `dashboard.charts.js`, `dashboard.phases.js`, `dashboard.business.js`: nguồn tạo hai trang từ các parquet gốc. Chạy từ dự án: `python report/phim_15_phut/build.py`. Chỉ dựng lại dashboard: `python report/phim_15_phut/build.py --dashboard-only`. Chỉ dựng slide: `python report/phim_15_phut/build.py --slides-only` (dùng ảnh trong `plots/`, notebook 00 và `methods_slides.py`, `slides.methods.css`). Cần Python và DuckDB đã có trong môi trường dự án. Script chỉ đọc dữ liệu gốc, ghi vào thư mục này.
- `data_validation.json`, `reference_checks.json`, `phase_reference_checks.json`, `business_reference_checks.json`, `browser_validation.json`: kiểm tra dữ liệu và giao diện. `python report/phim_15_phut/verify_phases.py` tính lại tham chiếu SQL độc lập cho đánh giá, lịch phát hành và ba biểu đồ kinh doanh. `node report/phim_15_phut/verify.cjs --dashboard-only` kiểm tra dashboard, lưu kết quả và ảnh; bỏ cờ để kiểm tra thêm slide và xuất PDF.

Đã đối chiếu bảy nhóm lọc với SQL độc lập; kiểm tra các biểu đồ, trạng thái rỗng, khoảng năm sai, hồ sơ phim, sắp xếp, phân trang, xuất CSV, hiển thị trên laptop/điện thoại, giải mã ảnh và PDF đủ 18 trang. Kiểm tra riêng slide 3 đúng vị trí và ảnh gốc; bốn slide phương pháp đúng thứ tự, có số liệu/nguồn notebook, ví dụ thật, ghi chú và phạm vi chỉ số. Không phát sinh yêu cầu mạng bên ngoài hay lỗi JavaScript trong kiểm tra.

Nguồn: IMDb Non-Commercial Datasets; TMDb API (watch providers do JustWatch cung cấp); MagnetDB và pipeline của dự án hiện tại. Tham khảo README ở gốc dự án để biết nguồn vào và điều kiện sử dụng.
