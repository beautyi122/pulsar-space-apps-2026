import hashlib, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class ManifestTests(unittest.TestCase):
    def test_all_declared_files_and_hashes(self):
        manifest=json.loads((ROOT/'Release Manifest.json').read_text(encoding='utf-8'))
        for item in manifest['files']:
            p=ROOT/item['path']
            self.assertTrue(p.is_file(),item['path'])
            data=p.read_bytes()
            self.assertEqual(len(data),item['size_bytes'],item['path'])
            self.assertEqual(hashlib.sha256(data).hexdigest(),item['sha256'],item['path'])
    def test_manifest_does_not_claim_independent_validation(self):
        manifest=json.loads((ROOT/'Release Manifest.json').read_text(encoding='utf-8'))
        self.assertFalse(manifest['independent_external_validation'])
        self.assertEqual(manifest['participants_in_development'],8)
if __name__=='__main__':unittest.main()
