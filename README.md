# Pulsar — Motion-Aware Astronaut Health Intelligence

**Team:** Stella Nova · **NASA Space Apps Challenge 2026**  
**Challenge:** [Create Health Monitoring Software for Astronauts on Space Missions](https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/)

**[Explore the live Pulsar website](https://beautyi122.github.io/pulsar-space-apps-2026/)**

## Why Pulsar?

During movement, a wrist optical pulse sensor can mistake motion-related patterns for a heartbeat. A convincing-looking number is not necessarily a dependable measurement.

Pulsar explores how motion-aware signal processing and measurement-reliability assessment can help a crew member interpret uncertain wrist-sensor readings. It combines scientific analysis with an interactive astronaut-health application that brings the evidence, uncertainty and crew self-assessment into one place.

## What the application offers

- **Interactive research replay:** Explore recorded exercise intervals, candidate pulse frequencies and measurement decisions.
- **Motion-aware analysis:** See how synchronized optical PPG and accelerometer signals can help distinguish physiological rhythm candidates from movement-related interference.
- **Reliability-focused reporting:** Investigate when a candidate reading is suitable to display and when a follow-up check is more appropriate.
- **Exploratory CSV analysis:** Examine a compatible short sensor recording locally in the browser.
- **Crew self-assessment and mission context:** Explore a review-oriented check-in alongside NASA human-research and exercise resources.

The interactive replay presents stored research findings. The exploratory CSV feature and the preserved Python reliability evaluation serve different purposes; the research measurements and validation methodology are documented in the scientific files below.

## Scientific evidence

The retrospective development study used **332 twenty-second windows** from **19 terrestrial exercise recordings across eight participants**. Among **329 windows with usable sensor candidates**, the raw strongest-peak estimate had a mean absolute error of **36.35 bpm**, compared with **21.69 bpm** for the motion-separated candidate.

In the participant-held-out reliability evaluation, the guarded approach displayed **125 of 332 windows (37.65% coverage)**, with **3.623 bpm mean absolute error among displayed readings**. Eight displayed readings had errors of at least 15 bpm.

These figures describe different evaluation subsets: conditional error among selectively displayed readings should be interpreted together with coverage, not as a direct like-for-like improvement over an unfiltered candidate stream. Activity-level results and full methodological qualifications are provided in the [scientific results](science/RESULTS.md) and [methods](science/METHODS.md).

## Scientific documentation and source

| Resource | Contents |
| --- | --- |
| [Scientific overview](science/README.md) | Research package and evidence guide |
| [Methods](science/METHODS.md) | Signal processing, risk modelling and evaluation design |
| [Results](science/RESULTS.md) | Quantitative comparisons and activity-level findings |
| [Reproduction guide](science/REPRODUCE.md) | Testing and independent recalculation instructions |
| [Research source code](science/research/) | Python analysis and evaluation implementation |
| [Experimental inputs](science/input/) | Preserved research inputs and supporting evidence |
| [Saved results and model](science/results/) | Evaluated outputs and model artifacts |
| [Scientific tests](science/tests/) | Python and archived-application tests |
| [Browser signal test](tests/browser-signal.test.js) | Sensor-input test for the archived browser implementation |
| [Evidence verification](science/Verification.md) | Reproducibility notes and integrity checks |
| [Release manifest](science/Release%20Manifest.json) | File sizes and SHA-256 hashes |
| [NASA resource mapping](science/NASA%20RESOURCES.md) | Connections between NASA research and application design |
| [Sources and attribution](science/Attributions.md) | Data origins, publications and software dependencies |

The `science/app/` directory contains a preserved application snapshot for regression testing; the current public website is served from the repository-root `index.html`.

## Reproduce the recorded evaluation

From the repository root, with Python 3.11+ and Node.js installed where applicable:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r science/requirements.txt
python -m unittest discover -s science/tests -v
node science/tests/test_app.js
node tests/browser-signal.test.js
```

For the complete evaluation workflow and instructions that avoid overwriting the deposited results, see [REPRODUCE.md](science/REPRODUCE.md).

A simulated 20-second synchronized PPG/accelerometer sample is provided as [Synthetic PPG.csv](Synthetic%20PPG.csv). It is demonstration data, not an astronaut recording.

## NASA relevance and research sources

NASA [Human Research Program hazards](https://www.nasa.gov/hrp/hazards/), [spaceflight risks](https://www.nasa.gov/hrp/risks/) and [ongoing research](https://www.nasa.gov/hrp/ongoing-hrp-research/) informed the application's mission context, focus on measurement integrity and crew review workflow. Additional NASA exercise references inform the contextual comparison in the interface.

The physiological research data come from the terrestrial [PhysioNet Wrist PPG During Exercise dataset](https://physionet.org/content/wrist/1.0.0/) rather than NASA astronaut recordings. Dataset attribution and applicable licensing information are recorded in [science/Attributions.md](science/Attributions.md).

## Scientific scope and licensing

Pulsar is a research demonstrator, not an approved clinical or flight-monitoring device. The reported results are retrospective development findings; independent testing would be required to establish performance in new populations or operational settings.

The repository's [MIT LICENSE](LICENSE) covers original materials the Stella Nova contributors are authorized to license. Third-party data and resources retain their applicable terms. This project does not imply NASA endorsement.
