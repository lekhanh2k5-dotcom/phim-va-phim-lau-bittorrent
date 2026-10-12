# Phim được biết đến, phát hành và chia sẻ như thế nào?

Bản trình chiếu dùng 27 hình của dự án ba nguồn, không chạy lại hoặc sửa pipeline. PNG được nhúng vào index.html để mở ngoại tuyến và chia sẻ một tệp. Các nhận xét trong bản này thu hẹp các kết luận quá mạnh ở chú thích gốc; biểu đồ giữ nguyên.

Mở `index.html` bằng Chrome/Edge. Dùng ←/→ hoặc Space, N mở lời dẫn, Z phóng to hình, F toàn màn hình, M mở mục lục. Có thể in sang PDF bằng nút In/PDF của trình duyệt.

## Trang 01 · Mở đầu · Phim được biết đến, phát hành và chia sẻ như thế nào?

Mở đầu bằng câu hỏi: cùng một phim, dữ liệu đánh giá, dữ liệu phát hành và dữ liệu chia sẻ có kể cùng một câu chuyện không? Bài này dùng ba nguồn của dự án gốc, chọn 27 hình và xếp lại theo câu hỏi.

## Trang 02 · Mở đầu · Ba nguồn, ba phần thông tin về cùng một bộ phim

IMDb giống hồ sơ của phim. TMDb thêm thông tin phim được phát hành và phân phối. MagnetDB ghi nhận các bản chia sẻ. Dữ liệu JustWatch được lấy qua TMDb, nên bài tổ chức thành ba nguồn thu thập chính. Không nguồn nào một mình trả lời đủ câu hỏi của bài.

## Trang 03 · Mở đầu · Nối các thông tin về cùng một phim bằng cách nào?

Hình gốc: `plots/5_combined/01_integration_diagram.png`

**Lời dẫn:** Một bộ phim có tên trong IMDb, mã tham chiếu trong TMDb và nhiều cách viết trong tên torrent. Giới thiệu đường nối để người nghe biết các hình sau thuộc phần nào của cùng câu chuyện.

**Cách đọc:** Theo các mũi tên về mã phim IMDb. Nhánh TMDb có định danh tham chiếu; nhánh MagnetDB cần kiểm tra tên, năm và bí danh. Phần ghép torrent sẽ được giải thích sau.

**Chốt:** IMDb là điểm nối: TMDb có mã tham chiếu, còn tên torrent cần được nhận diện về phim.

**Nối:** Trước khi ghép chi tiết, danh mục phim đang có những đặc điểm gì?

**Giới hạn:** Có mã tham chiếu hoặc tên gần giống chưa chứng minh mọi cặp ghép đều đúng. Không đồng nhất cấp phim, cấp file và cặp torrent–phim.

## Trang 04 · Mở đầu · Theo một trình tự: hiểu phim rồi mới giải thích chia sẻ

Bài có 32 trang, trong đó 27 trang dùng hình từ dự án gốc. Ngân sách, doanh thu, codec và nhóm phát hành được để ngoài mạch chính. Nhấn mạnh: số lượt đánh giá là chỉ báo mức được chú ý; điểm là mức được người dùng đánh giá cao; số torrent là nguồn chia sẻ quan sát được.

## Trang 05 · Phim · Danh mục phim thay đổi như thế nào qua các năm?

Hình gốc: `plots/1_imdb/01_movies_per_year.png`

**Lời dẫn:** Bắt đầu từ phim và năm, hai khái niệm quen thuộc. Ta cần biết các giai đoạn có quy mô khác nhau trước khi so cơ cấu.

**Cách đọc:** Trục ngang là năm IMDb; trục dọc là số bản ghi phim. Đường cao hơn nghĩa là danh mục có nhiều phim của năm đó hơn.

**Chốt:** IMDb ghi nhận nhiều phim hơn ở các giai đoạn gần đây; đây là bức tranh của danh mục đang dùng.

**Nối:** Những phim đó thuộc các thể loại nào, và cơ cấu có thay đổi không?

**Giới hạn:** Độ đầy đủ của IMDb thay đổi theo thời gian. Hình không đủ chứng minh máy quay số hoặc một sự kiện lịch sử gây ra thay đổi; năm IMDb cũng không phải thống kê sản lượng toàn thế giới.

