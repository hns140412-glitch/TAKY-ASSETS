import importlib.util, tempfile, unittest
from pathlib import Path
P=Path(__file__).with_name("approved_asset_registry.py")
s=importlib.util.spec_from_file_location("aar",P); aar=importlib.util.module_from_spec(s); s.loader.exec_module(aar)

class T(unittest.TestCase):
  def base(self,root):
    p=root/"approved"/"x.bin";p.parent.mkdir();p.write_bytes(b"approved")
    return {
      "schema":"TAKY_APPROVED_ASSET_REGISTRY_V1",
      "asset_id":"A",
      "classification":"APPROVED_ORIGINAL",
      "visual_id":"VID-01",
      "source":{"path":"approved/x.bin","sha256":aar.sha256(p)},
      "approval":{"status":"APPROVED","authority_ref":"USER_APPROVAL_REF"},
      "producer_pointer":{"pipeline_owner":"GUIDE_CHARACTER_PIPELINE","evidence_ref":"PIPELINE_RECEIPT_001"},
      "consumers":[{"repo":"Ready-Set","runtime_key":"guide.VID-01","pointer_status":"REGISTERED"}]
    }
  def test_approved_result_passes(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);self.assertEqual([],aar.validate(self.base(r),r))
  def test_production_state_forbidden(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);m=self.base(r);m["pipeline_state"]="CUTOUT_OPEN"
      self.assertTrue(any("PRODUCTION_STATE_OWNERSHIP_VIOLATION" in x for x in aar.validate(m,r)))
  def test_registry_cannot_be_producer(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);m=self.base(r);m["producer"]="TAKY-ASSETS"
      self.assertIn("REGISTRY_CANNOT_BE_PRODUCER",aar.validate(m,r))
  def test_tamper_fails(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);m=self.base(r);(r/"approved/x.bin").write_bytes(b"tampered")
      self.assertIn("SOURCE_SHA_MISMATCH",aar.validate(m,r))
if __name__=="__main__":unittest.main()
