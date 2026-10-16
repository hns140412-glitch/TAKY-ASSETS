from pathlib import Path
import json, base64, hashlib, sys, time
from openai import OpenAI
TOOLS=Path(r"D:\Git PWA\TAKY-ASSETS\tools")
sys.path.insert(0,str(TOOLS))
from openai_env import ensure_openai_api_key
ROOT=Path(r"D:\Git PWA\TAKY-ASSETS\badges\work\20261001\batch_001_005")
if (ROOT/"GENERATION_LOCKED.txt").exists(): raise SystemExit("HARD_LOCK: explicit user API/CLI generation approval required")
packet=json.loads((ROOT/"generation_detail_packet.json").read_text(encoding="utf-8"))
if not ensure_openai_api_key(): raise SystemExit("OPENAI_API_KEY_MISSING")
client=OpenAI()
for item in packet["items"]:
    slot=item["slot"]
    prompt="\n".join([packet["global"],f"BADGE {slot} current display item: {item['display']}",f"Core detail: {item['core']}",f"Authority motif: {item['motif']}",f"Exact production scene: {item['scene']}","Generate only the badge artwork. Do not render the Korean display item or any other text."])
    print(f"GENERATING {slot} {item['display']}", flush=True)
    res=client.images.generate(model="gpt-image-2",prompt=prompt,size="1024x1024",quality="high",background="transparent",output_format="png",n=1)
    data=base64.b64decode(res.data[0].b64_json)
    png=ROOT/f"{slot}_candidate_composite.png"
    png.write_bytes(data)
    meta={"slot":slot,"display_item":item["display"],"core_detail":item["core"],"motif":item["motif"],"model":"gpt-image-2","size":"1024x1024","quality":"high","background":"transparent","sha256":hashlib.sha256(data).hexdigest(),"prompt":prompt,"status":"CANDIDATE_NOT_APPROVED"}
    (ROOT/f"{slot}_generation_meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"DONE {slot} sha256={meta['sha256']}", flush=True)
print("BATCH_GENERATION_COMPLETE_NO_RETRY", flush=True)
