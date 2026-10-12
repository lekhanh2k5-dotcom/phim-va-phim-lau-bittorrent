"""Build a portable movie-first presentation using 27 original project figures."""
import base64
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SLIDES = []

def concept(phase, title, subtitle, cards, notes, kind='concept'):
    SLIDES.append(dict(phase=phase, title=title, subtitle=subtitle, cards=cards, notes=notes, kind=kind))

def chart(phase, image, title, finding, next_question, why, reading, limitation, scope, caution=''):
    SLIDES.append(dict(phase=phase, kind='chart', image='plots/'+image+'.png', title=title,
                       finding=finding, next_question=next_question, why=why, reading=reading,
                       limitation=limitation, scope=scope, caution=caution))

concept('Mở đầu','Phim được biết đến, phát hành và chia sẻ như thế nào?',
 'Một câu chuyện đi từ danh mục phim đến nguồn chia sẻ trên BitTorrent.',
 [('IMDb','Phim & sự chú ý'),('TMDb / JustWatch','Phát hành & nơi xem'),('MagnetDB','Bản chia sẻ được phát hiện')],
 'Mở đầu bằng câu hỏi: cùng một phim, dữ liệu đánh giá, dữ liệu phát hành và dữ liệu chia sẻ có kể cùng một câu chuyện không? Bài này dùng ba nguồn của dự án gốc, chọn 27 hình và xếp lại theo câu hỏi.',kind='hero')

concept('Mở đầu','Ba nguồn, ba phần thông tin về cùng một bộ phim',
 'Chúng ta cần biết mỗi nguồn trả lời được điều gì trước khi nối chúng.',
 [('IMDb','Danh mục phim: tên, năm, thể loại, điểm và số lượt người dùng đánh giá.'),
  ('TMDb','Thông tin phát hành. Phần nơi xem hợp pháp trong TMDb do JustWatch cung cấp.'),
  ('MagnetDB','Metadata torrent: tên tệp/gói tệp và thời điểm hệ thống thu thập phát hiện.')],
 'IMDb giống hồ sơ của phim. TMDb thêm thông tin phim được phát hành và phân phối. MagnetDB ghi nhận các bản chia sẻ. Dữ liệu JustWatch được lấy qua TMDb, nên bài tổ chức thành ba nguồn thu thập chính. Không nguồn nào một mình trả lời đủ câu hỏi của bài.')

chart('Mở đầu','5_combined/01_integration_diagram','Nối các thông tin về cùng một phim bằng cách nào?',
 'IMDb là điểm nối: TMDb có mã tham chiếu, còn tên torrent cần được nhận diện về phim.',
 'Trước khi ghép chi tiết, danh mục phim đang có những đặc điểm gì?',
 'Một bộ phim có tên trong IMDb, mã tham chiếu trong TMDb và nhiều cách viết trong tên torrent. Giới thiệu đường nối để người nghe biết các hình sau thuộc phần nào của cùng câu chuyện.',
 'Theo các mũi tên về mã phim IMDb. Nhánh TMDb có định danh tham chiếu; nhánh MagnetDB cần kiểm tra tên, năm và bí danh. Phần ghép torrent sẽ được giải thích sau.',
 'Có mã tham chiếu hoặc tên gần giống chưa chứng minh mọi cặp ghép đều đúng. Không đồng nhất cấp phim, cấp file và cặp torrent–phim.',
 'Sơ đồ phương pháp · ba nguồn', 'Sơ đồ định hướng; phần sau sẽ kiểm tra nhánh ghép torrent.')

concept('Mở đầu','Theo một trình tự: hiểu phim rồi mới giải thích chia sẻ',
 'Mỗi phần để lại một câu hỏi cho phần tiếp theo.',
 [('01 · Phim','Danh mục, thể loại, điểm và mức được chú ý.'),
  ('02 · Nơi xem','Có thể xem hợp pháp ở đâu, bằng cách nào và sau bao lâu?'),
  ('03 · Tích hợp','Hiểu torrent; xác định mỗi bản ghi thuộc phim nào.'),
  ('04 · Khác biệt','Độ phổ biến, thể loại và tuổi phim liên hệ với số torrent ra sao?'),
  ('05 · Thời điểm','Các bản chia sẻ xuất hiện quanh mốc phát hành trực tuyến thế nào?')],
 'Bài có 32 trang, trong đó 27 trang dùng hình từ dự án gốc. Ngân sách, doanh thu, codec và nhóm phát hành được để ngoài mạch chính. Nhấn mạnh: số lượt đánh giá là chỉ báo mức được chú ý; điểm là mức được người dùng đánh giá cao; số torrent là nguồn chia sẻ quan sát được.')

chart('Phim','1_imdb/01_movies_per_year','Danh mục phim thay đổi như thế nào qua các năm?',
 'IMDb ghi nhận nhiều phim hơn ở các giai đoạn gần đây; đây là bức tranh của danh mục đang dùng.',
 'Những phim đó thuộc các thể loại nào, và cơ cấu có thay đổi không?',
 'Bắt đầu từ phim và năm, hai khái niệm quen thuộc. Ta cần biết các giai đoạn có quy mô khác nhau trước khi so cơ cấu.',
 'Trục ngang là năm IMDb; trục dọc là số bản ghi phim. Đường cao hơn nghĩa là danh mục có nhiều phim của năm đó hơn.',
 'Độ đầy đủ của IMDb thay đổi theo thời gian. Hình không đủ chứng minh máy quay số hoặc một sự kiện lịch sử gây ra thay đổi; năm IMDb cũng không phải thống kê sản lượng toàn thế giới.',
 'IMDb · phim điện ảnh sau lọc người lớn', 'Đếm bản ghi trong IMDb; không coi đây là tổng điều tra sản lượng phim.')

