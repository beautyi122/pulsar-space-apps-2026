# Pulsar — Motion-aware Astronaut Health Intelligence

**Team:** Stella Nova · **NASA Space Apps Challenge 2026** · **Challenge:** Create Health Monitoring Software for Astronauts on Space Missions

## Open the live research demonstrator

[Public website](https://beautyi122.github.io/pulsar-space-apps-2026/) · [Official challenge](https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/)

**Pulsar's research question:** When wrist motion makes an optical heart-rate signal look convincingly wrong, can an algorithm recover alternative candidates and decide when to withhold a doubtful measurement?

This is a **finished interactive research demonstration with exploratory sensor analysis**, not a clinically validated health device. The public interface runs on static GitHub Pages, and the uploaded 20-second CSV is processed completely inside the browser. It does not run the Python trained risk classifier; the browser tool's outputs are unverified frequency candidates.

### Inspect and reproduce the science

- [Scientific methods, metrics, splits and limitations](science/METHODS.md)
- [Exact NASA challenge-resource integration](science/NASA%20RESOURCES.md)
- [Python reference implementation](science/research/)
- [Frozen scientific results](science/results/)
- [Development input evidence and integrity record](science/input/)
- [Automated tests](science/tests/)
- [Competition evidence and provenance](science/Submission%20Check.md)

The website's `data.js` is a replay of development decisions, not a live stream from spacecraft. Accuracy statistics are retrospective **participant-held-out development**, based on 332 windows from eight participants, and cannot establish clinical or astronaut performance. The new reliability architecture displayed 125 readings (37.7% coverage), 3.62 bpm conditional MAE and **8 serious errors**. Running was especially poor (2/73 displayed). The original strict scientific Gate 4 is not met.

### Run locally

Open `index.html` in a browser for the static application and local CSV analysis. Sample input: `Synthetic PPG.csv` (a **simulated**, 5120-row 20-second synchronized PPG/accelerometer recording).

For the original Python reference algorithm and research tests:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r science/requirements.txt
python -m unittest discover -s science/tests -v
python science/research/AnalyzeCSV.py 'science/app/Synthetic PPG.csv' --activity walk
node tests/browser-signal.test.js
```

### Space relevance and sources

The [NASA Human Research Program Five Hazards](https://www.nasa.gov/hrp/hazards/), [Human Spaceflight Risks](https://www.nasa.gov/hrp/risks/) and [Ongoing Research](https://www.nasa.gov/hrp/ongoing-hrp-research/) resources from the official challenge inform the application's measurement-integrity rationale and crew review workflow. See [NASA resource mapping](science/NASA%20RESOURCES.md). Additional NASA OCHMO exercise background is used as non-clinical reference context. Human PPG/ECG development evidence comes from [PhysioNet Wrist PPG During Exercise](https://physionet.org/content/wrist/1.0.0/) (ODC-By 1.0). This is not NASA astronaut data.

### Submission integrity

No independent final holdout. No live astronaut data. No medical efficacy claim. All synthetic data explicitly identified. Published methodology and results preserve research provenance. This repository does not imply NASA endorsement.

**Disclosure**

[Insert your disclosure here.]

**Project development history**

[Insert accurate project provenance and any earlier work used here.]

**Licensing and rights**

[Insert your reviewed licensing and rights statement here. Third-party source attributions remain in `science/Attributions.md`.]
