/* Pulsar — Orbital Clinic interactive presentation. No analytics or telemetry. */
(() => {
  'use strict';
  const $ = (s,root=document) => root.querySelector(s);
  const $$ = (s,root=document) => Array.from(root.querySelectorAll(s));
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const data = window.PULSAR_DATA;
  const nav = $('.nav'), consoleView = $('#console');
  if (!nav || !consoleView || !data || !Array.isArray(data.records)) return;
  const records = data.records;
  const byRecording = new Map();
  for(const item of records){if(!byRecording.has(item.id)) byRecording.set(item.id,[]);byRecording.get(item.id).push(item);}
  for(const items of byRecording.values()) items.sort((a,b)=>a.index-b.index);
  const safeNumber = (n,d=1) => typeof n==='number' && Number.isFinite(n) ? n.toFixed(d) : '—';
  const activeSeries = () => byRecording.get($('#recordSelect')?.value) || [];
  const activeWindow = () => {
    const items=activeSeries();return items[Math.max(0,Math.min(items.length-1,Number($('#windowSlider')?.value)||0))]||null;
  };
  const travelTo = (tab,anchor) => {
    const button=$(`.tab[data-tab="${tab}"]`);if(button) button.click();
    const target=anchor?document.getElementById(anchor):document.getElementById(tab);
    if(target) target.scrollIntoView({behavior:reduce.matches?'instant':'smooth',block:'start'});
  };
  function button(text,cls,fn){const b=document.createElement('button');b.type='button';b.className=cls;b.textContent=text;b.addEventListener('click',fn);return b;}
  const stage=document.createElement('section');
  stage.id='launch';stage.className='launch-stage';stage.setAttribute('aria-labelledby','launch-title');
  stage.innerHTML=`
    <div class="launch-copy">
      <div class="launch-kicker">STELLA NOVA &nbsp; / &nbsp; ASTRONAUT HEALTH RESEARCH</div>
      <h1 id="launch-title"><span>Pulsar</span></h1>
      <h2>When a signal looks certain, we ask if it deserves to be trusted.</h2>
      <p>An astronaut-health research demonstrator that explores motion-aware wrist sensing, measurement reliability and crew self-assessment. Built around real terrestrial exercise recordings.</p>
      <div class="launch-ctas" id="launchActions"></div>
      <div class="launch-disclaimer">Research replay, not live astronaut telemetry or a clinical device</div>
    </div>
    <div class="launch-monitor" aria-label="Research replay sample">
      <div class="launch-monitor-title"><b><span class="monitor-light"></span> CREW MONITOR / REPLAY</b><span>PPG + MOTION</span></div>
      <div class="monitor-head"><div><strong id="heroReading">Select an interval</strong><div class="research-note">Candidate rhythm · research-only</div></div><div class="status" id="heroDecision">REVIEW</div></div>
      <svg class="monitor-trace" viewBox="0 0 420 112" role="img" aria-label="Decorative heartbeat-inspired waveform, not a live measurement"><path d="M0 60H48 l9 -5 13 6 15 -27 15 50 13 -42 14 18 H165 l14 -7 10 5 15 -24 14 46 16 -38 13 18H280 l12 -4 11 5 17 -31 15 55 14 -47 13 19H420" /></svg>
      <div class="monitor-grid"><div><b>PPG</b><span>Optical candidate</span></div><div><b>MOTION</b><span>Accelerometer input</span></div><div><b>RELIABILITY</b><span id="heroCheck">Under review</span></div></div>
      <p class="research-note" style="margin:15px 0 0">Demonstrative waveform. Research values below change with the selected recording.</p>
    </div>
    <div class="launch-scroll">Scroll to explore</div><div class="launch-source">Photo: <a href="https://svs.gsfc.nasa.gov/webapps/planet-pen/Images/Cupola/" target="_blank" rel="noopener noreferrer">NASA / ISS Cupola</a></div>`;
  nav.insertAdjacentElement('afterend',stage);
  const actions=$('#launchActions');
  actions.append(
    button('Explore the monitor ↗','primary',()=>travelTo('console','monitor-anchor')),
    button('See the research ↗','secondary',()=>travelTo('science'))
  );
  const features=document.createElement('div');features.className='clinic-feature-rail';
  const featureData=[
    ['∿','Motion-aware sensing','PPG + accelerometer'],
    ['◎','Signal separation','Motion-linked interference'],
    ['◇','Reliability first','Display, review or withhold'],
    ['⊕','Crew self-check','Context and documentation']
  ];
  for(const [symbol,title,subtitle] of featureData){
    const f=document.createElement('div');f.className='clinic-feature';
    const symbolEl=document.createElement('div');symbolEl.className='glyph';symbolEl.textContent=symbol;symbolEl.setAttribute('aria-hidden','true');
    const desc=document.createElement('div'),b=document.createElement('b'),sm=document.createElement('small');b.textContent=title;sm.textContent=subtitle;desc.append(b,sm);f.append(symbolEl,desc);features.append(f);
  }
  stage.insertAdjacentElement('afterend',features);
  const cosmic=document.createElement('div');cosmic.className='orbital-layer';cosmic.setAttribute('aria-hidden','true');
  cosmic.innerHTML='<div class="orbital-sphere a"></div><div class="orbital-sphere b"></div>';
  for(let i=0;i<19;i++){
    const s=document.createElement('i');s.className='orbital-particle';
    s.style.left=((i*29+11)%99)+'%';s.style.top=((i*37+13)%95)+'%';s.style.setProperty('--period',`${4+i%6}s`);cosmic.append(s);
  }
  document.body.insertBefore(cosmic,document.body.firstChild);
  // Motion is a single throttled transform pass and is disabled for reduced-motion users.
  let busy=false;
  function parallax(){busy=false;if(reduce.matches)return;
    const y=Math.min(1600,window.scrollY);
    cosmic.style.setProperty('--scroll-drift',`${Math.round(y*.11)}px`);
    stage.style.backgroundPosition=`center ${Math.round(38+y*.022)}%`;
  }
  window.addEventListener('scroll',()=>{if(!busy){busy=true;requestAnimationFrame(parallax);}},{passive:true});

  // Story guide — explanations correspond to the real implemented research pipeline.
  const journey=document.createElement('section');journey.className='clinic-journey clinic-reveal';journey.id='monitor-anchor';
  const topics=[
    {title:'Capture',short:'Observe a sensor',icon:'01',body:'Pulsar examines 20-second windows of wrist optical PPG and three-axis acceleration. The public interface replays terrestrial exercise data, not flight telemetry.'},
    {title:'Separate',short:'Study motion effects',icon:'02',body:'Acceleration-derived predictors are used to estimate motion-linked components. Raw and motion-separated spectral candidates remain exploratory until independently verified.'},
    {title:'Evaluate',short:'Assess measurement risk',icon:'03',body:'The research gate evaluates whether a candidate meets a participant-held-out, training-derived display rule. A low model score is not a calibrated probability of correctness.'},
    {title:'Respond',short:'Document uncertainty',icon:'04',body:'The interface either cautiously displays a candidate, requests review or provides no reading. Crew check-ins document context; no diagnosis or operational advice is implied.'}
  ];
  journey.innerHTML='<div class="clinic-section-heading">A NEW KIND OF HEALTH INTERFACE</div><h2>From a number to a responsible decision.</h2><div class="journey-steps" role="group" aria-label="Explore the signal workflow"></div><div class="journey-result" aria-live="polite"><span class="journey-icon" id="journeyIcon">01</span><div><h3 id="journeyTitle"></h3><p id="journeyCopy"></p></div></div>';
  const journeyButtons=$('.journey-steps',journey);
  function setTopic(i){const t=topics[i];$('#journeyIcon',journey).textContent=t.icon;$('#journeyTitle',journey).textContent=t.title;$('#journeyCopy',journey).textContent=t.body;
    $$('.journey-step',journey).forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));
  }
  topics.forEach((t,i)=>{
    const b=document.createElement('button');b.type='button';b.className='journey-step';b.setAttribute('aria-pressed',String(i===0));
    b.innerHTML=`<strong>${t.icon} / ${t.title}</strong><span>${t.short}</span>`;b.addEventListener('click',()=>setTopic(i));journeyButtons.append(b);
  });
  setTopic(0);
  const existingHeader=$('.headerline',consoleView);if(existingHeader)existingHeader.before(journey);

  // Candidate estimate comparison; plotted from the original window-level corpus.
  const compare=document.createElement('section');compare.id='clinic-comparison';compare.className='clinic-compare clinic-reveal';
  compare.innerHTML=`<div class="clinic-compare-header"><div><div class="clinic-section-heading">INTERACTIVE RESEARCH COMPARISON / NOT RAW WAVEFORMS</div><h2>Move the boundary. Compare candidate estimates.</h2><p>Two time series from the selected exercise recording. The graph shows estimated frequency in bpm, not optical signal amplitude, ground truth or a demonstration of clinical accuracy.</p></div><span class="clinic-card-mark">ACTUAL RECORDING DATA</span></div>
  <div class="compare-stage"><svg viewBox="0 0 750 240" preserveAspectRatio="none" role="img" aria-label="Raw frequency estimates across selected recording"><path class="raw-path" id="compareRaw" /></svg><div class="compare-overlay" id="compareOverlay"><svg viewBox="0 0 750 240" preserveAspectRatio="none" role="img" aria-label="Motion-separated frequency estimates across selected recording"><path class="sep-path" id="compareSeparated" /></svg></div><div class="compare-divider" id="compareDivider"></div><span class="compare-label left">MOTION-SEPARATED</span><span class="compare-label right">RAW CANDIDATE</span></div>
  <label for="compareSlider" class="formrow" style="margin-top:15px">Drag to compare signal candidates</label><input class="compare-slider" type="range" id="compareSlider" min="0" max="100" value="50" aria-label="Reveal more of the motion-separated candidate trace" />
  <div class="compare-caption"><span id="compareSession">Recording selected above</span><span>Display acceptance requires separate reliability assessment</span></div>`;
  const stats=$('.stats',consoleView);if(stats)stats.after(compare);
  function linePath(items,key){if(!items.length)return '';
    const x=i=>20+i/Math.max(1,items.length-1)*710;
    const y=v=>208-Math.max(0,Math.min(1,(v-45)/170))*176;
    let out='',open=false;
    items.forEach((v,i)=>{const n=v[key];if(typeof n!=='number'||!Number.isFinite(n)){open=false;return;}
      out+=`${open?'L':'M'}${x(i).toFixed(1)} ${y(n).toFixed(1)} `;open=true;});return out;
  }
  function updateComparison(){const items=activeSeries();$('#compareRaw').setAttribute('d',linePath(items,'raw'));
    $('#compareSeparated').setAttribute('d',linePath(items,'res'));const first=items[0];
    $('#compareSession').textContent=first?`${first.sub.toUpperCase()} · ${first.activity.replaceAll('_',' ')} · ${items.length} × 20-second windows`:'No recording';}
  function updateWipe(){const val=Number($('#compareSlider').value)||0;
    $('#compareOverlay').style.clipPath=`inset(0 ${100-val}% 0 0)`;$('#compareDivider').style.left=val+'%';}
  $('#compareSlider').addEventListener('input',updateWipe);updateWipe();

  // Photographic astronaut moment: decor, not evidence of astronaut testing.
  const crew=document.createElement('section');crew.className='clinic-astronaut clinic-reveal';crew.id='crew-story';
  crew.innerHTML=`<div class="portrait" role="img" aria-label="Illustrative space-station astronaut scene"></div>
   <div class="story"><span class="clinic-section-heading">THE HUMAN SIDE OF SIGNAL RELIABILITY</span><h2>Designed around the moment a crew member asks: can I trust this reading?</h2>
   <p>Exercise, fatigue and changing physiological conditions make measurement context valuable. This scenario is a proposed application of terrestrial research, not a validated astronaut health system.</p>
   <button type="button" id="crewStoryButton">Try the crew self-assessment ↗</button><div class="source-credit">Astronaut photograph: <a href="https://svs.gsfc.nasa.gov/webapps/planet-pen/Images/Cupola/STS-130_EVA3_Nicholas_Patrick_1.jpg" target="_blank" rel="noopener noreferrer">NASA / STS-130</a>. For visual context only.</div></div>`;
  const cols=$('.two-col',consoleView);if(cols)cols.after(crew);
  $('#crewStoryButton').addEventListener('click',()=>travelTo('console','reportBtn'));
  // Self-assessment: preserve existing form values and original event handler.
  const checkin=$('#reportBtn')?.closest('.card');
  if(checkin){const progress=document.createElement('div');progress.className='clinic-crew-progress';progress.setAttribute('aria-hidden','true');progress.innerHTML='<i></i>';
    const heading=$('h3',checkin);if(heading)heading.after(progress);
    const inputs=$$('select,input[type="checkbox"]',checkin);
    function refreshProgress(){let completed=0;
      for(const el of inputs){if(el.type==='checkbox'){if(el.checked)completed++;}else if(el.selectedIndex>0)completed++;}
      progress.firstElementChild.style.width=(15+85*completed/Math.max(1,inputs.length))+'%';
    }
    inputs.forEach(el=>el.addEventListener('change',refreshProgress));refreshProgress();
  }
  // Evidence details reuse the exact results and limitations already disclosed on the page.
  const evidence=document.createElement('section');evidence.className='clinic-evidence';evidence.id='evidence-explorer';
  const notes=[
    ['01 / WHY THE ERROR MATTERS','The error–coverage trade-off','A lower error for displayed candidates is not sufficient on its own. At 37.7% display coverage, many readings are withheld; both coverage and conditional error must be reported together.'],
    ['02 / NEGATIVE EVIDENCE','The running limitation','During running, just 2 of 73 research windows were displayed, and one retained a serious error. This remains an unresolved limitation rather than a successfully met gate.'],
    ['03 / VALIDATION BOUNDARY','Development is not deployment','The participant-held-out study used eight people. It was not an untouched independent validation and did not involve astronauts or clinical monitoring.']
  ];
  for(const [minor,heading,body] of notes){const d=document.createElement('details'),sum=document.createElement('summary'),small=document.createElement('small'),p=document.createElement('p');
    small.textContent=minor;sum.textContent=heading;p.textContent=body;d.append(small,sum,p);evidence.append(d);}
  const science=$('#science');if(science){const hdr=$('.headerline',science);if(hdr)hdr.after(evidence);}
  // Additional precise chart tooltip, keyboard window selection, hover values.
  const chart=$('#timeChart');const tooltip=document.createElement('div');tooltip.className='clinic-tooltip';tooltip.hidden=true;tooltip.setAttribute('aria-hidden','true');document.body.append(tooltip);
  function chartMouse(event){const items=activeSeries();if(!chart||!items.length)return;
    const m=chart.getScreenCTM();if(!m)return;
    const pt=chart.createSVGPoint();pt.x=event.clientX;pt.y=event.clientY;
    const local=pt.matrixTransform(m.inverse());const i=Math.max(0,Math.min(items.length-1,Math.round((local.x-40)/682*(items.length-1))));const r=items[i];
    tooltip.replaceChildren();
    const title=document.createElement('strong');title.textContent=`${r.t}–${r.t+20} s`;tooltip.append(title,document.createElement('br'));
    for(const [name,val] of [['Raw candidate',r.raw],['Separated candidate',r.res]]){const span=document.createElement('span');span.textContent=name+': ';tooltip.append(span,document.createTextNode(safeNumber(val,1)+' bpm'),document.createElement('br'));}
    const state=document.createElement('span');state.textContent=(r.status||'').replaceAll('_',' ');tooltip.append(state);
    tooltip.style.left=Math.min(window.innerWidth-245,event.clientX+4)+'px';tooltip.style.top=Math.min(window.innerHeight-75,Math.max(70,event.clientY))+'px';tooltip.hidden=false;
  }
  if(chart){chart.tabIndex=0;chart.setAttribute('aria-label','Raw and motion-separated candidates. Use left/right arrow keys to choose an interval.');
    chart.addEventListener('pointermove',chartMouse);chart.addEventListener('pointerleave',()=>tooltip.hidden=true);
    chart.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();
      const s=$('#windowSlider');s.value=Math.max(Number(s.min)||0,Math.min(Number(s.max)||0,Number(s.value)+(e.key==='ArrowRight'?1:-1)));
      s.dispatchEvent(new Event('input',{bubbles:true}));});}
  // Hero mirrors the selected research case. Never portray missing/withheld values as a heart rate.
  function refreshHero(){const r=activeWindow();if(!r)return;
    const status=r.status||'REVIEW_SIGNAL';const valid=status==='DISPLAY_WITH_CAUTION';
    $('#heroReading').textContent=valid&&typeof r.res==='number'?`${r.res.toFixed(1)} candidate bpm`:'READING WITHHELD';
    $('#heroDecision').textContent=valid?'CAUTIOUS DISPLAY':status==='NO_SENSOR_CANDIDATE'?'NO READING':'REVIEW REQUIRED';
    $('#heroCheck').textContent=valid?'Cautious display':status==='NO_SENSOR_CANDIDATE'?'No candidate':'Needs review';
  }
  function refresh(){updateComparison();refreshHero();}
  $('#recordSelect')?.addEventListener('change',()=>requestAnimationFrame(refresh));
  $('#windowSlider')?.addEventListener('input',()=>requestAnimationFrame(refreshHero));
  refresh();
  // Reveal sections only when visible. Hidden tabs are handled when shown.
  const revealElements=$$('.card,.metric,.clinic-reveal,.pipe').filter(el=>!el.closest('.launch-stage'));
  if('IntersectionObserver' in window && !reduce.matches){const observer=new IntersectionObserver(entries=>{
    for(const entry of entries)if(entry.isIntersecting){entry.target.classList.add('in-view');observer.unobserve(entry.target);}
  },{rootMargin:'0px 0px -18px 0px',threshold:.035});
    revealElements.forEach(el=>{el.classList.add('clinic-reveal');observer.observe(el);});
  }else revealElements.forEach(el=>el.classList.add('in-view'));
  // One-off numeric count-ins are decorative only; the source values remain unchanged.
  if(!reduce.matches && 'IntersectionObserver' in window){const targets=$$('.metric strong').filter(el=>!el.id && /^\s*\d+(?:\.\d+)?%?\s*$/.test((el.firstChild?.textContent||'').trim()));
    const show=new IntersectionObserver(entries=>{for(const entry of entries){if(!entry.isIntersecting)continue;
      const el=entry.target, original=el.firstChild.textContent, number=Number(original.trim().replace('%',''));
      const decimal=(original.match(/\.(\d+)/)?.[1]||'').length,percentage=original.includes('%');
      const start=performance.now(),duration=800;const node=el.firstChild;
      function count(t){const f=Math.min(1,(t-start)/duration),e=1-Math.pow(1-f,3);node.textContent=(number*e).toFixed(decimal)+(percentage?'%':'');if(f<1)requestAnimationFrame(count);else node.textContent=original;}
      requestAnimationFrame(count);show.unobserve(el);
    }},{threshold:.3});targets.forEach(el=>show.observe(el));}
})();