## Trang 06 · Phim · Cơ cấu thể loại có giống nhau ở mọi thập niên?

Hình gốc: `plots/1_imdb/02_genre_share_by_decade.png`

**Lời dẫn:** Hình năm chỉ cho tổng số. Tách thể loại giúp xem thành phần của danh mục và giải quyết thắc mắc về chính kịch/tài liệu.

**Cách đọc:** Mỗi cột là cơ cấu chia trọng số. Phim hai nhãn đóng góp 1/2 cho mỗi nhãn, phim ba nhãn đóng góp 1/3. Drama là chính kịch; Documentary là tài liệu.

**Chốt:** Tỷ trọng các nhãn thay đổi theo thời gian; phải đọc đúng cách chia trọng số trước khi so chính kịch và tài liệu.

**Nối:** Sau cơ cấu thể loại, phim trong danh mục thường được chấm bao nhiêu điểm?

**Giới hạn:** Tài liệu có tỷ trọng cao hơn trong hình không đồng nghĩa có nhiều phim hơn chính kịch. Muốn trả lời số phim phải đếm trực tiếp từng nhãn. Không suy ra nguyên nhân xã hội chỉ từ cơ cấu này.

## Trang 07 · Phim · Các phim trong mẫu thường nhận mức điểm nào?

Hình gốc: `plots/1_imdb/03_rating_distribution.png`

**Lời dẫn:** Sau khi biết loại phim, chuyển sang cách người dùng đánh giá. Đây là mốc chung để so các thể loại ở hình tiếp.

**Cách đọc:** Trục ngang là điểm IMDb, thang 10. Phần cao của phân bố cho biết mức điểm có nhiều phim. Trung vị là điểm đứng giữa khi xếp các phim theo điểm.

**Chốt:** Phần lớn phim trong mẫu có điểm ở khoảng giữa thang đánh giá; điểm cực cao hoặc cực thấp ít hơn.

**Nối:** Sự khác nhau về điểm có tập trung ở một số thể loại không?

**Giới hạn:** Mẫu có ngưỡng ít nhất 1.000 lượt đánh giá, nên không đại diện cho mọi phim trong IMDb. Điểm của người dùng không phải chất lượng khách quan.

## Trang 08 · Phim · Các thể loại có được đánh giá giống nhau không?

Hình gốc: `plots/1_imdb/04_rating_by_genre.png`

**Lời dẫn:** Hình trước cho mặt bằng điểm chung. Hình này tách theo thể loại đã giới thiệu để xem mặt bằng đó có che các khác biệt không.

**Cách đọc:** Vạch trong hộp là trung vị, hộp chứa nửa số phim ở giữa. So vị trí hộp và phần chồng lấn giữa các thể loại, không chỉ đọc một con số.

**Chốt:** Điểm điển hình khác giữa các thể loại; tài liệu và tiểu sử có mức điểm cao hơn một số nhóm khác trong mẫu.

**Nối:** Có điểm khác nhau, vậy sự chú ý của người dùng có phân bố đều giữa các phim?

**Giới hạn:** Phim nhiều nhãn có mặt ở nhiều nhóm; thành phần khán giả và số lượt đánh giá khác nhau. Hình chưa chứng minh thể loại gây ra điểm cao hoặc thấp.

## Trang 09 · Phim · Có nhiều phim, nhưng sự chú ý có phân bố đều không?

Hình gốc: `plots/1_imdb/06_votes_lorenz.png`

**Lời dẫn:** Các hình điểm không cho biết có bao nhiêu người tham gia. Thêm số lượt đánh giá để phân biệt mức được chú ý với mức điểm.

**Cách đọc:** Đường cong cộng dồn lượt đánh giá khi xếp phim từ ít đến nhiều lượt. Đường càng xa đường chia đều thì mức tập trung càng lớn. Gini chỉ là chỉ số tóm tắt.

**Chốt:** Lượt đánh giá tập trung vào một nhóm nhỏ phim. Số phim nhiều không có nghĩa mỗi phim được chú ý như nhau.

**Nối:** Phim được nhiều người chú ý có đồng thời được chấm điểm cao hơn không?

**Giới hạn:** Lượt đánh giá trên IMDb không phải số người xem toàn thế giới; các phim ở nhiều giai đoạn có thời gian tích lũy đánh giá khác nhau.

