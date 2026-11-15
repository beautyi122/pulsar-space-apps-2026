# NASA Space Apps 2026 — specific challenge resource integration

**The official challenge:** [Create Health Monitoring Software for Astronauts on Space Missions](https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/). The [official challenge resources tab](https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/?tab=resources) provides Human Research Program and Canadian Space Agency material.

## Official NASA Human Research Program resources used

| Resource | Authoritative observation | What Pulsar actually uses it for |
|---|---|---|
| [NASA HRP — Five Hazards](https://www.nasa.gov/hrp/hazards/) | Altered gravity affects the body's systems; distance from Earth complicates access to care | The astronaut console introduces uncertainty-aware measurement and locally interpretable next steps instead of blind reliance on a sensor value |
| [NASA HRP — Risks of Human Spaceflight](https://www.nasa.gov/hrp/risks/) | Cardiovascular adaptations are among the physiological risks of spaceflight | The NASA context tab maps cardiovascular risk to **measurement integrity**, a specific engineering problem relevant to monitoring during exercise |
| [NASA HRP — Ongoing HRP Research in Space](https://www.nasa.gov/hrp/ongoing-hrp-research/) | NASA investigates human performance and exercise/countermeasures during missions | The application provides a mission-context comparison and demonstrates how a sensor-risk observation becomes a crew check-in; not clinical guidance |

Additional technical NASA context: [NASA OCHMO exercise overview](https://www.nasa.gov/ochmo-tb-031-exercise-overview-2/) and the historical CEVIS/T2 exercise figures used for the comparison UI. This is **supplementary**. It is not an astronaut-labeled waveform evaluation dataset.

## NASA evidence → operational design

**NASA-identified hazard:** gravity transitions can affect the cardiovascular system, and distance from Earth makes crew autonomy more important.

**Engineering failure mode:** movement can dominate wrist optical PPG and imitate a pulse rate. Naïve peak selection can output a wrong but confident-looking number.

**Operational prototype response:** Pulsar uses synchronized acceleration to derive alternative optical frequency candidates and an error-risk scoring experiment to decide when to withhold a reading. The crew interface says *repeat/verify the reading and log unresolved uncertainty*, not diagnose cardiovascular disease.

**Evidence:** a clearly labeled terrestrial development experiment of 332 windows; NOT astronaut or microgravity validation.

**Limit:** HRP hazards/risks are source-derived mission motivations. The decision rule, risk model, and user interface are Stella Nova's research prototype. NASA does not approve or endorse the algorithm. No physiological reference range or medical action threshold is inferred from NASA's background publications.

## Source distinctions

NASA Human Research Program materials inform the application design and are explained in the mission-context interface. The cited NASA sources support mission requirements; PhysioNet supplies the terrestrial exercise benchmark. No NASA endorsement or astronaut-accuracy validation is implied.

The original experiment source is [PhysioNet Wrist PPG During Exercise](https://physionet.org/content/wrist/1.0.0/), licensed ODC-By 1.0. Its public human recordings, not NASA astronaut physiology, support the PPG evaluation.
