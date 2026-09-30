import importlib.util,unittest
from pathlib import Path
P=Path(__file__).with_name("approved_asset_export.py")
s=importlib.util.spec_from_file_location("e",P);e=importlib.util.module_from_spec(s);s.loader.exec_module(e)
class T(unittest.TestCase):
  def test_only_approved_exported(self):
    rows=[
      {"asset_pointer":"P1","asset_id":"A","visual_id":"VID-A","approval_status":"APPROVED","sha256":"a"*64,"runtime_url":"assets/a.png","producer_pointer":"PIPE:1"},
      {"asset_pointer":"P2","asset_id":"B","visual_id":"VID-B","approval_status":"HOLD","sha256":"b"*64,"runtime_url":"assets/b.png","producer_pointer":"PIPE:2"}
    ]
    x=e.export(rows);self.assertTrue(x["pass"]);self.assertEqual(["P1"],[a["asset_pointer"] for a in x["assets"]])
  def test_production_state_is_not_exported(self):
    row={"asset_pointer":"P1","asset_id":"A","visual_id":"VID-A","approval_status":"APPROVED","sha256":"a"*64,"runtime_url":"assets/a.png","producer_pointer":"PIPE:1","pipeline_state":"MASK_OPEN"}
    x=e.export([row]);self.assertNotIn("pipeline_state",x["assets"][0])
  def test_duplicate_fails(self):
    row={"asset_pointer":"P1","asset_id":"A","visual_id":"VID-A","approval_status":"APPROVED","sha256":"a"*64,"runtime_url":"assets/a.png","producer_pointer":"PIPE:1"}
    x=e.export([row,row]);self.assertFalse(x["pass"]);self.assertTrue(any("POINTER_DUPLICATE" in z for z in x["detected"]))
if __name__=="__main__":unittest.main()
