// The same IMDb-led cohort is shared by all three views. Only torrent filters
// are local; release country and mode select which facts describe that cohort.
const phaseConfig={
 ratings:{source:'01 · IMDb',title:'Phim được đánh giá như thế nào?',description:'Khám phá điểm số và mức độ quan tâm trước khi theo dõi hành trình phát hành.',note:'Bộ lọc chung được giữ khi chuyển góc nhìn. Điểm và bình chọn là ảnh chụp năm 2026; bình chọn không phải lượt xem.'},
 releases:{source:'02 · TMDb / JustWatch',title:'Từ ngày ra mắt đến nơi xem phim',description:'Theo dõi lịch phát hành theo thị trường và hình thức, rồi khám phá nơi xem được ghi nhận tại Mỹ.',note:'Năm lọc là năm phim IMDb. Năm trên biểu đồ phát hành lấy từ ngày TMDb và có thể khác. Digital có thể gồm thuê hoặc mua, không đồng nghĩa thuê bao.'},
 torrents:{source:'03 · MagnetDB + IMDb + TMDb',title:'Mức độ chia sẻ phim',description:'Bình chọn, thể loại và thời điểm phát hành trong cùng một nhóm phim.',note:'Thời gian ghi nhận torrent: 01/04/2021 – 28/09/2024. Số bản chia sẻ khác số lượt tải. Nơi xem là ảnh chụp năm 2026.'}
};
const releaseModeNames=['Chiếu rạp','Digital','Đĩa / Physical','Truyền hình','Công chiếu / Premiere'];
const displayCountries=new Intl.DisplayNames(['vi'],{type:'region'});
const countryName=code=>displayCountries.of(code)||code;
// -1 = Tất cả: lấy mốc sớm nhất trên mọi thị trường / mọi hình thức.
const releaseCountryLabel=i=>i<0?'Tất cả thị trường':countryName(payload.releases.countries[i]);
const releaseModeLabel=mode=>mode<0?'Mọi hình thức':releaseModeNames[mode];
const releaseMatch=(r,country,mode)=>(country<0||r[1]===country)&&(mode<0||r[2]===mode);
const releaseCutoff=Math.floor(Date.parse(payload.method.release_cutoff+'T00:00:00Z')/86400000);
const isoDay=day=>day===null?'':new Date(day*86400000).toISOString().slice(0,10);
const dayYear=day=>new Date(day*86400000).getUTCFullYear();
let ratingPoints=[],ratingGenreData=[],ratingHistogram=[],rankingRows=[],releaseState=null,windowYearData=[],countryCounts=[],providerCounts=[];
for(const m of movies){m.releaseEvents=[];m.usWatch=[]}
for(const row of payload.releases.rows)movies[row[0]].releaseEvents.push(row);
for(const row of payload.watch.rows)movies[row[0]].usWatch.push(row);
function releaseDay(m,country,mode){let best=null;for(const r of m.releaseEvents)if(releaseMatch(r,country,mode)&&r[3]<=releaseCutoff&&(best===null||r[3]<best))best=r[3];return best}
function selectedReleaseCountry(){return Number($('release-country').value)}
function phaseHash(){return activeView==='ratings'?'explore':'explore-'+activeView}
function switchView(name,hash=true){
 if(!Object.hasOwn(phaseConfig,name))name='ratings';
 const changed=activeView!==name;activeView=name;
 const config=phaseConfig[name];
 $('phase-source').textContent=config.source;$('phase-title').textContent=config.title;$('phase-description').textContent=config.description;$('phase-filter-note').textContent=config.note;
 for(const n of Object.keys(phaseConfig)){
  $('view-'+n).hidden=n!==name;$('metrics-'+n).hidden=n!==name;
  $('view-tab-'+n).setAttribute('aria-selected',String(n===name));$('view-tab-'+n).tabIndex=n===name?0:-1;
 }
 $('release-controls').hidden=name!=='releases';
 document.querySelectorAll('[data-torrent-filter]').forEach(el=>el.hidden=name!=='torrents');
 $('tooltip').hidden=true;
 if(changed){sortKey=name==='torrents'?'torrents':'votes';sortDir=-1}
 if(hash)history.replaceState(null,'','#'+phaseHash());
 update();
}
function routeFromHash(){
 const hash=location.hash.slice(1);
 if(hash==='sources'||hash==='method'){switchTab(hash,false);switchView(activeView,false)}
 else {switchTab('explore',false);switchView(hash==='explore-torrents'?'torrents':hash==='explore-releases'?'releases':'ratings',false)}
}
function renderCharts(){
 if(activeTab!=='explore')return;
 if(activeView==='ratings'){renderRatingHistogram();renderRatingGenres();renderRatingScatter();renderRanking();renderRatingYear();renderRatingRuntime();renderRatingRegions();renderGenrePairs()}
 else if(activeView==='releases'){renderReleaseHeatmap();renderReleaseWindow();renderReleaseCountries();renderProviders();renderBusinessCharts()}
 else renderTorrentCharts();
}
function getReleaseState(){
 const country=selectedReleaseCountry(),mode=Number($('release-mode').value),dated=[],pairs=[];
 let future=0;
 for(const m of currentRows){
  const d=releaseDay(m,country,mode);
  if(d!==null)dated.push({m,day:d});
  if(d===null&&m.releaseEvents.some(r=>releaseMatch(r,country,mode)&&r[3]>releaseCutoff))future++;
  const t=releaseDay(m,country,0),digital=releaseDay(m,country,1);
  if(t!==null&&digital!==null)pairs.push({m,theatrical:t,digital,gap:digital-t,year:dayYear(t)});
 }
 return {country,mode,dated,pairs,valid:pairs.filter(r=>r.gap>=0&&r.gap<=365),future};
}
function renderPhaseMetrics(){
 const n=currentRows.length;
 if(activeView==='torrents'){renderMetrics();return}
 if(activeView==='ratings'){
  const rated=currentRows.filter(m=>Number.isFinite(m.rating)),high=rated.filter(m=>m.rating>=7).length;
  $('k-ratings-n').textContent=nf(n);$('k-rating').textContent=rated.length?nice(median(rated.map(m=>m.rating))):'—';
  $('k-rating-note').textContent=`${nf(rated.length)} phim có điểm · thang 1–10`;
  $('k-votes').textContent=n?nf(median(currentRows.map(m=>m.votes))):'—';
  $('k-high-rating').textContent=rated.length?pct(high/rated.length):'—';$('k-high-rating-note').textContent=`${nf(high)} / ${nf(rated.length)} phim có điểm`;
 }else{
  releaseState=getReleaseState();const s=releaseState,code=payload.releases.countries[s.country],streaming=currentRows.filter(m=>m.tmdb&&m.streaming===true).length,missing=currentRows.filter(m=>!m.tmdb).length;
  $('k-release-n').textContent=nf(s.dated.length);$('k-release-note').textContent=`${releaseModeLabel(s.mode)} · ${releaseCountryLabel(s.country)} · ${n?pct(s.dated.length/n):'—'} nhóm phim`;
  $('k-release-pairs').textContent=nf(s.pairs.length);$('k-release-pairs-note').textContent=s.country<0?'Mốc sớm nhất toàn cầu, hai mốc có thể ở hai nước':`Cả hai mốc tại ${releaseCountryLabel(s.country)}`;
  $('k-release-gap').textContent=s.valid.length?nice(median(s.valid.map(r=>r.gap)))+' ngày':'—';$('k-release-gap-note').textContent=`${nf(s.valid.length)} phim có khoảng cách 0–365 ngày`;
  $('k-release-streaming').textContent=n?pct(streaming/n):'—';$('k-release-streaming-note').textContent=`${nf(streaming)} / ${nf(n)} phim · ${nf(missing)} thiếu TMDb`;
 }
}
function svgFrame(id,H=310){const el=$(id),W=Math.max(270,Math.round(el.clientWidth));el.setAttribute('viewBox',`0 0 ${W} ${H}`);return {el,W,H}}
function svgEmpty(el,W,H,message='Không có phim đủ dữ liệu'){el.innerHTML=`<text x="${W/2}" y="${H/2}" text-anchor="middle" fill="#596778" font-size="14">${esc(message)}</text>`}
function quantileSorted(a,q){if(!a.length)return null;const p=(a.length-1)*q,i=Math.floor(p);return a[i]+(a[Math.ceil(p)]-a[i])*(p-i)}
function renderRatingHistogram(){
 const {el,W,H}=svgFrame('rating-histogram'),rated=currentRows.filter(m=>Number.isFinite(m.rating));
 ratingHistogram=Array.from({length:20},(_,i)=>({lo:i*.5,hi:(i+1)*.5,n:0}));
 for(const m of rated)ratingHistogram[Math.min(19,Math.max(0,Math.floor(m.rating*2)))].n++;
 $('rating-histogram-note').textContent=`${nf(rated.length)} phim có điểm trong nhóm đang chọn. Điểm và lượt bình chọn phản ánh hai khía cạnh khác nhau.`;
 if(!rated.length){svgEmpty(el,W,H);return}
 const L=44,R=15,T=30,B=43,pw=W-L-R,ph=H-T-B,top=Math.max(1,...ratingHistogram.map(b=>b.n))*1.15;
 let out=`<text x="${L}" y="15" font-size="12" fill="#596778">Số phim</text>`;
 for(let i=0;i<=4;i++){const v=Math.round(top*i/4),y=T+ph-v/top*ph;out+=`<line x1="${L}" x2="${W-R}" y1="${y}" y2="${y}" stroke="#e4e9f0"/><text x="${L-7}" y="${y+4}" text-anchor="end" font-size="11" fill="#596778">${nf(v)}</text>`}
 ratingHistogram.forEach((b,i)=>{const x=L+i*pw/20,h=b.n/top*ph;out+=`<rect x="${x+1}" y="${T+ph-h}" width="${Math.max(1,pw/20-2)}" height="${h}" rx="1" fill="${b.lo>=7?'#2670bc':'#a4c5e8'}"><title>${nice(b.lo)} đến ${nice(b.hi)}${i===19?' (gồm 10)':' (không gồm cận trên)'}: ${nf(b.n)} phim</title></rect>`});
 for(let v=0;v<=10;v+=2)out+=`<text x="${L+v/10*pw}" y="${H-B+20}" text-anchor="middle" font-size="12" fill="#596778">${v}</text>`;
 out+=`<text x="${L+pw/2}" y="${H-1}" text-anchor="middle" font-size="12" fill="#596778">Điểm IMDb</text>`;el.innerHTML=out;
}
function renderRatingGenres(){
 const {el,W,H}=svgFrame('rating-genres'),groups=new Map();
 for(const m of currentRows)if(Number.isFinite(m.rating))for(const g of m.genreList){if(g==='Adult')continue;if(!groups.has(g))groups.set(g,[]);groups.get(g).push(m.rating)}
 ratingGenreData=[...groups].sort((a,b)=>b[1].length-a[1].length).slice(0,8).map(([genre,values])=>{
  const s=values.sort((a,b)=>a-b);return {genre,n:s.length,p10:quantileSorted(s,.1),q1:quantileSorted(s,.25),median:quantileSorted(s,.5),q3:quantileSorted(s,.75),p90:quantileSorted(s,.9)};
 }).sort((a,b)=>b.median-a.median||b.n-a.n);
 if(!ratingGenreData.length){svgEmpty(el,W,H);return}
 const L=Math.min(125,W*.35),R=30,T=13,B=34,pw=W-L-R,step=(H-T-B)/ratingGenreData.length,x=v=>L+v/10*pw;
 let out='';for(let v=0;v<=10;v+=2)out+=`<line x1="${x(v)}" x2="${x(v)}" y1="${T}" y2="${H-B}" stroke="#e4e9f0"/><text x="${x(v)}" y="${H-13}" text-anchor="middle" font-size="11" fill="#596778">${v}</text>`;
 ratingGenreData.forEach((g,i)=>{const y=T+step*(i+.45),label=genreNames[g.genre]||g.genre;
  out+=`<g><title>${esc(label)}: trung vị ${nice(g.median)}, khoảng 25–75% ${nice(g.q1)}–${nice(g.q3)} · ${nf(g.n)} phim</title><text x="0" y="${y-1}" font-size="13" fill="#26364a">${esc(label)}</text><text x="0" y="${y+13}" font-size="10" fill="#647488">${nf(g.n)} phim</text><line x1="${x(g.p10)}" x2="${x(g.p90)}" y1="${y}" y2="${y}" stroke="#739ac3"/><rect x="${x(g.q1)}" y="${y-8}" width="${Math.max(1,x(g.q3)-x(g.q1))}" height="16" fill="#b4d0ee"/><line x1="${x(g.median)}" x2="${x(g.median)}" y1="${y-9}" y2="${y+9}" stroke="#16599d" stroke-width="3"/><text x="${x(g.p90)+5}" y="${y+4}" font-size="11" fill="#16599d">${nice(g.median)}</text></g>`;
 });el.innerHTML=out;
}
function renderRatingScatter(){
 const canvas=$('rating-scatter'),box=canvas.parentElement.getBoundingClientRect();if(!box.width)return;
 const dpr=window.devicePixelRatio||1,W=Math.round(box.width),H=Math.round(box.height);canvas.width=W*dpr;canvas.height=H*dpr;
 const c=canvas.getContext('2d');c.scale(dpr,dpr);c.font="12px 'Segoe UI',sans-serif";c.textBaseline='middle';
 const L=36,R=22,T=25,B=46,pw=W-L-R,ph=H-T-B,xmax=Math.max(4,...currentRows.map(m=>Math.log10(m.votes))),x=v=>L+(Math.log10(v)-3)/(xmax-3)*pw,y=v=>T+ph-(v-1)/9*ph;
 c.strokeStyle='#e4e9f0';c.fillStyle='#596778';c.textAlign='right';
 for(let v=2;v<=10;v+=2){c.beginPath();c.moveTo(L,y(v));c.lineTo(W-R,y(v));c.stroke();c.fillText(v,L-7,y(v))}
 c.textAlign='center';for(let v=3;v<=Math.floor(xmax);v++){c.fillText(nf(10**v),x(10**v),H-B+19)}
 c.fillText('Lượt bình chọn IMDb · thang log',L+pw/2,H-5);c.textAlign='left';c.fillText('Điểm IMDb',L,11);
 ratingPoints=currentRows.filter(m=>Number.isFinite(m.rating)).map(m=>({x:x(m.votes),y:y(m.rating),m}));
 c.fillStyle='#2670bc3d';for(const p of ratingPoints){c.beginPath();c.arc(p.x,p.y,2.4,0,Math.PI*2);c.fill()}
 if(!ratingPoints.length){c.fillStyle='#596778';c.textAlign='center';c.fillText('Không có phim phù hợp',W/2,H/2)}
 $('rating-scatter-note').textContent=`${nf(ratingPoints.length)} phim. Bình chọn thể hiện mức quan tâm trên IMDb, không phải số người xem. Không suy ra nhân quả.`;
}
function renderRanking(){
 const min=Number($('ranking-votes').value),eligible=currentRows.filter(m=>Number.isFinite(m.rating)&&m.votes>=min);
 rankingRows=eligible.sort((a,b)=>b.rating-a.rating||b.votes-a.votes||a.id.localeCompare(b.id)).slice(0,10);
 $('rating-ranking').innerHTML=rankingRows.length?rankingRows.map((m,i)=>`<div class="ranking-item"><span class="rank-number">${String(i+1).padStart(2,'0')}</span><div><button class="movie-btn" data-movie="${esc(m.id)}">${esc(m.title)}</button><small>${m.year} · ${nf(m.votes)} bình chọn</small></div><strong>${nice(m.rating)}</strong></div>`).join(''):'<p class="empty">Không có phim đủ ngưỡng bình chọn.</p>';
 $('ranking-note').textContent=`${nf(eligible.length)} phim đủ ngưỡng trong nhóm đang chọn. Ngưỡng này chỉ áp dụng cho bảng xếp hạng.`;
}
function renderReleaseHeatmap(){
 const {el,W,H}=svgFrame('release-heatmap'),s=releaseState,code=payload.releases.countries[s.country];
 const fy=getFilters(),outsideYears=s.dated.filter(r=>{const yr=dayYear(r.day);return yr<fy.min||yr>fy.max}).length;
 $('release-heatmap-caption').textContent=`${releaseModeLabel(s.mode)} · ${releaseCountryLabel(s.country)}${s.country<0||s.mode<0?' · mốc sớm nhất của mỗi phim':''}. Hàng là năm phát hành trên TMDb, không phải năm phim IMDb${outsideYears?`: ${nf(outsideYears)} / ${nf(s.dated.length)} mốc nằm ngoài ${fy.min}–${fy.max} (phát hành ở nước khác hoặc lên Digital/TV muộn hơn)`:''}. Di chuột vào ô để xem số phim.`;
 if(!s.dated.length){svgEmpty(el,W,H);$('release-heatmap-note').textContent=`Không có mốc ${releaseModeLabel(s.mode).toLowerCase()} phù hợp trong dữ liệu của thị trường này. Thiếu ghi nhận không có nghĩa là phim chưa phát hành.`;return}
 const years=s.dated.map(r=>dayYear(r.day)),min=Math.min(...years),max=Math.max(...years),binSize=max-min>11?10:1,counts=new Map();
 for(const r of s.dated){const d=new Date(r.day*86400000),year=Math.floor(d.getUTCFullYear()/binSize)*binSize,key=year+'-'+d.getUTCMonth();counts.set(key,(counts.get(key)||0)+1)}
 const bins=[...new Set(years.map(y=>Math.floor(y/binSize)*binSize))].sort((a,b)=>a-b),top=Math.max(...counts.values()),L=binSize===1?44:66,R=5,T=30,B=35,cw=(W-L-R)/12,rh=Math.min(42,(H-T-B)/bins.length);
 let out='';for(let month=0;month<12;month++)out+=`<text x="${L+(month+.5)*cw}" y="16" text-anchor="middle" font-size="11" fill="#596778">${month+1}</text>`;
 bins.forEach((year,i)=>{const yy=T+i*rh,label=binSize===1?year:year+'–'+String(year+9).slice(-2);out+=`<text x="${L-8}" y="${yy+rh/2+4}" text-anchor="end" font-size="11" fill="#596778">${label}</text>`;
  for(let m=0;m<12;m++){const n=counts.get(year+'-'+m)||0,t=n/top,color=n?`rgb(${Math.round(226-188*t)},${Math.round(237-125*t)},${Math.round(250-62*t)})`:'#f3f5f8',xx=L+m*cw;
   out+=`<g><title>Tháng ${m+1} · ${label}: ${nf(n)} phim</title><rect x="${xx+1}" y="${yy+1}" width="${Math.max(1,cw-3)}" height="${rh-3}" rx="2" fill="${color}"/>${n&&cw>27&&rh>22?`<text x="${xx+cw/2}" y="${yy+rh/2+3}" text-anchor="middle" font-size="10" fill="${t>.55?'white':'#344f6b'}">${n<1000?nf(n):nice(n/1000)+'k'}</text>`:''}</g>`;
  }
 });
 const ly=H-14;out+=`<text x="${L}" y="${ly}" font-size="11" fill="#596778">Ít</text>`;for(let i=0;i<5;i++)out+=`<rect x="${L+23+i*19}" y="${ly-11}" width="17" height="12" rx="1" fill="rgb(${226-i*47},${237-i*31},${250-i*15})"/>`;out+=`<text x="${L+125}" y="${ly}" font-size="11" fill="#596778">Nhiều</text>`;el.innerHTML=out;
 $('release-heatmap-note').textContent=`${nf(s.dated.length)} / ${nf(currentRows.length)} phim có mốc này. ${binSize===10?'Gộp theo thập niên do khoảng thời gian dài. ':''}Năm trên hình là năm phát hành TMDb, có thể khác năm IMDb.${s.future?' '+nf(s.future)+' mốc sau ngày chốt được bỏ khỏi hình.':''}`;
}
function renderReleaseWindow(){
 const {el,W,H}=svgFrame('release-window'),s=releaseState,groups=new Map();
 for(const r of s.valid){if(!groups.has(r.year))groups.set(r.year,[]);groups.get(r.year).push(r.gap)}
 windowYearData=[...groups].sort((a,b)=>a[0]-b[0]).map(([year,vals])=>{const v=vals.sort((a,b)=>a-b);return {year,n:v.length,q1:quantileSorted(v,.25),median:quantileSorted(v,.5),q3:quantileSorted(v,.75)}});
 $('release-window-note').textContent=`${nf(s.valid.length)} / ${nf(s.pairs.length)} phim đủ hai mốc ${s.country<0?'(rạp và Digital sớm nhất toàn cầu, có thể ở hai nước khác nhau)':'tại '+releaseCountryLabel(s.country)}, có khoảng cách 0–365 ngày; loại ${nf(s.pairs.filter(r=>r.gap<0).length)} giá trị âm và ${nf(s.pairs.filter(r=>r.gap>365).length)} giá trị trên 365 ngày. Năm có ít phim cần được đọc thận trọng.`;
 if(!windowYearData.length){svgEmpty(el,W,H,'Chưa đủ hai mốc rạp và Digital');return}
 const L=43,R=17,T=28,B=37,pw=W-L-R,ph=H-T-B,lo=windowYearData[0].year-.5,hi=windowYearData.at(-1).year+.5,top=Math.max(30,Math.ceil(Math.max(...windowYearData.map(g=>g.q3))/30)*30),x=y=>L+(y-lo)/(hi-lo)*pw,y=v=>T+ph-v/top*ph;
 let out=`<text x="${L}" y="14" font-size="12" fill="#596778">Số ngày</text>`;
 for(let i=0;i<=4;i++){const v=top*i/4,yy=y(v);out+=`<line x1="${L}" x2="${W-R}" y1="${yy}" y2="${yy}" stroke="#e4e9f0"/><text x="${L-7}" y="${yy+4}" text-anchor="end" font-size="11" fill="#596778">${nice(v)}</text>`}
 const upper=windowYearData.map(g=>x(g.year)+','+y(g.q3)).join(' '),lower=[...windowYearData].reverse().map(g=>x(g.year)+','+y(g.q1)).join(' ');
 out+=`<polygon points="${upper} ${lower}" fill="#e2edf9"/><polyline points="${windowYearData.map(g=>x(g.year)+','+y(g.median)).join(' ')}" fill="none" stroke="#2670bc" stroke-width="2.5"/>`;
 const tickStep=Math.max(1,Math.ceil(windowYearData.length/6));
 windowYearData.forEach((g,i)=>{out+=`<circle cx="${x(g.year)}" cy="${y(g.median)}" r="4" fill="#2670bc"><title>${g.year}: trung vị ${nice(g.median)} ngày, 25–75% ${nice(g.q1)}–${nice(g.q3)} ngày · ${nf(g.n)} phim</title></circle>`;if(i%tickStep===0||i===windowYearData.length-1)out+=`<text x="${x(g.year)}" y="${H-12}" text-anchor="middle" font-size="11" fill="#596778">${g.year}</text>`});el.innerHTML=out;
}
function renderReleaseCountries(){
 const counts=new Map(),mode=Number($('release-mode').value),selected=selectedReleaseCountry();
 for(const m of currentRows){const seen=new Set();for(const r of m.releaseEvents)if((mode<0||r[2]===mode)&&r[3]<=releaseCutoff)seen.add(r[1]);for(const c of seen)counts.set(c,(counts.get(c)||0)+1)}
 countryCounts=[...counts].map(([country,n])=>({country,n})).sort((a,b)=>b.n-a.n||a.country-b.country);
 const top=countryCounts.slice(0,8),extra=countryCounts.find(d=>d.country===selected);
 if(extra&&!top.some(d=>d.country===selected))top.push(extra);
 svgBars('release-countries',top.map(d=>({label:countryName(payload.releases.countries[d.country]),value:d.n,color:d.country===selected?'#2670bc':'#a4c5e8'})),{format:nf,height:310});
}
function renderProviders(){
 const mode=$('watch-mode').value,kinds=mode==='streaming'?new Set([0,1,2]):new Set([payload.watch.kinds.indexOf(mode)]),counts=new Map();let found=0;
 for(const m of currentRows){const providers=new Set(m.usWatch.filter(r=>kinds.has(r[1])).map(r=>r[2]));if(providers.size)found++;for(const p of providers)counts.set(p,(counts.get(p)||0)+1)}
 providerCounts=[...counts].map(([provider,n])=>({provider:payload.watch.providers[provider],n})).sort((a,b)=>b.n-a.n||a.provider.localeCompare(b.provider));
 svgBars('release-providers',providerCounts.slice(0,8).map(d=>({label:d.provider,value:d.n})),{format:nf,height:310,leftWidth:Math.min(205,$('release-providers').clientWidth*.48)});
 $('release-providers-note').textContent=`${nf(found)} / ${nf(currentRows.length)} phim có nơi xem thuộc hình thức đang chọn tại Mỹ. Mỗi phim chỉ được đếm một lần trên mỗi dịch vụ; một phim có thể có trên nhiều dịch vụ. Phạm vi Mỹ được giữ khi đổi thị trường phát hành. Đây là ảnh chụp 2026, không phải lịch sử danh mục.`;
}
function applyTableView(){
 const table=$('movie-table').closest('table');
 for(const tr of table.rows){if(tr.cells.length===1){tr.cells[0].colSpan=activeView==='ratings'?4:activeView==='releases'?5:6;continue}tr.cells[4].hidden=activeView!=='torrents';tr.cells[5].hidden=activeView==='ratings'}
}
function selectedReleaseProfile(m){
 const country=selectedReleaseCountry(),name=releaseCountryLabel(country);
 const events=m.releaseEvents.filter(r=>country<0||r[1]===country).sort((a,b)=>a[3]-b[3]||a[1]-b[1]);
 return `<h3>Lịch phát hành ${country<0?'tại mọi thị trường':'tại '+esc(name)}</h3>`+(events.length?`<div class="timeline">${events.map(r=>`<div><span>TMDb · ${country<0?esc(countryName(payload.releases.countries[r[1]]))+' · ':''}${releaseModeNames[r[2]]}</span>${dateText(isoDay(r[3]))}${r[3]>releaseCutoff?' · sau ngày chốt, chưa tính vào biểu đồ':''}</div>`).join('')}</div>`:'<p>Chưa có mốc phát hành được ghi nhận tại thị trường này.</p>');
}
function initPhases(){
 initBusiness();
 const options=payload.releases.countries.map((code,i)=>({code,i,label:countryName(code)})).sort((a,b)=>(a.code==='US'?-1:b.code==='US'?1:a.code==='VN'?-1:b.code==='VN'?1:a.label.localeCompare(b.label,'vi')));
 {const all=document.createElement('option');all.value='-1';all.textContent='Tất cả thị trường (mốc sớm nhất)';$('release-country').append(all)}
 for(const item of options){const option=document.createElement('option');option.value=item.i;option.textContent=item.label+' ('+item.code+')';$('release-country').append(option)}
 $('release-country').value=String(payload.releases.countries.indexOf('US'));
 $('release-cutoff-note').textContent=`Tính các mốc đến ${dateText(payload.method.release_cutoff)}; lịch tương lai được loại riêng.`;
 for(const b of document.querySelectorAll('[data-view]')){
  b.onclick=()=>switchView(b.dataset.view);
  b.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const names=Object.keys(phaseConfig),i=names.indexOf(b.dataset.view),next=e.key==='Home'?0:e.key==='End'?2:(i+(e.key==='ArrowRight'?1:2))%3;switchView(names[next]);$('view-tab-'+names[next]).focus()};
 }
 for(const b of document.querySelectorAll('[data-go-view]'))b.onclick=()=>{switchView(b.dataset.goView);$('phase-title').scrollIntoView({block:'start',behavior:'smooth'})};
 for(const b of document.querySelectorAll('[data-period]'))b.onclick=()=>{const [a,c]=b.dataset.period.split('-');$('year-min').value=a;$('year-max').value=c;update()};
 initYearFilter();
 $('release-country').onchange=update;$('release-mode').onchange=update;$('watch-mode').onchange=renderProviders;$('ranking-votes').onchange=renderRanking;
 const canvas=$('rating-scatter');
 const nearest=e=>{const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;let found=null,best=70;for(const p of ratingPoints){const d=(p.x-x)**2+(p.y-y)**2;if(d<best){found=p.m;best=d}}return found};
 canvas.addEventListener('pointermove',e=>{const m=nearest(e);canvas.style.cursor=m?'pointer':'default';if(!m){$('tooltip').hidden=true;return}$('tooltip').innerHTML=`${esc(m.title)} (${m.year})<small>${nice(m.rating)} điểm · ${nf(m.votes)} bình chọn</small>`;$('tooltip').hidden=false;$('tooltip').style.left=Math.max(5,Math.min(innerWidth-310,e.clientX+15))+'px';$('tooltip').style.top=Math.max(5,e.clientY-65)+'px'});
 canvas.addEventListener('pointerleave',()=>{$('tooltip').hidden=true});canvas.addEventListener('click',e=>{const m=nearest(e);if(m){$('tooltip').hidden=true;openMovie(m.id)}});
}

