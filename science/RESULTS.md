# Pulsar — measured scientific results

This page summarizes *development* evidence, not independent validation or spacecraft performance.

## Estimation and reliability comparison

| System | Displayed readings / available candidate readings | Coverage of all 332 windows | Conditional MAE (bpm) | Serious errors (absolute error ≥15 bpm) |
|---|---:|---:|---:|---:|
| Reference accepted-decision baseline | 54 | 16.3% | 21.07 | 16 |
| Raw PPG top-peak candidate, **unfiltered** | 329 | 99.1% candidate availability only | 36.35 | 189 |
| Motion-separated PPG top-peak candidate, **unfiltered** | 329 | 99.1% candidate availability only | 21.69 | 126 |
| Guarded display, participant-held-out development | 125 | 37.65% | 3.623 | 8 |

**Comparison interpretation:** The accepted subsets differ, so the conditional errors cannot be interpreted as a paired estimate of one algorithm's pure heart-rate advantage over the other. A nearly complete stream of *candidates* is not nearly complete *reliable monitoring*.

The unfiltered raw versus residual candidate streams can be compared on their 329 jointly available windows; the motion-separated estimate was closer to ECG on 179, farther on 96, and tied on 54. These observations support a useful mechanism, not guaranteed reliability.

## Activity breakdown for guarded output

| Activity | Displayed / all evaluated windows | MAE among displayed (bpm) | Serious errors among displayed |
|---|---:|---:|---:|
| High-resistance cycling | 51/63 | 1.49 | 0 |
| Low-resistance cycling | 44/87 | 3.68 | 1 |
| Walking | 28/109 | 6.46 | 6 |
| Running | 2/73 | 16.82 | 1 |

Performance varies by activity, particularly during running. The uncalibrated model score is an experimental risk ranking, not an individual clinical probability.

## Evaluation integrity

- Eight participants, 19 recordings, 332 non-overlapping 20-second ECG-eligible windows; three windows lack finite sensor candidates.
- The reliability evaluation excludes the assessed participant from the model fit and threshold selection within each outer fold; the dataset and its failure modes had also informed the development process.
- ECG labels support training and retrospective scoring, not the sensor-only waveform transformation or browser upload.
- The same material was **not** an untouched final validation set; no astronauts or live mission recordings were tested.
- Deterministic evidence: `results/Reliability Evidence.json`; saved classifier and model description in `results/`; compare `input/Phase 34 Development Comparison.json` for the raw versus motion-separated retrospective pilot.

The evidence therefore supports a retrospective method evaluation, with further independent testing required for deployment-oriented claims.
