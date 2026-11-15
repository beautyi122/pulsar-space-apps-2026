# Pulsar — scientific methods and limitations

**Team:** Stella Nova. **Challenge:** Create Health Monitoring Software for Astronauts on Space Missions. **Scope:** research demonstrator, not an approved monitoring device.

## Question and falsifiable claim

Can synchronized wrist acceleration help remove motion-generated periodicity in wrist optical PPG, and can a separate sensor-derived risk model reduce the number of misleading candidate heart rates displayed without suppressing all monitoring availability?

The hypothesis is falsifiable by comparing absolute errors against a simultaneously measured ECG reference, reporting accepted coverage and serious errors, and evaluating excluded participants. There is no clinical claim or astronaut-flight validation.

## Source and partition

The terrestrial physiological experiment uses PhysioNet's *Wrist PPG During Exercise* archive (ODC-By 1.0) with synchronized optical PPG, three-axis accelerometry, and ECG. The experiment includes **eight participants, 19 recordings and 332 ECG-referenced, 20-second windows**. These recordings were examined during the research development process, so the reported evaluation is **retrospective development evidence rather than untouched independent validation**.

The raw-signal experiment reads PPG and accelerometer channels only. ECG is opened separately to calculate development errors and train the error-risk classifier. `Phase34Run.py`, `Phase33SignalExperiment.py`, `Reliability.py`, `AnalyzeCSV.py`, data inputs and frozen hashes are supplied for audit.

## Estimation stage

1. Validate 256 Hz synchronized PPG + 3 accelerometer channels, twenty seconds per analysis window; reject nonfinite input.
2. Band-limit the optical signal. Derive accelerometer bases, their squares, cross-terms and magnitude, and three time lags for each base.
3. Fit ridge regressions on four of five contiguous time blocks and predict motion-correlated signal on the fifth; concatenate out-of-fold predictions.
4. Subtract the predicted motion-correlated component; inspect raw versus residual optical spectral peaks in the physiological candidate band, including subwindow stability.
5. **Important:** subtracting correlated motion can also remove true cardiac components if pulse and movement rhythms synchronize. The residual peak is a *candidate*, not a verified heart rate.

### Public browser implementation

`browser-signal.js` runs the sensor analysis **on the device**, without any request to a server. It uses a power-of-two FFT/zero-padded bandpass approximation rather than the Python pipeline's original exact-length FFT. It preserves the nonlinear basis and blocked ridge idea but is **not byte-for-byte numerically equivalent to the Python implementation**. It does not carry or execute the Python ExtraTrees risk classifier. Its output is a diagnostic, always shown as *WITHHELD / NOT A VERIFIED HEART RATE*. Judge the scientific accuracy claims on the packaged Python reference and its separate ECG development scoring, not the web input module.

## Reliability architecture and held-out experiment

`Reliability.py` constructs 32 sensor-derived features from residual and raw candidates, periodicity, motion spectra, stability and activity category. It trains an `ExtraTreesClassifier` predicting the **risk of ≥15 bpm estimation error**. The outer evaluation excludes one entire participant. Within each outer training fold, another leave-one-participant-out procedure selects the acceptance threshold from a prespecified 35%-eligible-coverage score quantile. ECG references never enter runtime features. This is a retrospective **participant-held-out development evaluation**, not a previously untouched validation cohort.

Reported model scores are **uncalibrated**; their raw values must not be presented as clinical probabilities.

## Measured results and denominators

| Comparison | Number displayed/available | Coverage out of 332 ECG-eligible | Conditional MAE (bpm) | Serious errors (≥15 bpm) |
|---|---:|---:|---:|---:|
| Reference accepted-decision baseline | 54 | 16.3% | 21.07 | 16 |
| Raw PPG strongest peak, unfiltered | 329 | 99.1% **candidate availability only** | 36.35 | 189 |
| Motion-separated strongest peak, unfiltered | 329 | 99.1% **candidate availability only** | 21.69 | 126 |
| Reliability-guarded display, outer participant-held-out | 125 | 37.7% | 3.62 | 8 |

The *accepted subsets differ*. Comparing the conditional MAEs does not isolate pure estimation improvement, and near-total candidate availability is not reliable display coverage. This is a study of the error/availability trade-off; preserve these denominators and caveats.

### By activity for guarded display

| Activity | Displayed / all evaluated windows | MAE among displayed | Serious errors among displayed |
|---|---:|---:|---:|
| High-resistance bike | 51 / 63 | 1.49 bpm | 0 |
| Low-resistance bike | 44 / 87 | 3.68 bpm | 1 |
| Walking | 28 / 109 | 6.46 bpm | 6 |
| Running | 2 / 73 | 16.82 bpm | 1 |

The denominators in the activity table count **all evaluated 20-second windows**, including the three windows without valid sensor candidates. Windows within people and recordings are dependent. Cluster bootstrap summaries over participants (95% descriptive interval, not external guarantees) are in `results/Reliability Evidence.json`.

## Reproduction

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r science/requirements.txt
python -m unittest discover -s science/tests -v
python science/research/AnalyzeCSV.py 'science/app/Synthetic PPG.csv' --activity walk
```

With Node.js installed, also run:

```bash
node science/tests/test_app.js
node tests/browser-signal.test.js
```

`science/research/Reliability.py` can be rerun using the bundled preserved reference evidence and derived development inputs; **running it refits and overwrites its output files**. Keep the provided results intact for frozen provenance. Fresh raw-signal preprocessing requires the original PhysioNet WFDB dataset cache and the source dataset reader, not just the saved JSON artifacts. Source hashes and partition limitations are documented in the bundled evidence.

## Scope of evidence

These results are retrospective development findings from eight participants, with activity-dependent performance and uncalibrated risk scores. The saved fully fitted model is a research artifact and has no untouched external validation score. The system has not been evaluated as a clinical device or on astronaut flight measurements. The full result counts and comparative outcomes remain in [RESULTS.md](RESULTS.md) and the preserved evidence records.
