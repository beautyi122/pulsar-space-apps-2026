#!/usr/bin/env python3
"""Pulsar reliability study. Participant-held-out retrospective development, not clinical validation.

Sensor-only features are computed without ECG labels. ECG references are loaded ONLY
into the development evaluation/training routine. Never refit or use ECG during app inference.
"""
from __future__ import annotations
import hashlib, json, math, sys, zipfile
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import LeaveOneGroupOut

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / 'input' / 'Phase 34 Sensor Pilot.json'
EVIDENCE = ROOT / 'input' / 'Phase 31 Evidence.zip'
REFERENCE_FILENAME = 'Phase 31 External Results.json'
OUTPUT = ROOT / 'results' / 'Reliability Evidence.json'
MODEL_OUT = ROOT / 'results' / 'Final Reliability Model.json'
FEATURE_NAMES = [
    'res_peak','raw_peak','res_vs_raw','res_log_power','res_margin','raw_log_power',
    'raw_margin','res_stability','raw_stability','motion_r2','original_score',
    'acc_near_res','acc_near_half','acc_near_double','acc_near_raw',
    'acc_primary','acc_primary_harmonic','acc_std','ppg_std',
    'res_to_motion_distance','res_half_motion_distance','res_double_motion_distance',
    'res_harmonic_power','raw_harmonic_power','res_prev_delta','raw_prev_delta',
    'is_walk','is_run','is_high_bike','is_low_bike',
    'original_present','original_difference',
]


def filehash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _good(v, default=0):
    try:
        x=float(v)
        return x if math.isfinite(x) else default
    except (TypeError, ValueError):return default


def _nearest_power(peaks,bpm,tolerance=9):
    if not peaks or bpm is None or not 30<=bpm<=240:return 0.0
    return sum(_good(x.get('power_fraction'),0) for x in peaks if abs(_good(x.get('bpm'),-1000)-bpm)<=tolerance)


def _gap(peaks):
    if not peaks:return 0.0
    return _good(peaks[0].get('relative_power')) / max(_good(peaks[1].get('relative_power')) if len(peaks)>1 else 1e-8, 1e-8)


def _stability(p,pair):
    if p is None or not pair or any(x is None for x in pair):return 80.0
    return max(abs(p-_good(x,p+80)) for x in pair)


def _get_ref_lookup(evidence):
    with zipfile.ZipFile(evidence) as z:
        raw=z.read(REFERENCE_FILENAME)
        d=json.loads(raw)
    return {(r['record'],int(w['window'])):w for r in d['records'] for w in r['windows']},d


