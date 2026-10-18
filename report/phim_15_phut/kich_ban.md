# Kịch bản thuyết trình

19 slide. Phân tích từng nguồn trước, tích hợp sau.

## 01. Một bộ phim. Ba góc nhìn.

Trong bài này, chúng tôi theo dõi một bộ phim qua ba góc nhìn: người dùng quan tâm ra sao, phim được phát hành khi nào và hệ thống ghi nhận những bản chia sẻ nào. Chúng tôi sẽ phân tích riêng từng nguồn, sau đó nối chúng để trả lời ba câu hỏi chung.

## 02. Ba nguồn dữ liệu và bước tiền xử lý

IMDb giống một danh mục phim có đánh giá của người dùng. TMDb bổ sung lịch phát hành và nơi xem. BitTorrent là cách chia sẻ tệp giữa nhiều máy tính; MagnetDB ghi nhận metadata các bản chia sẻ đó. Trước khi phân tích, dữ liệu đi qua năm bước tiền xử lý. Một, chỉ giữ phim lẻ, bỏ phim người lớn và tập phim bộ. Hai, chuẩn hóa tên phim: bỏ dấu, chữ thường, thêm tên phim theo từng nước. Ba, ghép thực thể: tách tên và năm từ tên torrent rồi đối chiếu với IMDb; TMDb nối qua mã IMDb. Bốn, làm sạch: bỏ tệp nhỏ, năm lệch, ca trùng tên và torrent giả. Năm, chỉ giữ giai đoạn thu thập ổn định từ tháng tư năm hai nghìn không trăm hai mươi mốt đến tháng chín năm hai nghìn không trăm hai mươi bốn.

## 03. Dữ liệu còn lại sau từng bước làm sạch

**Lời dẫn:** Hình này minh họa cụ thể các bước làm sạch vừa giới thiệu. Cụm xanh dương bên trái là nhánh dùng mã IMDb có sẵn trong MagnetDB; nhiều bản ghi bị loại sau khi kiểm tra loại nội dung, dung lượng, tên và năm. Cụm cam ở giữa là nhánh tự ghép tên torrent với IMDb, sau đó bỏ các trường hợp mơ hồ. Cụm xanh lá bên phải là hợp hai nguồn rồi áp dụng các bộ lọc chung. Không cộng trực tiếp hai nhánh vì chúng có phần giao nhau. Mỗi cụm dùng thang riêng, nên đọc nhãn số thay vì so chiều dài thanh giữa các cụm. Đây là phễu làm sạch trên phạm vi dữ liệu gốc, trước khi giới hạn cửa sổ quan sát của dashboard. Tiếp theo, chúng tôi đi vào từng thao tác chuẩn hóa, ghép thực thể, bổ sung TMDb và kiểm tra dữ liệu.

**Cách đọc:** Đọc ba cụm từ trái sang phải: mã IMDb có sẵn, tự ghép tên torrent, rồi hợp hai nguồn và lọc chung. Nhãn số cho biết số torrent còn lại sau mỗi bước.

**Chốt:** Hai nhánh ghép được làm sạch riêng, sau đó hợp nhất và lọc chung trước khi phân tích.

**Chuyển:** Đi vào từng thao tác: chuẩn hóa dữ liệu trước khi ghép phim.

**Lưu ý:** Mỗi cụm có thang riêng; không so trực tiếp độ dài thanh giữa các cụm và không cộng hai nhánh vì có phần giao nhau. Phễu dùng phạm vi dữ liệu gốc, khác cửa sổ thống kê của dashboard.

## 04. Chuẩn hóa dữ liệu và tạo chỉ mục tên phim

**Lời dẫn:** Trước hết, nhóm trích metadata cần dùng từ SQLite thay vì nạp cả cơ sở dữ liệu vào bộ nhớ. Các bản ghi giữ torrent_id để nối tên, file và thời điểm phát hiện. Với IMDb, nhóm giữ phim lẻ, nối điểm và bình chọn bằng tconst, rồi thêm tên ở nhiều quốc gia từ title.akas. Các tên được chuẩn hóa bằng cách bỏ dấu, viết thường và bỏ ký tự đặc biệt. Ví dụ El gran Lebowski tra về The Big Lebowski năm 1998. Chỉ mục có hơn 1,8 triệu tên, nên một phim có thể được tìm qua nhiều tên khác nhau.

