import importlib.util, json, tempfile, unittest
from pathlib import Path
P=Path(__file__).with_name("asset_composition_engine.py")
s=importlib.util.spec_from_file_location("ace",P); ace=importlib.util.module_from_spec(s); s.loader.exec_module(ace)

class T(unittest.TestCase):
  def reg(self,root):
    p=root/"assets"/"body.bin";p.parent.mkdir();p.write_bytes(b"body")
    q=root/"assets"/"neutral.bin";q.write_bytes(b"neutral")
    return {"schema":"TAKY_ASSET_COMPOSITION_REGISTRY_V1","characters":[{
      "character_id":"BELO","visual_id":"VID-08",
      "parts":[
        {"part_id":"belo-body","role":"BODY","path":"assets/body.bin","sha256":ace.sha256(p),"state":"APPROVED","actions":[]},
        {"part_id":"belo-neutral","role":"FACE","path":"assets/neutral.bin","sha256":ace.sha256(q),"state":"APPROVED","actions":["READ_BOOK"]}
      ],
      "fallback":{"character_id":"BELO","part_id":"belo-body"}
    }]}
  def test_registry_pass(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);self.assertEqual([],ace.validate_registry(self.reg(r),r))
  def test_resolve_approved(self):
    with tempfile.TemporaryDirectory() as td:
      reg=self.reg(Path(td));out=ace.resolve(reg,{"character_id":"BELO","action":"READ_BOOK","required_roles":["BODY","FACE"]})
      self.assertTrue(out["pass"]);self.assertFalse(out["fallback_used"])
  def test_missing_uses_same_character_fallback(self):
    with tempfile.TemporaryDirectory() as td:
      reg=self.reg(Path(td));out=ace.resolve(reg,{"character_id":"BELO","action":"USE_RADIO","required_roles":["EQUIPMENT"]})
      self.assertTrue(out["pass"]);self.assertTrue(out["fallback_used"]);self.assertFalse(out["generation_allowed"])
  def test_cross_character_fallback_forbidden(self):
    with tempfile.TemporaryDirectory() as td:
      r=Path(td);reg=self.reg(r);reg["characters"][0]["fallback"]={"character_id":"OTHER","part_id":"belo-body"}
      self.assertIn("BELO:CROSS_CHARACTER_FALLBACK_FORBIDDEN",ace.validate_registry(reg,r))
if __name__=="__main__":unittest.main()
