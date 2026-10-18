"""Independent SQL references for the rating and release dashboard views."""
import json
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
con = duckdb.connect()
for alias, name in [('i', 'imdb_movies_all'), ('r', 'tmdb_release_dates'), ('p', 'tmdb_watch_providers'), ('t', 'tmdb_movies')]:
    con.execute(f"CREATE VIEW {alias} AS SELECT * FROM read_parquet('{ROOT.as_posix()}/data_clean/{name}.parquet')")
con.execute("""CREATE TEMP VIEW eligible AS SELECT * FROM i
    WHERE NOT is_adult AND start_year BETWEEN 1920 AND 2024 AND num_votes>=1000""")
con.execute('CREATE TEMP VIEW cohort AS SELECT * FROM eligible WHERE start_year BETWEEN 2021 AND 2023')

def records(sql):
    result = con.execute(sql)
    return [dict(zip([c[0] for c in result.description], row)) for row in result.fetchall()]

def ratings(table):
    return records(f"""SELECT count(*) AS n,median(avg_rating) AS median_rating,
        median(num_votes) AS median_votes,count(*) FILTER(WHERE avg_rating>=7) AS high
        FROM {table}""")[0]

# Earliest country-specific dates, calculated from the long original table.
con.execute("""CREATE TEMP VIEW dates AS SELECT r.imdb_id,country,
    CASE WHEN type IN (2,3) THEN 0 WHEN type=4 THEN 1
         WHEN type=5 THEN 2 WHEN type=6 THEN 3 ELSE 4 END AS mode,
    min(release_date)::DATE AS day
    FROM r JOIN cohort ON r.imdb_id=cohort.tconst WHERE type BETWEEN 1 AND 6
    GROUP BY 1,2,3""")
cutoff = '2026-10-18'

def release_reference(country, mode=0):
    return records(f"""WITH known AS (SELECT * FROM dates WHERE country='{country}' AND day<=DATE '{cutoff}'),
        windows AS (SELECT a.imdb_id,date_diff('day',a.day,b.day) AS gap
            FROM known a JOIN known b ON a.imdb_id=b.imdb_id AND a.mode=0 AND b.mode=1)
        SELECT (SELECT count(*) FROM known WHERE mode={mode}) AS dated,
            count(*) AS pairs,count(*) FILTER(WHERE gap BETWEEN 0 AND 365) AS valid,
            median(gap) FILTER(WHERE gap BETWEEN 0 AND 365) AS median,
            count(*) FILTER(WHERE gap<0) AS negative,count(*) FILTER(WHERE gap>365) AS long_gap
        FROM windows""")[0]

references = {
    'cutoff': cutoff,
    'default_ratings': ratings('cohort'),
    'all_ratings': ratings('eligible'),
    'default_genres': records("""SELECT genre,count(*) AS n,
        quantile_cont(avg_rating,0.1) AS p10,quantile_cont(avg_rating,0.25) AS q1,
        median(avg_rating) AS median,quantile_cont(avg_rating,0.75) AS q3,
        quantile_cont(avg_rating,0.9) AS p90
        FROM cohort CROSS JOIN unnest(string_split(genres,',')) AS g(genre)
        WHERE genre<>'Adult' GROUP BY 1 ORDER BY n DESC LIMIT 8"""),
    'default_release_us': release_reference('US'),
    'default_release_vn': release_reference('VN'),
    'default_release_us_digital': release_reference('US', 1),
    'default_providers': records("""SELECT provider,count(DISTINCT imdb_id) AS n
        FROM p JOIN cohort ON p.imdb_id=cohort.tconst
        WHERE country='US' AND kind IN ('flatrate','free','ads')
        GROUP BY 1 ORDER BY 2 DESC,1"""),
    'default_rent_providers': records("""SELECT provider,count(DISTINCT imdb_id) AS n
        FROM p JOIN cohort ON p.imdb_id=cohort.tconst
        WHERE country='US' AND kind='rent' GROUP BY 1 ORDER BY 2 DESC,1"""),
}
(HERE/'phase_reference_checks.json').write_text(json.dumps(references,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in references.items() if not isinstance(v,list)},ensure_ascii=True))

# Independent notebook samples. Obtain US theatrical dates from the long source,
# rather than trusting the summary fields exported to the browser.
con.execute("""CREATE TEMP VIEW business_source AS SELECT i.tconst AS id,i.start_year AS imdb_year,
    i.num_votes,i.genres,t.* FROM t JOIN i ON t.imdb_id=i.tconst WHERE t.tmdb_found AND NOT i.is_adult""")
con.execute("""CREATE TEMP VIEW first_us_theatrical AS SELECT imdb_id,min(release_date)::DATE AS us_date
    FROM r WHERE country='US' AND type IN (2,3) GROUP BY 1""")

def business_reference(condition):
    con.execute(f'CREATE OR REPLACE TEMP VIEW business_sample AS SELECT * FROM business_source WHERE {condition}')
    con.execute("""CREATE OR REPLACE TEMP VIEW financial_sample AS SELECT * FROM business_sample
        WHERE year(release_date) BETWEEN 1980 AND 2024 AND budget>=1000000 AND revenue>=10000""")
    origin = records("""SELECT split_part(origin_country,',',1) AS country,count(*) AS n FROM business_sample
        WHERE year(release_date) BETWEEN 2000 AND 2024 AND nullif(split_part(origin_country,',',1),'') IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC,1""")
    missing = records("""SELECT count(*) AS n FROM business_sample WHERE year(release_date) BETWEEN 2000 AND 2024
        AND nullif(split_part(origin_country,',',1),'') IS NULL""")[0]['n']
    financial = records("""SELECT count(*) AS finance_n,
        count(*) FILTER(WHERE revenue/budget>=2.5) AS above_reference FROM financial_sample""")[0]
    months = records("""SELECT month(us_date) AS month,count(*) AS n_all,
        count(*) FILTER(WHERE revenue>=300000000) AS n_big
        FROM financial_sample JOIN first_us_theatrical ON id=first_us_theatrical.imdb_id GROUP BY 1 ORDER BY 1""")
    bins = [{'month':m,'all':next((r['n_all'] for r in months if r['month']==m),0),
             'big':next((r['n_big'] for r in months if r['month']==m),0)} for m in range(1,13)]
    return {'origin_total':sum(r['n'] for r in origin),'origin_missing':missing,**financial,
            'season_n':sum(r['all'] for r in bins),'season_big':sum(r['big'] for r in bins),'months':bins,'origins':origin}

business_references = {
    'default':business_reference('imdb_year BETWEEN 2021 AND 2023 AND num_votes>=1000'),
    'original':business_reference('true'),
    'action':business_reference("imdb_year BETWEEN 2021 AND 2023 AND num_votes>=1000 AND list_contains(string_split(genres,','),'Action')"),
}
(HERE/'business_reference_checks.json').write_text(json.dumps(business_references,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:{field:value for field,value in v.items() if field not in ('months','origins')} for k,v in business_references.items()}))
