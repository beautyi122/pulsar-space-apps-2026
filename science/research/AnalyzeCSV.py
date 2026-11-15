#!/usr/bin/env python3
"""Sensor-only CSV analyzer for Pulsar research demonstrator, not medical use.

Expected 5120 rows over 20s, columns time_s,ppg,ax_g,ay_g,az_g,
regularly sampled at 256 Hz. No ECG or truth labels. Outputs exploratory
candidate and uncalibrated risk score from the Phase34 development model.
"""
import csv, io, json, math, sys
from pathlib import Path
import numpy as np
import joblib
from Phase34Run import pilot_window
from Phase32RawProbe import signal_features
from Reliability import (_good,_nearest_power,_nearest_local,_gap,_stability,FEATURE_NAMES)
ROOT=Path(__file__).resolve().parents[1]
ALLOWED_ACTIVITY={'walk','run','high_resistance_bike','low_resistance_bike'}


def parse_csv(payload: str):
    rd=csv.DictReader(io.StringIO(payload))
    expected=['time_s','ppg','ax_g','ay_g','az_g']
    if rd.fieldnames is None or not set(expected).issubset(rd.fieldnames):
        raise ValueError('Columns required: '+', '.join(expected))
    if len(payload)>2000000: raise ValueError('File is too large for this 20-second local demo')
    vals=[]
    for rec in rd:
        try: row=[float(rec[k]) for k in expected]
        except (KeyError,ValueError,TypeError) as e: raise ValueError('Non-numeric sensor row') from e
        vals.append(row)
        if len(vals)>5120: raise ValueError('Expected exactly 5,120 sensor rows')
    if len(vals)!=5120:raise ValueError(f'Exactly 5,120 samples required (found {len(vals)})')
    arr=np.asarray(vals,dtype=float)
    if not np.isfinite(arr).all():raise ValueError('Sensor samples must all be finite')
    intervals=np.diff(arr[:,0])
    if not np.all(intervals>0) or abs(np.median(intervals)-1/256)>1e-5 or np.max(np.abs(intervals-1/256))>1e-4:
        raise ValueError('Samples must be synchronized and uniformly spaced at 256 Hz')
    if abs((arr[-1,0]-arr[0,0])-5119/256)>1e-3:
        raise ValueError('Expected a full 20-second window')
    if float(np.std(arr[:,1]))<1e-9:
        raise ValueError('PPG does not vary; cannot infer a pulse candidate')
    return arr[:,1],arr[:,2:5]


def features_for_sample(pilot,probe,activity):
    raw=pilot['exploratory_raw_ppg_peak_bpm'];res=pilot['exploratory_residual_peak_bpm']
    raw_peaks=pilot['raw_top_five'];res_peaks=pilot['residual_top_five']
    peaks=probe['acc_top_spectral_peaks'];ap=peaks[0]['bpm'] if peaks else None
    if raw is None or res is None:raise ValueError('Insufficient candidate peaks')
    feature=[
      _good(res),_good(raw),abs(res-raw),
      math.log1p(max(_good(res_peaks[0]['relative_power']) if res_peaks else 0,0)*1000),_gap(res_peaks),
      math.log1p(max(_good(raw_peaks[0]['relative_power']) if raw_peaks else 0,0)*1000),_gap(raw_peaks),
      _stability(res,pilot.get('residual_subwindow_top_peaks')),
      _stability(raw,pilot.get('raw_subwindow_top_peaks')),
      _good(pilot['motion_predictability_out_of_fold_r2']),0,
      _nearest_power(peaks,res),_nearest_power(peaks,res/2),_nearest_power(peaks,res*2),_nearest_power(peaks,raw),
      _good(peaks[0]['power_fraction'] if peaks else None),
      _good(peaks[1]['power_fraction'] if len(peaks)>1 else None),
      _good(probe['acc_magnitude_std_g']),_good(probe['ppg_std_raw_record_units']),
      abs(res-_good(ap)) if ap is not None else 200,
      abs(res/2-_good(ap)) if ap is not None else 200,
      abs(res*2-_good(ap)) if ap is not None else 200,
      _nearest_local(res_peaks,res*2),_nearest_local(raw_peaks,raw*2),
      40,40,
      int(activity=='walk'),int(activity=='run'),int(activity=='high_resistance_bike'),int(activity=='low_resistance_bike'),
      0,40,
    ]
    if len(feature)!=len(FEATURE_NAMES):raise RuntimeError('Internal sensor feature schema mismatch')
    return feature


def analyze_text(payload,activity='walk'):
    if activity not in ALLOWED_ACTIVITY:raise ValueError('Unsupported activity category')
    ppg,acc=parse_csv(payload)
    p=pilot_window(ppg,acc)
    movement=np.linalg.norm(acc,axis=1)
    diag=signal_features(ppg,movement,None,None)
    feats=features_for_sample(p,diag,activity)
    model=joblib.load(ROOT/'results'/'Reliability Model.joblib')
    meta=json.loads((ROOT/'results'/'Final Reliability Model.json').read_text())
    risk=float(model.predict_proba(np.asarray(feats).reshape(1,-1))[0][1])
    threshold=meta['final_threshold']
    grade='LOWER_RISK_RESEARCH_TIER' if risk<=threshold else 'REVIEW_SIGNAL'
    return {'status':'SENSOR_ONLY_NEW_RECORDING_EXPERIMENT_NOT_VALIDATED',
      'source':'Locally uploaded 20-second CSV; no ECG labels or network upload',
      'activity':activity,'raw_candidate_bpm':p['exploratory_raw_ppg_peak_bpm'],
      'motion_separated_candidate_bpm':p['exploratory_residual_peak_bpm'],
      'motion_prediction_out_of_fold_r2':p['motion_predictability_out_of_fold_r2'],
      'residual_stable_descriptive':p['residual_subwindow_top_consistent_descriptive'],
      'development_model_uncalibrated_risk_score':round(risk,5),
      'research_tier':grade,
      'caution':'Unvalidated new-data inference. Different sensors, units, or participant characteristics can invalidate development risk model. NOT a clinical or astronaut health reading.'}


def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('csv');ap.add_argument('--activity',choices=sorted(ALLOWED_ACTIVITY),default='walk')
    args=ap.parse_args()
    print(json.dumps(analyze_text(Path(args.csv).read_text(),args.activity),indent=2))

if __name__=='__main__':main()
