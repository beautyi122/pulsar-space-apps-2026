'use strict';
(function(){
  const data = window.PULSAR_DATA;
  if (!data || !Array.isArray(data.records) || data.records.length !== 332) {
    document.body.textContent='Pulsar data missing or corrupted. Re-extract the complete release package.'; return;
  }
  const byId=id=>document.getElementById(id);
  const format=(v,d=1)=>v===null||v===undefined||!Number.isFinite(Number(v))?'—':Number(v).toFixed(d);
  const isGood=r=>r && r.status==='DISPLAY_WITH_CAUTION';
  const records=[...new Set(data.records.map(x=>x.id))];
  const grouped=Object.fromEntries(records.map(n=>[n,data.records.filter(x=>x.id===n).sort((a,b)=>a.index-b.index)]));
  let selected = records.includes('s3_walk') ? 's3_walk' : records[0];
  let win = 0;
  function tab(name){
    document.querySelectorAll('.tab').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.tab===name)));
    document.querySelectorAll('.view').forEach(s=>s.hidden=s.id!==name);
    if(name==='console') draw();
  }
  document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.tab)));
  const sel=byId('recordSelect');
  records.forEach(n=>{
    const exemplar=grouped[n][0];
    const opt=document.createElement('option');opt.value=n;
    opt.textContent=exemplar.sub.toUpperCase()+' · '+exemplar.activity.replaceAll('_',' ');
    sel.appendChild(opt);
  });
  sel.value=selected;
  sel.addEventListener('change',()=>{selected=sel.value;win=0;draw();});
  byId('windowSlider').addEventListener('input',e=>{win=Number(e.target.value);draw();});
  function safeXML(v){return String(v).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');}
  function chart(points){
    const svg=byId('timeChart'),W=740,H=250,left=40,right=18,top=15,bottom=36;
    const x=i=>left+(i/(Math.max(points.length-1,1)))*(W-left-right);
    const lower=45, upper=215,y=val=>top+((upper-val)/(upper-lower))*(H-top-bottom);
    function path(k){
      let s='',open=false;
      points.forEach((p,i)=>{
        const v=p[k];if(v===null||v===undefined){open=false;return;}
        s+=(open?'L':'M')+x(i).toFixed(1)+','+y(v).toFixed(1)+' ';open=true;
      });return s;
    }
    let grid='';for(const v of [60,100,140,180])grid+=`<line class="gridline" x1="${left}" y1="${y(v)}" x2="${W-right}" y2="${y(v)}"/><text x="${left-7}" y="${y(v)+4}" text-anchor="end">${v}</text>`;
    grid+=`<text x="${left}" y="${H-8}">0:00</text><text x="${W-right}" y="${H-8}" text-anchor="end">${Math.round(points.length*20/60)} MIN</text>`;
    let status='';points.forEach((p,i)=>{
      const col=isGood(p)?'#80e8c7':p.status==='REVIEW_SIGNAL'?'#e9bd7a':'#dd818d';
      status+=`<rect x="${x(i)-3.4}" y="${H-27}" width="7" height="5" rx="1" fill="${col}" opacity=".86"/>`;
    });
    let focus=`<line x1="${x(win)}" y1="${top}" x2="${x(win)}" y2="${H-bottom+7}" stroke="#f5e1ad" stroke-width="1.5" stroke-dasharray="5 6"/>`;
    const p=points[win];if(p){
      if(p.raw!==null)focus+=`<circle class="point" cx="${x(win)}" cy="${y(p.raw)}" r="5.4" fill="#92add0"/>`;
      if(p.res!==null)focus+=`<circle class="point" cx="${x(win)}" cy="${y(p.res)}" r="6" fill="#55eedb"/>`;
    }
    svg.innerHTML=grid+`<path class="rawline" d="${path('raw')}"/><path class="resline" d="${path('res')}"/>`+status+focus;
    svg.querySelectorAll('.point').forEach(c=>c.setAttribute('aria-hidden','true'));
    const transparent=document.createElementNS('http://www.w3.org/2000/svg','rect');
    transparent.setAttribute('x',left);transparent.setAttribute('y',top);transparent.setAttribute('width',W-left-right);transparent.setAttribute('height',H-top-bottom);transparent.setAttribute('fill','transparent');transparent.style.cursor='crosshair';
    transparent.addEventListener('click',event=>{
      const coord=svg.createSVGPoint();coord.x=event.clientX;coord.y=event.clientY;
      const t=svg.getScreenCTM();if(!t)return;
      const point=coord.matrixTransform(t.inverse());
      win=Math.min(points.length-1,Math.max(0,Math.round((point.x-left)/(W-left-right)*(points.length-1))));draw();
    });svg.appendChild(transparent);
  }
  function draw(){
    const points=grouped[selected]||[];
    if(win>=points.length)win=points.length-1;
    const r=points[win];if(!r)return;
    byId('windowSlider').max=points.length-1;byId('windowSlider').value=win;
    byId('windowLabel').textContent=`${win+1} of ${points.length} · ${r.t}–${r.t+20} seconds`;
    chart(points);
    byId('rawVal').innerHTML=format(r.raw,2)+' <small>bpm</small>';
    byId('resVal').innerHTML=format(r.res,2)+' <small>bpm</small>';
    const decision=byId('signalState'),ab=byId('actionBox');
    if(r.status==='DISPLAY_WITH_CAUTION'){
      decision.innerHTML='<span class="state">CAUTIOUS DISPLAY</span>';ab.className='actionbox';
      byId('qualityText').textContent='The participant-excluded research policy marked this interval as lower risk relative to others. That does not prove it represents a genuine cardiac rhythm.';
      byId('actionHeadline').textContent='Record a tentative trend, not a diagnosis';
      byId('actionText').textContent='Use as an exploratory trend only. Confirm clinically important readings with an approved sensor and follow crew medical procedures.';
    } else if(r.status==='NO_SENSOR_CANDIDATE'){
      decision.innerHTML='<span class="state none">NO READING</span>';ab.className='actionbox none';
      byId('qualityText').textContent='The input signal did not support candidate extraction in this interval.';
      byId('actionHeadline').textContent='No physiological value available';
      byId('actionText').textContent='Record the missing interval. Check sensor contact, repeat acquisition, and use an approved reference device where necessary.';
    }else{
      decision.innerHTML='<span class="state review">REVIEW REQUIRED</span>';ab.className='actionbox review';
      byId('qualityText').textContent='The signal-derived reliability score did not meet the training-derived display rule. Do not report the candidate as a trusted heart rate.';
      byId('actionHeadline').textContent='Withhold the untrusted heart-rate display';
      byId('actionText').textContent='Repeat a measurement under more stable conditions. If the uncertainty persists, log it for crew medical review rather than silently filling a value.';
    }
    byId('couplingVal').textContent=format(r.motion,2);
    byId('riskVal').textContent=r.risk!==null?format(r.risk,2):'—';
    byId('stableVal').textContent=r.stab===null?'—':r.stab?'Yes':'No';
    byId('report').hidden=true;
    updateNASABars();
  }
  byId('reportBtn').addEventListener('click',()=>{
    const r=grouped[selected][win];
    const symptom=byId('symptom').checked;
    const status=isGood(r)?'A cautiously displayable candidate exists, but it is unverified.':'Optical signal cannot support a trustworthy reported heart rate.';
    const instructions=symptom?'Symptoms are reported. Escalate according to established crew medical protocols; do not use this demonstration to rule out a health problem.':
       isGood(r)?'Continue the check-in. Verify important values with a validated measurement before decisions.':'Recheck measurement quality and log the unresolved interval for review.';
    byId('report').textContent=[
       'CREW SELF-ASSESSMENT / SIMULATED RECORD',
       'Session: '+selected+' · '+r.t+'–'+(r.t+20)+' s',
       'Sensor status: '+r.status.replaceAll('_',' '),
       'Reported heart rate: '+(isGood(r)?format(r.res,1)+' bpm (research-only tentative)':'WITHHELD'),
       'Energy: '+byId('energy').value,'Sleep: '+byId('sleep').value,
       'Exercise in progress: '+(byId('activityNote').checked?'Yes':'No'),
       'Symptoms reported: '+(symptom?'Yes':'No'),
       '',status,instructions,
       '', 'NOT MEDICAL ADVICE / NOT LIVE ASTRONAUT DATA'
    ].join('\n');
    byId('report').hidden=false;
  });
  byId('csvRun').addEventListener('click',async ()=>{
    const input=byId('csvFile'),panel=byId('csvResponse');panel.hidden=false;
    if(!input.files.length){panel.textContent='Choose a local sensor CSV file or download the synthetic example first.';return;}
    panel.textContent='Analyzing the provided local sensor window…';
    try{
      const content=await input.files[0].text();
      if(content.length>2000000)throw Error('File exceeds 2 MB');
      const res=await fetch('/api/analyze?activity='+encodeURIComponent(byId('csvActivity').value),{method:'POST',headers:{'Content-Type':'text/csv'},body:content});
      let obj=await res.json();
      if(!res.ok)throw Error(obj.error||'Local analyzer failed');
      panel.textContent=[
        'NEW RECORDING · EXPERIMENTAL ONLY',
        'Raw spectral candidate: '+format(obj.raw_candidate_bpm,2)+' bpm',
        'Separated spectral candidate: '+format(obj.motion_separated_candidate_bpm,2)+' bpm',
        'Motion predictability R²: '+format(obj.motion_prediction_out_of_fold_r2,3),
        'Uncalibrated reliability risk score: '+format(obj.development_model_uncalibrated_risk_score,3),
        'Research tier: '+obj.research_tier.replaceAll('_',' '),
        '',obj.caution
      ].join('\n');
    }catch(err){panel.textContent='Local analysis unavailable: '+err.message+'\nRun the bundled Launch.py server; opening index.html directly supports research replay but not new CSV analysis.';}
  });
  function summaries(){
    const cats=[
      ['Raw PPG · all candidates',36.3515,'99.1% candidate availability','#799ac3'],
      ['Motion-separated · all candidates',21.6855,'99.1% candidate availability','#55eedb'],
      ['Guarded display · participant-held-out',3.623,'37.7% display coverage','#ffcf7b']
    ];
    byId('summaryBars').innerHTML=cats.map(([name,mae,note],i)=>`<div class="barrow"><div>${safeXML(name)}<div class="smallnote">${safeXML(note)}</div></div><div class="bartrack"><div class="barfill ${i===2?'warn':''}" style="width:${100*mae/40}%;background:${i===0?'#799ac3':i===1?'#55eedb':'#ffcf7b'}"></div></div><b>${format(mae,2)} bpm</b></div>`).join('');
    const byA=data.meta.by_activity;
    byId('activityRows').innerHTML=Object.entries(byA).map(([a,m])=>`<tr><td>${safeXML(a.replaceAll('_',' '))}</td><td class="num">${m.windows}</td><td class="num">${m.displayed}</td><td class="num">${(m.display_coverage_all_windows*100).toFixed(1)}%</td><td class="num">${format(m.conditional_mae_bpm,2)}</td><td class="num">${m.serious_errors_ge15}/${m.displayed}</td></tr>`).join('');
    const b=data.meta.bootstrap;
    byId('ciCover').textContent=b.coverage.map(x=>(x*100).toFixed(1)+'%').join('–');
    byId('ciMae').textContent=b.mae.map(x=>x.toFixed(2)).join('–')+' bpm';
    byId('ciSerious').textContent=b.serious_rate.map(x=>(x*100).toFixed(1)+'%').join('–');
  }
  function updateNASABars(){
    const nasa=data.meta.nasa;
    const mode=byId('nasaMode').value;
    const n=nasa[mode];
    byId('nasaAvg').textContent=n.avg_hr;byId('nasaPeak').textContent=n.peak_hr;byId('nasaDuration').textContent=n.duration_min;
    const sel=grouped[selected]&&grouped[selected][win];
    const reference=[['NASA historical average HR',n.avg_hr],['NASA historical peak HR',n.peak_hr]];
    if(sel&&isGood(sel))reference.push(['Terrestrial demo candidate',sel.res]);
    byId('nasaBars').innerHTML=reference.map(([label,v],i)=>`<div class="barrow"><span>${safeXML(label)}</span><div class="bartrack"><div class="barfill ${i===2?'warn':''}" style="width:${Math.min(100,100*v/210)}%"></div></div><b>${format(v,1)} bpm</b></div>`).join('');
  }
  byId('nasaMode').addEventListener('change',updateNASABars);
  summaries();draw();
})();