**Cách đọc:** Đọc hai cột đầu vào và ví dụ tên thay thế ở cuối. Phân biệt định danh với tên dùng để tra.

**Chốt:** Chuẩn hóa tên và bổ sung bí danh giúp ghép được phim mang tên ở ngôn ngữ khác.

**Chuyển:** Sau chuẩn hóa, quy tắc nào quyết định một torrent thuộc phim nào?

**Lưu ý:** Số phim ở đây là toàn danh mục IMDb trong notebook, khác mẫu dashboard có ngưỡng bình chọn.

## 05. Ghép chính xác tên chuẩn hóa + năm; bỏ ca mơ hồ

**Lời dẫn:** Nhánh ghép tên chính bỏ tiền tố rác, tách năm và phần tên đứng trước năm, rồi tra chính xác tên đã chuẩn hóa trong chỉ mục IMDb. Năm cho phép lệch một đơn vị. Những tên trùng nhiều phim hoặc quá chung chung được đánh dấu mơ hồ và bỏ. Notebook ghi nhận hơn 2,25 triệu dòng ghép ban đầu, trong đó gần 194 nghìn ca mơ hồ. Để đối chiếu, bước tám chạy riêng guessit và rapidfuzz trên 20 nghìn tên file, so với nhãn MagnetDB. Các chỉ số precision và recall của phép đối chiếu này không được coi là độ chính xác của toàn bộ nhánh ghép chính.

**Cách đọc:** Theo bốn bước từ trái sang phải, đọc ví dụ Parasite và phân biệt nhánh tra chính xác với phép đối chiếu gần đúng.

**Chốt:** Ghép tên có ràng buộc năm và cơ chế từ chối; không nhận mọi tên giống nhau thành cùng một phim.

**Chuyển:** Khi đã nhận diện được phim, TMDb bổ sung thông tin bằng khóa nào?

**Lưu ý:** Nhãn MagnetDB có lỗi. Precision/recall là kết quả đối chiếu trên mẫu 20.000 file, không phải kiểm định thủ công toàn tập.

## 06. Bổ sung TMDb bằng mã IMDb, rồi tách thành 3 bảng

**Lời dẫn:** Sau khi có mã IMDb, nhóm hợp danh sách phim rồi tìm mã TMDb qua endpoint find. Phản hồi JSON được lưu đệm để có thể chạy tiếp mà không tải lại. Bước bảy tách thành ba bảng có mức chi tiết khác nhau: một dòng thông tin phim, nhiều mốc phát hành theo nước và loại, và nơi xem theo nước cùng dịch vụ. Ví dụ Top Gun có mốc Premiere tại Mỹ khác các mốc ra rạp hoặc Digital. Khi tạo bảng phân tích theo phim, phải tổng hợp các bảng nhiều dòng trước khi nối. Nơi xem là ảnh chụp năm 2026, không phải lịch sử danh mục.

**Cách đọc:** Theo đường mã IMDb tới ba bảng. Đọc dòng mô tả mức chi tiết trên mỗi bảng và ví dụ Top Gun.

**Chốt:** Nối bằng mã phim; giữ riêng ngày phát hành lịch sử và nơi xem tại thời điểm thu thập.

**Chuyển:** Ghép được chưa đủ: những bản ghi nào còn cần bị loại hoặc gắn cờ?

**Lưu ý:** Các số liệu tiền chỉ minh họa hồ sơ Top Gun trong notebook; nơi xem có thể khác thời điểm ra mắt.

## 07. Bộ lọc A–J xử lý những lỗi nào?

**Lời dẫn:** Làm sạch gồm nhiều phép kiểm tra có mục tiêu khác nhau. A đến C loại nội dung không phải phim lẻ và các tệp quá nhỏ. D đến E2 kiểm tra năm, tên và số phần. F kiểm tra torrent quá sớm so với lần ra mắt, còn G đến I kiểm tra mâu thuẫn giữa hai nguồn và dấu hiệu phim bộ. J gắn cờ các bản phát hành có thời điểm khó hợp lý. Ba ví dụ trong notebook gồm tập S03E01 bị gán vào phim lẻ, Independence Day năm 2016 bị gán cho phim 1996, và một bản tự xưng BluRay xuất hiện trước khi Ant-Man ra rạp. Các bước đều để lại nhật ký hoặc cờ để truy vết.

