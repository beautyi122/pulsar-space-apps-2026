# Pulsar — competition final readiness and hard stops

## Completed in this package

- [x] Local/offline sensor input no longer uses `/api/analyze` on GitHub Pages. Browser FFT and blocked motion-regression function tested on synthetic 20s, 256 Hz signal.
- [x] Scientific reference Python source and its result files supplied in readable repository paths.
- [x] Retrospective development metrics, failed activities, varying denominators, source hashes and limitations documented.
- [x] NASA challenge-listed Human Research Program hazards, risks, and ongoing studies explicitly mapped to an actual mission interface and engineering workflow.
- [x] NASA technical exercise data and PhysioNet source differentiated.
- [x] Native 7-slide PDF + editable PPTX demonstration prepared.
- [x] Local JavaScript unit tests, original Python tests and static DOM tests passed.

## Not yet independently verified

- [ ] The updated website is live and fully functioning on GitHub Pages. Existing live site is the **old** version until you upload these files.
- [ ] Real Chrome/Safari/mobile visual and click-through tests. Automated browser navigation was blocked in the build environment. Perform real-device checks; see below.
- [ ] NASA submission platform links accessible in private/incognito browsing.
- [ ] Final official acceptance, eligibility and awards. Judges decide.

## Required entrant actions (critical)

1. **Upload expanded `Pulsar GitHub Upload.zip` contents to the repository root** (preserve `science/`, `demo/`, `tests/`; do NOT upload only the ZIP). GitHub tool write operations returned a 403 permission error; nothing was automatically pushed.
2. **Check published site** in an incognito/private window and on a phone. Switch all tabs, select another recording, scrub slider, generate check-in, switch CEVIS/T2 NASA mode, download `Synthetic PPG.csv`, upload it back and confirm the browser report shows **173.91 and 98.91 cycles/min** with **WITHHELD**.
3. **Publish demonstration link** by uploading `demo/Pulsar Demo.pdf` with website files, verify the link opens, and paste the public link into the NASA project form.
4. **Confirm global-judging eligibility** on the official team dashboard. If participating in the Universal Event, NASA's 2026 organizers say at least **2 registered participants** are required for Global Judging (Local Events follow other rules).
5. **Accurately document all pre-hackathon work.** NASA's 2026 organizer guidance says beginning project work before Nov 14 may risk disqualification. The entrant must distinguish earlier reused work from actual Nov 14–15 competition work. Do not fabricate start dates.
6. **Write your own required AI-use disclosure.** Submit where NASA requests it and in any required project metadata. NASA organizers say AI-generated images/videos require clear visible marking and AI-assisted code/data require descriptions and metadata. We have not inserted an AI-use disclosure into the project documents on your behalf.
7. **Confirm source/IP licensing.** MIT applies to code written for Pulsar where contributors have the right to grant it; PhysioNet source data remain under ODC-By 1.0 and NASA materials retain their own rights. Check any third-party components before uploading.
8. **Complete official NASA Space Apps project form and submit by 11:59 PM local on November 15**. Submission is not complete merely because GitHub Pages is live.
9. **Stylistic changes requested by the entrant remain to be specified and applied**; this package preserves the existing visual palette while adding functional and science-context upgrades.

## Name collision

Another 2026 team in the same astronaut health challenge publicly uses the product name **Pulsar** (team Quantum Astronauts). This project remains **Pulsar by Stella Nova** pending the entrant's naming decision. Do not present the duplicate name as an exclusive trademark or evidence of copied code.

## Demonstration instruction

The 7-slide PDF is the intended official short demonstration (maximum 7 slides). Use it instead of needing a 30-second video. Make sure the PDF URL is public and the final slides reflect the published website. The editable PowerPoint is provided for final visual adjustments and required entrant-authored notices.
