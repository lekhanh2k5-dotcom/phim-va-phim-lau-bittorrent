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
 const lag=currentRows.filter(m=>m.lag!==null&&Number.isFinite(m.lag));
 const lagBins=[{label:'Trước Digital',test:x=>x<0,color:'#8897ab'},{label:'Ngày 0–1',test:x=>x>=0&&x<=1,color:'#e58a36'},{label:'Ngày 2–7',test:x=>x>=2&&x<=7},{label:'Ngày 8–30',test:x=>x>=8&&x<=30},{label:'Sau 30 ngày',test:x=>x>30}];
 svgBars('lag-bars',lagBins.map(b=>({label:b.label,color:b.color,value:lag.filter(m=>b.test(m.lag)).length})),{format:nf});
 $('lag-note').textContent=`${nf(lag.length)} phim đủ ngày. Mốc là Digital tại Mỹ; ngày âm có thể do phim ra ở nước khác trước đó. Bộ lọc và cửa sổ thu thập ảnh hưởng kết quả.`;
 svgBars('availability-bars',[{label:'Có ghi nhận',value:currentRows.filter(m=>m.tmdb&&m.streaming===true).length},{label:'Chưa ghi nhận',value:currentRows.filter(m=>m.tmdb&&m.streaming!==true).length,color:'#a4bedc'},{label:'Thiếu TMDb',value:currentRows.filter(m=>!m.tmdb).length,color:'#aeb7c3'}],{format:nf});
 renderComparison();
}