chart('Phim','1_imdb/02_genre_share_by_decade','Cơ cấu thể loại có giống nhau ở mọi thập niên?',
 'Tỷ trọng các nhãn thay đổi theo thời gian; phải đọc đúng cách chia trọng số trước khi so chính kịch và tài liệu.',
 'Sau cơ cấu thể loại, phim trong danh mục thường được chấm bao nhiêu điểm?',
 'Hình năm chỉ cho tổng số. Tách thể loại giúp xem thành phần của danh mục và giải quyết thắc mắc về chính kịch/tài liệu.',
 'Mỗi cột là cơ cấu chia trọng số. Phim hai nhãn đóng góp 1/2 cho mỗi nhãn, phim ba nhãn đóng góp 1/3. Drama là chính kịch; Documentary là tài liệu.',
 'Tài liệu có tỷ trọng cao hơn trong hình không đồng nghĩa có nhiều phim hơn chính kịch. Muốn trả lời số phim phải đếm trực tiếp từng nhãn. Không suy ra nguyên nhân xã hội chỉ từ cơ cấu này.',
 'IMDb · cơ cấu theo thập niên · chia đều theo nhãn', 'Tỷ trọng chia theo nhãn ≠ số phim. Không kết luận tài liệu có nhiều phim hơn chính kịch.')

chart('Phim','1_imdb/03_rating_distribution','Các phim trong mẫu thường nhận mức điểm nào?',
 'Phần lớn phim trong mẫu có điểm ở khoảng giữa thang đánh giá; điểm cực cao hoặc cực thấp ít hơn.',
 'Sự khác nhau về điểm có tập trung ở một số thể loại không?',
 'Sau khi biết loại phim, chuyển sang cách người dùng đánh giá. Đây là mốc chung để so các thể loại ở hình tiếp.',
 'Trục ngang là điểm IMDb, thang 10. Phần cao của phân bố cho biết mức điểm có nhiều phim. Trung vị là điểm đứng giữa khi xếp các phim theo điểm.',
 'Mẫu có ngưỡng ít nhất 1.000 lượt đánh giá, nên không đại diện cho mọi phim trong IMDb. Điểm của người dùng không phải chất lượng khách quan.',
 'IMDb · phim có ≥1.000 lượt đánh giá', 'Điểm người dùng và chất lượng khách quan là hai khái niệm khác nhau.')

chart('Phim','1_imdb/04_rating_by_genre','Các thể loại có được đánh giá giống nhau không?',
 'Điểm điển hình khác giữa các thể loại; tài liệu và tiểu sử có mức điểm cao hơn một số nhóm khác trong mẫu.',
 'Có điểm khác nhau, vậy sự chú ý của người dùng có phân bố đều giữa các phim?',
 'Hình trước cho mặt bằng điểm chung. Hình này tách theo thể loại đã giới thiệu để xem mặt bằng đó có che các khác biệt không.',
 'Vạch trong hộp là trung vị, hộp chứa nửa số phim ở giữa. So vị trí hộp và phần chồng lấn giữa các thể loại, không chỉ đọc một con số.',
 'Phim nhiều nhãn có mặt ở nhiều nhóm; thành phần khán giả và số lượt đánh giá khác nhau. Hình chưa chứng minh thể loại gây ra điểm cao hoặc thấp.',
 'IMDb · điểm theo thể loại trong mẫu đủ lượt đánh giá')

chart('Phim','1_imdb/06_votes_lorenz','Có nhiều phim, nhưng sự chú ý có phân bố đều không?',
 'Lượt đánh giá tập trung vào một nhóm nhỏ phim. Số phim nhiều không có nghĩa mỗi phim được chú ý như nhau.',
 'Phim được nhiều người chú ý có đồng thời được chấm điểm cao hơn không?',
 'Các hình điểm không cho biết có bao nhiêu người tham gia. Thêm số lượt đánh giá để phân biệt mức được chú ý với mức điểm.',
 'Đường cong cộng dồn lượt đánh giá khi xếp phim từ ít đến nhiều lượt. Đường càng xa đường chia đều thì mức tập trung càng lớn. Gini chỉ là chỉ số tóm tắt.',
 'Lượt đánh giá trên IMDb không phải số người xem toàn thế giới; các phim ở nhiều giai đoạn có thời gian tích lũy đánh giá khác nhau.',
 'IMDb · số lượt đánh giá · phân bố sự chú ý', 'Lượt đánh giá là chỉ báo độ phổ biến trên IMDb, không phải lượt xem.')