**Cách đọc:** Đọc nhóm quy tắc bên trái, rồi nối ba ví dụ bên phải với bộ lọc B, D và J.

**Chốt:** Làm sạch kiểm tra cả nội dung và danh tính phim; có cờ và nhật ký để kiểm tra lại.

**Chuyển:** Sau làm sạch, dữ liệu có đơn vị gì và cửa sổ phân tích được chọn ra sao?

**Lưu ý:** implausible là cờ suy ra từ metadata và thời điểm; không xác minh nội dung của tệp.

## 08. Chốt hai bảng sạch, phân biệt đơn vị và thời gian

**Lời dẫn:** Cuối cùng, torrents_clean có một dòng cho một cặp torrent và phim, còn movie_analysis tổng hợp thành một dòng cho mỗi phim. Notebook ghi nhận 2.078.927 cặp sạch, tương ứng 2.066.598 torrent riêng biệt và 126.081 phim trên toàn phạm vi. Khi giới hạn ngày phát hiện từ 1 tháng 4 năm 2021 đến trước 29 tháng 9 năm 2024, còn 923.998 cặp. Cần tách năm phim IMDb, ngày phát hành TMDb và ngày hệ thống phát hiện torrent; đây là ba mốc khác nhau. Đếm bản ghi chia sẻ không cho biết lượt tải. Với dữ liệu đã được hình thành như vậy, chúng tôi bắt đầu nhìn riêng từng nguồn.

**Cách đọc:** So sánh mức chi tiết của hai bảng, ba số đếm toàn phạm vi và số cặp trong cửa sổ được tô màu.

**Chốt:** Đơn vị đếm và cửa sổ quan sát quyết định con số; không trộn cặp torrent–phim với torrent riêng biệt.

**Chuyển:** Bắt đầu với IMDb: quy mô kho phim và sự quan tâm của khán giả thay đổi thế nào?

**Lưu ý:** Cửa sổ vẫn có gián đoạn thu thập. Danh mục dashboard còn áp dụng bộ lọc năm, người lớn và bình chọn riêng.

## 09. Kho phim thay đổi thế nào theo thời gian?

**Lời dẫn:** Trước tiên, chúng tôi nhìn riêng vào IMDb. Hình này đếm các bản ghi phim theo năm. Quy mô danh mục tăng ở nhiều giai đoạn gần đây, nhưng cần nhớ IMDb không phải một cuộc tổng điều tra sản lượng phim toàn cầu. Điều quan trọng ở đây là các năm có quy mô khác nhau, nên khi đối chiếu các nhóm phim, ta cần giữ khoảng năm rõ ràng. Với một danh mục lớn như vậy, câu hỏi tiếp theo là: sự chú ý của người dùng có phân bố đều giữa các phim không?

**Cách đọc:** Trục ngang là năm phim trên IMDb; trục dọc là số bản ghi phim. Chỉ nhấn mạnh hình dạng xu hướng, không đọc từng năm.

**Chốt:** Quy mô danh mục khác nhau giữa các năm; cần hiểu nền dữ liệu trước khi so sánh.

**Chuyển:** Nhiều phim như vậy, sự chú ý có phân bố đều không?

**Lưu ý:** Số bản ghi IMDb chịu ảnh hưởng của độ đầy đủ dữ liệu; không phải tổng điều tra sản lượng phim.

## 10. Sự chú ý tập trung vào một nhóm phim nhỏ

**Lời dẫn:** Hình thứ hai trả lời câu hỏi về sự chú ý. Chúng tôi xếp phim từ ít đến nhiều lượt bình chọn. Nếu mọi phim nhận số bình chọn như nhau thì kết quả nằm trên đường chéo. Đường thực tế cong mạnh: trong nhóm có đánh giá, khoảng một phần trăm phim nhiều bình chọn nhất chiếm sáu mươi chín phần trăm tổng lượt bình chọn. Vì vậy, bình chọn là một góc nhìn hữu ích về mức độ quan tâm, dù không phải lượt xem. Nhưng được quan tâm chưa cho biết phim có thể được xem ở đâu.