// Bốn biểu đồ chỉ dùng IMDb: điểm theo năm, theo thời lượng, theo số vùng có tên riêng và theo cặp thể loại.
let ratingYearData=[],runtimeData=[],regionData=[],genrePairData=null;
function boxRowsSvg(id,rows,{left=150}={}){
 const {el,W,H}=svgFrame(id),data=rows.filter(r=>r.values.length);
 for(const r of data){const s=r.values.sort((a,b)=>a-b);Object.assign(r,{n:s.length,p10:quantileSorted(s,.1),q1:quantileSorted(s,.25),median:quantileSorted(s,.5),q3:quantileSorted(s,.75),p90:quantileSorted(s,.9)})}
 if(!data.length){svgEmpty(el,W,H);return data}
 const L=Math.min(left,W*.42),R=30,T=13,B=34,pw=W-L-R,step=(H-T-B)/rows.length,x=v=>L+v/10*pw;
 let out='';for(let v=0;v<=10;v+=2)out+=`<line x1="${x(v)}" x2="${x(v)}" y1="${T}" y2="${H-B}" stroke="#e4e9f0"/><text x="${x(v)}" y="${H-13}" text-anchor="middle" font-size="11" fill="#596778">${v}</text>`;
 rows.forEach((g,i)=>{const y=T+step*(i+.45);
  if(!g.values.length){out+=`<text x="0" y="${y+4}" font-size="13" fill="#9aa6b4">${esc(g.label)} · không có phim</text>`;return}
  out+=`<g><title>${esc(g.label)}: trung vị ${nice(g.median)}, khoảng 25–75% ${nice(g.q1)}–${nice(g.q3)} · ${nf(g.n)} phim${g.extra?' · '+g.extra:''}</title><text x="0" y="${y-1}" font-size="13" fill="#26364a">${esc(g.label)}</text><text x="0" y="${y+13}" font-size="10" fill="#647488">${nf(g.n)} phim${g.sub?' · '+esc(g.sub):''}</text><line x1="${x(g.p10)}" x2="${x(g.p90)}" y1="${y}" y2="${y}" stroke="#739ac3"/><rect x="${x(g.q1)}" y="${y-8}" width="${Math.max(1,x(g.q3)-x(g.q1))}" height="16" fill="#b4d0ee"/><line x1="${x(g.median)}" x2="${x(g.median)}" y1="${y-9}" y2="${y+9}" stroke="#16599d" stroke-width="3"/><text x="${x(g.p90)+5}" y="${y+4}" font-size="11" fill="#16599d">${nice(g.median)}</text></g>`;
 });el.innerHTML=out;return data;
}
function renderRatingYear(){
 // Luôn vẽ đủ 1920–2024 để thấy xu hướng; các bộ lọc khác (thể loại, bình chọn, tên) vẫn áp dụng.
 const {el,W,H}=svgFrame('rating-year'),f=getFilters(),pool=movies.filter(m=>Number.isFinite(m.rating)&&matches(m,{...f,min:payload.method.year_min,max:payload.method.year_max})),byYear=new Map();
 for(const m of pool){if(!byYear.has(m.year))byYear.set(m.year,[]);byYear.get(m.year).push(m.rating)}
 ratingYearData=[...byYear].filter(([,v])=>v.length>=20).sort((a,b)=>a[0]-b[0]).map(([year,v])=>{const s=v.sort((a,b)=>a-b);return {year,n:s.length,q1:quantileSorted(s,.25),median:quantileSorted(s,.5),q3:quantileSorted(s,.75)}});
 const y0=payload.method.year_min,y1=payload.method.year_max;
 $('rating-year-note').textContent=`${nf(pool.length)} phim (mọi năm 1920–2024, theo các bộ lọc khác); chỉ vẽ năm có từ 20 phim. Vùng tô cam là khoảng năm đang lọc (${f.min}–${f.max}); biểu đồ này cố ý hiện mọi năm để thấy xu hướng dài hạn, các bộ lọc khác vẫn áp dụng. Phim cũ còn được xem và chấm đến nay thường là phim hay (thiên lệch sống sót), nên điểm cao hơn không có nghĩa phim xưa hay hơn.`;
 if(ratingYearData.length<2){svgEmpty(el,W,H);return}
 const lo=Math.max(0,Math.floor(Math.min(...ratingYearData.map(d=>d.q1))-.5)),hi=Math.min(10,Math.ceil(Math.max(...ratingYearData.map(d=>d.q3))+.5));
 const L=40,R=14,T=24,B=36,x=yr=>L+(yr-y0)/(y1-y0)*(W-L-R),y=v=>T+(hi-v)/(hi-lo)*(H-T-B);
 let out=`<text x="${L}" y="13" font-size="12" fill="#596778">Điểm IMDb</text>`;
 const a=Math.max(f.min,y0),b=Math.min(f.max,y1);if(a<=b)out+=`<rect x="${x(a)}" y="${T}" width="${Math.max(2,x(b)-x(a))}" height="${H-T-B}" fill="#fdf3e8"/>`;
 for(let v=lo;v<=hi;v++)out+=`<line x1="${L}" x2="${W-R}" y1="${y(v)}" y2="${y(v)}" stroke="#e4e9f0"/><text x="${L-7}" y="${y(v)+4}" text-anchor="end" font-size="11" fill="#596778">${v}</text>`;
 for(let yr=1920;yr<=2020;yr+=20)out+=`<text x="${x(yr)}" y="${H-B+18}" text-anchor="middle" font-size="11" fill="#596778">${yr}</text>`;
 out+=`<path d="${ratingYearData.map((d,i)=>(i?'L':'M')+x(d.year).toFixed(1)+' '+y(d.q3).toFixed(1)).join('')}${[...ratingYearData].reverse().map(d=>'L'+x(d.year).toFixed(1)+' '+y(d.q1).toFixed(1)).join('')}Z" fill="#cfe0f3"/>`;
 out+=`<path d="${ratingYearData.map((d,i)=>(i?'L':'M')+x(d.year).toFixed(1)+' '+y(d.median).toFixed(1)).join('')}" fill="none" stroke="#16599d" stroke-width="2.2"/>`;
 const w=Math.max(2,(W-L-R)/(y1-y0+1));for(const d of ratingYearData)out+=`<rect x="${x(d.year)-w/2}" y="${T}" width="${w}" height="${H-T-B}" fill="transparent"><title>${d.year}: trung vị ${nice(d.median)} · 25–75%: ${nice(d.q1)}–${nice(d.q3)} · ${nf(d.n)} phim</title></rect>`;
 out+=`<g font-size="11" fill="#596778"><rect x="${W-R-215}" y="4" width="12" height="9" fill="#cfe0f3"/><text x="${W-R-199}" y="12">25–75% phim</text><rect x="${W-R-118}" y="7" width="12" height="3" fill="#16599d"/><text x="${W-R-102}" y="12">Trung vị</text></g>`;
 el.innerHTML=out;
}
function renderRatingRuntime(){
 const rated=currentRows.filter(m=>Number.isFinite(m.rating)&&Number.isFinite(m.runtime)&&m.runtime>0);
 const bins=[['Dưới 90 phút',0,90],['90–119 phút',90,120],['120–149 phút',120,150],['Từ 150 phút',150,Infinity]];
 runtimeData=boxRowsSvg('rating-runtime',bins.map(([label,a,b])=>({label,values:rated.filter(m=>m.runtime>=a&&m.runtime<b).map(m=>m.rating)})));
 $('rating-runtime-note').textContent=`${nf(rated.length)} phim có thời lượng trên IMDb. Hộp: 50% phim ở giữa; vạch đậm: trung vị; râu: 10–90%. Phim dài thường là phim chính kịch/tiểu sử, nên thể loại cũng góp phần.`;
}
function renderRatingRegions(){
 const rated=currentRows.filter(m=>Number.isFinite(m.rating));
 const bins=[['Dưới 5 vùng',0,5],['5–14 vùng',5,15],['15–29 vùng',15,30],['30–49 vùng',30,50],['Từ 50 vùng',50,Infinity]];
 regionData=boxRowsSvg('rating-regions',bins.map(([label,a,b])=>{const ms=rated.filter(m=>(m.regions||0)>=a&&(m.regions||0)<b),v=median(ms.map(m=>m.votes));return {label,values:ms.map(m=>m.rating),sub:ms.length?'trung vị '+(v>=1000?nice(v/1000)+' nghìn':nf(v))+' bình chọn':'',extra:ms.length?'bình chọn trung vị '+nf(v):''}}),{left:215});
 $('rating-regions-note').textContent=`Số vùng (quốc gia/lãnh thổ) có tên phim riêng trong IMDb title.akas, xem như mức độ phim được phát hành ra quốc tế. Phim được đặt tên ở nhiều nước cũng là phim nổi tiếng hơn, nên đây là mối liên hệ, không phải nguyên nhân.`;
}
function renderGenrePairs(){
 const box=$('genre-pairs'),bw=Math.max(270,Math.round(box.clientWidth)),cellGuess=Math.min(48,(bw-Math.min(118,bw*.26)-8)/10),Hfit=Math.round(8+10*cellGuess+86);box.style.height=Hfit+'px';
 const {el,W,H}=svgFrame('genre-pairs',Hfit),rated=currentRows.filter(m=>Number.isFinite(m.rating)),counts=new Map();
 for(const m of rated)for(const g of m.genreList)if(g!=='Adult')counts.set(g,(counts.get(g)||0)+1);
 const top=[...counts].sort((a,b)=>b[1]-a[1]).slice(0,10).map(([g])=>g),cells=new Map(),key=(a,b)=>a<b?a+'|'+b:b+'|'+a;
 for(const m of rated){const gs=m.genreList.filter(g=>top.includes(g));for(let i=0;i<gs.length;i++)for(let j=i;j<gs.length;j++){const k=key(gs[i],gs[j]);if(!cells.has(k))cells.set(k,[]);cells.get(k).push(m.rating)}}
 const all=rated.map(m=>m.rating).sort((a,b)=>a-b),overall=quantileSorted(all,.5);
 genrePairData={genres:top,overall,cells:new Map([...cells].map(([k,v])=>{const s=v.sort((a,b)=>a-b);return [k,{n:s.length,median:quantileSorted(s,.5)}]}))};
 $('genre-pairs-note').textContent=`10 thể loại có nhiều phim nhất trong nhóm đang chọn. Đường chéo: mọi phim có thể loại đó; ô khác: phim có cả hai thể loại. Màu so với trung vị chung ${overall===null?'—':nice(overall)} (xanh cao hơn, cam thấp hơn); ô dưới 30 phim để trống.`;
 if(top.length<2){svgEmpty(el,W,H);return}
 const L=Math.min(118,W*.26),T=8,B=86,size=Math.min((W-L-8)/top.length,(H-T-B)/top.length),name=g=>genreNames[g]||g;
 const color=v=>{const t=Math.max(-1,Math.min(1,(v-overall)/.8));return t>=0?`rgb(${Math.round(243-205*t)},${Math.round(245-133*t)},${Math.round(248-60*t)})`:`rgb(${Math.round(243+(229-243)*-t)},${Math.round(245+(138-245)*-t)},${Math.round(248+(54-248)*-t)})`};
 let out='';
 top.forEach((g,i)=>{out+=`<text x="${L-6}" y="${T+i*size+size/2+4}" text-anchor="end" font-size="11" fill="#26364a">${esc(name(g))}</text><text transform="translate(${L+i*size+size/2+4},${T+top.length*size+6}) rotate(-50)" text-anchor="end" font-size="11" fill="#26364a">${esc(name(g))}</text>`});
 top.forEach((a,i)=>top.forEach((b,j)=>{if(j>i)return;const c=genrePairData.cells.get(key(a,b)),xx=L+j*size,yy=T+i*size;
  if(!c||c.n<30){out+=`<rect x="${xx+1}" y="${yy+1}" width="${size-2}" height="${size-2}" fill="#f6f7f9"><title>${esc(name(a))}${a===b?'':' + '+esc(name(b))}: ${c?nf(c.n):0} phim (dưới 30, không tô)</title></rect>`;return}
  const v=(c.median-overall)/.8;out+=`<g><title>${esc(name(a))}${a===b?'':' + '+esc(name(b))}: trung vị ${nice(c.median)} · ${nf(c.n)} phim</title><rect x="${xx+1}" y="${yy+1}" width="${size-2}" height="${size-2}" rx="2" fill="${color(c.median)}" ${a===b?'stroke="#26364a" stroke-width="1"':''}/>${size>=30?`<text x="${xx+size/2}" y="${yy+size/2+4}" text-anchor="middle" font-size="${size>=40?11:10}" fill="${Math.abs(v)>.6?'white':'#26364a'}">${nice(c.median)}</text>`:''}</g>`}));
 el.innerHTML=out;
}

