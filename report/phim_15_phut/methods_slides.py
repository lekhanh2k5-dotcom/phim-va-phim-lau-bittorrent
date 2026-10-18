"""Build processing slides from the saved outputs of notebook 00 (no raw-data run)."""
import hashlib
import html
import json
from html.parser import HTMLParser


class SavedTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None
        self.in_table = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif self.in_table and tag == 'tr':
            self.row = []
        elif self.in_table and tag in ('td', 'th'):
            self.cell = []

    def handle_data(self, value):
        if self.cell is not None:
            self.cell.append(value)

    def handle_endtag(self, tag):
        if self.in_table and tag in ('td', 'th') and self.cell is not None:
            self.row.append(''.join(self.cell).strip())
            self.cell = None
        elif self.in_table and tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif tag == 'table':
            self.in_table = False


def saved_table(notebook, cell_index, required_column):
    cell = notebook['cells'][cell_index]
    for output in cell.get('outputs', []):
        source = output.get('data', {}).get('text/html')
        if not source:
            continue
        parser = SavedTable()
        parser.feed(''.join(source))
        if parser.rows and required_column in parser.rows[0]:
            headers = parser.rows[0]
            return [{k:v for k,v in zip(headers, row) if k}
                    for row in parser.rows[1:] if len(row) == len(headers)]
    raise ValueError(f'Notebook cell {cell_index} has no saved table with {required_column!r}')


def number(value):
    return f'{int(value):,}'.replace(',', '.')


def esc(value):
    return html.escape(str(value), quote=True)


def date_text(value):
    year, month, day = value.split('-')
    return f'{day}/{month}/{year}'


def money_label(value):
    value = float(value)
    scale, unit = (1e9, 'tỷ USD') if value>=1e9 else (1e6, 'triệu USD')
    label = f'{value/scale:.2f}'.rstrip('0').rstrip('.').replace('.',',')
    return f'{label} {unit}'


