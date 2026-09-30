import importlib.util, json, tempfile, unittest
from pathlib import Path
P=Path(__file__).with_name("asset_pipeline.py")
s=importlib.util.spec_from_file_location("ap",P); ap=importlib.util.module_from_spec(s); s.loader.exec_module(ap)
class T(unittest.TestCase):
  def base(self,root):
    p=root/"assets"/"x.bin";p.parent.mkdir();p.write_bytes(b"approved")
    return {"schema":"TAKY_ASSET_PIPELINE_V1","asset_id":"A","visual_id":"VID-01","classification":"APPROVED_ORIGINAL",
      "source":{"path":"assets/x.bin","sha256":ap.sha256(p)},"approval":{"authority_ref":"USER_APPROVED","status":"APPROVED"},
      "layers":[],"consumers":[{"repo":"Ready-Set","runtime_key":"hero","status":"VERIFIED"}],
      "integrity_verified":True,"runtime_ready":True}
  def test_pass(self):
    with tempfile.TemporaryDirectory() as td:self.assertEqual([],ap.validate_manifest(self.base(Path(td)),Path(td)))
  def test_tamper_fails(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);m=self.base(r);(r/"assets/x.bin").write_bytes(b"tampered")
      self.assertIn("SOURCE_SHA_MISMATCH",ap.validate_manifest(m,r))
  def test_no_visual_id_fails(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);m=self.base(r);m["visual_id"]=""
      self.assertIn("VISUAL_ID_MISSING",ap.validate_manifest(m,r))
  def test_runtime_requires_verified_consumer(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);m=self.base(r);m["consumers"][0]["status"]="BOUND"
      self.assertIn("RUNTIME_READY_WITH_UNVERIFIED_CONSUMER",ap.validate_manifest(m,r))
if __name__=="__main__":unittest.main()
