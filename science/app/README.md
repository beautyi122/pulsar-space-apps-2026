# Pulsar browser application

Team: Stella Nova. This folder contains an archived static application used by the scientific regression tests. The current public website is maintained separately at the repository root; this archived copy is not a representation of the current website design.

The public `browser-signal.js` sensor analyzer runs completely offline and provides *experimental, unverified frequency candidates only*. It is a documented FFT approximation of the reference Python method and does not execute the trained ExtraTrees risk classifier. The separate Python reference implementation under `../research/AnalyzeCSV.py` includes the development-trained classifier and remains research-only. Full methods: `../METHODS.md`.
