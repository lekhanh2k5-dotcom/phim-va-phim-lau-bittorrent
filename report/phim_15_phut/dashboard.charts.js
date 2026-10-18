function svgBars(id,items,{color='#2670bc',format=nice,height,leftWidth}={}){
 const el=$(id),W=Math.max(270,Math.round(el.clientWidth)),H=height??(id==='genre-bars'?310:210);
 el.setAttribute('viewBox',`0 0 ${W} ${H}`);
 if(!items.length){el.innerHTML=`<text x="${W/2}" y="${H/2}" text-anchor="middle" fill="#596778" font-size="14">Không có phim phù hợp</text>`;return}
 const max=Math.max(1,...items.map(d=>d.value??0)),left=leftWidth??Math.min(135,W*.36),right=62,plot=W-left-right,step=(H-10)/items.length;
 el.innerHTML=items.map((d,i)=>{
  const yy=10+i*step,bar=Math.min(23,step*.5),val=d.value??0,ww=val/max*plot;
  const subtitle=d.n!==undefined?`<text x="0" y="${yy+bar/2+16}" font-size="11" fill="#647488">${nf(d.n)} phim</text>`:'';
  const maxChars=Math.max(10,Math.floor((left-10)/7.1)),label=d.label.length>maxChars?d.label.slice(0,maxChars-1)+'…':d.label;
  return `<g><title>${esc(d.label)}: ${d.value===null?'không có phim':format(val)}${d.n!==undefined?' · '+nf(d.n)+' phim':''}</title><text x="0" y="${yy+bar/2}" dominant-baseline="middle" font-size="14" fill="#26364a">${esc(label)}</text>${subtitle}<rect x="${left}" y="${yy}" width="${plot}" height="${bar}" fill="#f0f3f7"/><rect x="${left}" y="${yy}" width="${ww}" height="${bar}" fill="${d.color||color}"/><text x="${left+ww+7}" y="${yy+bar/2}" dominant-baseline="middle" font-size="15" font-weight="600" fill="#172334">${d.value===null?'—':format(val)}</text></g>`;
 }).join('');
}
function voteColumns(items){
 const el=$('vote-bars'),W=Math.max(270,Math.round(el.clientWidth)),H=310;
 el.setAttribute('viewBox',`0 0 ${W} ${H}`);
 const max=Math.max(1,...items.map(d=>d.value??0)),magnitude=10**Math.floor(Math.log10(max)),top=Math.ceil(max/magnitude)*magnitude;
 const L=45,R=14,T=30,B=65,pw=W-L-R,ph=H-T-B,step=pw/items.length;
 let out=`<text x="${L}" y="15" font-size="12" fill="#596778">Torrent / phim</text>`;
 for(let i=0;i<=4;i++){const v=top*i/4,yy=T+ph-v/top*ph;out+=`<line x1="${L}" x2="${W-R}" y1="${yy}" y2="${yy}" stroke="#e4e9f0"/><text x="${L-7}" y="${yy}" dominant-baseline="middle" text-anchor="end" font-size="12" fill="#596778">${nice(v)}</text>`}
 const colors=['#a0c6eb','#5b98d4','#2670bc'];
 for(const [i,d] of items.entries()){
  const x=L+step*i+step/2,bw=Math.min(74,step*.58),v=d.value??0,hh=v/top*ph;
  out+=`<g><title>${esc(d.label)} bình chọn: ${d.value===null?'không có phim':nice(v)+' torrent trung vị/phim'} · ${nf(d.n)} phim</title><rect x="${x-bw/2}" y="${T+ph-hh}" width="${bw}" height="${hh}" fill="${colors[i]}"/><text x="${x}" y="${T+ph-hh-12}" text-anchor="middle" font-size="24" font-weight="650" fill="#172334">${d.value===null?'—':nice(v)}</text><text x="${x}" y="${H-B+24}" text-anchor="middle" font-size="13" fill="#172334">${esc(d.label)}</text><text x="${x}" y="${H-B+43}" text-anchor="middle" font-size="12" fill="#596778">${nf(d.n)} phim</text></g>`;
 }
 out+=`<text x="${L+pw/2}" y="${H-2}" text-anchor="middle" font-size="12" fill="#596778">Lượt bình chọn IMDb</text>`;
 el.innerHTML=out;
 const valid=items.filter(d=>d.value!==null);
 if(valid.length>=2){const a=valid[0],b=valid[valid.length-1];$('vote-callout').innerHTML=`${esc(a.label)}: <strong>${nice(a.value)}</strong> → ${esc(b.label)}: <strong>${nice(b.value)}</strong> torrent/phim.`}
 else $('vote-callout').textContent=valid.length?`Nhóm ${valid[0].label}: ${nice(valid[0].value)} torrent trung vị/phim.`:'Không có phim phù hợp.';
}
let comparisonData=[];
function renderComparison(){
 const f=getFilters();f.genre='';
 const valid=Number.isInteger(f.min)&&Number.isInteger(f.max)&&f.min>=1920&&f.max<=2024&&f.min<=f.max;
 const pool=valid?movies.filter(m=>matches(m,f)):[];
 const groups=[$('compare-a').value,$('compare-b').value].map(g=>{const ms=pool.filter(m=>m.genreList.includes(g));return {genre:g,label:genreNames[g]||g,n:ms.length,votes:median(ms.map(m=>m.votes)),torrents:median(ms.map(m=>m.torrents)),observed:ms.length?ms.filter(m=>m.torrents>0).length/ms.length:null}});
 comparisonData=groups;
 const el=$('comparison-svg'),W=Math.max(270,Math.round(el.clientWidth)),H=270,L=W<450?117:170,R=W<450?57:85,pw=W-L-R;
 el.setAttribute('viewBox',`0 0 ${W} ${H}`);
 const rows=[{key:'n',label:'Số phim',format:nf},{key:'votes',label:'Bình chọn trung vị',format:nf},{key:'torrents',label:'Torrent trung vị',format:nice},{key:'observed',label:'Có ghi nhận torrent',format:pct}];
 const font=W<450?12:14;
 let out='';
 rows.forEach((r,i)=>{
  const yy=14+i*64,max=r.key==='observed'?1:Math.max(1,...groups.map(g=>g[r.key]??0));
  out+=`<text x="0" y="${yy+22}" dominant-baseline="middle" font-size="${font}" fill="#26364a">${esc(r.label)}</text>`;
  groups.forEach((g,j)=>{const v=g[r.key],h=15,y=yy+j*23,w=(v??0)/max*pw;
   out+=`<g><title>${esc(g.label)} · ${esc(r.label)}: ${v===null?'chưa đủ dữ liệu':r.format(v)}</title><rect x="${L}" y="${y}" width="${pw}" height="${h}" fill="#f1f3f7"/><rect x="${L}" y="${y}" width="${w}" height="${h}" fill="${j?'#e58a36':'#2670bc'}"/><text x="${L+w+7}" y="${y+h/2}" dominant-baseline="middle" font-size="${font}" font-weight="600" fill="#172334">${v===null?'—':r.format(v)}</text></g>`;
  });
 });
 el.innerHTML=out;
}
function renderTorrentCharts(){
 scatter();
 const bins=[[1000,10000,'1.000–9.999'],[10000,100000,'10.000–99.999'],[100000,Infinity,'≥ 100.000']];
 voteColumns(bins.map(([a,b,label])=>{const ms=currentRows.filter(m=>m.votes>=a&&m.votes<b);return {label,value:median(ms.map(m=>m.torrents)),n:ms.length}}));
 const gs=new Map();for(const m of currentRows)for(const g of m.genreList){if(g==='Adult')continue;if(!gs.has(g))gs.set(g,[]);gs.get(g).push(m.torrents)}
 const genreItems=[...gs].sort((a,b)=>b[1].length-a[1].length).slice(0,8).map(([g,vals])=>({label:genreNames[g]||g,value:$('genre-measure').value==='films'?vals.length:median(vals),n:vals.length})).sort((a,b)=>b.value-a.value);
 svgBars('genre-bars',genreItems);
 // Tab Torrent không dùng ô Thị trường (torrent không có thông tin quốc gia); nút riêng chọn mốc Digital tại Mỹ (mặc định, như slide 19) hoặc sớm nhất thế giới.
 const usIndex=payload.releases.countries.indexOf('US'),lagCountry=$('lag-basis').value==='world'?-1:usIndex,lagUS=lagCountry===usIndex,lagPlace=marketPlace(lagCountry);
 const lagValue=m=>{if(lagUS)return m.lag;if(!m.web)return null;const d=releaseDay(m,lagCountry,1);return d===null?null:isoToDay(m.web)-d};
 const lag=currentRows.map(m=>({m,lag:lagValue(m)})).filter(r=>r.lag!==null&&Number.isFinite(r.lag));
 const lagBins=[{label:'Trước Digital',test:x=>x<0,color:'#8897ab'},{label:'Ngày 0–1',test:x=>x>=0&&x<=1,color:'#e58a36'},{label:'Ngày 2–7',test:x=>x>=2&&x<=7},{label:'Ngày 8–30',test:x=>x>=8&&x<=30},{label:'Sau 30 ngày',test:x=>x>30}];
 svgBars('lag-bars',lagBins.map(b=>({label:b.label,color:b.color,value:lag.filter(m=>b.test(m.lag)).length})),{format:nf});
 $('lag-scope').textContent=lagCountry<0?'Digital sớm nhất · mọi thị trường':'Digital '+lagPlace;
 $('lag-note').textContent=`${nf(lag.length)} phim đủ ngày. Mốc là Digital ${lagPlace}; ngày âm có thể do phim ra Digital ở nước khác trước đó. Bộ lọc và cửa sổ thu thập ảnh hưởng kết quả.`;
 svgBars('availability-bars',[{label:'Có ghi nhận',value:currentRows.filter(m=>m.tmdb&&m.streaming===true).length},{label:'Chưa ghi nhận',value:currentRows.filter(m=>m.tmdb&&m.streaming!==true).length,color:'#a4bedc'},{label:'Thiếu TMDb',value:currentRows.filter(m=>!m.tmdb).length,color:'#aeb7c3'}],{format:nf});
 renderFirstShare();
 renderComparison();
}

