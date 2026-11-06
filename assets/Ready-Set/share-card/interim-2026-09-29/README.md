# Ready & Set / Native Share Card / Interim environment assets

Canonical asset owner: **TAKY-ASSETS**, not the Ready app's generated build folder.

Four environment states: `drop-pre`, `drop-result`, `sail-pre`, `sail-result`. Each has one full environment WebP preview and three environment layer PNGs (`sky`, `world`, `foreground`). A single `manifest.json` pins original package entry, byte length and SHA-256 for all 16 files.

**Current status:** manifest registered, binary import pending. Do not label it a complete GitHub asset upload until every binary path is present, hashes verified and import receipt committed on this review branch. Do not silently change/overwrite any existing asset version.

Asset source: the independently generated *interim* scenery package `TAKY_READY_SHARE_UI_20260929.zip`; this is not a cropped screenshot of a completed card. Profile character, existing selected companions, brand SVG, captions, assignment and award evidence are **separate runtime layers** and never authored as sample values into environment images.

Consumer: Ready & Set Draft PR #119. App or staging build must fetch/verify the pinned asset manifest and stage selected files into the app's runtime `assets/share-card/` folder. That build output is **not another canonical source**. Use tested Profile Visual ID & selected expedition companion assets; do not use images of sample children from the composite board.

Branch policy: no main merge / no Netlify deploy / no automatic release. Confirm real native iPhone → KakaoTalk image+text separately.

Import workflow: the one-run PowerShell helper shipped with the user attachment checks all 16 SHA-256s and pushes to this dedicated `assets/ready-share-interim-20260929` review branch only. Do not request a credential in chat; Git Credential Manager handles an authorized Git push when available.