**Cách đọc:** Phim được xếp từ ít đến nhiều bình chọn. Nếu phân bố đều, đường xanh trùng đường chéo; đường thực tế cong mạnh cho thấy sự tập trung.

**Chốt:** Trong nhóm phim có đánh giá, 1% phim nhiều bình chọn nhất chiếm khoảng 69% tổng lượt bình chọn.

**Chuyển:** Khán giả có thể tiếp cận những bộ phim đó ở đâu?

**Lưu ý:** Bình chọn là chỉ báo mức độ quan tâm; không phải lượt xem. Không cần giải thích công thức Gini.

## 11. Nơi xem phim khác nhau giữa các quốc gia

**Lời dẫn:** Chuyển sang TMDb, chúng tôi xem riêng khả năng tiếp cận phim hợp pháp. Bản đồ cho thấy số phim có nơi xem được ghi nhận khác nhau giữa các quốc gia. Chỉ cần đối chiếu vài vùng theo chú giải để thấy danh mục không đồng nhất. Đây là dữ liệu nơi xem do JustWatch cung cấp qua TMDb, tại thời điểm thu thập năm hai nghìn không trăm hai mươi sáu. Nó chưa phản ánh danh mục của từng quốc gia trong quá khứ. Ngoài khác biệt về địa điểm, khán giả còn có thể tiếp cận một phim ở những thời điểm khác nhau.

**Cách đọc:** Đọc chú giải màu để so sánh số phim trong danh mục được ghi nhận. Chỉ chọn hai hoặc ba vùng để minh họa.

**Chốt:** Danh mục phim có nơi xem được ghi nhận khác nhau giữa các quốc gia.

**Chuyển:** Ngoài nơi xem, thời điểm tiếp cận có khác nhau không?

**Lưu ý:** Nơi xem là ảnh chụp tại thời điểm thu thập năm 2026, không phải danh mục lịch sử 2021–2024.

## 12. Từ chiếu rạp đến phát hành số mất bao lâu?

**Lời dẫn:** Biểu đồ tiếp theo cho thấy khoảng cách giữa chiếu rạp và phát hành Digital. Hai mốc này thuộc cùng một phim nhưng có thể cách nhau nhiều ngày. Digital là hình thức phát hành số, có thể gồm thuê hoặc mua phim, nên không đồng nghĩa chỉ xem theo thuê bao. Đây cũng là lý do ta không dùng năm phim trên IMDb thay cho ngày phát hành TMDb. Như vậy, TMDb cung cấp hai góc nhìn: nơi xem và lịch phát hành. Tiếp theo là nguồn ghi nhận một hình thức phân phối khác, các bản chia sẻ qua BitTorrent.

**Cách đọc:** Đọc khoảng cách ngày giữa hai mốc phát hành trong hình. Digital có thể gồm thuê hoặc mua phim, không chỉ xem theo thuê bao.

**Chốt:** Ngày chiếu rạp và ngày phát hành Digital là hai mốc khác nhau của cùng một phim.

**Chuyển:** Một hình thức phân phối khác được ghi nhận trong MagnetDB là gì?

**Lưu ý:** IMDb có năm phim; TMDb có ngày phát hành theo hình thức và quốc gia. Không dùng hai trường này thay thế nhau.

## 13. Trong kho chia sẻ có những loại nội dung nào?

**Lời dẫn:** MagnetDB chứa metadata của các torrent, tức các gói tệp được chia sẻ qua BitTorrent. Kho này không chỉ chứa phim. Sơ đồ cho thấy các nhánh nội dung khác nhau, vì vậy bước đầu là chọn phần liên quan đến phim và nhận diện nó về đúng hồ sơ phim. Chúng tôi đếm các bản chia sẻ được ghi nhận, không đếm số người tải hay người xem. Một câu hỏi cần kiểm tra trước khi phân tích xu hướng là: hệ thống thu thập có hoạt động đều qua thời gian không?

**Cách đọc:** Đọc từ vòng trong ra ngoài để thấy cơ cấu nội dung. Chỉ chỉ vào nhánh video/phim, không giải thích mọi nhánh.

**Chốt:** MagnetDB chứa nhiều loại nội dung; nghiên cứu này chọn phần liên quan đến phim.

**Chuyển:** Việc thu thập có đều qua thời gian không?