## Trang 10 · Phim · Được chú ý nhiều có đồng nghĩa được chấm điểm cao?

Hình gốc: `plots/1_imdb/08_votes_vs_rating.png`

**Lời dẫn:** Đặt hai biến cạnh nhau sau khi đã giới thiệu riêng. Đây là nền tảng để đọc các hình tích hợp theo độ phổ biến phía sau.

**Cách đọc:** Sang phải là nhiều lượt đánh giá hơn; lên trên là điểm cao hơn. Màu đậm là vùng có nhiều phim, đường tóm tắt cho xu hướng nhóm.

**Chốt:** Trong dữ liệu có liên hệ giữa lượt đánh giá và điểm; hai biến vẫn đo hai khía cạnh khác nhau.

**Nối:** Biết và đánh giá một phim rồi, người xem có dễ tìm được nơi xem hợp pháp không?

**Giới hạn:** Không suy ra lượt đánh giá làm điểm tăng. Các nhóm khác nhau về năm, thể loại, thị trường và người tham gia đánh giá.

## Trang 11 · Xem hợp pháp · Ở đâu có thể tiếp cận nhiều phim hợp pháp hơn?

Hình gốc: `plots/3_tmdb_streaming/01_world_catalog_map.png`

**Lời dẫn:** Chuyển từ đặc điểm phim sang khả năng tìm nơi xem. Bản đồ cho bối cảnh phân phối trước khi nói tới từng nền tảng.

**Cách đọc:** Màu đậm hơn nghĩa là nhiều tựa phim được ghi nhận qua thuê bao hoặc miễn phí. Màu xám là thiếu dữ liệu, không phải không có phim. Thanh màu dùng thang nén.

**Chốt:** Số phim có trong các dịch vụ thuê bao/miễn phí khác nhau giữa các quốc gia trong ảnh chụp dữ liệu.

**Nối:** Khác biệt này liên quan thế nào đến độ phủ và quy mô kho phim của các nền tảng?

**Giới hạn:** Đây là dữ liệu dịch vụ xem năm 2026, không phải lịch sử nơi xem trong giai đoạn torrent 2021–2024. Khác biệt còn phụ thuộc độ đầy đủ của nguồn.

## Trang 12 · Xem hợp pháp · Phủ nhiều quốc gia có đồng nghĩa kho phim lớn ở mỗi nơi?

Hình gốc: `plots/3_tmdb_streaming/02_brand_reach_vs_depth.png`

**Lời dẫn:** Bản đồ chưa cho biết nền tảng nào tạo ra độ phủ. Hình này phân biệt nhiều nơi phục vụ với nhiều phim tại mỗi nơi.

**Cách đọc:** Một trục đo số quốc gia, trục còn lại đo quy mô kho phim theo định nghĩa ghi trong hình. Vị trí xa ở một trục chưa chắc xa ở trục còn lại.

**Chốt:** Độ phủ quốc gia và độ sâu kho phim là hai cách nhìn khác nhau về một nền tảng.

**Nối:** Những phim có mặt đó được xem bằng thuê bao, miễn phí, thuê hay mua?

**Giới hạn:** Quy mô kho phim không đo số thuê bao, thị phần hoặc lịch sử mở rộng. Các chỉ số lấy từ ảnh chụp dịch vụ năm 2026.

## Trang 13 · Xem hợp pháp · “Có nơi xem” cụ thể là xem bằng cách nào?

Hình gốc: `plots/3_tmdb_streaming/03_access_mode_by_country.png`

**Lời dẫn:** Hình nền tảng chỉ nói đến có mặt. Hình thức tiếp cận giúp đọc cụ thể điều kiện xem trước khi xét kho phim trùng nhau.

**Cách đọc:** So các phần màu theo chú giải để phân biệt thuê bao/miễn phí với thuê hoặc mua lẻ. Đọc đơn vị trên trục vì một phim có thể có nhiều nơi và cách xem.

**Chốt:** Tỷ trọng thuê bao, miễn phí, thuê và mua khác nhau theo thị trường; có mặt chưa đồng nghĩa được xem trong gói thuê bao.

**Nối:** Nhiều dịch vụ như vậy có cung cấp cùng phim, hay kho phim bị phân mảnh?

