// Notebook-compatible TMDb samples plus a view of the shared dashboard cohort.
const originalFinance=payload.business.original_finance.rows.map(r=>Object.fromEntries(payload.business.original_finance.columns.map((k,i)=>[k,r[i]])));
const businessMethod=payload.business.method;
const businessMovieIndex=new Map(movies.map(m=>[m.id,m]));
let businessState=null,originTiles=[],financePoints=[];
const originCountryNames={US:'Mỹ',IN:'Ấn Độ',FR:'Pháp',JP:'Nhật',GB:'Anh',CA:'Canada',CN:'Trung Quốc',RU:'Nga',ES:'Tây Ban Nha',IT:'Ý',DE:'Đức',KR:'Hàn Quốc',BR:'Brazil',AU:'Úc',MX:'Mexico'};
const originName=code=>originCountryNames[code]||countryName(code);
const moneyTick=n=>'$'+(n>=1e9?nice(n/1e9)+' tỷ':n>=1e6?nice(n/1e6)+' tr':nice(n/1e3)+'k');
const moneyFull=n=>nf(n)+' USD';
function getBusinessState(){
 const original=$('business-scope').value==='original';
 let origins,missing,finance;
 if(original){origins=payload.business.original_origin.rows.map(([country,n])=>({country,n}));missing=payload.business.original_origin.missing;finance=originalFinance}
 else{
  // Nhóm đang lọc: theo đúng năm phim ở bộ lọc bên trái (mọi phim có hồ sơ TMDb). Mẫu gốc vẫn giữ năm TMDb 2000–2024 như notebook.
  const originPool=currentRows.filter(m=>m.tmdb),counts=new Map();
  missing=0;for(const m of originPool){if(m.origin)counts.set(m.origin,(counts.get(m.origin)||0)+1);else missing++}
  origins=[...counts].map(([country,n])=>({country,n})).sort((a,b)=>b.n-a.n||a.country.localeCompare(b.country));
  finance=currentRows.filter(m=>m.tmdb_year>=businessMethod.finance_year_min&&m.tmdb_year<=businessMethod.finance_year_max&&Number.isFinite(m.budget)&&m.budget>=businessMethod.budget_min&&Number.isFinite(m.revenue)&&m.revenue>=businessMethod.revenue_min);
 }
 // Mỹ giữ đúng trường us_theatrical của notebook; thị trường khác (hoặc Tất cả) dùng ngày rạp sớm nhất trong lịch TMDb.
 const seasonCountry=selectedReleaseCountry(),seasonUS=seasonCountry===payload.releases.countries.indexOf('US');let seasonOutside=0;
 const theatricalDate=m=>{if(seasonUS)return m.theatrical;const movie=businessMovieIndex.get(m.id);if(!movie){seasonOutside++;return null}const d=releaseDay(movie,seasonCountry,0);return d===null?null:isoDay(d)};
 const months=Array.from({length:12},(_,i)=>({month:i+1,all:0,big:0}));let seasonTotal=0,seasonBig=0;
 for(const m of finance){const theatrical=theatricalDate(m);if(!theatrical)continue;const month=new Date(theatrical+'T00:00:00Z').getUTCMonth();if(!Number.isInteger(month))continue;months[month].all++;seasonTotal++;if(m.revenue>=businessMethod.blockbuster_revenue_min){months[month].big++;seasonBig++}}
 return {original,origins,originTotal:origins.reduce((s,r)=>s+r.n,0),originMissing:missing,finance,months,seasonTotal,seasonBig,seasonCountry,seasonUS,seasonOutside,aboveReference:finance.filter(m=>m.revenue/m.budget>=businessMethod.reference_ratio).length};
}
function renderBusinessCharts(){
 businessState=getBusinessState();
 $('business-scope-note').classList.toggle('original-scope',businessState.original);
 $('business-scope-note').textContent=businessState.original?'Mẫu gốc của notebook: ba biểu đồ này không chịu bộ lọc bên trái. Các biểu đồ lịch phát hành và nơi xem ở trên vẫn dùng nhóm đang lọc.':`Tính từ nhóm ${nf(currentRows.length)} phim đang lọc. Mỗi biểu đồ chỉ giữ các phim đủ điều kiện năm phát hành và dữ liệu; điều kiện được ghi dưới hình.`;
 renderOriginTreemap();renderSeasonPolar();renderFinanceScatter();
}
// Squarified rectangles with areas exactly proportional to movie counts.
function treemapLayout(items,width,height){
 const total=items.reduce((s,d)=>s+d.n,0);if(!total)return [];
 const queue=items.map(d=>({...d,area:d.n/total*width*height})),out=[];
 let box={x:0,y:0,w:width,h:height},row=[];
 const worst=(r,side)=>{if(!r.length)return Infinity;const sum=r.reduce((s,d)=>s+d.area,0),values=r.map(d=>d.area);return Math.max(side*side*Math.max(...values)/(sum*sum),sum*sum/(side*side*Math.min(...values)))};
 const place=()=>{const area=row.reduce((s,d)=>s+d.area,0);if(box.w>=box.h){const w=area/box.h;let y=box.y;for(const d of row){const h=d.area/w;out.push({...d,x:box.x,y,w,h});y+=h}box={x:box.x+w,y:box.y,w:Math.max(0,box.w-w),h:box.h}}else{const h=area/box.w;let x=box.x;for(const d of row){const w=d.area/h;out.push({...d,x,y:box.y,w,h});x+=w}box={x:box.x,y:box.y+h,w:box.w,h:Math.max(0,box.h-h)}}row=[]};
 while(queue.length){const next=queue[0],side=Math.min(box.w,box.h);if(!row.length||worst([...row,next],side)<=worst(row,side)){row.push(queue.shift())}else place()}
 if(row.length)place();return out;
}
function renderOriginTreemap(){
 const {el,W,H}=svgFrame('origin-treemap',350),s=businessState;
 $('origin-scope').textContent=s.original?'Năm TMDb 2000–2024 · mẫu gốc':'Năm phim theo bộ lọc';
 $('origin-note').textContent=`${nf(s.originTotal)} phim ${s.original?'phát hành 2000–2024 theo năm TMDb':'trong nhóm đang lọc có hồ sơ TMDb'}, biết nước sản xuất chính (mục đầu trong origin_country). Loại ${nf(s.originMissing)} phim thiếu nước sản xuất. Top 14 nước, phần còn lại gộp chung. Độ phủ TMDb không đại diện đầy đủ sản lượng điện ảnh toàn cầu.`;
 if(!s.originTotal){originTiles=[];svgEmpty(el,W,H,'Không có phim có nước sản xuất trong nhóm đang chọn');$('origin-callout').textContent='Chưa có phim đủ dữ liệu nước sản xuất trong phạm vi này.';return}
 const colors=['#1d5092','#286ab8','#3987da','#6ba5e5'],top=s.origins.slice(0,14).map((d,i)=>({...d,label:originName(d.country),color:colors[i===0?0:i<4?1:i<9?2:3]})),rest=s.origins.slice(14);
 if(rest.length)top.push({country:null,label:nf(rest.length)+' nước khác',n:rest.reduce((a,b)=>a+b.n,0),color:'#aaa9a3'});
 top.sort((a,b)=>b.n-a.n||a.label.localeCompare(b.label));originTiles=treemapLayout(top,W,H);
 el.innerHTML=originTiles.map((d,i)=>{const label=`${d.label}: ${nf(d.n)} phim (${pct(d.n/s.originTotal)})`,show=d.w>48&&d.h>34,maxChars=Math.max(4,Math.floor((d.w-10)/6)),short=d.label.length>maxChars?d.label.slice(0,maxChars-1)+'…':d.label;
  return `<g data-origin-index="${i}" tabindex="0" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title><rect x="${d.x+1}" y="${d.y+1}" width="${Math.max(0,d.w-2)}" height="${Math.max(0,d.h-2)}" fill="${d.color}"/>${show?`<text x="${d.x+d.w/2}" y="${d.y+d.h/2-3}" text-anchor="middle" fill="white" font-size="12">${esc(short)}</text><text x="${d.x+d.w/2}" y="${d.y+d.h/2+14}" text-anchor="middle" fill="white" font-size="12">${pct(d.n/s.originTotal)}</text>`:''}</g>`;
 }).join('');
 $('origin-callout').textContent=s.origins.slice(0,2).map(d=>`${originName(d.country)}: ${pct(d.n/s.originTotal)}`).join(' · ');
}
function polarSector(cx,cy,r,start,end){
 if(r<=0)return '';
 return `M ${cx},${cy} L ${cx+r*Math.cos(start)},${cy+r*Math.sin(start)} A ${r},${r} 0 0 1 ${cx+r*Math.cos(end)},${cy+r*Math.sin(end)} Z`;
}
function renderSeasonPolar(){
 const {el,W,H}=svgFrame('season-polar',350),s=businessState;
 const place=s.seasonCountry<0?'ở bất kỳ thị trường nào (ngày sớm nhất)':'tại '+(s.seasonUS?'Mỹ':releaseCountryLabel(s.seasonCountry)),coverage=s.finance.length?s.seasonTotal/s.finance.length:0;
 $('season-scope').textContent=s.seasonCountry<0?'Ngày ra rạp sớm nhất · mọi thị trường':'Ngày ra rạp '+place;
 $('season-warning').hidden=!(s.finance.length&&coverage<.3);
 $('season-warning').textContent=`Chỉ ${pct(coverage)} phim đủ tài chính có ngày ra rạp ${place}, thường là phim lớn; cột xám không đại diện cho mọi phim. So sánh cần thận trọng.`;
 $('season-note').textContent=`${nf(s.seasonTotal)} / ${nf(s.finance.length)} phim đủ tài chính có ngày ra rạp ${place}, gồm ${nf(s.seasonBig)} bom tấn doanh thu ≥ 300 triệu USD. Tỷ lệ xám chia cho ${nf(s.seasonTotal)} phim; xanh chia cho ${nf(s.seasonBig)} bom tấn. Đổi theo ô Thị trường phát hành (luôn dùng hình thức chiếu rạp); mặc định Mỹ như notebook. Mẫu tài chính: năm TMDb 1980–2024.${s.seasonOutside?` ${nf(s.seasonOutside)} phim của mẫu gốc nằm ngoài danh mục dashboard nên không có lịch theo nước.`:''}${s.seasonTotal&&!s.seasonBig?' Không có bom tấn trong nhóm đang chọn.':''}`;
 if(!s.seasonTotal){svgEmpty(el,W,H,s.finance.length?'Chưa có phim đủ tài chính và ngày ra rạp '+place:'Mẫu tài chính chỉ gồm phim phát hành 1980–2024 (năm TMDb)');return}
 const cx=W/2,cy=H/2-4,R=Math.min((W-72)/2,(H-58)/2),fractions=s.months.flatMap(d=>[d.all/s.seasonTotal,s.seasonBig?d.big/s.seasonBig:0]),max=Math.max(.2,Math.ceil(Math.max(...fractions)/.05)*.05),angle=2*Math.PI/12,barWidth=angle*.42;
 let out='';
 for(const d of s.months){const theta=(d.month-1)*angle-Math.PI/2,all=d.all/s.seasonTotal,big=s.seasonBig?d.big/s.seasonBig:0;
  out+=`<path d="${polarSector(cx,cy,all/max*R,theta-barWidth,theta)}" fill="#aaa9a3"><title>Tháng ${d.month} · mọi phim đủ tài chính: ${nf(d.all)} / ${nf(s.seasonTotal)} (${pct(all)})</title></path><path d="${polarSector(cx,cy,big/max*R,theta,theta+barWidth)}" fill="#2670bc"><title>Tháng ${d.month} · bom tấn: ${nf(d.big)} / ${nf(s.seasonBig)} (${s.seasonBig?pct(big):'chưa có bom tấn'})</title></path>`;
 }
 const gridStep=max<=.25?.05:max<=.5?.1:.25;
 for(let v=gridStep;v<=max+.001;v+=gridStep){const r=v/max*R;out+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#dce2e8" stroke-opacity=".7"/><text x="${cx+r*.966+3}" y="${cy+r*.259+3}" font-size="9" fill="#647488">${Math.round(v*100)}%</text>`}
 for(let m=0;m<12;m++){const theta=m*angle-Math.PI/2,x=cx+R*Math.cos(theta),y=cy+R*Math.sin(theta);out+=`<line x1="${cx}" x2="${x}" y1="${cy}" y2="${y}" stroke="#e6eaf0"/><text x="${cx+(R+18)*Math.cos(theta)}" y="${cy+(R+18)*Math.sin(theta)+4}" text-anchor="middle" font-size="11" fill="#596778">Th${m+1}</text>`}
 el.innerHTML=out;
}
function renderFinanceScatter(){
 const canvas=$('finance-scatter'),box=canvas.parentElement.getBoundingClientRect();if(!box.width)return;
 const dpr=window.devicePixelRatio||1,W=Math.round(box.width),H=Math.round(box.height);canvas.width=W*dpr;canvas.height=H*dpr;
 const c=canvas.getContext('2d');c.scale(dpr,dpr);c.font="12px 'Segoe UI',sans-serif";c.textBaseline='middle';
 const s=businessState,rows=s.finance,L=W<500?64:74,R=23,T=30,B=48,pw=W-L-R,ph=H-T-B,xmin=6,xmax=Math.log10(Math.max(5e9,...rows.map(m=>m.budget*1.1))),ymin=4,ymax=Math.log10(Math.max(5e9,...rows.map(m=>m.revenue*1.1))),x=v=>L+(Math.log10(v)-xmin)/(xmax-xmin)*pw,y=v=>T+ph-(Math.log10(v)-ymin)/(ymax-ymin)*ph;
 $('finance-ratio').textContent=rows.length?pct(s.aboveReference/rows.length):'—';
 $('finance-note').textContent=`${nf(rows.length)} phim có ngân sách ≥ 1 triệu USD và doanh thu ≥ 10.000 USD, phát hành 1980–2024 theo TMDb; USD danh nghĩa, chưa điều chỉnh lạm phát. ${nf(s.aboveReference)} phim đạt ngưỡng doanh thu/ngân sách ≥ 2,5. Đây là ngưỡng tham khảo như notebook, không xác định lãi/lỗ thực tế; chưa có đầy đủ chi phí quảng bá và phần chia doanh thu.`;
 if(!rows.length){financePoints=[];c.fillStyle='#596778';c.textAlign='center';c.font="14px 'Segoe UI',sans-serif";c.fillText('Mẫu tài chính chỉ gồm phim phát hành 1980–2024 (năm TMDb), ngân sách ≥ 1 triệu USD',W/2,H/2);return}
 c.strokeStyle='#e4e9f0';c.fillStyle='#596778';c.textAlign='right';
 for(let v=ymin;v<=Math.floor(ymax);v++){const yy=y(10**v);c.beginPath();c.moveTo(L,yy);c.lineTo(W-R,yy);c.stroke();c.fillText(moneyTick(10**v),L-8,yy)}
 c.textAlign='center';for(let v=xmin;v<=Math.floor(xmax);v++){const xx=x(10**v);c.beginPath();c.moveTo(xx,T);c.lineTo(xx,H-B);c.stroke();c.fillText(moneyTick(10**v),xx,H-B+17)}
 c.fillText('Ngân sách sản xuất (USD · thang log)',L+pw/2,H-5);c.textAlign='left';c.fillText('Doanh thu toàn cầu (USD · thang log)',L,12);
 financePoints=rows.map(m=>({x:x(m.budget),y:y(m.revenue),m}));
 c.save();c.beginPath();c.rect(L,T,pw,ph);c.clip();c.fillStyle=rows.length>3000?'#2670bc40':'#2670bc77';for(const p of financePoints){c.beginPath();c.arc(p.x,p.y,rows.length>3000?1.9:2.6,0,Math.PI*2);c.fill()}
 for(const [factor,color] of [[1,'#66717d'],[businessMethod.reference_ratio,'#e58a36']]){c.strokeStyle=color;c.lineWidth=factor===1?1.4:2;c.beginPath();c.moveTo(x(10**xmin),y(10**xmin*factor));c.lineTo(x(10**xmax),y(10**xmax*factor));c.stroke()}
 c.restore();
 if(W>650){const labels=[...financePoints].sort((a,b)=>b.m.revenue-a.m.revenue).slice(0,3);labels.forEach((p,i)=>{const tx=Math.max(L+5,Math.min(W-R-190,p.x-175)),ty=T+12+i*20;c.strokeStyle='#b3bdca';c.lineWidth=.7;c.beginPath();c.moveTo(p.x,p.y);c.lineTo(tx+140,ty);c.stroke();c.fillStyle='#445569';c.fillText(p.m.title.length>30?p.m.title.slice(0,29)+'…':p.m.title,tx,ty)})}
 if(!rows.length){c.fillStyle='#596778';c.textAlign='center';c.fillText('Chưa có phim đủ dữ liệu tài chính',W/2,H/2)}
}
function businessTooltip(html,e){$('tooltip').innerHTML=html;$('tooltip').hidden=false;$('tooltip').style.left=Math.max(5,Math.min(innerWidth-310,e.clientX+15))+'px';$('tooltip').style.top=Math.max(5,e.clientY-95)+'px'}
function openFinanceMovie(m){
 if(businessMovieIndex.has(m.id)){openMovie(m.id);$('movie-detail').insertAdjacentHTML('afterbegin',`<h3>Ngân sách & doanh thu · TMDb</h3><dl class="detail-grid"><div><dt>Ngân sách sản xuất</dt><dd>${moneyFull(m.budget)}</dd></div><div><dt>Doanh thu toàn cầu</dt><dd>${moneyFull(m.revenue)}</dd></div></dl>`);return}
 $('movie-title').textContent=m.title+(m.tmdb_year?' ('+m.tmdb_year+')':'');
 const fields=[['IMDb',m.id],['Nước sản xuất chính',m.origin?originName(m.origin):'Thiếu dữ liệu'],['Ngân sách sản xuất',moneyFull(m.budget)],['Doanh thu toàn cầu',moneyFull(m.revenue)],['Doanh thu / ngân sách','×'+nice(m.revenue/m.budget)],['Ra rạp tại Mỹ',dateText(m.theatrical)]];
 $('movie-detail').innerHTML=`<p>TMDb · số liệu kinh doanh trong mẫu gốc của notebook.</p><dl class="detail-grid">${fields.map(([k,v])=>`<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl><p>Tiền là USD danh nghĩa. Hệ số doanh thu/ngân sách không phải lợi nhuận thực tế.</p>`;$('movie-dialog').showModal();
}
function initBusiness(){
 $('business-scope').onchange=renderBusinessCharts;
 const origin=$('origin-treemap');
 origin.addEventListener('pointermove',e=>{const g=e.target.closest('[data-origin-index]');if(!g){$('tooltip').hidden=true;return}const d=originTiles[Number(g.dataset.originIndex)];businessTooltip(`${esc(d.label)}<small>${nf(d.n)} / ${nf(businessState.originTotal)} phim · ${pct(d.n/businessState.originTotal)}</small>`,e)});
 origin.addEventListener('pointerleave',()=>{$('tooltip').hidden=true});
 const canvas=$('finance-scatter'),nearest=e=>{const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;let m=null,best=81;for(const p of financePoints){const d=(p.x-x)**2+(p.y-y)**2;if(d<best){m=p.m;best=d}}return m};
 canvas.addEventListener('pointermove',e=>{const m=nearest(e);canvas.style.cursor=m?'pointer':'default';if(!m){$('tooltip').hidden=true;return}businessTooltip(`${esc(m.title)} (${m.tmdb_year})<small>Ngân sách: ${moneyFull(m.budget)}<br>Doanh thu: ${moneyFull(m.revenue)}<br>Doanh thu / ngân sách: ×${nice(m.revenue/m.budget)}</small>`,e)});
 canvas.addEventListener('pointerleave',()=>{$('tooltip').hidden=true});canvas.addEventListener('click',e=>{const m=nearest(e);if(m){$('tooltip').hidden=true;openFinanceMovie(m)}});
}