chart('Phim','1_imdb/08_votes_vs_rating','Được chú ý nhiều có đồng nghĩa được chấm điểm cao?',
 'Trong dữ liệu có liên hệ giữa lượt đánh giá và điểm; hai biến vẫn đo hai khía cạnh khác nhau.',
 'Biết và đánh giá một phim rồi, người xem có dễ tìm được nơi xem hợp pháp không?',
 'Đặt hai biến cạnh nhau sau khi đã giới thiệu riêng. Đây là nền tảng để đọc các hình tích hợp theo độ phổ biến phía sau.',
 'Sang phải là nhiều lượt đánh giá hơn; lên trên là điểm cao hơn. Màu đậm là vùng có nhiều phim, đường tóm tắt cho xu hướng nhóm.',
 'Không suy ra lượt đánh giá làm điểm tăng. Các nhóm khác nhau về năm, thể loại, thị trường và người tham gia đánh giá.',
 'IMDb · lượt đánh giá và điểm · các trục có thang nén')

chart('Xem hợp pháp','3_tmdb_streaming/01_world_catalog_map','Ở đâu có thể tiếp cận nhiều phim hợp pháp hơn?',
 'Số phim có trong các dịch vụ thuê bao/miễn phí khác nhau giữa các quốc gia trong ảnh chụp dữ liệu.',
 'Khác biệt này liên quan thế nào đến độ phủ và quy mô kho phim của các nền tảng?',
 'Chuyển từ đặc điểm phim sang khả năng tìm nơi xem. Bản đồ cho bối cảnh phân phối trước khi nói tới từng nền tảng.',
 'Màu đậm hơn nghĩa là nhiều tựa phim được ghi nhận qua thuê bao hoặc miễn phí. Màu xám là thiếu dữ liệu, không phải không có phim. Thanh màu dùng thang nén.',
 'Đây là dữ liệu dịch vụ xem năm 2026, không phải lịch sử nơi xem trong giai đoạn torrent 2021–2024. Khác biệt còn phụ thuộc độ đầy đủ của nguồn.',
 'TMDb / JustWatch · ảnh chụp 2026 · thuê bao/miễn phí', 'Bối cảnh năm 2026; không dùng để suy ra điều kiện xem hợp pháp của năm 2021–2024.')

chart('Xem hợp pháp','3_tmdb_streaming/02_brand_reach_vs_depth','Phủ nhiều quốc gia có đồng nghĩa kho phim lớn ở mỗi nơi?',
 'Độ phủ quốc gia và độ sâu kho phim là hai cách nhìn khác nhau về một nền tảng.',
 'Những phim có mặt đó được xem bằng thuê bao, miễn phí, thuê hay mua?',
 'Bản đồ chưa cho biết nền tảng nào tạo ra độ phủ. Hình này phân biệt nhiều nơi phục vụ với nhiều phim tại mỗi nơi.',
 'Một trục đo số quốc gia, trục còn lại đo quy mô kho phim theo định nghĩa ghi trong hình. Vị trí xa ở một trục chưa chắc xa ở trục còn lại.',
 'Quy mô kho phim không đo số thuê bao, thị phần hoặc lịch sử mở rộng. Các chỉ số lấy từ ảnh chụp dịch vụ năm 2026.',
 'TMDb / JustWatch · độ phủ và độ sâu nền tảng')

chart('Xem hợp pháp','3_tmdb_streaming/03_access_mode_by_country','“Có nơi xem” cụ thể là xem bằng cách nào?',
 'Tỷ trọng thuê bao, miễn phí, thuê và mua khác nhau theo thị trường; có mặt chưa đồng nghĩa được xem trong gói thuê bao.',
 'Nhiều dịch vụ như vậy có cung cấp cùng phim, hay kho phim bị phân mảnh?',
 'Hình nền tảng chỉ nói đến có mặt. Hình thức tiếp cận giúp đọc cụ thể điều kiện xem trước khi xét kho phim trùng nhau.',
 'So các phần màu theo chú giải để phân biệt thuê bao/miễn phí với thuê hoặc mua lẻ. Đọc đơn vị trên trục vì một phim có thể có nhiều nơi và cách xem.',
 'Không có giá thuê bao, chi phí thực trả hoặc hành vi người xem trong phép so này. Không tự suy ra thuê/mua nhiều dẫn tới chia sẻ torrent nhiều.',
 'TMDb / JustWatch · hình thức tiếp cận · ảnh chụp 2026')

chart('Xem hợp pháp','3_tmdb_streaming/04_us_catalog_upset','Một dịch vụ có đủ phim, hay cần tìm ở nhiều dịch vụ?',
 'Kho phim ở các dịch vụ trong mẫu Mỹ ít trùng nhau; độ phân mảnh là một đặc điểm cần biết khi nói về khả năng tiếp cận.',
 'Sự phân mảnh đó có khiến phim ít nổi tiếng khó tìm nơi xem hơn không?',
 'Nhiều hình thức xem chưa cho biết mức trùng tựa phim. Hình giao tập giúp kiểm tra người xem có gặp cùng phim ở nhiều nền tảng không.',
 'Các chấm nối phía dưới chỉ tổ hợp nền tảng; cột phía trên đếm phim thuộc đúng tổ hợp đó. Một chấm nghĩa là chỉ có ở một nền tảng trong danh sách đang xét.',
 'Chỉ xét các dịch vụ và hình thức được chọn tại Mỹ. Không suy rộng thành mọi cách xem hợp pháp, mọi quốc gia hoặc toàn bộ lịch sử phân phối.',
 'TMDb / JustWatch · Mỹ · các dịch vụ được chọn')