**Giới hạn:** Không có giá thuê bao, chi phí thực trả hoặc hành vi người xem trong phép so này. Không tự suy ra thuê/mua nhiều dẫn tới chia sẻ torrent nhiều.

## Trang 14 · Xem hợp pháp · Một dịch vụ có đủ phim, hay cần tìm ở nhiều dịch vụ?

Hình gốc: `plots/3_tmdb_streaming/04_us_catalog_upset.png`

**Lời dẫn:** Nhiều hình thức xem chưa cho biết mức trùng tựa phim. Hình giao tập giúp kiểm tra người xem có gặp cùng phim ở nhiều nền tảng không.

**Cách đọc:** Các chấm nối phía dưới chỉ tổ hợp nền tảng; cột phía trên đếm phim thuộc đúng tổ hợp đó. Một chấm nghĩa là chỉ có ở một nền tảng trong danh sách đang xét.

**Chốt:** Kho phim ở các dịch vụ trong mẫu Mỹ ít trùng nhau; độ phân mảnh là một đặc điểm cần biết khi nói về khả năng tiếp cận.

**Nối:** Sự phân mảnh đó có khiến phim ít nổi tiếng khó tìm nơi xem hơn không?

**Giới hạn:** Chỉ xét các dịch vụ và hình thức được chọn tại Mỹ. Không suy rộng thành mọi cách xem hợp pháp, mọi quốc gia hoặc toàn bộ lịch sử phân phối.

## Trang 15 · Xem hợp pháp · Phim được chú ý nhiều hoặc chấm cao có dễ tìm nơi xem hơn?

Hình gốc: `plots/5_combined/06_availability_heatmap.png`

**Lời dẫn:** Nối lại hai biến đã giới thiệu ở IMDb với thông tin nơi xem của TMDb/JustWatch. Đây là câu hỏi không một nguồn đơn lẻ trả lời đủ.

**Cách đọc:** Mỗi ô kết hợp nhóm lượt đánh giá và nhóm điểm. So các hàng trong cùng cột hoặc các cột trong cùng hàng; số/màu thể hiện độ phủ theo định nghĩa trong hình.

**Chốt:** Trong mẫu, nhóm nhiều lượt đánh giá có độ phủ xem hợp pháp rộng hơn; điểm cần được đọc cùng mức độ phổ biến.

**Nối:** Ngoài việc xem ở đâu, người xem còn phải chờ bao lâu sau khi phim ra rạp?

**Giới hạn:** Lượt đánh giá và dịch vụ xem là ảnh chụp hiện tại; chưa chứng minh mức phổ biến tạo ra độ phủ, hoặc độ phủ làm phim phổ biến hơn.

## Trang 16 · Xem hợp pháp · Từ ra rạp đến phát hành trực tuyến thường cách nhau bao lâu?

Hình gốc: `plots/2_tmdb/04_theatrical_window.png`

**Lời dẫn:** Nơi xem là một ảnh chụp, còn ngày phát hành cung cấp lịch sử. Chuyển sang mốc thời gian để chuẩn bị cho phân tích quanh ngày Digital.

**Cách đọc:** Digital là ngày phát hành trực tuyến ghi trong TMDb, có thể gồm thuê/mua, không chỉ thuê bao. So số ngày giữa ra rạp và Digital theo nhóm năm ở Mỹ.

**Chốt:** Khoảng cách ra rạp–Digital trong mẫu Mỹ thay đổi theo giai đoạn. Đây là mốc thời gian sẽ dùng lại khi phân tích torrent.

**Nối:** Nếu muốn đối chiếu với chia sẻ trên mạng, chúng ta cần đo những bản ghi nào?

**Giới hạn:** Ngày phát hành có thể thiếu hoặc khác nhau giữa quốc gia. Hình cho thay đổi trong mẫu, chưa đủ kết luận một biến cố làm mô hình phát hành thay đổi vĩnh viễn.

## Trang 17 · Tích hợp · Trước khi đếm: torrent là gì?

Ví dụ minh họa, không phải kết quả đo: A.2022.720p và A.2022.1080p có thể cùng thuộc phim A năm 2022. Ta ghi nhận hai torrent, không phải hai phim hoặc hai người tải. Một torrent bộ sưu tập có thể chứa nhiều phim. Thời điểm thu thập thấy torrent cũng khác thời điểm tạo torrent.

