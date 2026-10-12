"""One-time template migration; rendering lives in build.py and dashboard.*."""
from pathlib import Path

here=Path(__file__).resolve().parent
p=here/'dashboard.template.html'
s=p.read_text(encoding='utf8')
if '<!-- DASHBOARD_STYLE -->' not in s:
    a=s.index('<style>');b=s.index('</style>',a)+len('</style>')
    s=s[:a]+'<style><!-- DASHBOARD_STYLE --></style>'+s[b:]
    a=s.index('<div class="shell">');b=s.index(' <section id="explore"',a)
    s=s[:a]+'''<header class="app-header">
 <div class="app-name">Phim &amp; chia sẻ<small>IMDb · TMDb / JustWatch · MagnetDB</small></div>
 <nav role="tablist" aria-label="Các phần dashboard">
  <button id="tab-explore" role="tab" aria-controls="explore" aria-selected="true" data-tab="explore">Phân tích</button>
  <button id="tab-sources" role="tab" aria-controls="sources" aria-selected="false" data-tab="sources">Nguồn dữ liệu</button>
  <button id="tab-method" role="tab" aria-controls="method" aria-selected="false" data-tab="method">Phương pháp</button>
 </nav>
 <a class="slide-link" href="slides.html">Mở slide ↗</a>
</header>
<main class="main">
'''+s[b:]
    a=s.index(' <section id="explore"');b=s.index(' <section id="sources"',a)
    s=s[:a]+'<!-- EXPLORE_MARKUP -->\n'+s[b:]
    s=s.replace('</main>\n</div>','</main>')
    a=s.index('function svgBars(');b=s.index('function availabilityLabel(',a)
    s=s[:a]+'<!-- CHART_CODE -->\n'+s[b:]
    s=s.replace("c.font=\"11px 'Segoe UI',sans-serif\"", "c.font=\"13px 'Segoe UI',sans-serif\"")
    s=s.replace('const L=50,R=18,T=20,B=43','const L=58,R=22,T=26,B=48')
    s=s.replace("c.strokeStyle='#e5e8df';c.fillStyle='#72827d'", "c.strokeStyle='#e4e9f0';c.fillStyle='#596778'")
    s=s.replace("c.fillStyle='#2d7ed34d'", "c.fillStyle='#2670bc4d'")
    s=s.replace("c.strokeStyle='#d9864d'", "c.strokeStyle='#e58a36'")
    s=s.replace("y(Math.max(0,10**(model.a+model.b*xmin)-1))", "T+ph-(model.a+model.b*xmin)/ymax*ph")
    s=s.replace("y(Math.max(0,10**(model.a+model.b*xmax)-1))", "T+ph-(model.a+model.b*xmax)/ymax*ph")
    old="$('filter-summary').textContent=`${nf(currentRows.length)} phim · Năm ${f.min}–${f.max} · ${f.genre?(genreNames[f.genre]||f.genre):'Tất cả thể loại'} · ≥ ${nf(f.votes)} bình chọn. Cửa sổ torrent cố định: 01/04/2021 ≤ ngày phát hiện < 29/09/2024.`;"
    new="$('filter-summary').textContent=`${nf(currentRows.length)} phim phù hợp · ${f.min}–${f.max}.`;"
    assert old in s;s=s.replace(old,new)
    s=s.replace("if(activeTab==='explore')scatter()", "if(activeTab==='explore')renderCharts()")
    s=s.replace("if(name==='explore')requestAnimationFrame(scatter)", "if(name==='explore')requestAnimationFrame(renderCharts)")
    s=s.replace("$('genre').focus()", "$('comparison').scrollIntoView({behavior:'smooth',block:'start'})")
    extra='''
for(const id of ['compare-a','compare-b']){for(const g of setOptions){const o=document.createElement('option');o.value=g;o.textContent=genreNames[g]||g;$(id).append(o)}$(id).onchange=renderComparison}
$('compare-a').value='Action';$('compare-b').value='Documentary';$('genre-measure').onchange=renderCharts;
'''
    s=s.replace("window.addEventListener('hashchange'",extra+"window.addEventListener('hashchange'")
    p.write_text(s,encoding='utf8')
print('Template migrated')
