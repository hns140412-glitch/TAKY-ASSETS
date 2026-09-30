# TAKY-ASSETS

Canonical repository for **approved asset results and pointers only**.

Ownership boundary:

`SPECIALIST PRODUCTION PIPELINE -> APPROVAL -> TAKY-ASSETS REGISTRY -> APP RUNTIME POINTER`

TAKY-ASSETS does **not** own:
- generation / cutout / mask / pose / art-batch production state
- retry state or production queues
- artistic QA work state
- behavior or composition decisions

TAKY-ASSETS owns:
- approved binary/result
- immutable SHA-256
- Visual ID / logical asset ID
- approval provenance
- pointer back to the specialist pipeline evidence
- consumer/runtime pointers

Validator:
`python tools/approved_asset_registry.py <manifest.json> --root .`

A manifest containing specialist production state fails closed.
