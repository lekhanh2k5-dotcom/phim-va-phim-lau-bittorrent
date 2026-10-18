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
 // Tab Torrent dùng ô Thị trường cho hai biểu đồ theo thị trường; ô Hình thức chỉ dùng ở tab Phát hành.
 $('release-controls').hidden=name==='ratings';$('release-mode').parentElement.style.display=name==='releases'?'':'none';
 document.querySelectorAll('[data-torrent-filter]').forEach(el=>el.hidden=name!=='torrents');
 $('demo-note').hidden=true;$('tooltip').hidden=true;
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
 if(activeView==='ratings'){renderRatingHistogram();renderRatingGenres();renderRatingScatter();renderRanking()}
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
 $('release-heatmap-caption').textContent=`${releaseModeLabel(s.mode)} · ${releaseCountryLabel(s.country)}${s.country<0||s.mode<0?' · mốc sớm nhất của mỗi phim':''}. Di chuột vào ô để xem số phim.`;
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
 for(const b of document.querySelectorAll('[data-period]'))b.onclick=()=>{$('year-min').value=b.dataset.period==='long'?1980:2021;$('year-max').value=b.dataset.period==='long'?2024:2023;update()};
 $('release-country').onchange=update;$('release-mode').onchange=update;$('watch-mode').onchange=renderProviders;$('ranking-votes').onchange=renderRanking;
 const canvas=$('rating-scatter');
 const nearest=e=>{const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;let found=null,best=70;for(const p of ratingPoints){const d=(p.x-x)**2+(p.y-y)**2;if(d<best){found=p.m;best=d}}return found};
 canvas.addEventListener('pointermove',e=>{const m=nearest(e);canvas.style.cursor=m?'pointer':'default';if(!m){$('tooltip').hidden=true;return}$('tooltip').innerHTML=`${esc(m.title)} (${m.year})<small>${nice(m.rating)} điểm · ${nf(m.votes)} bình chọn</small>`;$('tooltip').hidden=false;$('tooltip').style.left=Math.max(5,Math.min(innerWidth-310,e.clientX+15))+'px';$('tooltip').style.top=Math.max(5,e.clientY-65)+'px'});
 canvas.addEventListener('pointerleave',()=>{$('tooltip').hidden=true});canvas.addEventListener('click',e=>{const m=nearest(e);if(m){$('tooltip').hidden=true;openMovie(m.id)}});
}