def prepare_rows(pilot, probe):
    """Safe to use at inference: no ECG, no reference variables accepted."""
    probe_lookup={(r['record'],int(w['window'])):w for r in probe['records'] for w in r['windows']}
    rows=[]
    prev={}
    for r in pilot['records']:
        k=(r['record'],int(r['window']))
        s=r.get('pilot') or {}
        raw=s.get('exploratory_raw_ppg_peak_bpm')
        res=s.get('exploratory_residual_peak_bpm')
        pr=probe_lookup.get(k,{})
        feat=pr.get('signal_only_features') or {}
        acc_peaks=feat.get('acc_top_spectral_peaks') or []
        rpower=s.get('residual_top_five') or []
        wpower=s.get('raw_top_five') or []
        ap=acc_peaks[0]['bpm'] if acc_peaks else None
        orig=r.get('original_frozen_accepted_bpm')
        prev_r,prev_w=prev.get(r['record'],(None,None))
        # Features calculated strictly from previously computed sensor-only data.
        f=[
           _good(res),_good(raw),abs(_good(res)-_good(raw)),
           math.log1p(max(_good(rpower[0]['relative_power']) if rpower else 0,0)*1000),_gap(rpower),
           math.log1p(max(_good(wpower[0]['relative_power']) if wpower else 0,0)*1000),_gap(wpower),
           _stability(res,s.get('residual_subwindow_top_peaks')),_stability(raw,s.get('raw_subwindow_top_peaks')),
           _good(s.get('motion_predictability_out_of_fold_r2')),
           _good(pr.get('frozen_model_score')),
           _nearest_power(acc_peaks,res),_nearest_power(acc_peaks,res/2 if res is not None else None),
           _nearest_power(acc_peaks,res*2 if res is not None else None),_nearest_power(acc_peaks,raw),
           _good(acc_peaks[0]['power_fraction'] if acc_peaks else None),
           _good(acc_peaks[1]['power_fraction'] if len(acc_peaks)>1 else None),
           _good(feat.get('acc_magnitude_std_g')),_good(feat.get('ppg_std_raw_record_units')),
           abs(_good(res)-_good(ap)) if ap is not None else 200,
           abs(_good(res)/2-_good(ap)) if ap is not None else 200,
           abs(_good(res)*2-_good(ap)) if ap is not None else 200,
           _nearest_local(rpower,res*2 if res is not None else None),
           _nearest_local(wpower,raw*2 if raw is not None else None),
           abs(_good(res)-_good(prev_r)) if prev_r is not None else 40,
           abs(_good(raw)-_good(prev_w)) if prev_w is not None else 40,
           int(r['activity']=='walk'),int(r['activity']=='run'),
           int(r['activity']=='high_resistance_bike'),int(r['activity']=='low_resistance_bike'),
           int(orig is not None),abs(_good(res)-_good(orig)) if orig is not None else 40,
        ]
        if len(f)!=len(FEATURE_NAMES):raise RuntimeError('Feature count mismatch')
        if r['sensor_QC']!='finite' or not raw or not res:
            # Keep nonfinite or missing windows (not silently dropped).
            f=[0.0]*len(FEATURE_NAMES)
            eligible=False
        else:eligible=True
        rows.append({'record':r['record'],'window':int(r['window']),
            'subject':r['subject'],'activity':r['activity'],
            'start_seconds':r['start_seconds'],'raw_bpm':raw,'residual_bpm':res,
            'original_bpm':orig,'features':f,'eligible':eligible,
            'motion_r2':s.get('motion_predictability_out_of_fold_r2'),
            'raw_stable':s.get('raw_subwindow_top_consistent_descriptive'),
            'residual_stable':s.get('residual_subwindow_top_consistent_descriptive'),
            'acc_near_half':f[12]})
        prev[r['record']]=(res,raw)
    if len(rows)!=332 or len(set((x['record'],x['window']) for x in rows))!=332:
        raise RuntimeError('Unexpected Phase34 window counts / duplicates')
    return rows


def _nearest_local(peaks,bpm,tolerance=9):
    if bpm is None or not 30<=bpm<=240:return 0.0
    return sum(_good(x.get('relative_power')) for x in peaks or [] if abs(_good(x.get('bpm'),-1000)-bpm)<=tolerance)


def _classifier():
    return ExtraTreesClassifier(n_estimators=256, max_features=0.75,min_samples_leaf=6,
      max_depth=7,random_state=351, n_jobs=1,class_weight='balanced')


def _fit_predict(train_x, train_y, test_x):
    if len(set(train_y))<2:
        return np.full(len(test_x),float(np.mean(train_y)))
    mdl=_classifier();mdl.fit(train_x,train_y)
    return mdl.predict_proba(test_x)[:,list(mdl.classes_).index(1)]


def _group_oof(x,y,groups):
    p=np.full(len(y),np.nan)
    for tr,te in LeaveOneGroupOut().split(x,y,groups):
        p[te]=_fit_predict(x[tr],y[tr],x[te])
    if not np.all(np.isfinite(p)):raise RuntimeError('Missing inner OOF predictions')
    return p


