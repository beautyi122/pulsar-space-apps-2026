#!/usr/bin/env python3
"""EXPLORATORY motion-reference separation, not a heart-rate medical device.

Input format: .npz with ppg (N,), acc (N,3), fs (scalar); synchronized,
finite values, accelerometer and PPG at the SAME rate and time alignment.
Neither ECG nor any ground-truth labels are read by this experiment.
It emits candidates and diagnostics, NOT accepted reliable heart rates.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def fft_bandpass(x, fs, lo=.6, hi=3.5):
    x = np.asarray(x, dtype=float)
    x = x - np.mean(x,axis=0,keepdims=True)
    spec = np.fft.rfft(x, axis=0)
    freq = np.fft.rfftfreq(x.shape[0],d=1/fs)
    spec[(freq < lo) | (freq > hi),...] = 0
    return np.fft.irfft(spec,n=x.shape[0],axis=0)


def spectral_peaks(x,fs,top_k=5):
    x = np.asarray(x,float).ravel()
    n = len(x)
    nfft = 2**int(np.ceil(np.log2(n*4)))
    xx = (x-x.mean())*np.hanning(n)
    power = abs(np.fft.rfft(xx,n=nfft))**2
    hz = np.fft.rfftfreq(nfft,1/fs)
    valid = (hz >= 45/60) & (hz <= 210/60)
    candidates = np.flatnonzero(valid & (power > np.roll(power,1)) & (power >= np.roll(power,-1)))
    ranked = sorted(candidates,key=lambda i:power[i],reverse=True)
    picks = []
    for k in ranked:
        if all(abs(hz[k]-p['bpm']/60) >= 5/60 for p in picks):
            picks.append({'bpm':round(float(hz[k]*60),2),
                          'relative_power':round(float(power[k]/max(1e-16,power[valid].sum())),6)})
        if len(picks)>=top_k:
            break
    return picks


def shift_fill(x, shift):
    if shift == 0: return x.copy()
    shifted=np.empty_like(x)
    shifted[:shift]=0
    shifted[shift:]=x[:-shift]
    return shifted


def motion_design(acc,fs):
    # Harmonic terms capture gait modulation; no ECG or labels.
    a=np.asarray(acc,float)
    a=(a-a.mean(axis=0))/(a.std(axis=0)+1e-9)
    ax,ay,az = a.T
    mag=np.sqrt((a*a).sum(axis=1))
    bases=[ax,ay,az,ax*ax,ay*ay,az*az,ax*ay,ay*az,az*ax,mag]
    filtered=[fft_bandpass(q,fs) for q in bases]
    lags=sorted(set([0,max(1,int(fs*.04)),max(2,int(fs*.08))]))
    return np.column_stack([shift_fill(q,l) for q in filtered for l in lags])


def _blocked_motion_predict(y,X,nfolds=5,ridge=.04):
    n=len(y)
    valid = X.std(axis=0)>1e-7
    X=X[:,valid]
    if X.shape[1] == 0:
        return np.zeros(n)
    mean=X.mean(axis=0)
    std=X.std(axis=0)+1e-9
    X=np.column_stack([np.ones(n),(X-mean)/std])
    estimates=np.zeros(n)
    # Each contiguous segment gets predictions from a fit on OTHER segments.
    folds=np.array_split(np.arange(n),nfolds)
    for hold in folds:
        mask=np.ones(n,bool)
        mask[hold]=False
        train=X[mask]
        target=y[mask]
        lhs=train.T@train
        penalty=np.eye(X.shape[1])*ridge*len(train)
        penalty[0,0]=0
        coef=np.linalg.solve(lhs+penalty,train.T@target)
        estimates[hold]=X[hold]@coef
    return estimates


def analyze(ppg,acc,fs):
    ppg=np.asarray(ppg,float).reshape(-1)
    acc=np.asarray(acc,float)
    fs=float(fs)
    if not (fs>=10 and fs<=2000 and np.isfinite(fs)):
        raise ValueError('fs must be a finite sampling rate in [10,2000] Hz')
    if acc.ndim != 2 or acc.shape != (len(ppg),3):
        raise ValueError('acc must be synchronized to ppg, shaped (N,3)')
    if len(ppg)<int(fs*8):
        raise ValueError('at least eight seconds of synchronized data required')
    if not np.isfinite(ppg).all() or not np.isfinite(acc).all():
        raise ValueError('nonfinite sensor samples: stop rather than interpolate silently')
    y=fft_bandpass(ppg,fs)
    raw=spectral_peaks(y,fs)
    X=motion_design(acc,fs)
    pred=_blocked_motion_predict(y,X)
    residual=y-pred
    after=spectral_peaks(residual,fs)
    var_y=float(np.var(y))
    residual_var=float(np.var(residual))
    r2 = (1-residual_var/var_y) if var_y>1e-12 else 0.0
    # This is OUT-OF-FOLD predictability, not proof that subtracted component
    # is noncardiac. Genuine heart rhythms can synchronize with motion.
    return {
        'status':'EXPLORATORY_CANDIDATES_NOT_ESTIMATES',
        'no_ECG_or_ground_truth_used':True,
        'duration_seconds':len(ppg)/fs,
        'sampling_rate_hz':fs,
        'raw_ppg_peaks':raw,
        'out_of_fold_motion_prediction_r2':round(r2,6),
        'residual_ppg_peaks':after,
        'prototype_residual_top_peak_bpm':after[0]['bpm'] if after else None,
        'cannot_certify_heartbeat_or_reliability':True,
        'risk_note':'Motion regression can remove true heart rhythms near cadence; do not turn peak into accepted BPM without raw clinical-label evaluation.',
    }


def synthetic_case(seed=1,truth_bpm=99,step_bpm=87,noise=.11,heart_amplitude=1.0,motion_amplitude=5.0):
    rng=np.random.default_rng(seed)
    fs=128.0
    t=np.arange(20*128)/fs
    u=2*np.pi*step_bpm/60*t
    acc=np.column_stack([np.sin(u),np.sin(u+.8),np.cos(u+.3)])
    acc+=.03*rng.standard_normal(acc.shape)
    cardiac = heart_amplitude*(np.sin(2*np.pi*truth_bpm/60*t+.4)+.23*np.sin(4*np.pi*truth_bpm/60*t+.9))
    # Synchronous gait fundamental and its second harmonic; varied phases.
    motion=motion_amplitude*(.20*acc[:,0]+1.4*(acc[:,0]**2-.5)+.05*acc[:,1])
    ppg=cardiac+motion+noise*rng.standard_normal(len(t))
    return ppg,acc,fs


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--npz',help='Synchronized raw sensor file; if omitted, synthetic DEMO only')
    p.add_argument('--output',default='results/Phase 33 Signal Experiment.json')
    a=p.parse_args()
    if a.npz:
        with np.load(a.npz,allow_pickle=False) as z:
            ppg=np.array(z['ppg']);acc=np.array(z['acc']);fs=float(z['fs'])
        result=analyze(ppg,acc,fs)
        result['input_type']='RAW_SENSOR_INPUT'
        result['npz_sha256']=hashlib.sha256(Path(a.npz).read_bytes()).hexdigest()
    else:
        ppg,acc,fs=synthetic_case()
        result=analyze(ppg,acc,fs)
        result['input_type']='SYNTHETIC_DEMO_ONLY'
        result['synthetic_generation_truth_bpm_not_used_by_analyzer']=99
        result['synthetic_generation_motion_bpm_not_used_by_analyzer']=87
    out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Exploratory signal experiment:',result['input_type'])
    print('Raw top peak:', result['raw_ppg_peaks'][:1])
    print('Residual top peak:',result['residual_ppg_peaks'][:1])
    print('NOT an independently validated heartbeat estimate')
    print('output:',out)


if __name__=='__main__':
    main()