def build_method_slides(root):
    path = root/'notebooks/00_quy_trinh_xu_ly.ipynb'
    notebook = json.loads(path.read_text(encoding='utf8'))
    tables = {idx:saved_table(notebook, idx, column) for idx, column in [
        (8,'so_file_video_da_ghep'), (10,'ten_chuan_hoa'), (11,'moi_phim_IMDb'),
        (13,'ten_torrent'), (14,'torrent_ghep_duoc'), (16,'tmdb_title'), (17,'nuoc'),
        (20,'precision'), (22,'nguon'), (25,'bi_loai_vi'), (27,'phat_hien'), (32,'cap_torrent_phim_sach')]}
    index, matched, evaluated, clean = (tables[idx][0] for idx in (11,14,20,32))
    facts = {
        'imdb_movies':int(index['moi_phim_IMDb']), 'indexed_names':int(index['so_ten_trong_chi_muc']),
        'matched_rows':int(matched['torrent_ghep_duoc']), 'ambiguous_rows':int(matched['ca_mo_ho_bi_bo']),
        'matched_movies':int(matched['so_phim']), 'evaluation_files':int(evaluated['so_ten_file']),
        'evaluation_precision':float(evaluated['precision']), 'evaluation_recall':float(evaluated['recall']),
        'clean_pairs':int(clean['cap_torrent_phim_sach']), 'clean_torrents':int(clean['so_torrent']),
        'clean_movies':int(clean['so_phim']), 'stable_pairs':int(clean['trong_giai_doan_on_dinh']),
    }
    parasite = next(r for r in tables[13] if r['phim_IMDb']=='Parasite')
    lebowski = next(r for r in tables[10] if r['ten_chuan_hoa']=='el gran lebowski')
    topgun = next(r for r in tables[16] if r['imdb_id']=='tt1745960')
    premiere = next(r for r in tables[17] if r['imdb_id']==topgun['imdb_id'] and r['nuoc']=='US' and r['loai']=='1')
    wrong_year = next(r for r in tables[25] if r['bi_gan_vao']=='Independence Day')
    fake = tables[27][0]
    reference = {'notebook':path.relative_to(root).as_posix(),
        'notebook_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'source_cells':sorted(tables), 'facts':facts,
        'examples':{'alias':lebowski,'match':parasite,'tmdb':topgun,'premiere':premiere,
                    'wrong_year':wrong_year,'implausible':fake}}
    slides = []

    def add(key,title,subtitle,body,notes,reading,finding,caution,next_question,cells):
        slides.append({'kind':'method','method_id':key,'phase':'Tiền xử lý','title':title,
            'subtitle':subtitle,'body':body,'notes':notes,'why':notes,'reading':reading,'finding':finding,
            'limitation':caution,'caution':caution,'next_question':next_question,
            'scope':'Nguồn: notebooks/00_quy_trinh_xu_ly.ipynb · kết quả đã lưu trong notebook.',
            'source_cells':cells})

    add('normalize','Chuẩn hóa dữ liệu và tạo chỉ mục tên phim',
        'Bước 01–03, 10 · Trích phần cần dùng, giữ định danh và đưa tên phim về cùng một dạng.',
        f'''<div class="method-columns">
        <article class="method-card"><span class="method-label">MagnetDB · SQLite 117 GB</span><h3>Lấy metadata cần phân tích</h3>
        <ul><li>Tên torrent, tên file, dung lượng và thời điểm phát hiện.</li><li>Ghép theo <code>torrent_id</code>, chuyển phần trích xuất sang Parquet.</li><li>Sửa tên lỗi mã hóa; giữ dữ liệu gốc để đối chiếu.</li></ul>
        <p class="method-output">Đầu ra: <code>matched_files</code>, <code>magnetdb_matched_slice</code>, <code>mdb_*</code></p></article>
        <article class="method-card"><span class="method-label">IMDb · basics + ratings + akas</span><h3>Một phim có nhiều tên để tra</h3>
        <ul><li>Giữ <code>titleType = movie</code>; nối điểm và bình chọn bằng <code>tconst</code>.</li><li>Thêm tên gốc và tên ở các nước từ <code>title.akas</code>.</li><li>Bỏ dấu, viết thường và bỏ ký tự đặc biệt.</li></ul>
        <p class="method-output"><b>{number(facts['imdb_movies'])}</b> phim · <b>{number(facts['indexed_names'])}</b> tên trong chỉ mục.</p></article></div>
        <div class="method-example"><span class="method-label">Ví dụ tên thay thế trong notebook</span>
        <div class="method-alias"><span>El gran Lebowski</span><span class="method-arrow">→</span><code>{esc(lebowski['ten_chuan_hoa'])}</code><span class="method-arrow">→</span><strong>The Big Lebowski · {esc(lebowski['start_year'])}<small>{esc(lebowski['tconst'])}</small></strong></div>
        <p>Tên thay thế vẫn dẫn về cùng một mã IMDb; chưa cần so khớp gần đúng.</p></div>''',
        'Trước hết, nhóm trích metadata cần dùng từ SQLite thay vì nạp cả cơ sở dữ liệu vào bộ nhớ. Các bản ghi giữ torrent_id để nối tên, file và thời điểm phát hiện. Với IMDb, nhóm giữ phim lẻ, nối điểm và bình chọn bằng tconst, rồi thêm tên ở nhiều quốc gia từ title.akas. Các tên được chuẩn hóa bằng cách bỏ dấu, viết thường và bỏ ký tự đặc biệt. Ví dụ El gran Lebowski tra về The Big Lebowski năm 1998. Chỉ mục có hơn 1,8 triệu tên, nên một phim có thể được tìm qua nhiều tên khác nhau.',
        'Đọc hai cột đầu vào và ví dụ tên thay thế ở cuối. Phân biệt định danh với tên dùng để tra.',
        'Chuẩn hóa tên và bổ sung bí danh giúp ghép được phim mang tên ở ngôn ngữ khác.',
        'Số phim ở đây là toàn danh mục IMDb trong notebook, khác mẫu dashboard có ngưỡng bình chọn.',
        'Sau chuẩn hóa, quy tắc nào quyết định một torrent thuộc phim nào?',[8,10,11])

    precision = str(round(facts['evaluation_precision']*100,1)).replace('.',',')
    recall = str(round(facts['evaluation_recall']*100,1)).replace('.',',')
    add('matching','Ghép chính xác tên chuẩn hóa + năm; bỏ ca mơ hồ',
        'Bước 04, 08 · Nhánh ghép tên chính dùng chỉ mục IMDb; một pipeline khác được dùng để đối chiếu.',
        f'''<ol class="method-flow"><li><b>01 · Làm sạch tên</b><span>Bỏ tiền tố trang, đuôi file; loại dấu hiệu phim bộ.</span></li>
        <li><b>02 · Tách tên + năm</b><span>Lấy tên trước năm; không nhầm 1080p với năm phim.</span></li>
        <li><b>03 · Tra chính xác</b><span>Tên chuẩn hóa trùng chỉ mục; năm lệch tối đa ±1.</span></li>
        <li><b>04 · Bỏ mơ hồ</b><span>Nhiều phim trùng tên hoặc tên quá chung chung.</span></li></ol>
        <div class="method-example method-match-example"><span class="method-label">Ví dụ ghép thật</span><code class="method-raw-name">{esc(parasite['ten_torrent'])}</code>
        <div class="method-alias"><span>parasite + {esc(parasite['nam'])}</span><span class="method-arrow">→</span><strong>{esc(parasite['phim_IMDb'])} ({esc(parasite['start_year'])})</strong></div></div>
        <div class="method-metrics"><div><strong>{number(facts['matched_rows'])}</strong><span>dòng ghép ban đầu</span></div><div><strong>{number(facts['ambiguous_rows'])}</strong><span>ca mơ hồ bị bỏ</span></div><div><strong>{number(facts['matched_movies'])}</strong><span>phim sau loại mơ hồ</span></div></div>
        <p class="method-audit"><b>Đối chiếu độc lập:</b> guessit + rapidfuzz trên {number(facts['evaluation_files'])} tên file, so với nhãn MagnetDB: precision <b>{precision}%</b>, recall <b>{recall}%</b>. Đây là phép đối chiếu tham chiếu, không phải tỷ lệ đúng của toàn bộ pipeline chính.</p>''',
        'Nhánh ghép tên chính bỏ tiền tố rác, tách năm và phần tên đứng trước năm, rồi tra chính xác tên đã chuẩn hóa trong chỉ mục IMDb. Năm cho phép lệch một đơn vị. Những tên trùng nhiều phim hoặc quá chung chung được đánh dấu mơ hồ và bỏ. Notebook ghi nhận hơn 2,25 triệu dòng ghép ban đầu, trong đó gần 194 nghìn ca mơ hồ. Để đối chiếu, bước tám chạy riêng guessit và rapidfuzz trên 20 nghìn tên file, so với nhãn MagnetDB. Các chỉ số precision và recall của phép đối chiếu này không được coi là độ chính xác của toàn bộ nhánh ghép chính.',
        'Theo bốn bước từ trái sang phải, đọc ví dụ Parasite và phân biệt nhánh tra chính xác với phép đối chiếu gần đúng.',
        'Ghép tên có ràng buộc năm và cơ chế từ chối; không nhận mọi tên giống nhau thành cùng một phim.',
        'Nhãn MagnetDB có lỗi. Precision/recall là kết quả đối chiếu trên mẫu 20.000 file, không phải kiểm định thủ công toàn tập.',
        'Khi đã nhận diện được phim, TMDb bổ sung thông tin bằng khóa nào?',[13,14,20])

    add('tmdb','Bổ sung TMDb bằng mã IMDb, rồi tách thành 3 bảng',
        'Bước 05–07 · Hợp danh sách phim → tìm TMDb theo imdb_id → lưu đệm JSON → xuất Parquet.',
        f'''<div class="method-keyflow"><code>IMDb · tconst</code><span>→</span><code>TMDb · /find</code><span>→</span><span>JSON lưu đệm</span><span>→</span><strong>3 bảng theo mức chi tiết</strong></div>
        <div class="method-columns method-three">
        <article class="method-card"><span class="method-label">1 dòng / phim</span><h3><code>tmdb_movies</code></h3><p>Ngân sách, doanh thu, ngôn ngữ và các mốc phát hành tóm tắt.</p><div class="method-data-example"><b>{esc(topgun['tmdb_title'])}</b><span>{esc(topgun['imdb_id'])}</span><span>Ngân sách: {money_label(topgun['budget'])}</span><span>Doanh thu: khoảng {money_label(topgun['revenue'])}</span></div></article>
        <article class="method-card"><span class="method-label">Nhiều dòng / phim</span><h3><code>tmdb_release_dates</code></h3><p>Ngày phát hành theo quốc gia và hình thức: Premiere, rạp, Digital, đĩa, TV.</p><div class="method-data-example"><b>Cùng phim · thị trường Mỹ</b><span><code>country = US</code> · <code>type = 1</code></span><span>Premiere: {date_text(premiere['ngay'])}</span><span>Mỗi hình thức có mốc riêng.</span></div></article>
        <article class="method-card"><span class="method-label">Phim × nước × hình thức × dịch vụ</span><h3><code>tmdb_watch_providers</code></h3><p>Nơi xem theo quốc gia; phân biệt thuê bao, miễn phí, quảng cáo, thuê và mua.</p><div class="method-data-example"><b>Cùng phim · nơi xem tại Mỹ</b><span>{esc(topgun['us_streaming_providers'].split(',')[0])} và các dịch vụ khác.</span><span>Ảnh chụp năm 2026.</span><span>Không phải danh mục lúc phim ra mắt.</span></div></article></div>
        <p class="method-audit"><b>Khi gộp về một phim:</b> tổng hợp ngày và nơi xem trước khi nối; không nhân số phim theo số dòng phát hành. Digital có thể gồm thuê/mua, không đồng nghĩa thuê bao.</p>''',
        'Sau khi có mã IMDb, nhóm hợp danh sách phim rồi tìm mã TMDb qua endpoint find. Phản hồi JSON được lưu đệm để có thể chạy tiếp mà không tải lại. Bước bảy tách thành ba bảng có mức chi tiết khác nhau: một dòng thông tin phim, nhiều mốc phát hành theo nước và loại, và nơi xem theo nước cùng dịch vụ. Ví dụ Top Gun có mốc Premiere tại Mỹ khác các mốc ra rạp hoặc Digital. Khi tạo bảng phân tích theo phim, phải tổng hợp các bảng nhiều dòng trước khi nối. Nơi xem là ảnh chụp năm 2026, không phải lịch sử danh mục.',
        'Theo đường mã IMDb tới ba bảng. Đọc dòng mô tả mức chi tiết trên mỗi bảng và ví dụ Top Gun.',
        'Nối bằng mã phim; giữ riêng ngày phát hành lịch sử và nơi xem tại thời điểm thu thập.',
        'Các số liệu tiền chỉ minh họa hồ sơ Top Gun trong notebook; nơi xem có thể khác thời điểm ra mắt.',
        'Ghép được chưa đủ: những bản ghi nào còn cần bị loại hoặc gắn cờ?',[16,17])

    add('cleaning','Bộ lọc A–J xử lý những lỗi nào?',
        'Bước 09 · Kiểm tra nội dung, danh tính phim, sự nhất quán giữa nguồn và các mốc thời gian.',
        f'''<div class="method-columns method-clean-columns"><article class="method-card"><h3>Năm nhóm kiểm tra</h3>
        <dl class="method-rules"><div><dt>A–C</dt><dd>Chỉ phim lẻ; bỏ tập phim bộ và file dưới 100 MB.</dd></div>
        <div><dt>D–E2</dt><dd>Kiểm tra năm, độ giống tên và đúng phần phim.</dd></div>
        <div><dt>F</dt><dd>Bỏ torrent sớm hơn lần ra mắt đầu tiên trên 60 ngày.</dd></div>
        <div><dt>G–I</dt><dd>Bỏ ghép mâu thuẫn, dấu hiệu phim bộ và năm lệch.</dd></div>
        <div><dt>J</dt><dd>Gắn cờ bản WEB/BluRay có thời điểm khó hợp lý; loại cờ này khi phân tích.</dd></div></dl></article>
        <article class="method-card"><h3>Ba ví dụ bị loại trong notebook</h3><div class="method-error-example"><b>B · Nhầm phim bộ thành phim lẻ</b><p><code>…S03E01…</code> bị gán vào <i>A Series of Unfortunate Events</i> (2004).</p></div>
        <div class="method-error-example"><b>D · Tên đúng, năm sai</b><p><i>Independence Day</i> · tên file <b>{esc(wrong_year['nam_trong_ten'])}</b> nhưng phim được gán là <b>{esc(wrong_year['nam_phim'])}</b>.</p></div>
        <div class="method-error-example"><b>J · Tự xưng BluRay trước ngày ra mắt</b><p><i>Ant-Man and the Wasp: Quantumania</i><br>Phát hiện <b>{date_text(fake['phat_hien'])}</b> · ra rạp <b>{date_text(fake['ra_rap'])}</b>.</p></div></article></div>
        <p class="method-audit"><b>Có thể truy vết:</b> số lượng còn lại được ghi trong <code>cleaning_log.csv</code>; bảng torrent giữ các cờ như <code>is_pack</code>, <code>quality_tier</code> và <code>implausible</code>.</p>''',
        'Làm sạch gồm nhiều phép kiểm tra có mục tiêu khác nhau. A đến C loại nội dung không phải phim lẻ và các tệp quá nhỏ. D đến E2 kiểm tra năm, tên và số phần. F kiểm tra torrent quá sớm so với lần ra mắt, còn G đến I kiểm tra mâu thuẫn giữa hai nguồn và dấu hiệu phim bộ. J gắn cờ các bản phát hành có thời điểm khó hợp lý. Ba ví dụ trong notebook gồm tập S03E01 bị gán vào phim lẻ, Independence Day năm 2016 bị gán cho phim 1996, và một bản tự xưng BluRay xuất hiện trước khi Ant-Man ra rạp. Các bước đều để lại nhật ký hoặc cờ để truy vết.',
        'Đọc nhóm quy tắc bên trái, rồi nối ba ví dụ bên phải với bộ lọc B, D và J.',
        'Làm sạch kiểm tra cả nội dung và danh tính phim; có cờ và nhật ký để kiểm tra lại.',
        'implausible là cờ suy ra từ metadata và thời điểm; không xác minh nội dung của tệp.',
        'Sau làm sạch, dữ liệu có đơn vị gì và cửa sổ phân tích được chọn ra sao?',[22,25,27])

    add('outputs','Chốt hai bảng sạch, phân biệt đơn vị và thời gian',
        'Đầu ra bước 09 · Một bảng theo cặp torrent–phim và một bảng tổng hợp theo phim.',
        f'''<div class="method-columns"><article class="method-card"><span class="method-label">1 dòng = 1 cặp torrent–phim</span><h3><code>torrents_clean</code></h3><p>Mã torrent + IMDb; nguồn ghép, chất lượng, cờ gói nhiều phim, cờ bất thường và ngày phát hiện UTC.</p><p class="method-output">Số cặp có thể lớn hơn số torrent vì một gói chứa nhiều phim.</p></article>
        <article class="method-card"><span class="method-label">1 dòng = 1 phim</span><h3><code>movie_analysis</code></h3><p>Hồ sơ IMDb + TMDb và thống kê torrent theo phim trong cửa sổ quan sát.</p><p class="method-output">Đếm torrent riêng biệt theo phim trước khi tính chỉ số so sánh.</p></article></div>
        <div class="method-metrics method-four"><div><strong>{number(facts['clean_pairs'])}</strong><span>cặp sạch · toàn phạm vi</span></div><div><strong>{number(facts['clean_torrents'])}</strong><span>torrent riêng biệt · toàn phạm vi</span></div><div><strong>{number(facts['clean_movies'])}</strong><span>phim có cặp sạch · toàn phạm vi</span></div><div class="method-highlight"><strong>{number(facts['stable_pairs'])}</strong><span>cặp trong cửa sổ quan sát</span></div></div>
        <div class="method-window"><b>Cửa sổ thống kê chính · UTC</b><code>01/04/2021 ≤ ngày phát hiện &lt; 29/09/2024</code><span>Chọn giai đoạn thu thập ổn định hơn; vẫn có gián đoạn.</span></div>
        <div class="method-clocks"><span><b>IMDb</b> · năm phim</span><span><b>TMDb</b> · ngày phát hành theo nước/loại</span><span><b>MagnetDB</b> · ngày hệ thống phát hiện</span></div>
        <p class="method-footnote">Các số đếm sạch loại <code>implausible</code>. Ngày phát hiện không phải ngày tạo torrent; điểm và nơi xem là ảnh chụp năm 2026.</p>''',
        'Cuối cùng, torrents_clean có một dòng cho một cặp torrent và phim, còn movie_analysis tổng hợp thành một dòng cho mỗi phim. Notebook ghi nhận 2.078.927 cặp sạch, tương ứng 2.066.598 torrent riêng biệt và 126.081 phim trên toàn phạm vi. Khi giới hạn ngày phát hiện từ 1 tháng 4 năm 2021 đến trước 29 tháng 9 năm 2024, còn 923.998 cặp. Cần tách năm phim IMDb, ngày phát hành TMDb và ngày hệ thống phát hiện torrent; đây là ba mốc khác nhau. Đếm bản ghi chia sẻ không cho biết lượt tải. Với dữ liệu đã được hình thành như vậy, chúng tôi bắt đầu nhìn riêng từng nguồn.',
        'So sánh mức chi tiết của hai bảng, ba số đếm toàn phạm vi và số cặp trong cửa sổ được tô màu.',
        'Đơn vị đếm và cửa sổ quan sát quyết định con số; không trộn cặp torrent–phim với torrent riêng biệt.',
        'Cửa sổ vẫn có gián đoạn thu thập. Danh mục dashboard còn áp dụng bộ lọc năm, người lớn và bình chọn riêng.',
        'Bắt đầu với IMDb: quy mô kho phim và sự quan tâm của khán giả thay đổi thế nào?',[29,31,32])
    return slides, reference


def render_method_slide(slide):
    return (f'<p class="method-subtitle">{esc(slide["subtitle"])}</p>'
            f'<div class="method-content method-{esc(slide["method_id"])}">{slide["body"]}</div>'
            '<p class="method-source">Nguồn: notebook 00_quy_trinh_xu_ly · số liệu và ví dụ từ kết quả đã lưu.</p>')
