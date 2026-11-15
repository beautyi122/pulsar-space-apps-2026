"""Regression tests for Pulsar competition-release evidence and sensor-only input path."""
import copy,hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research'))
from Reliability import prepare_rows,FEATURE_NAMES,_summarize
from AnalyzeCSV import analyze_text,parse_csv,features_for_sample

class ReleaseTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.pilot=json.loads((ROOT/'input'/'Phase 34 Sensor Pilot.json').read_text())
    cls.probe=json.loads((ROOT/'input'/'Phase 32 Raw Signal Probe.json').read_text())
    cls.study=json.loads((ROOT/'results'/'Reliability Evidence.json').read_text())
    cls.app=(ROOT/'app/index.html').read_text()
    cls.sample=(ROOT/'app/Synthetic PPG.csv').read_text()

  def test_source_checks_match_original_uploads(self):
    h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    self.assertEqual(self.study['source_sha256']['pilot'],h(ROOT/'input'/'Phase 34 Sensor Pilot.json'))
    self.assertEqual(self.study['source_sha256']['phase32_probe'],h(ROOT/'input'/'Phase 32 Raw Signal Probe.json'))
    self.assertEqual(self.study['source_sha256']['phase31_evidence'],h(ROOT/'input'/'Phase 31 Evidence.zip'))
    self.assertFalse(self.pilot['reference_accessed_during_sensor_pilot'])

  def test_all_windows_present_no_duplicate_and_correct_outcomes(self):
    rows=self.study['records'];self.assertEqual(len(rows),332)
    self.assertEqual(len({(r['record'],r['window']) for r in rows}),332)
    self.assertEqual(len({r['subject'] for r in rows}),8)
    self.assertEqual(len({r['record'] for r in rows}),19)
    self.assertEqual(sum(r['decision']=='DISPLAY_WITH_CAUTION' for r in rows),125)
    self.assertEqual(sum(r['decision']=='REVIEW_SIGNAL' for r in rows),204)
    self.assertEqual(sum(r['decision']=='NO_SENSOR_CANDIDATE' for r in rows),3)
    self.assertEqual(_summarize(rows),self.study['overall'])
    self.assertEqual(self.study['overall']['serious_errors_ge15'],8)
    self.assertEqual(self.study['by_activity']['run']['displayed'],2)

  def test_sensor_features_invariant_to_added_ecg_fields(self):
    original=prepare_rows(self.pilot,self.probe)
    pilot=copy.deepcopy(self.pilot)
    probe=copy.deepcopy(self.probe)
    for r in pilot['records']:r['ecg_reference_bpm']=-2222.0
    for r in probe['records']:
      r['ecg_reference_bpm']=-2222.0
      for w in r['windows']:w['ecg_reference_bpm']=-2222.0
    modified=prepare_rows(pilot,probe)
    self.assertEqual([r['features'] for r in original],[r['features'] for r in modified])
    self.assertTrue(all(len(r['features'])==len(FEATURE_NAMES) for r in original))
    self.assertTrue(all('ecg' not in n.lower() for n in FEATURE_NAMES))

  def test_synthetic_sensor_recovery(self):
    out=analyze_text(self.sample,'walk')
    self.assertTrue(out['status'].endswith('NOT_VALIDATED'))
    self.assertAlmostEqual(out['raw_candidate_bpm'],173.91,places=2)
    self.assertAlmostEqual(out['motion_separated_candidate_bpm'],98.91,places=2)
    self.assertLess(abs(out['motion_separated_candidate_bpm']-99),2)
    self.assertEqual(out['research_tier'],'LOWER_RISK_RESEARCH_TIER')

  def test_reject_malformed_and_missing_samples(self):
    with self.assertRaisesRegex(ValueError,'columns|Columns'):
      parse_csv('hello,world\n1,2\n')
    with self.assertRaisesRegex(ValueError,'5,120'):
      parse_csv(self.sample.split('\n',maxsplit=2)[0]+'\n'+self.sample.split('\n',maxsplit=2)[1]+'\n')
    with self.assertRaisesRegex(ValueError,'activity'):
      analyze_text(self.sample,'spacewalk')

  def test_nasa_sources_and_safety_bounds(self):
    self.assertIn('NASA OCHMO',self.app)
    self.assertIn('PhysioNet',self.app)
    self.assertIn('not a medical',self.app.lower())
    self.assertFalse(self.study['gate4_met'])
    self.assertTrue(self.study['original_phase31_data_reused_not_independent'])
    self.assertTrue('independent' in ' '.join(self.study['limitations']).lower())
    self.assertEqual(self.study['by_activity']['high_resistance_bike']['serious_errors_ge15'],0)
    self.assertEqual(self.study['by_activity']['walk']['serious_errors_ge15'],6)

if __name__=='__main__':unittest.main()
