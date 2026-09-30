# TAKY-ASSETS

Canonical production asset repository.

## Asset Pipeline V1
Approved assets are not considered registered by filename alone.

Required chain:
`APPROVAL -> SOURCE BINARY -> SHA-256 -> VISUAL ID -> LAYERS/DERIVATIVES -> CONSUMER BINDING -> RUNTIME VERIFICATION`

Validator:
`python tools/asset_pipeline.py validate <manifest.json> --root .`

Intake refuses to invent approval or Visual IDs; the caller must provide the real authority reference.
Golden references are classified separately from runtime assets and must never be used as runtime backgrounds merely because they exist here.
