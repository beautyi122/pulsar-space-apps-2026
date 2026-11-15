# Data, software and scientific sources

## Wrist PPG development signals — third party

**Contains information from [Wrist PPG During Exercise v1.0.0](https://physionet.org/content/wrist/1.0.0/), made available under the [Open Data Commons Attribution License v1.0](https://physionet.org/content/wrist/view-license/1.0.0/).**

Jarchi, D. & Casson, A. J. (2017). *Description of a Database Containing Wrist PPG Signals Recorded during Physical Exercise with Both Accelerometer and Gyroscope Measures of Motion*. Data, 2(1), 1. https://doi.org/10.3390/data2010001

PhysioNet database record: Casson, A. (2017). *Wrist PPG During Exercise, version 1.0.0*. DOI: https://doi.org/10.13026/C2PQ1X

PhysioNet platform citation: Pollard, T. et al. (2026). *PhysioNet as a global platform for biomedical research*. Nature Health. DOI: https://doi.org/10.1038/s44360-026-00096-z

This research package contains derived window-level metrics, preserved reference evidence, and sensor-only analysis features—not the entire original raw database. The original data's attribution and license apply to covered derived uses.

## NASA sources — mission context

National Aeronautics and Space Administration (2023). NASA Office of the Chief Health & Medical Officer. *NASA-STD-3001 Technical Brief: Exercise Overview*, OCHMO-TB-031, p. 11. https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-031-exercise-overview.pdf

NASA (2024). *Astronaut Exercise*. https://www.nasa.gov/missions/station/iss-research/astronaut-exercise/

NASA (2025). *About the Open Science Data Repository*. https://science.nasa.gov/biological-physical/data/osdr/

NASA International Space Apps Challenge (2026). *Create Health Monitoring Software for Astronauts on Space Missions*. https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/

The technical brief's historic ISS exercise session summaries drive the app's NASA comparison module. They are NOT ECG truth data for this prototype and are NOT healthy/unsafe heart-rate thresholds. The OSDR link is included as a possible research resource for future work, **not** as a dataset analyzed in the reported experiments.

## Dependencies

Runtime code uses the Python standard library, NumPy, SciPy, scikit-learn and joblib. The optional raw-record reconstruction scripts additionally use the PhysioNet WFDB Python reader. Each dependency remains subject to its own publicly available license; the `requirements.txt` file lists required versions for reproducing the serialized classifier. Static web files use HTML, CSS and JavaScript with no external UI libraries or embedded copyrighted media.

## Scientific evidence lineage

The research evidence comprises signal-processing methods, sensor-based candidate estimates, reliability-model evaluation, source inputs, derived results, and accompanying tests. The methods, verification record, and release manifest provide traceable links between the reported findings and the preserved files. Technical filenames and machine-readable identifiers remain unchanged to support reproducibility.