def _train_cutoff(pred_error, true_error, target_coverage=0.35):
    """Train-only threshold chosen for a fixed nominal eligible-candidate coverage.
    No reference values from held-out participants enter the threshold calculation.
    """
    if not len(pred_error):return -1.0
    # Quantile based on TRAIN inner-OOF model predictions only, no label peeking.
    return float(np.quantile(pred_error, target_coverage,method='higher'))


def _summarize(rs):
    all_e=[x for x in rs if x['eligible']]
    yes=[x for x in rs if x['decision']=='DISPLAY_WITH_CAUTION']
    errors=[abs(x['residual_bpm']-x['ecg_reference_bpm']) for x in yes]
    return {'windows':len(rs),'candidate_windows':len(all_e),'displayed':len(yes),
        'display_coverage_all_windows':round(len(yes)/len(rs),4) if rs else 0,
        'display_coverage_eligible':round(len(yes)/len(all_e),4) if all_e else 0,
        'conditional_mae_bpm':round(float(np.mean(errors)),3) if errors else None,
        'serious_errors_ge15':sum(e>=15 for e in errors),
        'serious_rate_displayed':round(sum(e>=15 for e in errors)/len(errors),4) if errors else None,
        'within5':sum(e<=5 for e in errors), 'within10':sum(e<=10 for e in errors)}


def _bootstrap_by_subject(results,iterations=300,seed=351):
    rng=np.random.default_rng(seed)
    by=defaultdict(list)
    for r in results:by[r['subject']].append(r)
    subs=list(by)
    out={'coverage':[],'serious_rate':[],'mae':[]}
    for _ in range(iterations):
        res=[item for who in rng.choice(subs,len(subs),replace=True) for item in by[who]]
        met=_summarize(res)
        out['coverage'].append(met['display_coverage_all_windows'])
        if met['conditional_mae_bpm'] is not None:out['mae'].append(met['conditional_mae_bpm'])
        if met['serious_rate_displayed'] is not None:out['serious_rate'].append(met['serious_rate_displayed'])
    return {k:[round(float(np.quantile(v,0.025)),4),round(float(np.quantile(v,0.975)),4)] if v else None for k,v in out.items()}


