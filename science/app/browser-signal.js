/* Pulsar browser-only, sensor-only, exploratory analysis.
 * Research implementation: idealized frequency suppression + blocked ridge projection
 * using FFT with zero-padding. This approximates, but is NOT numerically equivalent to,
 * the NumPy implementation's exact-length circular bandpass or trained risk classifier.
 * Never access truth labels. Never claim validated heart rate.
 * Copyright attribution: scientific method and limitations in science/METHODS.md.
 */
(function(root){
'use strict';
const FS=256,ROWS=5120,LOW=45/60,HIGH=210/60;
function check(ok,m){if(!ok)throw Error(m);}
function mean(v){let s=0;for(let i=0;i<v.length;i++)s+=v[i];return s/v.length;}
function variance(v){const m=mean(v);let s=0;for(let i=0;i<v.length;i++)s+=(v[i]-m)**2;return s/v.length;}
function fft(real,imag,inverse=false){
 const n=real.length;check((n&(n-1))===0,'FFT size must be power of two');
 for(let i=1,j=0;i<n;i++){
  let bit=n>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;
  if(i<j){let t=real[i];real[i]=real[j];real[j]=t;t=imag[i];imag[i]=imag[j];imag[j]=t;}
 }
 for(let len=2;len<=n;len<<=1){
  const a=(inverse?2:-2)*Math.PI/len,wr0=Math.cos(a),wi0=Math.sin(a);
  for(let i=0;i<n;i+=len){let wr=1,wi=0;
   for(let j=0;j<len/2;j++){
    const k=i+j,l=k+len/2,vr=real[l]*wr-imag[l]*wi,vi=real[l]*wi+imag[l]*wr;
    real[l]=real[k]-vr;imag[l]=imag[k]-vi;real[k]+=vr;imag[k]+=vi;
    const nw=wr*wr0-wi*wi0;wi=wr*wi0+wi*wr0;wr=nw;
   }
  }
 }
 if(inverse){for(let i=0;i<n;i++){real[i]/=n;imag[i]/=n;}}
}
function bandpass(sig,lo=.6,hi=3.5){
 // Zero-padding differs at signal boundaries from NumPy's exact N-point FFT.
 const n=sig.length,M=8192,r=new Float64Array(M),q=new Float64Array(M),avg=mean(sig);
 for(let i=0;i<n;i++)r[i]=sig[i]-avg;
 fft(r,q);
 for(let k=0;k<M;k++){
  const f=Math.min(k,M-k)*FS/M;
  if(f<lo||f>hi){r[k]=0;q[k]=0;}
 }
 fft(r,q,true);return r.slice(0,n);
}
function peaks(sig,maxCount=5){
 const n=sig.length,M=32768,r=new Float64Array(M),q=new Float64Array(M),avg=mean(sig);
 for(let i=0;i<n;i++)r[i]=(sig[i]-avg)*(0.5-0.5*Math.cos(2*Math.PI*i/(n-1)));
 fft(r,q);
 const out=[],powers=new Float64Array(M/2+1);
 let total=0;
 for(let i=0;i<powers.length;i++){
  const p=r[i]*r[i]+q[i]*q[i];powers[i]=p;
  const bpm=i*FS*60/M;if(bpm>=45&&bpm<=210)total+=p;
 }
 for(let k=1;k<powers.length-1;k++){
  const bpm=k*FS*60/M;
  if(bpm<45||bpm>210||powers[k]<=powers[k-1]||powers[k]<powers[k+1])continue;
  out.push({bpm:Math.round(bpm*100)/100,relative_power:Math.round(powers[k]/Math.max(total,1e-16)*1e6)/1e6});
 }
 out.sort((a,b)=>b.relative_power-a.relative_power);
 const kept=[];
 for(const p of out){if(kept.every(x=>Math.abs(x.bpm-p.bpm)>=5))kept.push(p);if(kept.length===maxCount)break;}
 return kept;
}
function solve(matrix,target){ // regularized 31x31 normal equations; partial pivoting
 const n=target.length,A=matrix.map((r,i)=>Float64Array.from([...r,target[i]]));
 for(let j=0;j<n;j++){
  let best=j;for(let i=j+1;i<n;i++)if(Math.abs(A[i][j])>Math.abs(A[best][j]))best=i;
  if(Math.abs(A[best][j])<1e-12)continue;
  if(best!==j){const t=A[j];A[j]=A[best];A[best]=t;}
  const inv=1/A[j][j];for(let k=j;k<=n;k++)A[j][k]*=inv;
  for(let i=j+1;i<n;i++){
   const factor=A[i][j];if(!factor)continue;
   for(let k=j;k<=n;k++)A[i][k]-=factor*A[j][k];
  }
 }
 const result=new Float64Array(n);
 for(let i=n-1;i>=0;i--){let v=A[i][n];for(let k=i+1;k<n;k++)v-=A[i][k]*result[k];result[i]=v;}
 return result;
}
function motionResidual(ppg,acc){
 const n=ppg.length,pred=new Float64Array(n),y=bandpass(ppg),axes=[];
 for(let j=0;j<3;j++){
  const a=Float64Array.from(acc.map(z=>z[j])),av=mean(a),s=Math.sqrt(variance(a))+1e-9;
  axes.push(Float64Array.from(a,z=>(z-av)/s));
 }
 const [x,z,w]=axes,base=[x,z,w,new Float64Array(n),new Float64Array(n),new Float64Array(n),new Float64Array(n),new Float64Array(n),new Float64Array(n),new Float64Array(n)];
 for(let i=0;i<n;i++){
  base[3][i]=x[i]*x[i];base[4][i]=z[i]*z[i];base[5][i]=w[i]*w[i];
  base[6][i]=x[i]*z[i];base[7][i]=z[i]*w[i];base[8][i]=w[i]*x[i];
  base[9][i]=Math.sqrt(x[i]*x[i]+z[i]*z[i]+w[i]*w[i]);
 }
 const columns=[];
 for(const arr of base){const f=bandpass(arr);
  for(const lag of [0,10,20]){
   const v=new Float64Array(n);
   for(let i=lag;i<n;i++)v[i]=f[i-lag];
   if(Math.sqrt(variance(v))>1e-7)columns.push(v);
  }
 }
 const p=columns.length+1;
 const m=columns.map(mean),dev=columns.map((v,j)=>Math.sqrt(variance(v))+1e-9);
 // Standardization is fixed from the sensor window, never uses ECG/ground truth.
 for(let k=0;k<5;k++){
  const from=Math.floor(n*k/5),until=Math.floor(n*(k+1)/5),Q=Array.from({length:p},()=>new Float64Array(p)),b=new Float64Array(p),row=new Float64Array(p);
  let count=0;
  for(let i=0;i<n;i++){
   if(i>=from&&i<until)continue;
   row[0]=1;for(let j=1;j<p;j++)row[j]=(columns[j-1][i]-m[j-1])/dev[j-1];
   const target=y[i];count++;
   for(let a=0;a<p;a++){b[a]+=row[a]*target;for(let c=0;c<=a;c++)Q[a][c]+=row[a]*row[c];}
  }
  for(let a=0;a<p;a++){
   for(let c=0;c<a;c++)Q[c][a]=Q[a][c];
   if(a)Q[a][a]+=.04*count;
  }
  const beta=solve(Q,b);
  for(let i=from;i<until;i++){
   let v=beta[0];for(let j=1;j<p;j++)v+=beta[j]*(columns[j-1][i]-m[j-1])/dev[j-1];
   pred[i]=v;
  }
 }
 const residual=new Float64Array(n);for(let i=0;i<n;i++)residual[i]=y[i]-pred[i];
 const varY=variance(y),r2=varY>1e-12?1-variance(residual)/varY:0;
 return {raw:y,residual,r2};
}
function parseCSV(source){
 check(typeof source==='string'&&source.length<2e6,'File must be a CSV smaller than 2 MB');
 const lines=source.replace(/^\uFEFF/,'').trim().split(/\r?\n/);
 check(lines.length===ROWS+1,'CSV must contain exactly 5,120 sensor rows at 256 Hz');
 const fields=lines[0].split(',').map(s=>s.trim().toLowerCase()),required=['time_s','ppg','ax_g','ay_g','az_g'],ind=required.map(s=>fields.indexOf(s));
 check(ind.every(i=>i>=0),'Required columns: '+required.join(', '));
 const ppg=new Float64Array(ROWS),acc=new Array(ROWS);let lastTime=NaN,beginTime=0;
 for(let j=0;j<ROWS;j++){
  const cells=lines[j+1].split(',');
  const values=ind.map(i=>Number(cells[i]));
  check(values.every(v=>Number.isFinite(v)),'Nonfinite/non-numeric sensor row '+(j+1));
  const [t,pp,ax,ay,az]=values;
  if(j===0)beginTime=t;
  else check(t>lastTime&&Math.abs(t-lastTime-1/FS)<=1e-4,'Samples must be synchronized at 256 Hz');
  lastTime=t;ppg[j]=pp;acc[j]=[ax,ay,az];
 }
 check(Math.abs(lastTime-beginTime-(ROWS-1)/FS)<=1e-3,'Expected a full 20-second window');
 check(Math.sqrt(variance(ppg))>=1e-9,'Optical signal contains no measurable variation');
 return {ppg,acc};
}
function analyzeCSV(source){
 const {ppg,acc}=parseCSV(source),{raw,residual,r2}=motionResidual(ppg,acc);
 const rawP=peaks(raw),sepP=peaks(residual),rawB=rawP[0]?.bpm??null,sepB=sepP[0]?.bpm??null;
 const half=ROWS/2,split=(v)=>[peaks(v.slice(0,half),1)[0]?.bpm??null,peaks(v.slice(half),1)[0]?.bpm??null];
 const a=split(raw),b=split(residual),consistent=sepB!==null&&b.every(x=>x!==null&&Math.abs(x-sepB)<=10);
 return {status:'BROWSER_EXPLORATORY_CANDIDATES_NOT_VALIDATED',sampling_hz:FS,samples:ROWS,
  raw_candidate_bpm:rawB,motion_separated_candidate_bpm:sepB,motion_prediction_out_of_fold_r2:r2,
  raw_top_five:rawP,separated_top_five:sepP,raw_half_rates:a,separated_half_rates:b,
  residual_stable_descriptive:consistent,health_decision:'WITHHELD_UNTIL_VALIDATED',
  algorithm:'Blocked five-fold nonlinear accelerometer regression; browser FFT approximation of Python Phase33 model',
  caution:'Experimental frequency candidates are NOT verified heart rates. The production ExtraTrees risk classifier is not run here; no clinical or astronaut-monitoring validity is claimed.'};
}
root.PulsarBrowserSignal={analyzeCSV,parseCSV,fft,peaks,motionResidual};
})(typeof window!=='undefined'?window:globalThis);
