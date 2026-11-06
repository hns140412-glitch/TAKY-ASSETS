import importlib.util,unittest
from pathlib import Path
P=Path(__file__).with_name("specialist_handoff_accept.py")
s=importlib.util.spec_from_file_location("h",P);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
GOOD={"schema":"TAKY_SPECIALIST_TO_ASSET_REGISTRY_HANDOFF_V1","pipeline_owner":"P","pipeline_receipt_ref":"R","asset_id":"A","visual_id":"VID-A","approval_status":"APPROVED","binary_sha256":"a"*64,"runtime_url":"assets/a.png","handoff_sha256":"b"*64}
class T(unittest.TestCase):
 def test_accept(self):self.assertEqual([],h.validate(GOOD))
 def test_reject_state_leak(self):
  self.assertTrue(any("PRODUCTION_STATE_LEAK" in x for x in h.validate({**GOOD,"pipeline_state":"MASK"})))
 def test_reject_hold(self):
  self.assertIn("NOT_APPROVED",h.validate({**GOOD,"approval_status":"HOLD"}))
if __name__=="__main__":unittest.main()
