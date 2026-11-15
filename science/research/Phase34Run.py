#!/usr/bin/env python3
"""Astrona Phase 34 -- labelled-blind pilot on PREVIOUSLY EXAMINED PhysioNet wrist recordings.

STAGE 1: ONLY wrist PPG and three wrist accelerometer channels are read. No ECG
waveform, .atr annotation, or ECG references are loaded. All outcomes are
EXPLORATORY candidates, not accepted heart-rate estimates. No Phase30/31/32
source, cache, or frozen prediction is written to. Fail closed on integrity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from Phase32RawProbe import (FS, WINDOW, CACHE, ZIP, SRC, load_original_external,
    select_channels_external, sha_file)
import Phase32RawProbe as old
from Phase33SignalExperiment import (analyze, fft_bandpass, motion_design,
    _blocked_motion_predict, spectral_peaks, synthetic_case)

ROOT=Path(__file__).resolve().parent
IN=ROOT/'input'/'Phase 31 Evidence.zip'
PROBE=ROOT/'input'/'Phase 32 Raw Signal Probe.json'
OUT=ROOT/'results'/'Phase 34 Sensor Pilot.json'


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _json_bytes(data):
    return (json.dumps(data,indent=2,allow_nan=False)+'\n').encode('utf-8')


def write_new_only(path, content):
    """A later run may confirm identical output, but never overwrites a mismatch."""
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=content:
            raise RuntimeError('Existing Phase34 output differs; refusing overwrite: '+str(path))
        return 'already_identical'
    with path.open('xb') as f:
        f.write(content)
    return 'created'


def candidate_consistency(whole_bpm, first, second, tolerance=10):
    """Descriptive stability only; not a frozen acceptance/abstention rule."""
    if whole_bpm is None or not first or not second:
        return None
    return bool(abs(whole_bpm-first[0]['bpm'])<=tolerance and
                abs(whole_bpm-second[0]['bpm'])<=tolerance)


def pilot_window(ppg, acc_g, fs=FS):
    """Pure synchronized-sensor diagnostic. Does NOT receive or use ECG labels."""
    ppg=np.asarray(ppg,dtype=float)
    acc_g=np.asarray(acc_g,dtype=float)
    if ppg.ndim!=1 or acc_g.shape!=(len(ppg),3):
        raise ValueError('Expected PPG (N,) and synchronised acceleration (N,3)')
    if not (np.all(np.isfinite(ppg)) and np.all(np.isfinite(acc_g))):
        raise ValueError('nonfinite sensor window')
    res=analyze(ppg,acc_g,fs)
    # Recompute the same out-of-fold residual to inspect temporal consistency.
    y=fft_bandpass(ppg,fs)
    X=motion_design(acc_g,fs)
    prediction=_blocked_motion_predict(y,X)
    residual=y-prediction
    midpoint=len(ppg)//2
    first_raw=spectral_peaks(y[:midpoint],fs,top_k=1)
    second_raw=spectral_peaks(y[midpoint:],fs,top_k=1)
    first_res=spectral_peaks(residual[:midpoint],fs,top_k=1)
    second_res=spectral_peaks(residual[midpoint:],fs,top_k=1)
    raw=res['raw_ppg_peaks'][0]['bpm'] if res['raw_ppg_peaks'] else None
    clean=res['prototype_residual_top_peak_bpm']
    return {
        'exploratory_raw_ppg_peak_bpm':raw,
        'exploratory_residual_peak_bpm':clean,
        'motion_predictability_out_of_fold_r2':res['out_of_fold_motion_prediction_r2'],
        'raw_top_five':res['raw_ppg_peaks'],
        'residual_top_five':res['residual_ppg_peaks'],
        'raw_subwindow_top_peaks':[first_raw[0]['bpm'] if first_raw else None,
                                   second_raw[0]['bpm'] if second_raw else None],
        'residual_subwindow_top_peaks':[first_res[0]['bpm'] if first_res else None,
                                        second_res[0]['bpm'] if second_res else None],
        'raw_subwindow_top_consistent_descriptive':candidate_consistency(raw,first_raw,second_raw),
        'residual_subwindow_top_consistent_descriptive':candidate_consistency(clean,first_res,second_res),
        'all_candidates_exploratory_not_accepted':True,
    }


def load_preflight():
    if not IN.is_file() or not PROBE.is_file():
        raise FileNotFoundError('Missing unmodified bundled evidence/probe')
    with zipfile.ZipFile(IN) as z:
        pred_bytes=z.read('Phase 31 Locked Predictions.json')
        pred=json.loads(pred_bytes)
        lock=json.loads(z.read('Phase 31 Prediction Lock.json'))
        frozen=json.loads(z.read('Phase 30 Freeze Manifest.json'))
    probe=json.loads(PROBE.read_text())
    if lock['predictions_sha256']!=_sha(pred_bytes):
        raise RuntimeError('Phase31 locked predictions SHA mismatch')
    if pred['archive_sha256']!=probe['official_archive_sha256']:
        raise RuntimeError('Original archive SHA disagreement across evidence and probe')
    if frozen['model_sha256']!=probe['phase30_frozen_model_sha256']:
        raise RuntimeError('Frozen model SHA disagreement across evidence and probe')
    if probe['phase31_locked_prediction_sha256']!=lock['predictions_sha256']:
        raise RuntimeError('Probe vs Phase31 predictions hash mismatch')
    if sha_file(Path(old.__file__))!=probe['phase32_probe_source_sha256']:
        raise RuntimeError('Bundled original Phase32 loader source is not the executed loader')
    if (len(pred['records']),sum(len(r['windows']) for r in pred['records']))!=(19,332):
        raise RuntimeError('Unexpected frozen dataset identity/shape')
    if not ZIP.exists() or not CACHE.is_dir():
        raise FileNotFoundError('Missing Phase30-31 official cached wrist archive/recordings at '+str(ZIP))
    if sha_file(ZIP)!=pred['archive_sha256']:
        raise RuntimeError('Original cached source archive SHA mismatch')
    if not SRC.is_file() or sha_file(SRC)!=frozen['phase31_source_sha256']:
        raise RuntimeError('Original frozen external loader source SHA mismatch')
    # The untouched Phase32 probe is also a source-checkpoint and QC reference.
    if {(r['record'],w['window']) for r in pred['records'] for w in r['windows']} != {
        (r['record'],w['window']) for r in probe['records'] for w in r['windows']}:
        raise RuntimeError('Probe windows do not match frozen prediction windows')
    return pred,lock,probe


def run_real():
    import wfdb
    preds,lock,probe=load_preflight()
    external=load_original_external()  # validates the source against frozen manifest.
    check={(rec['record'],w['window']):w['sensor_QC']
           for rec in probe['records'] for w in rec['windows']}
    rows=[]
    for rec in preds['records']:
        name=rec['record']
        base=CACHE/name
        if not base.with_suffix('.hea').exists():
            raise FileNotFoundError('Missing official recording header '+str(base))
        header=wfdb.rdheader(str(base))
        ppg_index,acc_indices,factor,channels=select_channels_external(external,header)
        # The ONLY waveform channels read: PPG + 3 ACC. No ECG loaded.
        sensor=wfdb.rdrecord(str(base),channels=[ppg_index,*acc_indices],physical=True)
        arr=np.asarray(sensor.p_signal,dtype=float)
        if arr.ndim!=2 or arr.shape[1]!=4 or sensor.fs!=FS:
            raise RuntimeError('Unexpected PPG/accelerometer schema in '+name)
        for w in rec['windows']:
            wi=int(w['window']); start=wi*WINDOW*FS; end=start+WINDOW*FS
            if start<0 or end>len(arr):raise RuntimeError('Window outside sensor array '+name)
            ppg=arr[start:end,0]
            acc=arr[start:end,1:]*factor
            finite=bool(np.isfinite(ppg).all() and np.isfinite(acc).all())
            expect='finite' if finite else 'nonfinite_skip'
            if check[(name,wi)]!=expect:
                raise RuntimeError('Sensor QC disagrees with original Phase32 probe '+name+' '+str(wi))
            analysis=pilot_window(ppg,acc,FS) if finite else None
            rows.append({
                'record':name,'subject':rec['subject'],'activity':rec['activity'],
                'window':wi,'start_seconds':wi*WINDOW,
                'sensor_QC':expect,'original_frozen_accepted_bpm':w['prediction_bpm'],
                'original_frozen_kind':w['source'],'original_phase13_candidate_bpm':w['frozen_phase13_bpm'],
                'pilot':analysis,
            })
        print(name,'processed',len(rec['windows']),'windows (sensor channels only)',flush=True)
    if len(rows)!=332:raise RuntimeError('Incomplete: expected exactly 332 windows')
    payload={
        'status':'PHASE34_REAL_SENSOR_EXPLORATORY_PILOT_NO_ECG_USED_NOT_VALIDATION',
        'dataset_partition':'PHASE31_ALREADY_EXAMINED_DEVELOPMENT_DATA',
        'reference_accessed_during_sensor_pilot':False,
        'prediction_is_not_accepted_or_medically_validated':True,
        'source_checks':{
            'official_archive_sha256':sha_file(ZIP),
            'phase31_locked_predictions_sha256':lock['predictions_sha256'],
            'phase32_raw_probe_sha256':sha_file(PROBE),
            'phase32_raw_probe_source_sha256':sha_file(Path(old.__file__)),
            'phase33_experimental_model_sha256':sha_file(ROOT/'Phase33SignalExperiment.py'),
            'phase34_pilot_source_sha256':sha_file(Path(__file__)),
        },
        'method':'20 second windows at 256Hz, original header-based PPG+3 ACC channels; Phase33 exploratory nonlinear motion regression and subwindow stability diagnostics',
        'records':rows,
        'limitations':['Already examined development material only; never an untouched holdout.',
            'Residual peak is not proof of cardiac identity.',
            'Motion regression may remove real cardiac power near cadence.',
            'No trained or prospectively validated reliability policy.',
            'Do not treat this algorithm as medical or astronaut monitoring.'],
    }
    status=write_new_only(OUT,_json_bytes(payload))
    print('PHASE34 SENSOR PILOT:',status,'Upload:',OUT)
    return payload


def smoke():
    ppg,acc,fs=synthetic_case()
    result=pilot_window(ppg,acc,fs)
    assert len(result['raw_top_five'])>0 and len(result['residual_top_five'])>0
    print('SYNTHETIC SMOKE ONLY raw:',result['exploratory_raw_ppg_peak_bpm'],
          'residual:',result['exploratory_residual_peak_bpm'])
    return result


if __name__=='__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--smoke',action='store_true',help='synthetic smoke only; DOES NOT read human waveforms')
    a=cli.parse_args()
    try:
        smoke() if a.smoke else run_real()
    except Exception as ex:
        print('HARD STOP:',type(ex).__name__,str(ex),file=sys.stderr)
        sys.exit(1)
