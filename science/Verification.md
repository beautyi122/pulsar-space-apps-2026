# Pulsar — evidence integrity and reproducibility

The scientific package preserves the original research algorithms, derived sensor inputs, frozen reliability evaluation, serialized model, and automated tests. The source filenames and JSON keys identify the analytical pipeline. Publication-only metadata edits are documented below.

## Evidence summary

- Dataset: PhysioNet *Wrist PPG During Exercise*, eight development participants, 19 recordings and 332 evaluated 20-second windows.
- Candidate availability: 329 of 332 windows.
- Retrospective participant-held-out guarded display: 125 of 332 windows, 37.65% coverage, 3.623 bpm conditional mean absolute error, eight serious errors (absolute error at least 15 bpm).
- The results are **retrospective development findings**; no independent final holdout or astronaut measurements were used.

## File integrity

The `Release Manifest.json` file records SHA-256 checksums and byte sizes of all deposited files in `science/`, except the manifest itself. Research source code, quantitative evidence and evaluation decisions are preserved. For publication, obsolete internal milestone-status fields were removed from two JSON files, and a milestone-specific sentence was replaced with a factual validation limitation. These editorial metadata changes do not alter measured results. The manifest records the resulting file sizes and hashes; publication documentation was revised for clarity.

## Reproduction

Automated tests validate file integrity, record counts, numerical summaries, feature separation and the archived browser demonstration. The saved-data evaluation can be reproduced using [REPRODUCE.md](REPRODUCE.md); it must be rerun in a disposable copy so the published output files are not overwritten. Complete preprocessing from the original raw waveforms requires the separately sourced PhysioNet recordings and the referenced upstream header-based reader, which are not bundled.

## Safe handling of model artifacts

The preserved `.joblib` model is a serialized Python object and should only be deserialized in a trusted environment after verifying its checksum. The JSON model descriptor and numerical evidence can be inspected without loading the serialized model.