chart('Xem hợp pháp','5_combined/06_availability_heatmap','Phim được chú ý nhiều hoặc chấm cao có dễ tìm nơi xem hơn?',
 'Trong mẫu, nhóm nhiều lượt đánh giá có độ phủ xem hợp pháp rộng hơn; điểm cần được đọc cùng mức độ phổ biến.',
 'Ngoài việc xem ở đâu, người xem còn phải chờ bao lâu sau khi phim ra rạp?',
 'Nối lại hai biến đã giới thiệu ở IMDb với thông tin nơi xem của TMDb/JustWatch. Đây là câu hỏi không một nguồn đơn lẻ trả lời đủ.',
 'Mỗi ô kết hợp nhóm lượt đánh giá và nhóm điểm. So các hàng trong cùng cột hoặc các cột trong cùng hàng; số/màu thể hiện độ phủ theo định nghĩa trong hình.',
 'Lượt đánh giá và dịch vụ xem là ảnh chụp hiện tại; chưa chứng minh mức phổ biến tạo ra độ phủ, hoặc độ phủ làm phim phổ biến hơn.',
 'IMDb × TMDb / JustWatch · ảnh chụp hiện tại', 'Không đem độ phủ hiện tại giải thích trực tiếp torrent trong các năm trước.')

chart('Xem hợp pháp','2_tmdb/04_theatrical_window','Từ ra rạp đến phát hành trực tuyến thường cách nhau bao lâu?',
 'Khoảng cách ra rạp–Digital trong mẫu Mỹ thay đổi theo giai đoạn. Đây là mốc thời gian sẽ dùng lại khi phân tích torrent.',
 'Nếu muốn đối chiếu với chia sẻ trên mạng, chúng ta cần đo những bản ghi nào?',
 'Nơi xem là một ảnh chụp, còn ngày phát hành cung cấp lịch sử. Chuyển sang mốc thời gian để chuẩn bị cho phân tích quanh ngày Digital.',
 'Digital là ngày phát hành trực tuyến ghi trong TMDb, có thể gồm thuê/mua, không chỉ thuê bao. So số ngày giữa ra rạp và Digital theo nhóm năm ở Mỹ.',
 'Ngày phát hành có thể thiếu hoặc khác nhau giữa quốc gia. Hình cho thay đổi trong mẫu, chưa đủ kết luận một biến cố làm mô hình phát hành thay đổi vĩnh viễn.',
 'TMDb · ngày ra rạp và Digital tại Mỹ', 'Phát hành Digital không đồng nghĩa lên một dịch vụ thuê bao cụ thể.')

concept('Tích hợp','Trước khi đếm: torrent là gì?',
 'Một phim, nhiều phiên bản chia sẻ; một bản ghi, có thể nhiều phim.',
 [('BitTorrent','Cách các máy chia sẻ tệp với nhau. Bài chỉ phân tích thông tin mô tả, không tải nội dung phim.'),
  ('Torrent','Bản ghi mô tả một tệp hoặc gói tệp. Một phim có thể có bản 720p, 1080p hoặc nhiều ngôn ngữ.'),
  ('Điều đang đo','Số torrent được phát hiện và ghép về phim. Dữ liệu không có số người tải hoặc số người xem.')],
 'Ví dụ minh họa, không phải kết quả đo: A.2022.720p và A.2022.1080p có thể cùng thuộc phim A năm 2022. Ta ghi nhận hai torrent, không phải hai phim hoặc hai người tải. Một torrent bộ sưu tập có thể chứa nhiều phim. Thời điểm thu thập thấy torrent cũng khác thời điểm tạo torrent.')

chart('Tích hợp','4_magnetdb/01_content_sunburst','Mạng chia sẻ này có phải chỉ chứa phim?',
 'MagnetDB có nhiều loại nội dung. Phải xác định nhóm phim trước khi phân tích, không coi mọi video là phim điện ảnh.',
 'Bên cạnh loại nội dung, hệ thống thu thập có hoạt động đều theo thời gian không?',
 'Người nghe vừa biết torrent là bản ghi chia sẻ. Hình cơ cấu nội dung cho thấy vì sao cần lọc thay vì đếm toàn bộ nguồn.',
 'Đọc các vòng theo nhóm nội dung và chú ý hình dùng dung lượng hay số tệp. Nhóm video bao gồm nhiều nội dung ngoài phim điện ảnh.',
 'Hình tổng quan dùng dữ liệu/mẫu file theo phạm vi của notebook gốc. Tỷ trọng dung lượng không phải tỷ trọng người dùng hay số phim.',
 'MagnetDB · cơ cấu file tổng quan', 'Video ≠ phim điện ảnh; dung lượng ≠ số người tải.')

