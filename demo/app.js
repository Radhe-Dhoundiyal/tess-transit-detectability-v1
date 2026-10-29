'use strict';
(() => {
  const data = window.RECORDED_DATA, curve = window.CURVE_DATA;
  const $ = id => document.getElementById(id);
  const modes = ['real','synthetic','model','normalization'];
  const state = {mode:'real', selected:null, page:0, coordinate:'phase'};
  const pageSize = 8;
  function el(tag, text, cls) { const n=document.createElement(tag); if(text!==undefined)n.textContent=String(text); if(cls)n.className=cls; return n; }
  function category(r) { const s=r.outcome; return s.includes('OUTSIDE')?'outside':s.includes('NOT_RECOVERED')?'nonrecovery':s.includes('HARMONIC')?'harmonic':s.includes('ALIAS')?'alias':'direct'; }
  const labels={direct:'Direct recovery',harmonic:'Harmonic recovery',alias:'Alias',nonrecovery:'Not recovered',outside:'Outside search range'};
  function cleanPath(s) { s=String(s); const marker='TESS-Transit-Detectability'; const at=s.indexOf(marker); if(at>=0)return s.slice(at+marker.length).replace(/^[\\/]+/,'').replaceAll('\\','/'); return /^[A-Z]:[\\/]/i.test(s)?'[local workspace]/'+s.split(/[\\/]/).pop():s; }
  function cleanRow(row) { return Object.fromEntries(Object.entries(row).map(([k,v])=>[k,typeof v==='string'?cleanPath(v):v])); }
  function addField(dl,label,value,wrapped=false) { const dt=el('dt',label), dd=el('dd',value===undefined||value===null||value===''?'Not recorded':value); if(wrapped){const group=el('div');group.append(dt,dd);dl.append(group);}else dl.append(dt,dd); }
  function sourceBlock(source) { const box=el('div',undefined,'source-id'); box.append(el('strong',cleanPath(source.original_path)),el('br'),el('span','SHA-256: '+source.sha256,'hash')); return box; }
  function rowsForMode() { const q=$('search').value.trim().toLowerCase(), c=$('outcome-filter').value; const preferred=state.mode==='real'?'WASP-127 b':'IR-01-05'; const ordered=[...data[state.mode]].sort((a,b)=>a.id===preferred?-1:b.id===preferred?1:0); return ordered.filter(r=>(c==='all'||category(r)===c)&&(!q||[r.id,r.host,r.outcome,r.raw.match_class||''].join(' ').toLowerCase().includes(q))); }
  function buildFilter() { const categories=state.mode==='real'?['direct','harmonic','alias','nonrecovery','outside']:['direct','harmonic','alias','nonrecovery']; $('outcome-filter').replaceChildren(); const all=el('option','All outcomes');all.value='all';$('outcome-filter').append(all); for(const c of categories){const n=data[state.mode].filter(r=>category(r)===c).length;const o=el('option',labels[c]+' · '+n);o.value=c;$('outcome-filter').append(o);} }
  function renderList() {
    const rows=rowsForMode(), pages=Math.max(1,Math.ceil(rows.length/pageSize)); state.page=Math.min(state.page,pages-1);
    $('count').textContent=`${rows.length} of ${data[state.mode].length} recorded cases`;
    $('page-count').textContent=`${state.page+1} / ${pages}`;
    $('previous').disabled=state.page===0; $('next').disabled=state.page>=pages-1;
    $('list').replaceChildren();
    const visible=rows.slice(state.page*pageSize,(state.page+1)*pageSize);
    if(!visible.length){$('list').append(el('p','No matching recorded cases.','chart-caption')); showEmpty(); return;}
    for(const r of visible){ const b=el('button'); b.type='button';b.dataset.id=r.id; b.setAttribute('aria-label','View '+r.id); b.setAttribute('aria-pressed','false'); b.append(el('span',r.title,'record-name'),el('small',labels[category(r)],category(r)));b.addEventListener('click',()=>showRecord(r));$('list').append(b); }
    showRecord(visible.find(r=>r.id===state.selected)||visible[0]);
  }
  function showEmpty() { state.selected=null; $('case-title').textContent='No matching case'; $('case-outcome').textContent='';$('case-ambiguity').textContent='';$('parameters').replaceChildren();$('case-note').textContent='Change the search or outcome filter to inspect a saved record.';$('curve-region').hidden=true;$('curve-controls').hidden=true;$('no-curve').hidden=false;$('no-curve-note').textContent='No record is selected.';$('matrix-region').hidden=true;$('record-source').replaceChildren();$('original-row').textContent='';$('match-details').replaceChildren(); }
  function showRecord(r) {
    state.selected=r.id;
    document.querySelectorAll('#list button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.id===r.id)));
    $('case-title').textContent=r.title; $('case-kind').textContent=state.mode==='real'?'Known catalogue signal':'Accepted synthetic trial';
    $('case-outcome').textContent=labels[category(r)];$('case-outcome').className=category(r);
    $('case-ambiguity').textContent=state.mode==='real'&&r.raw.ambiguity_flag==='True'?'Ambiguity flagged':'';
    $('parameters').replaceChildren();
    addField($('parameters'),state.mode==='real'?'Catalogue period (days)':'Injected period (days)',r.period,true);
    addField($('parameters'),'Candidate period (days)',r.candidate_period,true);
    addField($('parameters'),state.mode==='real'?'Candidate rank':'Requested model depth (ppm)',state.mode==='real'?r.candidate_rank:r.raw.depth_ppm,true);
    addField($('parameters'),state.mode==='real'?'Truth eligibility':'Expected SNR',state.mode==='real'?r.raw.truth_eligibility_status:r.raw.expected_snr,true);
    $('match-details').replaceChildren();
    const keys=state.mode==='real'?['match_class','primary_recovery_success','epoch_matches','epoch_offset','epoch_tolerance','phase_drift','duration_matches','ambiguity_flag','searched_min_period','searched_max_period']:['recovery_class','primary_recovery_success','top10_direct_or_harmonic_recovery','candidate_rank','epoch','search_status','normalization_status','preflight_status'];
    for(const key of keys)if(key in r.raw)addField($('match-details'),key.replaceAll('_',' '),r.raw[key]);
    const hasCurve=state.mode==='real'&&r.id===curve.planet&&r.raw.selection_unit_id===curve.selection_unit_id&&r.host===curve.host;
    $('curve-region').hidden=!hasCurve; $('curve-controls').hidden=!hasCurve; $('no-curve').hidden=hasCurve; $('matrix-region').hidden=state.mode!=='synthetic';
    $('plot-title').textContent=state.mode==='real'?'Retained TESS observations':'Recorded synthetic experiment';
    $('case-note').textContent=state.mode==='real'?'Saved catalogue-matching outcome · candidate parameters are historical.':`Host ${r.host} · stored ${r.raw.search_status||'search'} result · no injection is executed.`;
    $('no-curve-note').textContent=state.mode==='real'?'This case has a saved outcome, but matching time-series arrays are not bundled in this interface.':'Historical injected-flux arrays are not retained. The original trial parameters and outcome are shown.';
    $('original-row').textContent=JSON.stringify(cleanRow(r.raw),null,2);
    $('record-source').replaceChildren(sourceBlock(data.sources[state.mode]));
    $('record-source').append(el('p','Complete source paths and identities are retained in the package manifest. Absolute local path prefixes are omitted from the recording interface.'));
    if(hasCurve){const p=el('p',`TIC ${curve.tic} · sectors ${curve.products.map(x=>x.sector).join(', ')} · PDCSAP_FLUX → PRIMARY preprocessing → final_keep. Stored detrended relative flux is dimensionless and zero-centered.`);$('record-source').append(p,el('p',`Catalogue fold: P = ${curve.period_days} days; epoch = ${curve.epoch_btjd} BTJD. ${curve.time_unit}. Formula: ${curve.phase_formula}.`));for(const product of curve.products){$('record-source').append(el('p',`${product.processed_path}\nSHA-256: ${product.processed_sha256}`,'hash'));} drawCurve();}
    if(state.mode==='synthetic'){document.querySelectorAll('#matrix button').forEach(b=>{const active=b.dataset.id===r.id;b.setAttribute('aria-pressed',String(active));b.tabIndex=active?0:-1;});}
    $('selection-status').textContent=r.title+' — '+labels[category(r)];
  }
  function accounting() { const entries=state.mode==='real'?[['direct',15],['harmonic',10],['alias',1],['nonrecovery',25],['outside',19]]:[['direct',98],['harmonic',25],['alias',12],['nonrecovery',185]];$('accounting').replaceChildren();for(const [c,n] of entries){const s=el('span',undefined,c);s.append(el('b',n+' '),document.createTextNode(labels[c]));$('accounting').append(s);} $('accounting').append(el('span',state.mode==='real'?'51 eligible · 70 total':'123/320 direct or harmonic','scope')); }
  function renderMatrix() { const hostOrders=[...new Set(data.synthetic.map(r=>Number(r.raw.benchmark_order)))].sort((a,b)=>a-b); for(let i=0;i<8;i++)for(const order of hostOrders){const r=data.synthetic.find(x=>Number(x.raw.benchmark_order)===order&&Number(x.raw.injection_index)===i);if(!r)throw Error('Missing stored matrix cell');const b=el('button',undefined,category(r));b.type='button';b.dataset.id=r.id;b.title=`${r.id} · ${r.host} · ${labels[category(r)]}`;b.setAttribute('aria-label',`Inspect ${r.id}, ${r.host}, ${labels[category(r)]}`);b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>{ $('search').value='';$('outcome-filter').value='all';const all=rowsForMode();state.page=Math.floor(all.findIndex(x=>x.id===r.id)/pageSize);state.selected=r.id;renderList(); });$('matrix').append(b);} }
  function selectMode(next) { state.mode=next;document.body.dataset.mode=next;for(const id of modes){const active=id===next;$(id).setAttribute('aria-selected',String(active));$(id).tabIndex=active?0:-1;} $('records').hidden=!['real','synthetic'].includes(next);$('records').setAttribute('aria-labelledby',next==='synthetic'?'synthetic':'real');$('model-panel').hidden=next!=='model';$('normalization-panel').hidden=next!=='normalization';$('mode-context').textContent=next==='normalization'?'Actual pinned function · five synthetic model samples':next==='model'?'Saved predictions · internal host-grouped validation':'Historical records · selection does not rerun a search';if(['real','synthetic'].includes(next)){ $('rail-kind').textContent=next==='real'?'Observed':'Synthetic';$('search').value='';state.selected=null;state.page=0;buildFilter();accounting();renderList(); } }
  for(const id of modes){$(id).addEventListener('click',()=>selectMode(id));$(id).addEventListener('keydown',event=>{const n=modes.indexOf(id);let target;if(event.key==='ArrowRight')target=modes[(n+1)%4];if(event.key==='ArrowLeft')target=modes[(n+3)%4];if(event.key==='Home')target=modes[0];if(event.key==='End')target=modes[3];if(target){event.preventDefault();selectMode(target);$(target).focus();}});}
  $('search').addEventListener('input',()=>{state.page=0;renderList();});$('outcome-filter').addEventListener('change',()=>{state.page=0;renderList();});$('previous').addEventListener('click',()=>{state.page--;renderList();});$('next').addEventListener('click',()=>{state.page++;renderList();});
  function coordinates(next) {state.coordinate=next;$('phase-view').setAttribute('aria-pressed',String(next==='phase'));$('time-view').setAttribute('aria-pressed',String(next==='time'));drawCurve();}
  $('phase-view').addEventListener('click',()=>coordinates('phase'));$('time-view').addEventListener('click',()=>coordinates('time'));
  function drawCurve() {
    if($('curve-region').hidden||$('records').hidden)return;
    const canvas=$('curve'), box=canvas.getBoundingClientRect(), dpr=window.devicePixelRatio||1;
    canvas.width=Math.round(box.width*dpr);canvas.height=Math.round(box.height*dpr);
    const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);const w=box.width,h=box.height;
    const left=66,right=18,top=24,bottom=44; const xs=state.coordinate==='phase'?curve.phase:curve.time;
    const xmin=state.coordinate==='phase'?-.5:curve.time[0], xmax=state.coordinate==='phase'?.5:curve.time[curve.time.length-1];
    const ymin=-.03,ymax=.03;const x=v=>left+(v-xmin)/(xmax-xmin)*(w-left-right),y=v=>h-bottom-(v-ymin)/(ymax-ymin)*(h-top-bottom);
    ctx.clearRect(0,0,w,h);ctx.font='12px Segoe UI, sans-serif';ctx.lineWidth=1;
    for(const v of [-.03,-.015,0,.015,.03]){ctx.strokeStyle=v===0?'#3a4a5c':'#203044';ctx.beginPath();ctx.moveTo(left,y(v));ctx.lineTo(w-right,y(v));ctx.stroke();ctx.fillStyle='#a8b7cb';ctx.textAlign='right';ctx.fillText(v.toFixed(3),left-10,y(v)+4);}
    ctx.strokeStyle='#6c819b';ctx.beginPath();ctx.moveTo(left,top);ctx.lineTo(left,h-bottom);ctx.lineTo(w-right,h-bottom);ctx.stroke();
    for(let i=0;i<=4;i++){const v=xmin+(xmax-xmin)*i/4;ctx.fillStyle='#a8b7cb';ctx.textAlign='center';ctx.fillText(state.coordinate==='phase'?v.toFixed(2):v.toFixed(1),x(v),h-bottom+19);}
    ctx.save();ctx.beginPath();ctx.rect(left,top,w-left-right,h-top-bottom);ctx.clip();ctx.fillStyle='rgba(87,195,204,.48)';for(let i=0;i<xs.length;i++){ctx.beginPath();ctx.arc(x(xs[i]),y(curve.flux[i]),1.1,0,Math.PI*2);ctx.fill();}ctx.restore();
    ctx.fillStyle='#c8d7e8';ctx.textAlign='center';ctx.font='13px Segoe UI, sans-serif';ctx.fillText(state.coordinate==='phase'?'Orbital phase · catalogue ephemeris':'Time (BTJD = BJD_TDB − 2457000 days)',(w+left-right)/2,h-5);
    ctx.save();ctx.translate(14,(h+top-bottom)/2);ctx.rotate(-Math.PI/2);ctx.fillText('Detrended relative flux',0,0);ctx.restore();
    ctx.textAlign='right';ctx.font='11px Segoe UI, sans-serif';ctx.fillStyle='#a8b7cb';ctx.fillText('WASP-127 · saved PRIMARY samples',w-right,13);
    const description=state.coordinate==='phase'?`Phase coordinates use the recorded catalogue period ${curve.period_days} days and epoch ${curve.epoch_btjd} BTJD.`:'Chronological coordinates use the stored BTJD timestamps. Gaps are not interpolated.';
    canvas.setAttribute('aria-label',`WASP-127 b retained TESS observations. ${description} Dimensionless zero-centered detrended flux. 8000 actual saved samples.`);
    $('curve-description').textContent=description;
    $('curve-stats').textContent='8,000 displayed / 371,497 retained samples · sectors 35, 62, 72, 89 · deterministic chronological subsample';
  }
  new ResizeObserver(()=>drawCurve()).observe($('curve'));
  const ns='http://www.w3.org/2000/svg';function svgEl(tag,attrs,text){const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;return n;}
  function calibration() {const svg=svgEl('svg',{viewBox:'0 0 640 380',role:'img','aria-label':'Original saved calibration values: mean predicted probability against observed direct-recovery rate. Dashed diagonal is perfect calibration.'});const x=v=>82+v*520,y=v=>320-v*280;
    for(let i=0;i<=5;i++){const v=i/5;svg.append(svgEl('line',{x1:82,x2:602,y1:y(v),y2:y(v),stroke:'#26374a'}),svgEl('text',{x:70,y:y(v)+4,fill:'#a8b7cb','text-anchor':'end','font-size':12},v.toFixed(1)),svgEl('text',{x:x(v),y:340,fill:'#a8b7cb','text-anchor':'middle','font-size':12},v.toFixed(1)));}
    svg.append(svgEl('line',{x1:82,x2:602,y1:320,y2:40,stroke:'#7e8fa4','stroke-dasharray':'5 6'}),svgEl('text',{x:364,y:374,fill:'#d8e3f0','text-anchor':'middle','font-size':14},'Mean predicted probability'),svgEl('text',{x:20,y:180,fill:'#d8e3f0','text-anchor':'middle','font-size':14,transform:'rotate(-90 20 180)'},'Observed direct-recovery rate'),svgEl('text',{x:460,y:23,fill:'#a8b7cb','font-size':12},'Dashed: perfect calibration'));
    for(const row of data.calibration){const tr=el('tr');for(const k of ['bin','count','bin_mean_prediction','observed_rate'])tr.append(el('td',row[k]));$('bins').append(tr);if(Number(row.count)>0){const dot=svgEl('circle',{cx:x(Number(row.bin_mean_prediction)),cy:y(Number(row.observed_rate)),r:5,fill:'#7caeff',stroke:'#d5e4ff','stroke-width':1});dot.append(svgEl('title',{},`Bin ${row.bin}; n=${row.count}; mean=${row.bin_mean_prediction}; observed=${row.observed_rate}`));svg.append(dot);}}
    $('calibration-chart').append(svg);$('calibration-source').append(sourceBlock(data.sources.calibration));
  }
  async function runDepth(button) {const buttons=[...document.querySelectorAll('[data-depth]')];buttons.forEach(b=>b.disabled=true);$('function-status').className='';$('function-status').textContent='Executing the pinned function on five synthetic samples…';$('depth-values').hidden=true;$('function-json').hidden=true;$('depth-empty').hidden=false;$('depth-empty').textContent='Waiting for the local function response…';try{if(location.protocol==='file:')throw Error('Start the local server');const response=await fetch('/api/normalization?case='+encodeURIComponent(button.dataset.depth),{cache:'no-store'});if(!response.ok)throw Error('Local function did not complete');const j=await response.json();if(j.classification!=='NEW_EXPLICITLY_SYNTHETIC_CODE_DEMONSTRATION'||j.module_sha256!=='A0D4F942E4216577C0A022B8F48BC344EF16094F6C7D4FF3793AA9085ABBB826'||j.requested_depth_ppm!==Number(button.dataset.depth)||j.max_error_ppm>=1e-6)throw Error('Unexpected function receipt');$('function-status').textContent='Actual function completed. New synthetic arithmetic demonstration only.';$('depth-empty').hidden=true;$('depth-values').hidden=false;$('function-json').hidden=false;$('depth-values').replaceChildren(el('p','Depth contract met','executed'));const dl=el('dl');addField(dl,'Requested depth',j.requested_depth_ppm+' ppm',true);addField(dl,'Realized depth',j.realized_depth_ppm.toFixed(8)+' ppm',true);addField(dl,'Absolute error',j.max_error_ppm.toExponential(3)+' ppm',true);addField(dl,'Samples',j.normalized_model.length,true);$('depth-values').append(dl,el('h3','Returned normalized model'),el('p',JSON.stringify(j.normalized_model),'sample-output'),el('p','Exact floating-point values and execution timestamp are in the receipt.','chart-caption'));$('function-output').textContent=JSON.stringify(j,null,2);}catch(error){$('function-status').className='failure';$('function-status').textContent='Function unavailable. Launch the included local Python server; no output is substituted.';$('depth-empty').hidden=false;$('depth-empty').textContent='No completed function output.';$('function-output').textContent='';}finally{buttons.forEach(b=>b.disabled=false);}}
  document.querySelectorAll('[data-depth]').forEach(b=>b.addEventListener('click',()=>runDepth(b)));
  $('fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{$('selection-status').textContent='Use the browser full-screen shortcut, F11.';}});document.addEventListener('fullscreenchange',()=>{$('fullscreen').querySelector('span').textContent=document.fullscreenElement?'Exit full screen':'Full screen';});
  renderMatrix();
  const matrixButtons=[...document.querySelectorAll('#matrix button')];
  matrixButtons.forEach((button,index)=>button.addEventListener('keydown',event=>{let target;if(event.key==='ArrowRight')target=Math.min(319,index+1);if(event.key==='ArrowLeft')target=Math.max(0,index-1);if(event.key==='ArrowDown')target=Math.min(319,index+40);if(event.key==='ArrowUp')target=Math.max(0,index-40);if(event.key==='Home')target=0;if(event.key==='End')target=319;if(target!==undefined){event.preventDefault();matrixButtons.forEach(b=>b.tabIndex=-1);matrixButtons[target].tabIndex=0;matrixButtons[target].focus();}}));
  calibration();selectMode('real');
})();
