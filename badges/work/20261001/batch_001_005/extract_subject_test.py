from pathlib import Path
import cv2, numpy as np
from PIL import Image
ROOT=Path(r"D:\Git PWA\TAKY-ASSETS\badges\work\20261001\batch_001_005")
rects={
"001":(470,430,400,430),
"002":(120,130,780,760),
"003":(250,170,500,680),
"004":(140,140,740,720),
"005":(130,120,780,760),
}
for s,rect in rects.items():
    p=ROOT/f"{s}_candidate_composite.png"
    rgba=np.array(Image.open(p).convert("RGBA"))
    bgr=cv2.cvtColor(rgba[:,:,:3],cv2.COLOR_RGB2BGR)
    # composite transparent exterior to near-white for segmentation
    a=rgba[:,:,3]/255.0
    white=np.full_like(bgr,245)
    comp=(bgr*a[...,None]+white*(1-a[...,None])).astype(np.uint8)
    mask=np.zeros(comp.shape[:2],np.uint8)
    bgd=np.zeros((1,65),np.float64); fgd=np.zeros((1,65),np.float64)
    cv2.grabCut(comp,mask,rect,bgd,fgd,7,cv2.GC_INIT_WITH_RECT)
    fg=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    # remove anything outside original alpha and tiny islands
    fg=np.minimum(fg,rgba[:,:,3])
    n,labels,stats,_=cv2.connectedComponentsWithStats((fg>0).astype(np.uint8),8)
    keep=np.zeros_like(fg)
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA] >= 30:
            keep[labels==i]=255
    # soften 1px
    keep=cv2.GaussianBlur(keep,(3,3),0)
    out=rgba.copy(); out[:,:,3]=(keep.astype(np.float32)*(rgba[:,:,3]/255.0)).astype(np.uint8)
    Image.fromarray(out).save(ROOT/f"{s}_subject_test.png")
    print(s,"subject_pixels",int((keep>8).sum()))