chart('Tích hợp','4_magnetdb/03_crawler_coverage','Số bản ghi thay đổi vì chia sẻ, hay vì hệ thống thu thập?',
 'Thu thập không đều. Cần giới hạn thời gian và thận trọng với các khoảng gián đoạn trước khi diễn giải xu hướng.',
 'Trong phạm vi đã chọn, làm sao loại các cặp torrent–phim ghép không phù hợp?',
 'Sau lọc nội dung, kiểm tra chất lượng theo thời gian. Một khoảng không có bản ghi có thể là hệ thống ngừng, không phải cộng đồng ngừng chia sẻ.',
 'Đường thể hiện số torrent được phát hiện theo tháng; vùng đánh dấu giải thích các giai đoạn thu thập. Phần phân tích chính dùng từ 04/2021 đến 09/2024.',
 'Cửa sổ được chọn vẫn có gián đoạn, đặc biệt 06/2024. Đây là thời điểm phát hiện, không phải thời điểm đăng. Bản trình bày giữ phạm vi xử lý của bản gốc.',
 'MagnetDB · lịch hoạt động thu thập', 'Không diễn giải khoảng trống thu thập thành không có chia sẻ.')

chart('Tích hợp','6_integration/01_cleaning_funnel','Vì sao phải làm sạch trước khi đếm torrent của phim?',
 'Các bước lọc loại bản ghi không phù hợp về loại nội dung, tên, năm và các điều kiện khác; còn lại là tập để phân tích.',
 'Mã ghép có sẵn đã đủ chưa, hay cần thêm một cách nhận diện?',
 'Sơ đồ đầu bài chỉ cho đường nối. Phễu này kiểm tra các bản ghi đi qua đường nối đó và cho thấy tích hợp cần xử lý chất lượng.',
 'Mỗi bước cho số bản ghi còn lại sau lọc. Phải đọc đúng đơn vị của từng nhánh: file, torrent và cặp torrent–phim không hoàn toàn giống nhau.',
 'Tên/năm phù hợp là bằng chứng metadata, không kiểm tra nội dung tệp. Một số bộ lọc dùng ngày Digital và vì vậy ảnh hưởng phân tích thời điểm ở phần sau.',
 'IMDb × TMDb × MagnetDB · quy trình làm sạch', 'Làm sạch bằng metadata; chưa xác nhận nội dung của từng torrent.')

chart('Tích hợp','6_integration/02_coverage_by_source','Tự ghép tên bổ sung được bao nhiêu dữ liệu?',
 'Tự ghép tên tìm thêm nhiều bản ghi ngoài nhánh mã có sẵn. Lựa chọn cách ghép ảnh hưởng trực tiếp độ phủ của phân tích.',
 'Việc bổ sung đó có thay đổi kết quả của các phim cụ thể không?',
 'Phễu cho thấy số bản ghi bị loại nhưng chưa cho biết dữ liệu nào được bổ sung. So hai nhánh để thấy giá trị của nhận diện thực thể.',
 'Các phần màu biểu thị cặp chỉ tìm thấy ở từng phương pháp và phần giao nhau. So đơn vị cặp ghép, không nhầm với số người chia sẻ.',
 'Phương pháp nhiều bản ghi hơn chưa chắc chính xác hơn. Tự ghép cần tên/năm rõ và có thể bỏ phim trùng tên.',
 'IMDb × MagnetDB · so hai phương pháp ghép')

chart('Tích hợp','6_integration/03_top_movies_dumbbell','Một phim có thể “biến mất” chỉ vì cách ghép dữ liệu không?',
 'Một số phim có rất ít hoặc không có torrent theo mã sẵn, nhưng có nhiều bản ghi khi tự ghép. Thiếu ghép dễ bị nhầm thành ít chia sẻ.',
 'Độ phủ tăng rồi, chúng ta kiểm tra mức đáng tin của ghép như thế nào?',
 'Hình trước là tổng số; hình này đưa tên phim cụ thể để người nghe thấy tác động thực tế của phương pháp tới kết quả.',
 'Hai đầu đoạn nối là số bản ghi của cùng phim theo hai cách ghép. Đoạn dài nghĩa là cách nhận diện làm thay đổi số lượng mạnh.',
 'Đây là các ví dụ được chọn, không phải mẫu ngẫu nhiên toàn bộ phim. Số 0 trong nhánh mã sẵn chỉ là không tìm thấy theo nhánh đó.',
 'IMDb × MagnetDB · ví dụ ảnh hưởng của tích hợp')

chart('Tích hợp','6_integration/04_match_agreement','Hai cách ghép thống nhất với nhau đến mức nào?',
 'Mức đồng thuận sau làm sạch cao hơn trước làm sạch. Điều này hỗ trợ kiểm tra phương pháp, chưa phải độ chính xác tuyệt đối.',
 'Sau tích hợp, phim nào có nhiều bản chia sẻ được quan sát nhất?',
 'Đã thấy tăng độ phủ, giờ cần đánh giá chất lượng. So phương pháp trên các cặp có thể đối chiếu thay vì chỉ báo tổng số lớn.',
 'Đọc riêng các phép đối chiếu trong hình. Tỷ lệ thống nhất với mã tham chiếu nói về cùng kết quả ghép, không chứng minh nội dung tệp đúng.',
 'Hai cách có thể cùng sai hoặc cùng bỏ sót. Không gọi mức đồng thuận 99,4% là độ chính xác 99,4%, cũng không suy ra 0,6% là toàn bộ tỷ lệ sai.',
 'IMDb × MagnetDB · đối chiếu cách ghép', 'Đồng thuận giữa phương pháp ≠ độ chính xác đã kiểm chứng thủ công.')