// Thời gian từ ngày ra rạp (sớm nhất thế giới hoặc tại Mỹ, theo nút riêng) đến bản chia sẻ đầu tiên trong cửa sổ quan sát.
// Chỉ giữ phim ra rạp đủ sớm/đủ muộn để theo dõi trọn 60 ngày trước đến 365 ngày sau.
const shareDayMin=-60,shareDayMax=365;
let firstShareState=null;
const isoToDay=s=>s?Math.round(Date.parse(s+'T00:00:00Z')/86400000):null;
function marketPlace(country){return country<0?'sớm nhất ở bất kỳ thị trường nào':'tại '+(country===payload.releases.countries.indexOf('US')?'Mỹ':releaseCountryLabel(country))}
function renderFirstShare(){
 const {el,W,H}=svgFrame('first-share',320),country=$('first-share-basis').value==='us'?payload.releases.countries.indexOf('US'):-1,place=marketPlace(country);
 const start=isoToDay(payload.method.observed_start),end=isoToDay(payload.method.observed_end_exclusive)-1;
 const cohort=[];let outside=0,noDate=0;
 for(const m of currentRows){const t=releaseDay(m,country,0);if(t===null){noDate++;continue}if(t+shareDayMin<start||t+shareDayMax>end){outside++;continue}
  cohort.push({m,t,any:m.first_share===null?null:m.first_share-t,hq:m.first_hq===null?null:m.first_hq-t})}
 const n=cohort.length;
 const curve=key=>{const v=cohort.map(r=>r[key]).filter(x=>x!==null).sort((a,b)=>a-b),pts=[];let i=0;for(let d=shareDayMin;d<=shareDayMax;d++){while(i<v.length&&v[i]<=d)i++;pts.push(n?i/n:0)}return pts};
 const any=curve('any'),hq=curve('hq'),at=(c,d)=>c[d-shareDayMin];
 firstShareState={n,outside,noDate,any,hq};
 $('first-share-scope').textContent=country<0?'Ngày ra rạp sớm nhất · mọi thị trường':'Ngày ra rạp '+place;
 $('first-share-warning').hidden=n>=50;
 $('first-share-warning').textContent=`Chỉ ${nf(n)} phim ra rạp ${place} trong khoảng theo dõi được; đường cong dao động mạnh, đọc thận trọng.`;
 if(n<10){svgEmpty(el,W,H,`Cần phim ra rạp ${place} từ 31/05/2021 đến 29/09/2023; nhóm đang chọn chỉ có ${nf(n)} phim`);$('first-share-note').textContent=`${nf(n)} phim đủ điều kiện. ${nf(noDate)} phim không có ngày ra rạp ${place}; ${nf(outside)} phim ra rạp ngoài khoảng theo dõi được.`;return}
 const L=46,R=18,T=26,B=38,x=d=>L+(d-shareDayMin)/(shareDayMax-shareDayMin)*(W-L-R),y=p=>T+(1-p)*(H-T-B);
 let out='';
 for(const p of [0,.25,.5,.75,1])out+=`<line x1="${L}" x2="${W-R}" y1="${y(p)}" y2="${y(p)}" stroke="#e3e8ee"/><text x="${L-8}" y="${y(p)+4}" text-anchor="end" font-size="11" fill="#596778">${Math.round(p*100)}%</text>`;
 for(const d of [-60,0,30,90,180,270,365])out+=`<text x="${x(d)}" y="${H-B+18}" text-anchor="middle" font-size="11" fill="#596778">${d>0?'+'+d:d}</text>`;
 out+=`<text x="${(L+W-R)/2}" y="${H-4}" text-anchor="middle" font-size="11" fill="#596778">Số ngày so với ngày ra rạp</text>`;
 out+=`<line x1="${x(0)}" x2="${x(0)}" y1="${T-6}" y2="${H-B}" stroke="#172334" stroke-dasharray="3 3"/><text x="${x(0)+5}" y="${T-10}" font-size="11" fill="#172334">Ra rạp</text>`;
 const path=c=>c.map((p,i)=>(i?'L':'M')+x(i+shareDayMin).toFixed(1)+' '+y(p).toFixed(1)).join('');
 out+=`<path d="${path(any)}" fill="none" stroke="#e58a36" stroke-width="2.5"/><path d="${path(hq)}" fill="none" stroke="#2670bc" stroke-width="2.5"/>`;
 for(const d of [0,7,30,90,180,365])for(const [c,color,label] of [[any,'#e58a36','Bản bất kỳ'],[hq,'#2670bc','Bản chất lượng cao']])
  out+=`<circle cx="${x(d)}" cy="${y(at(c,d))}" r="4" fill="${color}" stroke="white"><title>${label} · ${d>0?'+'+d:d} ngày: ${pct(at(c,d))} của ${nf(n)} phim</title></circle>`;
 const lx=Math.max(x(30),W-R-330),ly=y(.18);out+=`<g font-size="12"><rect x="${lx}" y="${ly-4}" width="14" height="3" fill="#e58a36"/><text x="${lx+19}" y="${ly}" fill="#172334">Bản bất kỳ</text><rect x="${lx+100}" y="${ly-4}" width="14" height="3" fill="#2670bc"/><text x="${lx+119}" y="${ly}" fill="#172334">Bản chất lượng cao (WEB, đĩa, TV)</text></g>`;
 el.innerHTML=out;
 $('first-share-note').textContent=`${nf(n)} phim ra rạp ${place} từ ${dateText(isoDay(start-shareDayMin))} đến ${dateText(isoDay(end-shareDayMax))}. Ngày ra rạp: ${pct(at(any,0))} đã có bản bất kỳ; sau 30 ngày: ${pct(at(any,30))} có bản bất kỳ, ${pct(at(hq,30))} có bản chất lượng cao; sau 365 ngày: ${pct(at(hq,365))} có bản chất lượng cao. Chỉ tính bản ghi nhận trong cửa sổ quan sát; ${nf(noDate)} phim không có ngày ra rạp ${place} và ${nf(outside)} phim ra rạp ngoài khoảng theo dõi được không được tính. Đây là thời điểm hệ thống ghi nhận, không phải lượt tải.${country<0?' Mốc sớm nhất thế giới có thể là suất chiếu giới hạn hoặc liên hoan phim, sớm hơn ngày chiếu đại trà.':''}`;
}
