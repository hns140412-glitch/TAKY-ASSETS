# TAKY-ASSETS — Asset Generation Engine

Status: SCAFFOLD / 2026-09-30
Authority: TAKY `OS/CHARACTER_ASSET_BEHAVIOR_PIPELINE.md` + `MASTER/DESIGN_UI_ASSET_SOURCE_PROTOCOL.md`.

## 1. Boundary

`ASSET GENERATION ENGINE != CHARACTER BEHAVIOR ENGINE`.

This repository owns approved reusable visual binaries, release-safe derivatives, metadata and shared registries.
It does not decide live character behavior, relationship progression, dialogue, rewards or scene logic.

## 2. Scope / ownership

This shared engine owns:
- USER CHARACTER pipeline: private photo intake -> candidate -> Character Master -> release-safe derivatives -> registry.
- BADGE asset pipeline.
- BACKGROUND asset pipeline.
- UI ILLUSTRATION asset pipeline.
- Shared registration of approved outputs from specialist pipelines.

GUIDE / COMPANION production is NOT owned here.
GUIDE Visual ID source locking, cutout/mask generation, per-ID art production and artistic QA stay with the existing GUIDE specialist pipeline.
TAKY-ASSETS stores only stable source pointers and later approved output pointers/SHA/version received from that owner.

`SHARED REGISTRY != SPECIALIST PRODUCTION STATE MACHINE`.

## 3. Canonical shared flow

For pipelines owned here:
`SOURCE -> PRESERVE/CHANGE/NEW DECISION -> GENERATE/EDIT -> VALIDATE -> SHA256 -> VERSION -> REGISTRY -> CONSUMER POINTER -> BUILD COPY`.

For external specialist pipelines:
`SPECIALIST OWNER -> APPROVED OUTPUT -> SHA/VERSION -> SHARED REGISTRY POINTER -> CONSUMER`.

Production completion requires actual approved binaries when binaries are expected.
Manifest-only entries do not count as finished assets.

## 4. Runtime rule

App runtimes consume approved registry entries or verified build copies.
A runtime asset gap must use an approved fallback or report a gap.
It must not silently create a new canonical visual.

## 5. Privacy / child source boundary

Raw child photos are private intake and are not stored in a public deployment path.
Only consented release-safe derivatives may be registered for app use.

## 6. Directory roles

- `characters/users/` — approved user Character Masters and release-safe derivatives
- `characters/guides/` — approved GUIDE runtime outputs received from GUIDE specialist owner; no duplicate production state machine
- `badges/` — badge masters, motifs and reusable layers
- `backgrounds/` — background masters and layered derivatives
- `ui/` — UI illustration assets
- `registry/` — shared approved asset/character/badge pointers
- `schemas/` — registry schemas and validation contracts

END