def evaluate():
    pilot=json.loads(PILOT.read_bytes());probe=json.loads((ROOT/'input'/'Phase 32 Raw Signal Probe.json').read_bytes())
    if not pilot.get('reference_accessed_during_sensor_pilot') is False:
        raise RuntimeError('Pilot must remain sensor only')
    rows=prepare_rows(pilot,probe)
    lookup,source=_get_ref_lookup(EVIDENCE)
    if pilot['source_checks']['phase31_locked_predictions_sha256']!=source['prediction_file_sha256']:
        raise RuntimeError('Frozen prediction hash mismatch')
    if len(lookup)!=len(rows) or set(lookup)!=set((r['record'],r['window']) for r in rows):
        raise RuntimeError('Missing reference or duplicate keys')
    elig=[i for i,r in enumerate(rows) if r['eligible']]
    x=np.asarray([rows[i]['features'] for i in elig],float)
    groups=np.asarray([rows[i]['subject'] for i in elig])
    ref=np.asarray([lookup[(rows[i]['record'],rows[i]['window'])]['ecg_reference_bpm'] for i in elig],float)
    res=np.asarray([rows[i]['residual_bpm'] for i in elig],float)
    errors=np.abs(res-ref)
    y=np.asarray(errors>=15,int)
    # Each participant is excluded from ALL training and inner-threshold selection.
    p=np.full(len(elig),np.nan)
    cutoff_per_subject={}
    for tr,te in LeaveOneGroupOut().split(x,y,groups):
        pred_inner=_group_oof(x[tr],y[tr],groups[tr]);cutoff=_train_cutoff(pred_inner,y[tr]);
        p[te]=_fit_predict(x[tr],y[tr],x[te]);cutoff_per_subject[groups[te[0]]]=cutoff
    for r in rows:
        r['ecg_reference_bpm']=lookup[(r['record'],r['window'])]['ecg_reference_bpm']
        r['predicted_serious_error_risk']=None
        r['decision']='NO_SENSOR_CANDIDATE'
    for j,i in enumerate(elig):
        r=rows[i];prob=float(p[j]);r['predicted_serious_error_risk']=round(prob,5)
        threshold=cutoff_per_subject[r['subject']]
        r['decision']='DISPLAY_WITH_CAUTION' if prob<=threshold else 'REVIEW_SIGNAL'
    overall=_summarize(rows)
    by_activity={a:_summarize([r for r in rows if r['activity']==a]) for a in sorted({r['activity'] for r in rows})}
    by_subject={s:_summarize([r for r in rows if r['subject']==s]) for s in sorted({r['subject'] for r in rows})}
    # Separate engineering reference for a model fit to ALL previously examined development participants:
    # it is a candidate model, NOT a tested final holdout model; no claims from it.
    final_model=_classifier();final_model.fit(x,y)
    artifact={'type':'ExtraTreesClassifier','features':FEATURE_NAMES,
      'hyperparameters':{'n_estimators':256,'max_features':0.75,'min_samples_leaf':6,'max_depth':7,
        'random_state':351,'class_weight':'balanced'},
      'development_only':True,'model_requires_sklearn':True,
      'final_threshold':_train_cutoff(p,y),
      'phase34_sensor_pilot_sha256':filehash(PILOT),'trained_on_participants':sorted(set(groups))}
    result={
      'status':'RETROSPECTIVE_PARTICIPANT_HELD_OUT_DEVELOPMENT_ONLY',
      'date':'2026-11-15','gate4_met':False,
      'reference_access_in_reliability_training_only':True,
      'original_phase31_data_reused_not_independent':True,
      'method':'LOPO outer; separate inner LOPO on training participants to set a predicted-risk 35%-eligible-coverage quantile; ExtraTrees risk model trained only on outer training participants; no ECG feature',
      'decision_definition':'DISPLAY_WITH_CAUTION is experimental low-risk screen, NOT validated medical confidence. REVIEW_SIGNAL means recheck measurement. Never diagnosis.',
      'source_sha256':{'pilot':filehash(PILOT),'phase32_probe':filehash(ROOT/'input'/'Phase 32 Raw Signal Probe.json'),'phase31_evidence':filehash(EVIDENCE)},
      'overall':overall,'by_activity':by_activity,'by_subject':by_subject,
      'subject_cluster_bootstrap_95pct_descriptive_interval':_bootstrap_by_subject(rows),
      'baseline_phase31':{'accepted':54,'coverage':54/332,'conditional_mae_bpm':21.0726381481,'serious_errors':16},
      'baseline_residual_unfiltered':{'accepted':329,'coverage':329/332,'conditional_mae_bpm':21.6855284802,'serious_errors':126},
      'records':[{k:v for k,v in r.items() if k!='features'} for r in rows],
      'limitations':['Eight examined people, 19 recordings and 332 windows. Clustered correlated observations.',
         'Out-of-participant retrospective development only; not an independent frozen dataset.',
         'Possible repeated development decisions influenced by earlier inspected errors; exploratory not unbiased publication-grade validation.',
         'No medical or astronaut-flight validation; no medical thresholds or health diagnoses.',
         'Risk probabilities are uncalibrated scores, not medical probabilities.',
         'Training the final deployment model requires the saved compatible model/feature code; app uses audited held-out predictions for demonstration, not a live physiological sensor.',
         'An apparent low error count can accompany low coverage; all relevant denominators supplied.']}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    MODEL_OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    import joblib
    joblib.dump(final_model,ROOT / 'results' / 'Reliability Model.joblib',compress=3)
    print(json.dumps({'overall':overall,'by_activity':by_activity,'bootstrap':result['subject_cluster_bootstrap_95pct_descriptive_interval']},indent=2))
    return result

if __name__=='__main__':evaluate()