// Bộ lọc năm: thanh kéo hai đầu + biểu đồ cột mini + ô nhập (áp dụng khi Enter hoặc rời ô).
const yearCounts=new Map();for(const m of movies)yearCounts.set(m.year,(yearCounts.get(m.year)||0)+1);
const YEAR_MIN=1920,YEAR_MAX=2024;
function yearValues(){return [Number($('year-min').value),Number($('year-max').value)]}
function syncYearUI(live){
 const [a,b]=live||yearValues(),ok=Number.isInteger(a)&&Number.isInteger(b)&&a>=YEAR_MIN&&b<=YEAR_MAX&&a<=b;
 $('year-label').textContent=ok?(a===b?String(a):a+' – '+b):'—';
 if(ok){$('year-slider-min').value=a;$('year-slider-max').value=b}
 const pos=v=>(v-YEAR_MIN)/(YEAR_MAX-YEAR_MIN)*100;
 $('year-fill').style.left=(ok?pos(a):0)+'%';$('year-fill').style.width=(ok?pos(b)-pos(a):0)+'%';
 const top=Math.max(...yearCounts.values()),w=210/(YEAR_MAX-YEAR_MIN+1);let out='';
 for(let y=YEAR_MIN;y<=YEAR_MAX;y++){const n=yearCounts.get(y)||0,h=Math.max(n?1:0,n/top*27);out+=`<rect x="${(y-YEAR_MIN)*w}" y="${28-h}" width="${w+.15}" height="${h}" fill="${ok&&y>=a&&y<=b?'#2670bc':'#cfdbe8'}"/>`}
 $('year-spark').innerHTML=out;
 for(const btn of document.querySelectorAll('[data-period]'))btn.classList.toggle('active',ok&&btn.dataset.period===a+'-'+b);
}
function initYearFilter(){
 const smin=$('year-slider-min'),smax=$('year-slider-max');
 // Khi kéo: chỉ đổi nhãn, ô nhập và thanh màu; dashboard cập nhật khi thả tay.
 const drag=which=>{let a=Number(smin.value),b=Number(smax.value);if(a>b){if(which==='min')a=b;else b=a;smin.value=a;smax.value=b}$('year-min').value=a;$('year-max').value=b;syncYearUI([a,b])};
 smin.addEventListener('input',()=>drag('min'));smax.addEventListener('input',()=>drag('max'));
 smin.addEventListener('change',update);smax.addEventListener('change',update);
 // Hai núm có thể chồng nhau (ví dụ 2021–2023): đưa núm gần điểm bấm lên trên; trùng nhau thì bấm bên trái nắm núm năm đầu.
 const pick=e=>{const r=smin.getBoundingClientRect(),v=YEAR_MIN+(e.clientX-r.left-8)/Math.max(1,r.width-16)*(YEAR_MAX-YEAR_MIN),a=Number(smin.value),b=Number(smax.value);
  const useMin=Math.abs(v-a)<Math.abs(v-b)||(Math.abs(v-a)===Math.abs(v-b)&&v<=a);smin.style.zIndex=useMin?3:1;smax.style.zIndex=useMin?1:3};
 smin.parentElement.addEventListener('pointerdown',pick,true);smin.parentElement.addEventListener('mousemove',pick);
 // Ô nhập: chuẩn hóa (giới hạn 1920–2024, tự đổi chỗ nếu năm đầu lớn hơn) khi nhấn Enter hoặc rời ô.
 const commit=()=>{let [a,b]=yearValues();if(!Number.isFinite(a))a=YEAR_MIN;if(!Number.isFinite(b))b=YEAR_MAX;a=Math.min(YEAR_MAX,Math.max(YEAR_MIN,Math.round(a)));b=Math.min(YEAR_MAX,Math.max(YEAR_MIN,Math.round(b)));if(a>b)[a,b]=[b,a];$('year-min').value=a;$('year-max').value=b;update()};
 for(const id of ['year-min','year-max']){$(id).addEventListener('change',commit);$(id).addEventListener('keydown',e=>{if(e.key==='Enter')commit()})}
 syncYearUI();
}