## Trang 18 · Tích hợp · Mạng chia sẻ này có phải chỉ chứa phim?

Hình gốc: `plots/4_magnetdb/01_content_sunburst.png`

**Lời dẫn:** Người nghe vừa biết torrent là bản ghi chia sẻ. Hình cơ cấu nội dung cho thấy vì sao cần lọc thay vì đếm toàn bộ nguồn.

**Cách đọc:** Đọc các vòng theo nhóm nội dung và chú ý hình dùng dung lượng hay số tệp. Nhóm video bao gồm nhiều nội dung ngoài phim điện ảnh.

**Chốt:** MagnetDB có nhiều loại nội dung. Phải xác định nhóm phim trước khi phân tích, không coi mọi video là phim điện ảnh.

**Nối:** Bên cạnh loại nội dung, hệ thống thu thập có hoạt động đều theo thời gian không?

**Giới hạn:** Hình tổng quan dùng dữ liệu/mẫu file theo phạm vi của notebook gốc. Tỷ trọng dung lượng không phải tỷ trọng người dùng hay số phim.

## Trang 19 · Tích hợp · Số bản ghi thay đổi vì chia sẻ, hay vì hệ thống thu thập?

Hình gốc: `plots/4_magnetdb/03_crawler_coverage.png`

**Lời dẫn:** Sau lọc nội dung, kiểm tra chất lượng theo thời gian. Một khoảng không có bản ghi có thể là hệ thống ngừng, không phải cộng đồng ngừng chia sẻ.

**Cách đọc:** Đường thể hiện số torrent được phát hiện theo tháng; vùng đánh dấu giải thích các giai đoạn thu thập. Phần phân tích chính dùng từ 04/2021 đến 09/2024.

**Chốt:** Thu thập không đều. Cần giới hạn thời gian và thận trọng với các khoảng gián đoạn trước khi diễn giải xu hướng.

**Nối:** Trong phạm vi đã chọn, làm sao loại các cặp torrent–phim ghép không phù hợp?

**Giới hạn:** Cửa sổ được chọn vẫn có gián đoạn, đặc biệt 06/2024. Đây là thời điểm phát hiện, không phải thời điểm đăng. Bản trình bày giữ phạm vi xử lý của bản gốc.

## Trang 20 · Tích hợp · Vì sao phải làm sạch trước khi đếm torrent của phim?

Hình gốc: `plots/6_integration/01_cleaning_funnel.png`

**Lời dẫn:** Sơ đồ đầu bài chỉ cho đường nối. Phễu này kiểm tra các bản ghi đi qua đường nối đó và cho thấy tích hợp cần xử lý chất lượng.

**Cách đọc:** Mỗi bước cho số bản ghi còn lại sau lọc. Phải đọc đúng đơn vị của từng nhánh: file, torrent và cặp torrent–phim không hoàn toàn giống nhau.

**Chốt:** Các bước lọc loại bản ghi không phù hợp về loại nội dung, tên, năm và các điều kiện khác; còn lại là tập để phân tích.

**Nối:** Mã ghép có sẵn đã đủ chưa, hay cần thêm một cách nhận diện?

**Giới hạn:** Tên/năm phù hợp là bằng chứng metadata, không kiểm tra nội dung tệp. Một số bộ lọc dùng ngày Digital và vì vậy ảnh hưởng phân tích thời điểm ở phần sau.

## Trang 21 · Tích hợp · Tự ghép tên bổ sung được bao nhiêu dữ liệu?

Hình gốc: `plots/6_integration/02_coverage_by_source.png`

**Lời dẫn:** Phễu cho thấy số bản ghi bị loại nhưng chưa cho biết dữ liệu nào được bổ sung. So hai nhánh để thấy giá trị của nhận diện thực thể.

**Cách đọc:** Các phần màu biểu thị cặp chỉ tìm thấy ở từng phương pháp và phần giao nhau. So đơn vị cặp ghép, không nhầm với số người chia sẻ.

**Chốt:** Tự ghép tên tìm thêm nhiều bản ghi ngoài nhánh mã có sẵn. Lựa chọn cách ghép ảnh hưởng trực tiếp độ phủ của phân tích.

**Nối:** Việc bổ sung đó có thay đổi kết quả của các phim cụ thể không?

