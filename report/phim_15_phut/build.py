"""Build offline slides and dashboard from the original three-source project."""
import argparse
import base64
import html
import json
import shutil
from pathlib import Path

import duckdb

try:
    from .methods_slides import build_method_slides, render_method_slide
except ImportError:
    from methods_slides import build_method_slides, render_method_slide

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSETS = HERE / 'assets'
ASSETS.mkdir(exist_ok=True)

def json_text(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('</', '<\\/')

def export_data():
    con = duckdb.connect()
    con.execute(f"CREATE VIEW i AS SELECT * FROM read_parquet('{ROOT.as_posix()}/data_clean/imdb_movies_all.parquet')")
    con.execute(f"CREATE VIEW m AS SELECT * FROM read_parquet('{ROOT.as_posix()}/data_clean/movie_analysis.parquet')")
    con.execute(f"CREATE VIEW t AS SELECT * FROM read_parquet('{ROOT.as_posix()}/data_clean/tmdb_movies.parquet')")
    con.execute(f"CREATE VIEW tor AS SELECT * FROM read_parquet('{ROOT.as_posix()}/data_clean/torrents_clean.parquet')")
    # Same recorded observation window and cleaning as the original project.
    con.execute("""CREATE TEMP TABLE web AS SELECT imdb_id, min(discovered_at_utc)::DATE AS first_web
        FROM tor WHERE NOT implausible AND in_stable_window AND quality_tier='web' GROUP BY 1""")
    sql = """SELECT i.tconst, i.title, i.start_year, i.genres, i.avg_rating, i.num_votes,
        coalesce(m.n_torrents_stable,0), coalesce(t.tmdb_found,false),
        CASE WHEN t.tmdb_found THEN t.us_streaming_now ELSE NULL END,
        CASE WHEN t.tmdb_found THEN t.n_countries_streaming ELSE NULL END,
        t.us_streaming_providers, t.us_theatrical::DATE::VARCHAR, t.us_digital::DATE::VARCHAR,
        web.first_web::VARCHAR, date_diff('day',t.us_digital::DATE,web.first_web),
        m.imdb_id IS NOT NULL, nullif(split_part(t.origin_country,',',1),''),
        year(t.release_date), t.budget, t.revenue
        FROM i LEFT JOIN m ON i.tconst=m.imdb_id LEFT JOIN t ON i.tconst=t.imdb_id
        LEFT JOIN web ON i.tconst=web.imdb_id
        WHERE NOT i.is_adult AND i.start_year BETWEEN 1920 AND 2024 AND i.num_votes>=1000
        ORDER BY i.num_votes DESC, i.tconst"""
    rows = [list(r) for r in con.execute(sql).fetchall()]
    assert len(rows) == len({r[0] for r in rows})
    # Alternate names for search only: IMDb original title plus Vietnamese (region VN) akas.
    con.execute("CREATE TEMP TABLE ids AS SELECT unnest(?) AS tconst", [[r[0] for r in rows]])
    alt = dict(con.execute(f"""SELECT tconst, string_agg(DISTINCT name, ' · ') FROM (
        SELECT tconst, original_title AS name FROM i WHERE tconst IN (SELECT tconst FROM ids) AND original_title<>title
        UNION SELECT a.titleId, a.title FROM read_csv('{ROOT.as_posix()}/data_raw/imdb/title.akas.tsv.gz',
            delim='\t', quote='', header=true, all_varchar=true) a
        JOIN ids ON ids.tconst=a.titleId WHERE a.region='VN')
        GROUP BY 1""").fetchall())
    for r in rows:
        r.append(alt.get(r[0]))
    keys = ['id','title','year','genres','rating','votes','torrents','tmdb','streaming',
            'countries','providers','theatrical','digital','web','lag','matched',
            'origin','tmdb_year','budget','revenue','alt']
    # Compact, deduplicated facts for interactive country and access-mode selection.
    # Movie indices use exactly the same ordering as the IMDb-led export above.
    con.execute("""CREATE TEMP TABLE eligible AS
        SELECT tconst AS imdb_id,
            (row_number() OVER (ORDER BY num_votes DESC,tconst)-1)::INTEGER AS movie_index
        FROM i WHERE NOT is_adult AND start_year BETWEEN 1920 AND 2024 AND num_votes>=1000""")
    release_facts = con.execute(f"""SELECT e.movie_index,r.country,
        CASE WHEN r.type IN (2,3) THEN 0 WHEN r.type=4 THEN 1
             WHEN r.type=5 THEN 2 WHEN r.type=6 THEN 3 ELSE 4 END AS mode,
        date_diff('day',DATE '1970-01-01',min(r.release_date)::DATE)::INTEGER AS day
        FROM read_parquet('{ROOT.as_posix()}/data_clean/tmdb_release_dates.parquet') r
        JOIN eligible e USING(imdb_id)
        WHERE r.release_date IS NOT NULL AND r.country IS NOT NULL AND r.type BETWEEN 1 AND 6
        GROUP BY 1,2,3 ORDER BY 1,2,3""").fetchall()
    countries = sorted({r[1] for r in release_facts})
    country_index = {v:k for k,v in enumerate(countries)}
    releases = {'countries':countries, 'modes':['theatrical','digital','physical','tv','premiere'],
        'columns':['movie_index','country_index','mode_index','days_since_1970'],
        'rows':[[m,country_index[c],mode,day] for m,c,mode,day in release_facts]}
    watch_facts = con.execute(f"""SELECT DISTINCT e.movie_index,p.kind,p.provider
        FROM read_parquet('{ROOT.as_posix()}/data_clean/tmdb_watch_providers.parquet') p
        JOIN eligible e USING(imdb_id) WHERE p.country='US'
        AND p.kind IN ('flatrate','free','ads','rent','buy') ORDER BY 1,2,3""").fetchall()
    provider_names = sorted({r[2] for r in watch_facts})
    provider_index = {v:k for k,v in enumerate(provider_names)}
    watch_kinds = ['flatrate','free','ads','rent','buy']
    watch = {'country':'US','providers':provider_names,'kinds':watch_kinds,
        'columns':['movie_index','kind_index','provider_index'],
        'rows':[[m,watch_kinds.index(k),provider_index[p]] for m,k,p in watch_facts]}
    # Reproduce the three notebook samples without embedding the full TMDb catalog.
    origin_counts = con.execute("""SELECT split_part(t.origin_country,',',1) AS country,count(*) AS n
        FROM t JOIN i ON i.tconst=t.imdb_id WHERE t.tmdb_found AND NOT i.is_adult
        AND year(t.release_date) BETWEEN 2000 AND 2024
        AND nullif(split_part(t.origin_country,',',1),'') IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC,1""").fetchall()
    origin_missing = con.execute("""SELECT count(*) FROM t JOIN i ON i.tconst=t.imdb_id
        WHERE t.tmdb_found AND NOT i.is_adult AND year(t.release_date) BETWEEN 2000 AND 2024
        AND nullif(split_part(t.origin_country,',',1),'') IS NULL""").fetchone()[0]
    finance_keys = ['id','title','year','genres','rating','votes','origin','tmdb_year','budget','revenue','theatrical']
    finance_rows = [list(r) for r in con.execute("""SELECT i.tconst,coalesce(t.tmdb_title,i.title),
        i.start_year,i.genres,i.avg_rating,i.num_votes,nullif(split_part(t.origin_country,',',1),''),
        year(t.release_date),t.budget,t.revenue,t.us_theatrical::DATE::VARCHAR
        FROM t JOIN i ON i.tconst=t.imdb_id WHERE t.tmdb_found AND NOT i.is_adult
        AND t.budget>=1000000 AND t.revenue>=10000 AND year(t.release_date) BETWEEN 1980 AND 2024
        ORDER BY i.tconst""").fetchall()]
    business = {'original_origin':{'rows':[list(r) for r in origin_counts],'missing':origin_missing},
        'original_finance':{'columns':finance_keys,'rows':finance_rows},
        'method':{'origin_year_min':2000,'origin_year_max':2024,'finance_year_min':1980,'finance_year_max':2024,
            'budget_min':1000000,'revenue_min':10000,'blockbuster_revenue_min':300000000,'reference_ratio':2.5}}
    stats = {
        'catalog': con.execute('SELECT count(*) FROM i WHERE NOT is_adult').fetchone()[0],
        'tmdb_found': con.execute('SELECT count(*) FROM t WHERE tmdb_found').fetchone()[0],
        'matched_movies': con.execute('SELECT count(*) FROM m WHERE NOT is_adult').fetchone()[0],
        'eligible_movies': len(rows),
        'pairs': con.execute('SELECT count(*) FROM tor WHERE NOT implausible AND in_stable_window').fetchone()[0],
        'distinct_torrents': con.execute('SELECT count(DISTINCT torrent_id) FROM tor WHERE NOT implausible AND in_stable_window').fetchone()[0],
    }
    payload = {'columns': keys, 'rows': rows, 'stats': stats, 'releases':releases, 'watch':watch,'business':business,
        'method': {'year_min':1920,'year_max':2024,'votes_min':1000,
          'observed_start':'2021-04-01', 'observed_end_exclusive':'2024-09-29',
          'snapshot_label':'2026 (theo tài liệu dự án)',
          'release_cutoff':'2026-10-18',
          'unit':'Số torrent riêng biệt theo từng phim; tổng qua phim là số cặp torrent–phim.',
          'zero':'Không ghi nhận trong dữ liệu đã ghép và làm sạch; không khẳng định phim không được chia sẻ.',
          'lag':'Ngày phát hiện bản WEB đầu tiên trong cửa sổ quan sát trừ ngày Digital tại Mỹ.'}}
    (HERE/'data.json').write_text(json_text(payload), encoding='utf8')
    defaults = [r for r in rows if 2021 <= r[2] <= 2023]
    checks = {'eligible_movies':len(rows),'default_movies':len(defaults),
        'default_pairs':sum(r[6] for r in defaults),'default_unobserved':sum(r[6]==0 for r in defaults),
        'default_tmdb':sum(r[7] for r in defaults),'unique_ids':True,
        'default_votes':sum(r[5] for r in defaults),
        'release_facts':len(release_facts),'us_watch_facts':len(watch_facts),
        'release_countries':len(countries), 'watch_country':'US',
        'original_origin_movies':sum(r[1] for r in origin_counts),'original_finance_movies':len(finance_rows)}
    (HERE/'data_validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2), encoding='utf8')
    return payload

def build_slides():
    original = json.loads((ROOT/'report/thuyet_trinh_ba_nguon/mach_trinh_bay.json').read_text(encoding='utf8'))
    by_image = {s.get('image'):s for s in original if s.get('image')}
    slides = []
    method_slides, method_reference = build_method_slides(ROOT)
    (HERE/'methods_reference.json').write_text(json.dumps(method_reference,ensure_ascii=False,indent=2),encoding='utf8')
    narration = {
      '6_integration/01_cleaning_funnel': 'Hình này minh họa cụ thể các bước làm sạch vừa giới thiệu. Cụm xanh dương bên trái là nhánh dùng mã IMDb có sẵn trong MagnetDB; nhiều bản ghi bị loại sau khi kiểm tra loại nội dung, dung lượng, tên và năm. Cụm cam ở giữa là nhánh tự ghép tên torrent với IMDb, sau đó bỏ các trường hợp mơ hồ. Cụm xanh lá bên phải là hợp hai nguồn rồi áp dụng các bộ lọc chung. Không cộng trực tiếp hai nhánh vì chúng có phần giao nhau. Mỗi cụm dùng thang riêng, nên đọc nhãn số thay vì so chiều dài thanh giữa các cụm. Đây là phễu làm sạch trên phạm vi dữ liệu gốc, trước khi giới hạn cửa sổ quan sát của dashboard. Tiếp theo, chúng tôi đi vào từng thao tác chuẩn hóa, ghép thực thể và kiểm tra dữ liệu.',
      '1_imdb/01_movies_per_year': 'Trước tiên, chúng tôi nhìn riêng vào IMDb. Hình này đếm các bản ghi phim theo năm. Quy mô danh mục tăng ở nhiều giai đoạn gần đây, nhưng cần nhớ IMDb không phải một cuộc tổng điều tra sản lượng phim toàn cầu. Điều quan trọng ở đây là các năm có quy mô khác nhau, nên khi đối chiếu các nhóm phim, ta cần giữ khoảng năm rõ ràng. Với một danh mục lớn như vậy, câu hỏi tiếp theo là: sự chú ý của người dùng có phân bố đều giữa các phim không?',
      '1_imdb/06_votes_lorenz': 'Hình thứ hai trả lời câu hỏi về sự chú ý. Chúng tôi xếp phim từ ít đến nhiều lượt bình chọn. Nếu mọi phim nhận số bình chọn như nhau thì kết quả nằm trên đường chéo. Đường thực tế cong mạnh: trong nhóm có đánh giá, khoảng một phần trăm phim nhiều bình chọn nhất chiếm sáu mươi chín phần trăm tổng lượt bình chọn. Vì vậy, bình chọn là một góc nhìn hữu ích về mức độ quan tâm, dù không phải lượt xem. Nhưng được quan tâm chưa cho biết phim có thể được xem ở đâu.',
      '3_tmdb_streaming/01_world_catalog_map': 'Chuyển sang TMDb, chúng tôi xem riêng khả năng tiếp cận phim hợp pháp. Bản đồ cho thấy số phim có nơi xem được ghi nhận khác nhau giữa các quốc gia. Chỉ cần đối chiếu vài vùng theo chú giải để thấy danh mục không đồng nhất. Đây là dữ liệu nơi xem do JustWatch cung cấp qua TMDb, tại thời điểm thu thập năm hai nghìn không trăm hai mươi sáu. Nó chưa phản ánh danh mục của từng quốc gia trong quá khứ. Ngoài khác biệt về địa điểm, khán giả còn có thể tiếp cận một phim ở những thời điểm khác nhau.',
      '2_tmdb/04_theatrical_window': 'Biểu đồ tiếp theo cho thấy khoảng cách giữa chiếu rạp và phát hành Digital. Hai mốc này thuộc cùng một phim nhưng có thể cách nhau nhiều ngày. Digital là hình thức phát hành số, có thể gồm thuê hoặc mua phim, nên không đồng nghĩa chỉ xem theo thuê bao. Đây cũng là lý do ta không dùng năm phim trên IMDb thay cho ngày phát hành TMDb. Như vậy, TMDb cung cấp hai góc nhìn: nơi xem và lịch phát hành. Tiếp theo là nguồn ghi nhận một hình thức phân phối khác, các bản chia sẻ qua BitTorrent.',
      '4_magnetdb/01_content_sunburst': 'MagnetDB chứa metadata của các torrent, tức các gói tệp được chia sẻ qua BitTorrent. Kho này không chỉ chứa phim. Sơ đồ cho thấy các nhánh nội dung khác nhau, vì vậy bước đầu là chọn phần liên quan đến phim và nhận diện nó về đúng hồ sơ phim. Chúng tôi đếm các bản chia sẻ được ghi nhận, không đếm số người tải hay người xem. Một câu hỏi cần kiểm tra trước khi phân tích xu hướng là: hệ thống thu thập có hoạt động đều qua thời gian không?',
      '4_magnetdb/03_crawler_coverage': 'Số bản ghi theo tháng thay đổi theo hoạt động của hệ thống thu thập. Một tháng ít dữ liệu chưa chắc cộng đồng chia sẻ ít hơn. Vì vậy, bài giữ cửa sổ quan sát của pipeline gốc từ ngày một tháng tư năm hai nghìn không trăm hai mươi mốt đến trước ngày hai mươi chín tháng chín năm hai nghìn không trăm hai mươi bốn. Cửa sổ này vẫn có gián đoạn. Đến đây ta đã hiểu riêng ba nguồn; bước tiếp theo là nối chúng về cùng một bộ phim.',
      '5_combined/01_integration_diagram': 'Sơ đồ này là phần cốt lõi của tích hợp. IMDb có mã phim tconst; TMDb có mã tham chiếu imdb_id, nên có thể nối bằng mã. Nhánh MagnetDB khó hơn vì torrent không luôn có mã phim chuẩn. Dự án phải chuẩn hóa tên, đối chiếu năm và bí danh, rồi kiểm tra các cặp không phù hợp. Khi nối được, một dòng phim có thông tin bình chọn, lịch phát hành và số torrent. Cách ghép bổ sung thêm được bao nhiêu dữ liệu so với liên kết có sẵn?',
      '6_integration/02_coverage_by_source': 'Biểu đồ tách các cặp được tìm thấy bằng liên kết có sẵn, bằng tự ghép tên, và bằng cả hai. Phần tự ghép bổ sung nhiều dữ liệu, cho thấy nhận diện thực thể ảnh hưởng trực tiếp tới độ phủ của nghiên cứu. Tuy nhiên, nhiều cặp hơn chưa chứng minh các cặp chính xác hơn; độ chính xác cần được kiểm tra riêng. Sau khi có tập dữ liệu chung, chúng tôi quay lại câu hỏi từ phần IMDb: phim được nhiều người quan tâm có nhiều bản chia sẻ được ghi nhận hơn không?',
      '7_piracy_movies/02_popularity_vs_piracy': 'Mỗi chấm trên hình là một phim trong mẫu đã ghép, ra năm hai nghìn không trăm hai mươi mốt đến hai nghìn không trăm hai mươi ba và có ít nhất một nghìn lượt bình chọn. Khi lượt bình chọn tăng, số torrent thường cũng tăng. Đường cam mô tả xu hướng này trong thang log. Các chấm lệch khỏi đường nhắc rằng mức độ quan tâm chưa giải thích hết mọi khác biệt; độ phủ ghép cũng có thể làm một phim bị đếm thiếu. Đây là mối liên hệ quan sát, chưa phải nguyên nhân. Chúng tôi tiếp tục xem liệu các thể loại có khác nhau sau khi xét mức độ quan tâm hay không.',
      '7_piracy_movies/03_genre_piracy_ratio': 'Hình này dùng kết quả mô hình ở hình trước. Đường cam bằng một là số torrent mô hình dự đoán từ bình chọn. Trung vị của nhóm Hành động nằm về bên phải, còn Tài liệu nằm về bên trái: trong mẫu, hai nhóm có mức ghi nhận khác nhau so với dự đoán. Hình không đếm số phim của mỗi thể loại, nên không trả lời Chính kịch hay Tài liệu có nhiều phim hơn. Một phim có thể thuộc nhiều thể loại. Ngoài sự quan tâm và thể loại, chúng tôi bổ sung lịch phát hành để xem các bản chia sẻ được phát hiện vào thời điểm nào.',
      '7_piracy_movies/07_web_lag': 'Ngày không trên hình là ngày Digital tại Mỹ. Cột dương là WEB đầu tiên được ghi nhận sau mốc đó; cột âm là trước mốc đó. Phân bố tập trung gần mốc Digital trong mẫu đang xét. Cần nhớ một phim có thể đã phát hành Digital ở nước khác trước Mỹ, và hệ thống có thể phát hiện muộn hơn ngày đăng. Bộ lọc metadata cũng ảnh hưởng phân bố. Vì vậy, ta chỉ kết luận về thời điểm ghi nhận trong dữ liệu, không khẳng định Digital gây ra chia sẻ. Đây cũng là điểm kết của bài: tích hợp ba nguồn giúp đặt sự quan tâm, thể loại và thời điểm phát hành của cùng một bộ phim vào chung một bối cảnh. Cảm ơn thầy cô và các bạn đã lắng nghe.'
    }
    def concept(title,subtitle,cards,notes,kind='concept',phase='Mở đầu',steps=None,result=None):
        slides.append(dict(title=title,subtitle=subtitle,cards=cards,notes=notes,kind=kind,phase=phase,
                           steps=steps or [],result=result))
    def chart(image,phase,title,finding,next_question,reading,caution):
        s=by_image['plots/'+image+'.png'].copy()
        s.update(phase=phase,title=title,finding=finding,next_question=next_question,reading=reading,
                 caution=caution,why=narration[image])
        slides.append(s)
    concept('Một bộ phim. Ba góc nhìn.',
        'Sự quan tâm của khán giả, khả năng tiếp cận và các bản chia sẻ trên BitTorrent liên hệ thế nào?',
        [('IMDb','Phim & sự quan tâm'),('TMDb / JustWatch','Phát hành & nơi xem'),('MagnetDB','Các bản chia sẻ được ghi nhận')],
        'Trong bài này, chúng tôi theo dõi một bộ phim qua ba góc nhìn: người dùng quan tâm ra sao, phim được phát hành khi nào và hệ thống ghi nhận những bản chia sẻ nào. Chúng tôi sẽ phân tích riêng từng nguồn, sau đó nối chúng để trả lời ba câu hỏi chung.','hero')
    concept('Ba nguồn dữ liệu và bước tiền xử lý',
        'Mỗi nguồn trả lời một phần câu hỏi; tiền xử lý đưa ba nguồn về cùng một bộ phim.',
        [('IMDb','Hồ sơ phim: tên, năm, thể loại, điểm và lượt bình chọn. Lượt bình chọn là chỉ báo sự quan tâm.'),
         ('TMDb / JustWatch','Ngày phát hành và nơi xem hợp pháp. Thông tin nơi xem trong TMDb do JustWatch cung cấp.'),
         ('MagnetDB','Metadata các gói tệp chia sẻ qua BitTorrent. Đếm bản chia sẻ, không đếm người tải hoặc người xem.')],
        'IMDb giống một danh mục phim có đánh giá của người dùng. TMDb bổ sung lịch phát hành và nơi xem. BitTorrent là cách chia sẻ tệp giữa nhiều máy tính; MagnetDB ghi nhận metadata các bản chia sẻ đó. '
        'Trước khi phân tích, dữ liệu đi qua năm bước tiền xử lý. Một, chỉ giữ phim lẻ, bỏ phim người lớn và tập phim bộ. Hai, chuẩn hóa tên phim: bỏ dấu, chữ thường, thêm tên phim theo từng nước. '
        'Ba, ghép thực thể: tách tên và năm từ tên torrent rồi đối chiếu với IMDb; TMDb nối qua mã IMDb. Bốn, làm sạch: bỏ tệp nhỏ, năm lệch, ca trùng tên và torrent giả. '
        'Năm, chỉ giữ giai đoạn thu thập ổn định từ tháng tư năm hai nghìn không trăm hai mươi mốt đến tháng chín năm hai nghìn không trăm hai mươi bốn.',
        steps=[('Lọc phim','Chỉ phim lẻ; bỏ phim người lớn, tập phim bộ, sự kiện thể thao'),
               ('Chuẩn hóa tên','Bỏ dấu, chữ thường, thêm tên theo từng nước (akas)'),
               ('Ghép thực thể','Tên + năm từ tên torrent ↔ IMDb; TMDb nối qua imdb_id'),
               ('Làm sạch','Bỏ tệp < 100 MB, năm lệch, ca trùng tên, torrent giả'),
               ('Cửa sổ thời gian','Chỉ giữ giai đoạn thu thập ổn định 04/2021 – 09/2024')],
        result='Kết quả: '+format(method_reference['facts']['clean_pairs'],',').replace(',','.')+
               ' cặp torrent–phim sạch · '+format(method_reference['facts']['clean_movies'],',').replace(',','.')+' phim')
    chart('6_integration/01_cleaning_funnel','Tiền xử lý','Dữ liệu còn lại sau từng bước làm sạch',
        'Hai nhánh ghép được làm sạch riêng, sau đó hợp nhất và lọc chung trước khi phân tích.',
        'Đi vào từng thao tác: chuẩn hóa dữ liệu trước khi ghép phim.',
        'Đọc ba cụm từ trái sang phải: mã IMDb có sẵn, tự ghép tên torrent, rồi hợp hai nguồn và lọc chung. Nhãn số cho biết số torrent còn lại sau mỗi bước.',
        'Mỗi cụm có thang riêng; không so trực tiếp độ dài thanh giữa các cụm và không cộng hai nhánh vì có phần giao nhau. Phễu dùng phạm vi dữ liệu gốc, khác cửa sổ thống kê của dashboard.')
    slides.extend(method_slides)
    chart('1_imdb/01_movies_per_year','IMDb','Kho phim thay đổi thế nào theo thời gian?',
        'Quy mô danh mục khác nhau giữa các năm; cần hiểu nền dữ liệu trước khi so sánh.',
        'Nhiều phim như vậy, sự chú ý có phân bố đều không?',
        'Trục ngang là năm phim trên IMDb; trục dọc là số bản ghi phim. Chỉ nhấn mạnh hình dạng xu hướng, không đọc từng năm.',
        'Số bản ghi IMDb chịu ảnh hưởng của độ đầy đủ dữ liệu; không phải tổng điều tra sản lượng phim.')
    chart('1_imdb/06_votes_lorenz','IMDb','Sự chú ý tập trung vào một nhóm phim nhỏ',
        'Trong nhóm phim có đánh giá, 1% phim nhiều bình chọn nhất chiếm khoảng 69% tổng lượt bình chọn.',
        'Khán giả có thể tiếp cận những bộ phim đó ở đâu?',
        'Phim được xếp từ ít đến nhiều bình chọn. Nếu phân bố đều, đường xanh trùng đường chéo; đường thực tế cong mạnh cho thấy sự tập trung.',
        'Bình chọn là chỉ báo mức độ quan tâm; không phải lượt xem. Không cần giải thích công thức Gini.')
    chart('3_tmdb_streaming/01_world_catalog_map','TMDb','Nơi xem phim khác nhau giữa các quốc gia',
        'Danh mục phim có nơi xem được ghi nhận khác nhau giữa các quốc gia.',
        'Ngoài nơi xem, thời điểm tiếp cận có khác nhau không?',
        'Đọc chú giải màu để so sánh số phim trong danh mục được ghi nhận. Chỉ chọn hai hoặc ba vùng để minh họa.',
        'Nơi xem là ảnh chụp tại thời điểm thu thập năm 2026, không phải danh mục lịch sử 2021–2024.')
    chart('2_tmdb/04_theatrical_window','TMDb','Từ chiếu rạp đến phát hành số mất bao lâu?',
        'Ngày chiếu rạp và ngày phát hành Digital là hai mốc khác nhau của cùng một phim.',
        'Một hình thức phân phối khác được ghi nhận trong MagnetDB là gì?',
        'Đọc khoảng cách ngày giữa hai mốc phát hành trong hình. Digital có thể gồm thuê hoặc mua phim, không chỉ xem theo thuê bao.',
        'IMDb có năm phim; TMDb có ngày phát hành theo hình thức và quốc gia. Không dùng hai trường này thay thế nhau.')
    chart('4_magnetdb/01_content_sunburst','MagnetDB','Trong kho chia sẻ có những loại nội dung nào?',
        'MagnetDB chứa nhiều loại nội dung; nghiên cứu này chọn phần liên quan đến phim.',
        'Việc thu thập có đều qua thời gian không?',
        'Đọc từ vòng trong ra ngoài để thấy cơ cấu nội dung. Chỉ chỉ vào nhánh video/phim, không giải thích mọi nhánh.',
        'Đây là metadata được thu thập; tên và nhãn không xác nhận nội dung thực tế của từng tệp.')
    chart('4_magnetdb/03_crawler_coverage','MagnetDB','Chọn thời gian quan sát trước khi so sánh',
        'Thu thập không đều; các phân tích chính giới hạn vào cửa sổ quan sát của dự án.',
        'Làm sao biết các bản ghi ở ba nguồn thuộc cùng một phim?',
        'Các điểm là số torrent được hệ thống phát hiện theo tháng. Khoảng giảm mạnh có thể liên quan đến hoạt động thu thập.',
        'Ngày phát hiện không phải ngày đăng. Cửa sổ gốc: 01/04/2021 ≤ ngày phát hiện < 29/09/2024; vẫn có gián đoạn.')
    chart('5_combined/01_integration_diagram','Tích hợp','Nối ba nguồn về cùng một bộ phim',
        'Mã IMDb là điểm nối; nhánh MagnetDB cần nhận diện tên phim và năm.',
        'Cách ghép bổ sung được bao nhiêu dữ liệu?',
        'Theo hai đường nối: TMDb có imdb_id; torrent cần chuẩn hóa tên, đối chiếu tên/năm/bí danh và loại các cặp không phù hợp.',
        'Cùng tên chưa đủ xác nhận cùng phim. Tích hợp cần làm sạch và kiểm tra các cặp ghép.')
    chart('6_integration/02_coverage_by_source','Tích hợp','Tự ghép tên bổ sung độ phủ của dữ liệu',
        'Nhánh tự ghép bổ sung nhiều cặp torrent–phim ngoài các liên kết có sẵn.',
        'Sau tích hợp, phim được quan tâm nhiều có nhiều bản chia sẻ hơn không?',
        'Màu biểu thị phần chỉ có ở mỗi phương pháp và phần giao nhau. So độ phủ theo thời gian, không đọc thành số người dùng.',
        'Độ phủ tăng không chứng minh độ chính xác tăng. Tổng qua các phim là số cặp torrent–phim.')
    chart('7_piracy_movies/02_popularity_vs_piracy','Phân tích chung','Sự quan tâm liên hệ thế nào với số bản chia sẻ?',
        'Trong mẫu phim đã ghép, lượt bình chọn cao thường đi cùng nhiều torrent được ghi nhận hơn.',
        'Mức độ quan tâm đã giải thích hết khác biệt giữa các phim chưa?',
        'Mỗi chấm là một phim. Trục ngang là lượt bình chọn IMDb; trục dọc là số torrent + 1. Hai trục theo thang log. Khoảng cách tới đường mô hình cho thấy ngoại lệ.',
        'Hình gốc dùng phim 2021–2023 ≥ 1.000 bình chọn trong nhóm đã ghép; dashboard còn giữ phim chưa ghi nhận torrent.')
    chart('7_piracy_movies/03_genre_piracy_ratio','Phân tích chung','Thể loại còn khác nhau sau khi xét sự quan tâm?',
        'Một số thể loại có số bản chia sẻ cao hoặc thấp hơn mức mô hình dự đoán từ lượt bình chọn.',
        'Ngoài đặc điểm phim, thời điểm phát hành có cung cấp thêm thông tin không?',
        'Đường cam ×1 là mức dự đoán. Vạch giữa hộp là trung vị: bên phải ×1 cao hơn dự đoán, bên trái thấp hơn. Chọn Hành động và Tài liệu làm hai ví dụ.',
        'Đây là so sánh với mô hình, không phải số phim mỗi thể loại. Một phim có thể thuộc nhiều thể loại; chưa chứng minh nguyên nhân.')
    chart('7_piracy_movies/07_web_lag','Phân tích chung','Bản WEB được ghi nhận gần mốc Digital đến đâu?',
        'Các bản WEB thường được ghi nhận gần ngày phát hành Digital tại Mỹ trong mẫu đang xét.',
        'Kết thúc: cảm ơn và mời câu hỏi.',
        'Ngày 0 là Digital tại Mỹ; âm là được phát hiện trước mốc đó, dương là sau. Hai cột ngoài cùng gom độ trễ ngoài giới hạn.',
        'Mốc Mỹ có thể muộn hơn nước khác; bộ lọc và thời điểm phát hiện ảnh hưởng phân bố. Không suy ra tác động nhân quả.')
    N=len(slides)
    esc=lambda x:html.escape(str(x),quote=True)
    rendered=[]
    for n,s in enumerate(slides):
        head=f"<div class='slide-heading'><p class='eyebrow'>{esc(s['phase'])} <span>• {n+1:02d} / {N}</span></p><h2>{esc(s['title'])}</h2></div>"
        if s['kind']=='chart':
            image=ROOT/s['image']
            asset=image.parent.name+'_'+image.name
            shutil.copyfile(image,ASSETS/asset)
            uri='data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode()
            # Slide biểu đồ chỉ gồm tiêu đề + hình; lời dẫn, điều rút ra, lưu ý nằm trong kich_ban.md
            body=f"<button class='figure-frame' data-zoom aria-label='Phóng to: {esc(s['title'])}'><img src='{uri}' alt='{esc(s['title'])}'></button>"
        elif s['kind']=='method':
            body=render_method_slide(s)
        else:
            body=f"<p class='subtitle'>{esc(s['subtitle'])}</p><div class='concept-cards'>"+''.join(f"<div><span class='card-number'>{j+1:02d}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></div>" for j,(t,d) in enumerate(s['cards']))+'</div>'
            if s.get('steps'):
                body+="<div class='prep'><p class='prep-label'>Tiền xử lý</p><ol class='prep-steps'>"+''.join(
                    f"<li><span class='prep-n'>{j+1}</span><h4>{esc(t)}</h4><p>{esc(d)}</p></li>" for j,(t,d) in enumerate(s['steps']))+"</ol>"
                if s.get('result'):body+=f"<p class='prep-result'>{esc(s['result'])}</p>"
                body+="</div>"
            if s['kind']=='hero':body+=f"<p class='hero-footer'>Tích hợp và Phân tích dữ liệu lớn <span>{N} slide</span></p>"
        extra=' with-prep' if s.get('steps') else ''
        rendered.append(f"<section class='slide {s['kind']}{extra} {'active' if n==0 else ''}' aria-label='Trang {n+1}'>{head}{body}</section>")
    template=(ROOT/'report/thuyet_trinh_ba_nguon/template.html').read_text(encoding='utf8')
    template=template.replace('Mạch thuyết trình · 32 trang',f'Mạch thuyết trình · {N} slide')
    template=template.replace('<div class="tools">','<div class="tools"><a class="dashboard-link" href="dashboard.html" target="_blank" rel="noopener">Dashboard ↗</a>')
    template=template.replace('</style>', '.dashboard-link{font-size:13px;color:var(--teal);padding:7px 10px;text-decoration:none;border:1px solid var(--teal);border-radius:7px;background:var(--tint)}@media print{.dashboard-link{display:none}}\n'
        # slide biểu đồ không còn khối chữ bên dưới -> hình chiếm hết chiều cao còn lại
        '.slide.chart .figure-frame{flex:1;min-height:0}\n'
        # dải "Tiền xử lý" trên slide 2
        '.slide.with-prep .concept-cards{flex:0;margin-top:22px}.slide.with-prep .concept-cards>div{padding:16px 22px}.prep{margin-top:26px}.prep-label{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--teal);margin:0 0 8px;font-weight:600}'
        '.prep-steps{list-style:none;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:0;padding:0}'
        '.prep-steps li{background:var(--tint);border-radius:10px;padding:16px 16px;position:relative}'
        '.prep-steps li:not(:last-child)::after{content:"→";position:absolute;right:-10px;top:50%;transform:translateY(-50%);color:var(--muted);font-size:14px}'
        '.prep-n{display:inline-block;width:20px;height:20px;border-radius:50%;background:var(--teal);color:white;font-size:12px;text-align:center;line-height:20px;margin-right:6px}'
        '.prep-steps h4{display:inline;font-size:18px;margin:0}.prep-steps p{font-size:16px;line-height:1.45;color:var(--muted);margin:8px 0 0}'
        '.prep-result{font-size:17px;margin:16px 0 0;color:var(--ink,inherit)}'
        '@media (max-width:900px){.prep-steps{grid-template-columns:1fr}.prep-steps li::after{display:none}}\n</style>')
    template=template.replace('</style>',(HERE/'slides.methods.css').read_text(encoding='utf8')+'\n</style>')
    # Bỏ tab Lời dẫn trên slide; lời dẫn vẫn nằm trong kich_ban.md
    template=template.replace(' · N lời dẫn','')
    template=template.replace('</style>','#notes-toggle,#notes{display:none!important}\n</style>')
    template=template.replace("else if(k==='n')toggleNotes();",'')
    result=template.replace('<!-- SLIDES -->','\n'.join(rendered)).replace('<!-- DATA -->',json_text(slides))
    (HERE/'slides.html').write_text(result,encoding='utf8')
    (HERE/'slides.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf8')
    outline=['# Kịch bản thuyết trình',f'{N} slide. Phân tích từng nguồn trước, tích hợp sau.']
    for n,s in enumerate(slides,1):
        outline.append(f"## {n:02d}. {s['title']}")
        if s['kind'] in ('chart','method'):
            outline.extend([f"**Lời dẫn:** {s['why']}",f"**Cách đọc:** {s['reading']}",f"**Chốt:** {s['finding']}",f"**Chuyển:** {s['next_question']}",f"**Lưu ý:** {s['caution']}"])
        else:outline.append(s['notes'])
    (HERE/'kich_ban.md').write_text('\n\n'.join(outline),encoding='utf8')
    return slides

def build_dashboard(payload):
    template=(HERE/'dashboard.template.html').read_text(encoding='utf8')
    for marker,filename in [('<!-- DASHBOARD_STYLE -->','dashboard.css'),('<!-- EXPLORE_MARKUP -->','dashboard.explore.html'),('<!-- CHART_CODE -->','dashboard.charts.js'),('<!-- PHASE_CODE -->','dashboard.phases.js'),('<!-- BUSINESS_CODE -->','dashboard.business.js')]:
        template=template.replace(marker,(HERE/filename).read_text(encoding='utf8'))
    (HERE/'dashboard.html').write_text(template.replace('<!-- EMBEDDED_DATA -->',json_text(payload)),encoding='utf8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    selection=parser.add_mutually_exclusive_group()
    selection.add_argument('--dashboard-only',action='store_true',help='Rebuild the dashboard without changing slides.')
    selection.add_argument('--slides-only',action='store_true',help='Rebuild slides from existing images and notebook outputs.')
    args=parser.parse_args()
    result={}
    if not args.slides_only:
        payload=export_data()
        build_dashboard(payload)
        result.update(movies=len(payload['rows']),release_facts=len(payload['releases']['rows']),
                      watch_facts=len(payload['watch']['rows']))
    if not args.dashboard_only:
        slides=build_slides()
        result.update(slides=len(slides))
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