**Lưu ý:** Đây là metadata được thu thập; tên và nhãn không xác nhận nội dung thực tế của từng tệp.

## 14. Chọn thời gian quan sát trước khi so sánh

**Lời dẫn:** Số bản ghi theo tháng thay đổi theo hoạt động của hệ thống thu thập. Một tháng ít dữ liệu chưa chắc cộng đồng chia sẻ ít hơn. Vì vậy, bài giữ cửa sổ quan sát của pipeline gốc từ ngày một tháng tư năm hai nghìn không trăm hai mươi mốt đến trước ngày hai mươi chín tháng chín năm hai nghìn không trăm hai mươi bốn. Cửa sổ này vẫn có gián đoạn. Đến đây ta đã hiểu riêng ba nguồn; bước tiếp theo là nối chúng về cùng một bộ phim.

**Cách đọc:** Các điểm là số torrent được hệ thống phát hiện theo tháng. Khoảng giảm mạnh có thể liên quan đến hoạt động thu thập.

**Chốt:** Thu thập không đều; các phân tích chính giới hạn vào cửa sổ quan sát của dự án.

**Chuyển:** Làm sao biết các bản ghi ở ba nguồn thuộc cùng một phim?

**Lưu ý:** Ngày phát hiện không phải ngày đăng. Cửa sổ gốc: 01/04/2021 ≤ ngày phát hiện < 29/09/2024; vẫn có gián đoạn.

## 15. Nối ba nguồn về cùng một bộ phim

**Lời dẫn:** Sơ đồ này là phần cốt lõi của tích hợp. IMDb có mã phim tconst; TMDb có mã tham chiếu imdb_id, nên có thể nối bằng mã. Nhánh MagnetDB khó hơn vì torrent không luôn có mã phim chuẩn. Dự án phải chuẩn hóa tên, đối chiếu năm và bí danh, rồi kiểm tra các cặp không phù hợp. Khi nối được, một dòng phim có thông tin bình chọn, lịch phát hành và số torrent. Cách ghép bổ sung thêm được bao nhiêu dữ liệu so với liên kết có sẵn?

**Cách đọc:** Theo hai đường nối: TMDb có imdb_id; torrent cần chuẩn hóa tên, đối chiếu tên/năm/bí danh và loại các cặp không phù hợp.

**Chốt:** Mã IMDb là điểm nối; nhánh MagnetDB cần nhận diện tên phim và năm.

**Chuyển:** Cách ghép bổ sung được bao nhiêu dữ liệu?

**Lưu ý:** Cùng tên chưa đủ xác nhận cùng phim. Tích hợp cần làm sạch và kiểm tra các cặp ghép.

## 16. Tự ghép tên bổ sung độ phủ của dữ liệu

**Lời dẫn:** Biểu đồ tách các cặp được tìm thấy bằng liên kết có sẵn, bằng tự ghép tên, và bằng cả hai. Phần tự ghép bổ sung nhiều dữ liệu, cho thấy nhận diện thực thể ảnh hưởng trực tiếp tới độ phủ của nghiên cứu. Tuy nhiên, nhiều cặp hơn chưa chứng minh các cặp chính xác hơn; độ chính xác cần được kiểm tra riêng. Sau khi có tập dữ liệu chung, chúng tôi quay lại câu hỏi từ phần IMDb: phim được nhiều người quan tâm có nhiều bản chia sẻ được ghi nhận hơn không?

**Cách đọc:** Màu biểu thị phần chỉ có ở mỗi phương pháp và phần giao nhau. So độ phủ theo thời gian, không đọc thành số người dùng.

**Chốt:** Nhánh tự ghép bổ sung nhiều cặp torrent–phim ngoài các liên kết có sẵn.

**Chuyển:** Sau tích hợp, phim được quan tâm nhiều có nhiều bản chia sẻ hơn không?

**Lưu ý:** Độ phủ tăng không chứng minh độ chính xác tăng. Tổng qua các phim là số cặp torrent–phim.

## 17. Sự quan tâm liên hệ thế nào với số bản chia sẻ?