**Giới hạn:** Phương pháp nhiều bản ghi hơn chưa chắc chính xác hơn. Tự ghép cần tên/năm rõ và có thể bỏ phim trùng tên.

## Trang 22 · Tích hợp · Một phim có thể “biến mất” chỉ vì cách ghép dữ liệu không?

Hình gốc: `plots/6_integration/03_top_movies_dumbbell.png`

**Lời dẫn:** Hình trước là tổng số; hình này đưa tên phim cụ thể để người nghe thấy tác động thực tế của phương pháp tới kết quả.

**Cách đọc:** Hai đầu đoạn nối là số bản ghi của cùng phim theo hai cách ghép. Đoạn dài nghĩa là cách nhận diện làm thay đổi số lượng mạnh.

**Chốt:** Một số phim có rất ít hoặc không có torrent theo mã sẵn, nhưng có nhiều bản ghi khi tự ghép. Thiếu ghép dễ bị nhầm thành ít chia sẻ.

**Nối:** Độ phủ tăng rồi, chúng ta kiểm tra mức đáng tin của ghép như thế nào?

**Giới hạn:** Đây là các ví dụ được chọn, không phải mẫu ngẫu nhiên toàn bộ phim. Số 0 trong nhánh mã sẵn chỉ là không tìm thấy theo nhánh đó.

## Trang 23 · Tích hợp · Hai cách ghép thống nhất với nhau đến mức nào?

Hình gốc: `plots/6_integration/04_match_agreement.png`

**Lời dẫn:** Đã thấy tăng độ phủ, giờ cần đánh giá chất lượng. So phương pháp trên các cặp có thể đối chiếu thay vì chỉ báo tổng số lớn.

**Cách đọc:** Đọc riêng các phép đối chiếu trong hình. Tỷ lệ thống nhất với mã tham chiếu nói về cùng kết quả ghép, không chứng minh nội dung tệp đúng.

**Chốt:** Mức đồng thuận sau làm sạch cao hơn trước làm sạch. Điều này hỗ trợ kiểm tra phương pháp, chưa phải độ chính xác tuyệt đối.

**Nối:** Sau tích hợp, phim nào có nhiều bản chia sẻ được quan sát nhất?

**Giới hạn:** Hai cách có thể cùng sai hoặc cùng bỏ sót. Không gọi mức đồng thuận 99,4% là độ chính xác 99,4%, cũng không suy ra 0,6% là toàn bộ tỷ lệ sai.

## Trang 24 · Khác biệt · Những phim nào có nhiều bản chia sẻ được quan sát nhất?

Hình gốc: `plots/7_piracy_movies/01_top20_pirated.png`

**Lời dẫn:** Bắt đầu kết quả tích hợp bằng tên phim cụ thể. Sau đó cần đi từ ví dụ nổi bật sang quan hệ trên nhiều phim.

**Cách đọc:** Thanh dài hơn nghĩa là có nhiều torrent khác nhau được ghép vào phim trong cửa sổ quan sát. Đây là top trong dữ liệu, không phải top lượt tải.

**Chốt:** Các tên đứng đầu chủ yếu là phim đại chúng gần đây. Bảng xếp hạng mở ra câu hỏi về vai trò của độ phổ biến.

**Nối:** Có nhiều torrent vì phim được nhiều người chú ý hơn không?

**Giới hạn:** Ghép sai, thiếu ghép và bộ sưu tập có thể ảnh hưởng thứ hạng. Chỉ xét các phim có bản ghi quan sát; không đại diện cho tất cả phim ngoài mẫu.

## Trang 25 · Khác biệt · Phim nhiều người đánh giá có thường nhiều torrent hơn?

Hình gốc: `plots/7_piracy_movies/02_popularity_vs_piracy.png`

**Lời dẫn:** Top phim gợi ý độ phổ biến. Kiểm tra quan hệ trên nhiều phim và dùng mốc chung để đọc khác biệt thể loại phía sau.

**Cách đọc:** Sang phải là nhiều lượt đánh giá, lên trên là nhiều torrent. Trục nén để thấy cả nhỏ và lớn. Điểm xa đường mô hình có thể là ngoại lệ hoặc sai số ghép.

