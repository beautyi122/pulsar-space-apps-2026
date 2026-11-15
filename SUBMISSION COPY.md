# Pulsar — suggested NASA project text (entrant review required)

**Project title:** Pulsar: Motion-Aware Astronaut Health Intelligence

**Team:** Stella Nova

**Challenge:** Create Health Monitoring Software for Astronauts on Space Missions

**Short summary**

Pulsar is a motion-aware astronaut health-monitoring research demonstrator. Wrist optical sensors can confuse repeated arm movement with a heartbeat, creating plausible-looking but wrong values. Pulsar combines synchronized PPG and accelerometer signals to generate motion-separated frequency candidates, tests a separate reliability-warning model, and turns uncertainty into a transparent crew action: cautiously display, repeat/verify, or withhold an unreliable reading. Its web application includes real human exercise replay, a local browser-only sensor experiment, astronaut check-ins, and NASA Human Research Program-informed mission context.

**Technical contribution**

The research combines nonlinear accelerometer harmonics and lags with five-block out-of-fold motion regression, then studies a risk classifier intended to predict serious (≥15 bpm) disagreement with ECG. The classifier is evaluated through leave-one-participant-out development folds, with inner participant-held-out threshold selection. ECG references are used only in training/evaluation—not sensor-only candidate extraction. A separate in-browser analyzer processes a new synchronized 20-second CSV without a server; it uses an explicitly labeled approximation and does not run the trained risk classifier or certify heart rates.

**Evidence and limitations**

The development dataset contains 332 20-second windows from eight participants across 19 terrestrial exercise recordings. In this already-examined set, the unfiltered raw strongest-peak method had 36.35 bpm mean absolute error across 329 candidates, versus 21.69 bpm for motion-separated candidates. In the retrospective participant-held-out reliability experiment, the guarded system displayed 125 of 332 windows (37.7%) at 3.62 bpm conditional mean absolute error, with **eight serious errors**. Running performed poorly, with only 2 of 73 windows displayed and one serious error. Different displayed subsets must not be compared as if they were identical cases. No new untouched clinical or astronaut-flight validation has occurred, and Pulsar is not medical software.

**NASA data and resource use**

The official challenge's NASA Human Research Program resources—Five Hazards of Human Spaceflight, Risks of Human Spaceflight, and Ongoing HRP Research in Space—shape the mission-specific logic. Altered gravity and cardiovascular adaptation motivate monitoring integrity; distance from Earth motivates explicit uncertainty, independent check-ins and review-oriented guidance. Supplementary NASA exercise-reference findings inform the mission-context comparison and are not clinical thresholds. Ground-truth optical/ECG measurements come from PhysioNet Wrist PPG During Exercise, not astronauts. All sources are linked and differentiated in `science/NASA RESOURCES.md`.

**Links (after updating GitHub)**

- Final project: https://beautyi122.github.io/pulsar-space-apps-2026/
- Public source and evidence: https://github.com/beautyi122/pulsar-space-apps-2026
- Seven-slide demonstration (expected once uploaded): https://beautyi122.github.io/pulsar-space-apps-2026/demo/Pulsar%20Demo.pdf

**Required entrant-authored disclosures and provenance**

Add your own required AI/tool disclosure to the NASA submission form and any required repository/project metadata, including AI-generated imagery/video watermark requirements if applicable. Review and accurately distinguish work performed before the official November 14 start from modifications made during the hackathon. Do not submit a claim about development dates or authorship that you cannot document. Confirm the chosen Local/Universal Event and number of registered participants against current Global Judging eligibility rules.