**Lời dẫn:** Mỗi chấm trên hình là một phim trong mẫu đã ghép, ra năm hai nghìn không trăm hai mươi mốt đến hai nghìn không trăm hai mươi ba và có ít nhất một nghìn lượt bình chọn. Khi lượt bình chọn tăng, số torrent thường cũng tăng. Đường cam mô tả xu hướng này trong thang log. Các chấm lệch khỏi đường nhắc rằng mức độ quan tâm chưa giải thích hết mọi khác biệt; độ phủ ghép cũng có thể làm một phim bị đếm thiếu. Đây là mối liên hệ quan sát, chưa phải nguyên nhân. Chúng tôi tiếp tục xem liệu các thể loại có khác nhau sau khi xét mức độ quan tâm hay không.

**Cách đọc:** Mỗi chấm là một phim. Trục ngang là lượt bình chọn IMDb; trục dọc là số torrent + 1. Hai trục theo thang log. Khoảng cách tới đường mô hình cho thấy ngoại lệ.

**Chốt:** Trong mẫu phim đã ghép, lượt bình chọn cao thường đi cùng nhiều torrent được ghi nhận hơn.

**Chuyển:** Mức độ quan tâm đã giải thích hết khác biệt giữa các phim chưa?

**Lưu ý:** Hình gốc dùng phim 2021–2023 ≥ 1.000 bình chọn trong nhóm đã ghép; dashboard còn giữ phim chưa ghi nhận torrent.

## 18. Thể loại còn khác nhau sau khi xét sự quan tâm?

**Lời dẫn:** Hình này dùng kết quả mô hình ở hình trước. Đường cam bằng một là số torrent mô hình dự đoán từ bình chọn. Trung vị của nhóm Hành động nằm về bên phải, còn Tài liệu nằm về bên trái: trong mẫu, hai nhóm có mức ghi nhận khác nhau so với dự đoán. Hình không đếm số phim của mỗi thể loại, nên không trả lời Chính kịch hay Tài liệu có nhiều phim hơn. Một phim có thể thuộc nhiều thể loại. Ngoài sự quan tâm và thể loại, chúng tôi bổ sung lịch phát hành để xem các bản chia sẻ được phát hiện vào thời điểm nào.

**Cách đọc:** Đường cam ×1 là mức dự đoán. Vạch giữa hộp là trung vị: bên phải ×1 cao hơn dự đoán, bên trái thấp hơn. Chọn Hành động và Tài liệu làm hai ví dụ.

**Chốt:** Một số thể loại có số bản chia sẻ cao hoặc thấp hơn mức mô hình dự đoán từ lượt bình chọn.

**Chuyển:** Ngoài đặc điểm phim, thời điểm phát hành có cung cấp thêm thông tin không?

**Lưu ý:** Đây là so sánh với mô hình, không phải số phim mỗi thể loại. Một phim có thể thuộc nhiều thể loại; chưa chứng minh nguyên nhân.

## 19. Bản WEB được ghi nhận gần mốc Digital đến đâu?

**Lời dẫn:** Ngày không trên hình là ngày Digital tại Mỹ. Cột dương là WEB đầu tiên được ghi nhận sau mốc đó; cột âm là trước mốc đó. Phân bố tập trung gần mốc Digital trong mẫu đang xét. Cần nhớ một phim có thể đã phát hành Digital ở nước khác trước Mỹ, và hệ thống có thể phát hiện muộn hơn ngày đăng. Bộ lọc metadata cũng ảnh hưởng phân bố. Vì vậy, ta chỉ kết luận về thời điểm ghi nhận trong dữ liệu, không khẳng định Digital gây ra chia sẻ. Đây cũng là điểm kết của bài: tích hợp ba nguồn giúp đặt sự quan tâm, thể loại và thời điểm phát hành của cùng một bộ phim vào chung một bối cảnh. Cảm ơn thầy cô và các bạn đã lắng nghe.

**Cách đọc:** Ngày 0 là Digital tại Mỹ; âm là được phát hiện trước mốc đó, dương là sau. Hai cột ngoài cùng gom độ trễ ngoài giới hạn.

**Chốt:** Các bản WEB thường được ghi nhận gần ngày phát hành Digital tại Mỹ trong mẫu đang xét.

**Chuyển:** Kết thúc: cảm ơn và mời câu hỏi.

**Lưu ý:** Mốc Mỹ có thể muộn hơn nước khác; bộ lọc và thời điểm phát hiện ảnh hưởng phân bố. Không suy ra tác động nhân quả.