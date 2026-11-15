#!/usr/bin/env python3
"""Phase32 signal-only spectral/motion diagnostic on Phase31 ALREADY-EXAMINED data.

Reads only PPG and accelerometer channels. NEVER loads ECG waveforms or .atr
annotations and NEVER recomputes or overwrites the Phase30/31 model, locked
predictions, or their external validation results. Not independent validation.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math, re, sys, zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
CORE=Path.home()/'Downloads'/'Phase 30-31'
SRC=CORE/'External.py'
CACHE=CORE/'cache'/'wrist_original'
ZIP=CORE/'cache'/'wrist-1.0.0.zip'
OUT=ROOT/'results'/'Phase 32 Raw Signal Probe.json'
IN=ROOT/'input'/'Phase 31 Evidence.zip'
FS=256
WINDOW=20


def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def power_spectrum(x,fs=256):
    """Unitless relative PPG/ACC spectral power; diagnostic, not a rate estimator."""
    from scipy.signal import detrend
    a=np.asarray(x,dtype=float)
    if a.ndim!=1 or len(a)<2*fs or not np.all(np.isfinite(a)):
        raise ValueError('Invalid signal for diagnostic spectrum')
    d=detrend(a,type='linear'); d-=np.mean(d)
    f=np.fft.rfftfreq(len(d),d=1/fs)
    p=np.abs(np.fft.rfft(d*np.hanning(len(d))))**2
    inband=(f>=0.5)&(f<=3.5)
    norm=float(np.sum(p[inband]))
    if norm<=1e-18: return f,np.zeros_like(p)
    return f,p/norm


def band(fr,po,rate_bpm,margin_bpm=6):
    if rate_bpm is None:return None
    v=float(po[(np.abs(fr*60-float(rate_bpm))<=margin_bpm)].sum())
    return round(v,7)


def top_peaks(fr,po,n=5):
    rates=fr*60; valid=np.where((rates>=40)&(rates<=210))[0]
    order=sorted(valid,key=lambda i:-po[i]);picked=[]
    for idx in order:
        if all(abs(rates[idx]-q['bpm'])>=6 for q in picked):
            picked.append({'bpm':round(float(rates[idx]),3),'power_fraction':round(float(po[idx]),7)})
        if len(picked)>=n:break
    return picked


def signal_features(ppg, acc, selected, original):
    pf,pp=power_spectrum(ppg,FS)
    mf,mp=power_spectrum(acc,FS)
    return {'ppg_top_spectral_peaks':top_peaks(pf,pp),
            'acc_top_spectral_peaks':top_peaks(mf,mp),
            'ppg_power_at_selected_rate':band(pf,pp,selected),
            'ppg_power_at_original_rate':band(pf,pp,original),
            'ppg_power_at_half_selected':band(pf,pp,selected/2 if selected else None),
            'acc_power_at_selected_rate':band(mf,mp,selected),
            'acc_power_at_original_rate':band(mf,mp,original),
            'acc_power_at_half_selected':band(mf,mp,selected/2 if selected else None),
            'ppg_std_raw_record_units':round(float(np.std(ppg)),6),
            'acc_magnitude_std_g':round(float(np.std(acc)),6)}


def select_channels_external(external,header):
    units=[str(u).lower().replace(' ','').replace('ms^-2','m/s^2') for u in header.units]
    ppg,acc,factor,channels=external.find_channels(header.sig_name,units)
    return ppg,acc,factor,channels


def load_original_external():
    if not SRC.is_file():raise FileNotFoundError('Original Phase 30-31/External.py not found; do not replace files')
    with zipfile.ZipFile(IN) as z:
        freeze=json.loads(z.read('Phase 30 Freeze Manifest.json'))
    if sha_file(SRC)!=freeze['phase31_source_sha256']:
        raise RuntimeError('Original external code differs from frozen manifest; hard stop')
    spec=importlib.util.spec_from_file_location('original_frozen_external',SRC)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj


def run():
    if not IN.exists():raise FileNotFoundError('Bundled unmodified Phase31 evidence ZIP missing')
    with zipfile.ZipFile(IN) as z:
        preds=json.loads(z.read('Phase 31 Locked Predictions.json'))
        lock=json.loads(z.read('Phase 31 Prediction Lock.json'))
        freeze=json.loads(z.read('Phase 30 Freeze Manifest.json'))
        original_predictions=z.read('Phase 31 Locked Predictions.json')
    if lock['predictions_sha256']!=hashlib.sha256(original_predictions).hexdigest():
        raise RuntimeError('Phase31 predictions integrity mismatch')
    if not ZIP.is_file() or not CACHE.is_dir():
        raise FileNotFoundError('Phase31 cached official dataset not found. Expected '+str(ZIP)+' and '+str(CACHE))
    if sha_file(ZIP)!=preds['archive_sha256']:
        raise RuntimeError('Cached official source ZIP differs from original Phase31; hard stop')
    external=load_original_external()
    import wfdb
    records=[]
    for rec in preds['records']:
        name=rec['record'];base=CACHE/name
        if not base.with_suffix('.hea').is_file():raise FileNotFoundError('Missing official header '+str(base))
        head=wfdb.rdheader(str(base))
        ppg,acc,factor,channels=select_channels_external(external,head)
        # Restrict read to selected PPG + 3 ACC streams. No ECG channel or ECG annotation accessed.
        data=wfdb.rdrecord(str(base),channels=[ppg,*acc],physical=True)
        a=np.asarray(data.p_signal,dtype=float)
        if a.ndim!=2 or a.shape[1]!=4 or data.fs!=FS:
            raise RuntimeError('Unexpected selected sensor schema '+name)
        motion=np.sqrt(np.sum((a[:,1:]*factor)**2,axis=1))
        out=[]
        for w in rec['windows']:
            wi=int(w['window']);start=wi*WINDOW*FS;end=(wi+1)*WINDOW*FS
            if end>len(a):raise RuntimeError('Window bounds exceed official source '+name)
            ppg_seg=a[start:end,0];motion_seg=motion[start:end]
            row={'window':wi,'start_seconds':wi*WINDOW,
                'selected_kind':w['source'],'selected_bpm':w['prediction_bpm'],
                'original_estimate_bpm':w['frozen_phase13_bpm'],
                'frozen_model_score':w['score_not_medical_probability']}
            if np.isfinite(ppg_seg).all() and np.isfinite(motion_seg).all():
                row['sensor_QC']='finite';row['signal_only_features']=signal_features(
                    ppg_seg,motion_seg,w['prediction_bpm'],w['frozen_phase13_bpm'])
            else:
                row['sensor_QC']='nonfinite_skip';row['signal_only_features']=None
            out.append(row)
        records.append({'record':name,'subject':rec['subject'],'activity':rec['activity'],
                        'channels_selected_no_ECG':channels,'windows':out})
        print(name,len(out),'windows, ECG never opened',flush=True)
    payload={'status':'PHASE32_RAW_SIGNAL_PROBE_RETROSPECTIVE_DEV_NO_ECG_ACCESSED',
             'official_archive_sha256':sha_file(ZIP),
             'phase31_locked_prediction_sha256':lock['predictions_sha256'],
             'phase30_frozen_model_sha256':freeze['model_sha256'],
             'phase32_probe_source_sha256':sha_file(Path(__file__)),
             'method':'Whole 20-s raw 256-Hz sensor-only segment: linear detrending, Hann-spectrum relative power in 0.5-3.5 Hz; 6-bpm power bands; no change to original predictor.',
             'no_ECG_reference_used_in_this_probe':True,
             'no_model_refit_or_validation_rescoring':True,
             'records':records,
             'limitations':['This is a retrospective diagnostic on an ALREADY inspected external dataset, NOT independent validation.',
                           'Window-local frequency power is not identical to the original full-record 97-tap low-pass and interpolation.',
                           'Spectral peaks alone cannot identify true heartbeats; motion and cross-sensor ambiguity require separate validation.',
                           'No clinical or astronaut monitoring validation.']}
    OUT.parent.mkdir(exist_ok=True)
    data=json.dumps(payload,indent=2,allow_nan=False)+'\n'
    if OUT.exists() and OUT.read_text()!=data:raise RuntimeError('Existing diagnostic results differ, refusing to overwrite')
    OUT.write_text(data)
    print('COMPLETE. Upload:',OUT,flush=True)

if __name__=='__main__':
    try:run()
    except Exception as err:
        print('HARD STOP:',type(err).__name__,str(err),file=sys.stderr);sys.exit(1)
