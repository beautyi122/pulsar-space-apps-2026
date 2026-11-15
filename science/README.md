# Pulsar — scientific evidence directory

**Team:** Stella Nova · **Project:** Pulsar · **Scope:** research-backed engineering demonstrator.

## Start with these five documents

1. [Scientific methodology](METHODS.md): hypothesis, separation algorithm, reliability model, participant exclusions, metric denominators and limitations.
2. [Measured results](RESULTS.md): the exact comparative findings, activity-by-activity failures and interpretation.
3. [Reproduction instructions](REPRODUCE.md): commands that re-create the development evaluation without modifying the deposited frozen results.
4. [NASA resource mapping](NASA%20RESOURCES.md): direct NASA links and the design decisions those references informed.
5. [External attributions](Attributions.md): PhysioNet dataset, NASA references, software libraries and source rights.

## Files and evidence

- `research/`: readable Python algorithms and the evaluation procedure. Original frozen source filenames and source hashes are preserved.
- `input/`: preserved reference evidence, sensor-only features, a real-sensor pilot and a retrospective development comparison. These inputs are **not** a new independent holdout.
- `results/`: the exact deterministic out-of-participant development predictions, experiment summary, final research model and output logs.
- `tests/`: Python and Node.js tests; root `tests/` contains an additional browser-only sensor test.
- `app/`: an archived version of the application retained for scientific regression tests. The current public website is the repository-root `index.html`; this archive is not its current design.
- `Release Manifest.json`: per-file size and SHA-256 inventory, excluding itself to avoid recursive hashing. See [Verification.md](Verification.md).

## Scientific interpretation

The retrospective participant-held-out development evaluation covers 332 windows from eight participants. The reliability-guarded model displayed 125 readings (37.65% coverage) with a conditional mean absolute error of 3.623 bpm. Complete activity-wise findings, error counts and methodological limitations are reported in [RESULTS.md](RESULTS.md) and [METHODS.md](METHODS.md). The public CSV analyzer is an approximate browser implementation and does not execute the trained ExtraTrees reliability classifier.

No raw source waveform archive is bundled. Recreating the waveform preprocessing from scratch requires the separately acquired original PhysioNet WFDB records. Recreating the **saved-data reliability study** from the saved, integrity-checked inputs does **not** require re-downloading raw WFDB data.
