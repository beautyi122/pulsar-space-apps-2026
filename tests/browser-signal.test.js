'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert');
// Verify the preserved scientific application snapshot. The live project website is maintained separately.
const root=path.resolve(__dirname,'..','science','app');
require(path.join(root,'browser-signal.js'));
const run=globalThis.PulsarBrowserSignal;
const csv=fs.readFileSync(path.join(root,'Synthetic PPG.csv'),'utf8');
const source=fs.readFileSync(path.join(root,'app.js'),'utf8');
const index=fs.readFileSync(path.join(root,'index.html'),'utf8');
assert(index.includes('src="browser-signal.js"'),'missing online browser module');
assert(!source.includes("fetch('/api/analyze"),'static website still depends on Python API');
let o=run.analyzeCSV(csv);
assert.equal(o.sampling_hz,256);
assert.equal(o.samples,5120);
assert(Math.abs(o.raw_candidate_bpm-173.91)<1,`raw ${o.raw_candidate_bpm}`);
assert(Math.abs(o.motion_separated_candidate_bpm-98.91)<2,`separated ${o.motion_separated_candidate_bpm}`);
assert.equal(o.health_decision,'WITHHELD_UNTIL_VALIDATED');
assert.equal(o.residual_stable_descriptive,true);
assert.throws(()=>run.analyzeCSV('time_s,ppg,ax_g,ay_g,az_g\n1,2,3,4,5'),/5,120/);
assert.throws(()=>run.analyzeCSV(csv.replace('time_s,ppg','time_s,foo')),/Required columns/);
// ECG/ground truth deliberately absent from the input feature schema.
assert(!Object.keys(o).some(k=>/ecg_reference|ground_truth/.test(k)));
console.log('PASS: complete browser-only sensor input, 5120-sample validation, raw and separated peaks, withhold behavior');
