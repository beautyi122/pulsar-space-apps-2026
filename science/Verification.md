# Pulsar — evidence integrity and reproducibility

The scientific package preserves the original research algorithms, derived sensor inputs, frozen reliability evaluation, serialized model, and automated tests. The source filenames and JSON keys identify the analytical pipeline and must not be silently rewritten.

## Evidence summary

- Dataset: PhysioNet *Wrist PPG During Exercise*, eight development participants, 19 recordings and 332 evaluated 20-second windows.
- Candidate availability: 329 of 332 windows.
- Retrospective participant-held-out guarded display: 125 of 332 windows, 37.65% coverage, 3.623 bpm conditional mean absolute error, eight serious errors (absolute error at least 15 bpm).
- The results are **retrospective development findings**; no independent final holdout or astronaut measurements were used.

## File integrity

The `Release Manifest.json` file records SHA-256 checksums and byte sizes of all deposited files in `science/`, except the manifest itself. Research source code and the original saved experimental inputs and outputs have been retained byte-for-byte from the supplied source archive. The publication documents have been revised for clarity and their hashes regenerated.

## Reproduction

Automated tests validate file integrity, record counts, numerical summaries, feature separation and the archived browser demonstration. The saved-data evaluation can be reproduced using [REPRODUCE.md](REPRODUCE.md); it must be rerun in a disposable copy so the published output files are not overwritten. Complete preprocessing from the original raw waveforms requires the separately sourced PhysioNet recordings and the referenced upstream header-based reader, which are not bundled.

## Safe handling of model artifacts

The preserved `.joblib` model is a serialized Python object and should only be deserialized in a trusted environment after verifying its checksum. The JSON model descriptor and numerical evidence can be inspected without loading the serialized model.