**Chốt:** Nhiều lượt đánh giá đi cùng nhiều torrent trong mẫu đã ghép. Quan hệ chung vẫn để lại các phim cao hoặc thấp hơn mốc dự đoán.

**Nối:** Sau khi xét lượt đánh giá, khác biệt giữa thể loại còn lại như thế nào?

**Giới hạn:** Bản gốc chủ yếu phân tích phim đã quan sát được torrent. Vote là ảnh chụp hiện tại; không đại diện mức phổ biến tại thời điểm torrent xuất hiện và không chứng minh nhân quả.

## Trang 26 · Khác biệt · Khác biệt thể loại có chỉ đến từ mức độ phổ biến?

Hình gốc: `plots/7_piracy_movies/03_genre_piracy_ratio.png`

**Lời dẫn:** Các thể loại vốn khác nhau về điểm và sự chú ý ở phần đầu. So phần còn lại sau mốc dự đoán để tránh chỉ đọc số tổng.

**Cách đọc:** Mốc ×1 là phù hợp mô hình độ phổ biến. Trên ×1 là nhiều hơn mốc, dưới ×1 là ít hơn. Đây là phần chênh lệch mô tả, không phải tác động riêng do thể loại.

**Chốt:** Trong phép so với mốc theo lượt đánh giá, một số thể loại có nhiều torrent hơn mốc và một số ít hơn.

**Nối:** Nguồn chia sẻ này chỉ thuộc phim mới, hay còn nhiều phim cũ?

**Giới hạn:** Phim nhiều nhãn chồng lấn giữa nhóm. Mô hình bản gốc chưa giữ cố định mọi khác biệt về năm, thị trường và cơ hội quan sát; phần còn lại có cả sai số ghép.

## Trang 27 · Khác biệt · Bản chia sẻ mới được phát hiện có phải luôn là phim mới?

Hình gốc: `plots/7_piracy_movies/05_film_age_of_uploads.png`

**Lời dẫn:** Độ phổ biến và thể loại chưa nói đến tuổi phim. Tách nhóm năm để phân biệt tuổi nội dung với thời điểm quan sát bản ghi.

**Cách đọc:** Các phần màu là nhóm năm của phim; so tỷ trọng trong từng giai đoạn. Phim trước 2010 vẫn đóng góp đáng kể theo hình.

**Chốt:** Nguồn chia sẻ quan sát được có cả phim cũ. Mới được phát hiện và mới được phát hành là hai điều khác nhau.

**Nối:** Với phim có lịch phát hành, torrent thay đổi thế nào quanh ngày ra bản trực tuyến?

**Giới hạn:** Tỷ trọng không đo xác suất một phim của thập niên đó được chia sẻ. Nhiều torrent có thể là các phiên bản/gói khác nhau; chưa xác nhận chúng là remaster hoặc bản lồng tiếng mới.

## Trang 28 · Thời điểm · Các bản chia sẻ thay đổi thế nào quanh ngày phát hành Digital?

Hình gốc: `plots/7_piracy_movies/06_event_study_digital.png`

**Lời dẫn:** Đưa ngày phát hành TMDb vào để mở rộng từ phim nào sang khi nào. Đây là phần ba nguồn cùng tham gia câu hỏi thời gian.

**Cách đọc:** Tuần 0 là ngày Digital sớm nhất ghi trong nguồn. So bản WEB với các bản khác ở hai phía của mốc. Trục dọc là số bản ghi trung bình trên phim trong mẫu.

**Chốt:** Hình gốc cho thấy tăng mạnh quanh mốc Digital; cách lọc trước Digital ảnh hưởng trực tiếp hình dạng này.

**Nối:** Khi lấy ngày Digital tại Mỹ làm mốc, bản WEB đầu tiên được phát hiện sau bao lâu?

**Giới hạn:** Bộ lọc bản gốc đã loại WEB bị cho là xuất hiện quá sớm. Vì vậy sự thiếu WEB trước Digital một phần do chính quy tắc lọc; hệ số tăng trong hình không phải bằng chứng độc lập về tác động của phát hành.

## Trang 29 · Thời điểm · Bản WEB đầu tiên được phát hiện cách ngày Digital ở Mỹ bao lâu?

Hình gốc: `plots/7_piracy_movies/07_web_lag.png`