chart('Khác biệt','7_piracy_movies/01_top20_pirated','Những phim nào có nhiều bản chia sẻ được quan sát nhất?',
 'Các tên đứng đầu chủ yếu là phim đại chúng gần đây. Bảng xếp hạng mở ra câu hỏi về vai trò của độ phổ biến.',
 'Có nhiều torrent vì phim được nhiều người chú ý hơn không?',
 'Bắt đầu kết quả tích hợp bằng tên phim cụ thể. Sau đó cần đi từ ví dụ nổi bật sang quan hệ trên nhiều phim.',
 'Thanh dài hơn nghĩa là có nhiều torrent khác nhau được ghép vào phim trong cửa sổ quan sát. Đây là top trong dữ liệu, không phải top lượt tải.',
 'Ghép sai, thiếu ghép và bộ sưu tập có thể ảnh hưởng thứ hạng. Chỉ xét các phim có bản ghi quan sát; không đại diện cho tất cả phim ngoài mẫu.',
 'Ba nguồn đã tích hợp · torrent quan sát 04/2021–09/2024', 'Số bản ghi chia sẻ không đo mức tổn thất doanh thu hoặc số người tải.')

chart('Khác biệt','7_piracy_movies/02_popularity_vs_piracy','Phim nhiều người đánh giá có thường nhiều torrent hơn?',
 'Nhiều lượt đánh giá đi cùng nhiều torrent trong mẫu đã ghép. Quan hệ chung vẫn để lại các phim cao hoặc thấp hơn mốc dự đoán.',
 'Sau khi xét lượt đánh giá, khác biệt giữa thể loại còn lại như thế nào?',
 'Top phim gợi ý độ phổ biến. Kiểm tra quan hệ trên nhiều phim và dùng mốc chung để đọc khác biệt thể loại phía sau.',
 'Sang phải là nhiều lượt đánh giá, lên trên là nhiều torrent. Trục nén để thấy cả nhỏ và lớn. Điểm xa đường mô hình có thể là ngoại lệ hoặc sai số ghép.',
 'Bản gốc chủ yếu phân tích phim đã quan sát được torrent. Vote là ảnh chụp hiện tại; không đại diện mức phổ biến tại thời điểm torrent xuất hiện và không chứng minh nhân quả.',
 'IMDb × MagnetDB · mẫu phim có torrent', 'Kết quả trên mẫu đã ghép; chưa bao gồm đầy đủ phim không quan sát thấy torrent.')

chart('Khác biệt','7_piracy_movies/03_genre_piracy_ratio','Khác biệt thể loại có chỉ đến từ mức độ phổ biến?',
 'Trong phép so với mốc theo lượt đánh giá, một số thể loại có nhiều torrent hơn mốc và một số ít hơn.',
 'Nguồn chia sẻ này chỉ thuộc phim mới, hay còn nhiều phim cũ?',
 'Các thể loại vốn khác nhau về điểm và sự chú ý ở phần đầu. So phần còn lại sau mốc dự đoán để tránh chỉ đọc số tổng.',
 'Mốc ×1 là phù hợp mô hình độ phổ biến. Trên ×1 là nhiều hơn mốc, dưới ×1 là ít hơn. Đây là phần chênh lệch mô tả, không phải tác động riêng do thể loại.',
 'Phim nhiều nhãn chồng lấn giữa nhóm. Mô hình bản gốc chưa giữ cố định mọi khác biệt về năm, thị trường và cơ hội quan sát; phần còn lại có cả sai số ghép.',
 'IMDb × MagnetDB · thể loại so với mốc độ phổ biến', 'Khác biệt còn lại chưa phải bằng chứng thể loại gây ra chia sẻ.')

chart('Khác biệt','7_piracy_movies/05_film_age_of_uploads','Bản chia sẻ mới được phát hiện có phải luôn là phim mới?',
 'Nguồn chia sẻ quan sát được có cả phim cũ. Mới được phát hiện và mới được phát hành là hai điều khác nhau.',
 'Với phim có lịch phát hành, torrent thay đổi thế nào quanh ngày ra bản trực tuyến?',
 'Độ phổ biến và thể loại chưa nói đến tuổi phim. Tách nhóm năm để phân biệt tuổi nội dung với thời điểm quan sát bản ghi.',
 'Các phần màu là nhóm năm của phim; so tỷ trọng trong từng giai đoạn. Phim trước 2010 vẫn đóng góp đáng kể theo hình.',
 'Tỷ trọng không đo xác suất một phim của thập niên đó được chia sẻ. Nhiều torrent có thể là các phiên bản/gói khác nhau; chưa xác nhận chúng là remaster hoặc bản lồng tiếng mới.',
 'IMDb × MagnetDB · năm phim và thời điểm phát hiện')

