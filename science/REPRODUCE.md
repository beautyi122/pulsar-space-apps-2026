# Pulsar — reproduce the reported evidence

Run from the **repository root** with Python 3.11+ and Node.js where applicable. The pinned Python dependencies are in `science/requirements.txt`.

## Tests (do not modify original results)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r science/requirements.txt
python -m unittest discover -s science/tests -v
node science/tests/test_app.js
node tests/browser-signal.test.js
```

These tests verify source hashes, record counts, no ECG input to sensor features, numerical summaries, synthetic motion separation, and the DOM control bindings. Browser automation and actual smartphone visual interaction require an additional human inspection.

## Recreate the complete participant-held-out development result

**Run the evaluation only in a disposable copy of the `science/` directory.** The original script writes model and evidence files to `science/results/`. Rerunning it in place would overwrite the frozen deposited outputs.

```bash
cp -R science science-reproduction
python science-reproduction/research/Reliability.py
```

Compare `science-reproduction/results/Reliability Evidence.json` against `science/results/Reliability Evidence.json` (and their SHA-256 hashes). The recorded reproduction audit regenerated **identical JSON evidence, model descriptor and serialized model bytes**, matching the deposited SHA-256 hashes.

The experiment is a nested leave-one-participant-out **development** evaluation, with its inner acceptance thresholds chosen from each outer training partition. The script does **not** convert previously examined participants into an untouched cohort.

## Run a new synthetic sample through the research input

```bash
python science/research/AnalyzeCSV.py 'science/app/Synthetic PPG.csv' --activity walk
```

The intended synthetic pulse is approximately 99 bpm; the motion-dominated raw peak is approximately 173.91 cycles/min, and the motion-separated candidate approximately 98.91 cycles/min. **This is a controlled synthetic diagnostic and not evidence of clinical accuracy.**

The static website's browser-based CSV analysis uses an approximation of this pipeline and always withholds its result as an unverified candidate. It is not the same as the Python trained classifier.

## To reproduce the raw-signal pilot from waveform files

Fresh raw waveform processing requires the original PhysioNet records/cache, the original referenced header-based loader, and the `wfdb` Python package (for example, `pip install wfdb==4.3.1`). The ZIP includes derived sensor-only features and the corresponding scoring artifacts, but **not** the entire original human waveform dataset. See [METHODS.md](METHODS.md) for exact constraints, and [Attributions.md](Attributions.md) for the data source.

## Verification inventory

`Release Manifest.json` records SHA-256 hashes of every deposited science file except the manifest itself. Do not alter the archived inputs or trained-model bytes without explicitly recording a new version.