**Lời dẫn:** Hình tuần tổng hợp chưa cho biết độ trễ từng phim. Chuyển sang số ngày và làm rõ mốc Mỹ khác mốc Digital sớm nhất của hình trước.

**Cách đọc:** Ngày 0 là Digital ở Mỹ; số âm là phát hiện trước mốc Mỹ, số dương là sau. Hai cột ngoài cùng gom các độ trễ vượt giới hạn hiển thị.

**Chốt:** Nhiều phim có bản WEB được phát hiện gần mốc Digital tại Mỹ. Giá trị âm cần xét lịch phát hành ở quốc gia khác.

**Nối:** Xuất hiện sớm hơn có đồng nghĩa tổng số bản chia sẻ năm đầu lớn hơn không?

**Giới hạn:** Đây là ngày hệ thống phát hiện, không phải thời điểm tạo torrent. Chênh lệch quốc gia, thiếu ngày và bộ lọc trước Digital đều ảnh hưởng phân bố.

## Trang 30 · Thời điểm · Đổi thời điểm phát hành có đi cùng đổi tổng lượng chia sẻ?

Hình gốc: `plots/7_piracy_movies/08_release_strategy_effect.png`

**Lời dẫn:** Sau độ trễ, kiểm tra tổng số trong cửa sổ năm đầu để tránh nhầm xuất hiện sớm với xuất hiện nhiều. Hình giữ các điều kiện của mô hình gốc.

**Cách đọc:** Nhóm chiếu rạp trước 4–45 ngày là mốc ×1. Chấm là tỷ lệ theo mô hình; vạch ngang là khoảng ước lượng. Khoảng đi qua ×1 chưa tách rõ khỏi mốc.

**Chốt:** Mô hình của bản gốc chưa cho thấy khác biệt rõ giữa các nhóm phát hành. Chưa có bằng chứng khác biệt không có nghĩa các nhóm tương đương.

**Nối:** Tên bản WEB cung cấp thêm dấu hiệu gì về dịch vụ nguồn?

**Giới hạn:** Đây là mô hình quan sát, không phải thử nghiệm chiến lược phát hành. Biến năm đầu của mã gốc còn đếm các bản ghi từ 60 ngày trước mốc đầu, nên không nên gọi là phép đo riêng sau phát hành.

## Trang 31 · Thời điểm · Tên bản WEB thường ghi những dịch vụ nguồn nào?

Hình gốc: `plots/8_piracy_ecosystem/05_streaming_rip_sources.png`

**Lời dẫn:** Quay lại các nền tảng đã giới thiệu ở phần xem hợp pháp. Tên torrent là một dấu hiệu bổ sung, không xác nhận nguồn nội dung.

**Cách đọc:** Các phần màu đếm bản WEB có nhãn dịch vụ trong tên. Không đọc chúng thành thị phần toàn bộ torrent. Năm 2021 và 2024 trong hình không đủ 12 tháng.

**Chốt:** Amazon và Netflix xuất hiện nhiều trong nhóm WEB có ghi tên dịch vụ; chỉ một phần bản WEB có thông tin này.

**Nối:** Ba nguồn đã giúp trả lời gì, và những điều nào vẫn chưa thể kết luận?

**Giới hạn:** Nhãn do tên torrent tự khai, có thể sai. Nhóm không ghi nguồn bị loại khỏi hình; không suy ra nền tảng kho lớn gây ra nhiều chia sẻ hoặc đa số mọi WEB đến từ các nền tảng này.

## Trang 32 · Kết luận · Ba nguồn giúp nhìn một phim theo ba chiều

Chốt ba ý: nguồn IMDb giúp hiểu phim; TMDb/JustWatch giúp hiểu phát hành và tiếp cận; MagnetDB cho một góc nhìn chia sẻ. Tích hợp có giá trị khi nối đúng đối tượng và giữ đúng ngữ nghĩa thời gian. Nếu tiếp tục nghiên cứu, nên kiểm tra thủ công cặp ghép, giữ phim chưa quan sát torrent và đánh giá độ nhạy khi thay bộ lọc Digital.

## Nguồn

IMDb Non-Commercial Datasets; TMDb API (dữ liệu watch providers do JustWatch cung cấp); MagnetDB (Seidenberger và cộng sự, 2025). Bản đồ nền: Natural Earth. Xem README của dự án gốc để biết đầu vào và giấy phép.