chart('Thời điểm','7_piracy_movies/06_event_study_digital','Các bản chia sẻ thay đổi thế nào quanh ngày phát hành Digital?',
 'Hình gốc cho thấy tăng mạnh quanh mốc Digital; cách lọc trước Digital ảnh hưởng trực tiếp hình dạng này.',
 'Khi lấy ngày Digital tại Mỹ làm mốc, bản WEB đầu tiên được phát hiện sau bao lâu?',
 'Đưa ngày phát hành TMDb vào để mở rộng từ phim nào sang khi nào. Đây là phần ba nguồn cùng tham gia câu hỏi thời gian.',
 'Tuần 0 là ngày Digital sớm nhất ghi trong nguồn. So bản WEB với các bản khác ở hai phía của mốc. Trục dọc là số bản ghi trung bình trên phim trong mẫu.',
 'Bộ lọc bản gốc đã loại WEB bị cho là xuất hiện quá sớm. Vì vậy sự thiếu WEB trước Digital một phần do chính quy tắc lọc; hệ số tăng trong hình không phải bằng chứng độc lập về tác động của phát hành.',
 'Ba nguồn · Digital sớm nhất · phim đạt điều kiện sự kiện', 'Bộ lọc đã loại WEB trước Digital: hình này chưa độc lập chứng minh tác động của phát hành.')

chart('Thời điểm','7_piracy_movies/07_web_lag','Bản WEB đầu tiên được phát hiện cách ngày Digital ở Mỹ bao lâu?',
 'Nhiều phim có bản WEB được phát hiện gần mốc Digital tại Mỹ. Giá trị âm cần xét lịch phát hành ở quốc gia khác.',
 'Xuất hiện sớm hơn có đồng nghĩa tổng số bản chia sẻ năm đầu lớn hơn không?',
 'Hình tuần tổng hợp chưa cho biết độ trễ từng phim. Chuyển sang số ngày và làm rõ mốc Mỹ khác mốc Digital sớm nhất của hình trước.',
 'Ngày 0 là Digital ở Mỹ; số âm là phát hiện trước mốc Mỹ, số dương là sau. Hai cột ngoài cùng gom các độ trễ vượt giới hạn hiển thị.',
 'Đây là ngày hệ thống phát hiện, không phải thời điểm tạo torrent. Chênh lệch quốc gia, thiếu ngày và bộ lọc trước Digital đều ảnh hưởng phân bố.',
 'Ba nguồn · mốc Digital Mỹ · phim 04/2021–09/2023', 'Đổi mốc: hình trước là Digital sớm nhất; hình này dùng Digital tại Mỹ.')

chart('Thời điểm','7_piracy_movies/08_release_strategy_effect','Đổi thời điểm phát hành có đi cùng đổi tổng lượng chia sẻ?',
 'Mô hình của bản gốc chưa cho thấy khác biệt rõ giữa các nhóm phát hành. Chưa có bằng chứng khác biệt không có nghĩa các nhóm tương đương.',
 'Tên bản WEB cung cấp thêm dấu hiệu gì về dịch vụ nguồn?',
 'Sau độ trễ, kiểm tra tổng số trong cửa sổ năm đầu để tránh nhầm xuất hiện sớm với xuất hiện nhiều. Hình giữ các điều kiện của mô hình gốc.',
 'Nhóm chiếu rạp trước 4–45 ngày là mốc ×1. Chấm là tỷ lệ theo mô hình; vạch ngang là khoảng ước lượng. Khoảng đi qua ×1 chưa tách rõ khỏi mốc.',
 'Đây là mô hình quan sát, không phải thử nghiệm chiến lược phát hành. Biến năm đầu của mã gốc còn đếm các bản ghi từ 60 ngày trước mốc đầu, nên không nên gọi là phép đo riêng sau phát hành.',
 'Ba nguồn · lịch phát hành Mỹ · mô hình quan sát', 'Chưa thấy khác biệt rõ ≠ đã chứng minh không khác. Cửa sổ gốc có cả 60 ngày trước mốc đầu.')

chart('Thời điểm','8_piracy_ecosystem/05_streaming_rip_sources','Tên bản WEB thường ghi những dịch vụ nguồn nào?',
 'Amazon và Netflix xuất hiện nhiều trong nhóm WEB có ghi tên dịch vụ; chỉ một phần bản WEB có thông tin này.',
 'Ba nguồn đã giúp trả lời gì, và những điều nào vẫn chưa thể kết luận?',
 'Quay lại các nền tảng đã giới thiệu ở phần xem hợp pháp. Tên torrent là một dấu hiệu bổ sung, không xác nhận nguồn nội dung.',
 'Các phần màu đếm bản WEB có nhãn dịch vụ trong tên. Không đọc chúng thành thị phần toàn bộ torrent. Năm 2021 và 2024 trong hình không đủ 12 tháng.',
 'Nhãn do tên torrent tự khai, có thể sai. Nhóm không ghi nguồn bị loại khỏi hình; không suy ra nền tảng kho lớn gây ra nhiều chia sẻ hoặc đa số mọi WEB đến từ các nền tảng này.',
 'MagnetDB · tên dịch vụ tự khai trong bản WEB', 'Chỉ nhóm WEB có ghi dịch vụ; không đại diện toàn bộ bản WEB.')

concept('Kết luận','Ba nguồn giúp nhìn một phim theo ba chiều',
 'Danh mục và sự chú ý → khả năng tiếp cận → nguồn chia sẻ và thời điểm.',
 [('Điều thấy được','Mức chú ý, thể loại và tuổi phim đi cùng các khác biệt về số torrent quan sát được.'),
  ('Giá trị tích hợp','Ghép cùng phim để nối lượt đánh giá, ngày phát hành và thời điểm phát hiện; kiểm tra cách ghép làm thay đổi kết quả.'),
  ('Phạm vi kết luận','Chưa đo lượt tải, người xem, thất thu hoặc nguyên nhân. Phần thời gian cần đọc cùng bộ lọc và các mốc quốc gia.')],
 'Chốt ba ý: nguồn IMDb giúp hiểu phim; TMDb/JustWatch giúp hiểu phát hành và tiếp cận; MagnetDB cho một góc nhìn chia sẻ. Tích hợp có giá trị khi nối đúng đối tượng và giữ đúng ngữ nghĩa thời gian. Nếu tiếp tục nghiên cứu, nên kiểm tra thủ công cặp ghép, giữ phim chưa quan sát torrent và đánh giá độ nhạy khi thay bộ lọc Digital.',kind='ending')

def build():
    assert len(SLIDES)==32
    charts=[s for s in SLIDES if s['kind']=='chart']
    assert len(charts)==27 and len({s['image'] for s in charts})==27
    for s in charts:assert (ROOT/s['image']).is_file(),s['image']
    template=(HERE/'template.html').read_text(encoding='utf-8')
    esc=lambda x:html.escape(str(x),quote=True)
    rendered=[]
    for i,s in enumerate(SLIDES):
        head=f"<div class='slide-heading'><p class='eyebrow'>{esc(s['phase'])} <span>• {i+1:02d} / {len(SLIDES)}</span></p><h2>{esc(s['title'])}</h2></div>"
        if s['kind']=='chart':
            uri='data:image/png;base64,'+base64.b64encode((ROOT/s['image']).read_bytes()).decode('ascii')
            body=f"<p class='scope'>{esc(s['scope'])}</p><button class='figure-frame' aria-label='Phóng to biểu đồ: {esc(s['title'])}' data-zoom><img src='{uri}' alt='{esc(s['title'])}' decoding='async'></button>"
            body+=f"<div class='takeaways'><div><span class='label'>Điều rút ra</span><p>{esc(s['finding'])}</p></div><div class='next-question'><span class='label'>Câu hỏi tiếp</span><p>{esc(s['next_question'])}</p></div></div>"
            body+=f"<p class='caution'>{esc(s['caution'])}</p>" if s['caution'] else "<p class='figure-hint'>Bấm vào hình hoặc nhấn Z để phóng to · N mở lời dẫn</p>"
        else:
            body=f"<p class='subtitle'>{esc(s['subtitle'])}</p><div class='concept-cards'>"+''.join(f"<div><span class='card-number'>{j+1:02d}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></div>" for j,(t,d) in enumerate(s['cards']))+'</div>'
            if s['kind']=='hero':body+="<p class='hero-footer'>Tích hợp và Phân tích dữ liệu lớn <span>27 biểu đồ · 32 trang · ba nguồn</span></p>"
        rendered.append(f"<section class='slide {s['kind']} {'active' if i==0 else ''}' data-index='{i}' aria-label='Trang {i+1}: {esc(s['title'])}'>{head}{body}</section>")
    # Embed only narrative in JSON. Each original raster is embedded once in its slide.
    data=json.dumps(SLIDES,ensure_ascii=False).replace('</','<\\/')
    result=template.replace('<!-- SLIDES -->','\n'.join(rendered)).replace('<!-- DATA -->',data)
    (HERE/'index.html').write_text(result,encoding='utf-8')
    (HERE/'mach_trinh_bay.json').write_text(json.dumps(SLIDES,ensure_ascii=False,indent=2),encoding='utf-8')
    outline=['# Phim được biết đến, phát hành và chia sẻ như thế nào?','Bản trình chiếu dùng 27 hình của dự án ba nguồn, không chạy lại hoặc sửa pipeline. PNG được nhúng vào index.html để mở ngoại tuyến và chia sẻ một tệp. Các nhận xét trong bản này thu hẹp các kết luận quá mạnh ở chú thích gốc; biểu đồ giữ nguyên.',
             'Mở `index.html` bằng Chrome/Edge. Dùng ←/→ hoặc Space, N mở lời dẫn, Z phóng to hình, F toàn màn hình, M mở mục lục. Có thể in sang PDF bằng nút In/PDF của trình duyệt.']
    for i,s in enumerate(SLIDES,1):
        outline.extend([f"## Trang {i:02d} · {s['phase']} · {s['title']}"])
        if s['kind']=='chart':
            outline.extend([f"Hình gốc: `{s['image']}`",f"**Lời dẫn:** {s['why']}",f"**Cách đọc:** {s['reading']}",f"**Chốt:** {s['finding']}",f"**Nối:** {s['next_question']}",f"**Giới hạn:** {s['limitation']}"])
        else:outline.append(s['notes'])
    outline.extend(['## Nguồn','IMDb Non-Commercial Datasets; TMDb API (dữ liệu watch providers do JustWatch cung cấp); MagnetDB (Seidenberger và cộng sự, 2025). Bản đồ nền: Natural Earth. Xem README của dự án gốc để biết đầu vào và giấy phép.'])
    (HERE/'README.md').write_text('\n\n'.join(outline),encoding='utf-8')
    print(f'Built {len(SLIDES)} pages, {len(charts)} embedded figures; HTML {(HERE/"index.html").stat().st_size/1024/1024:.2f} MB.')

if __name__=='__main__':build()
