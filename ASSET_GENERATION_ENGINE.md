# TAKY-ASSETS — Asset Generation Engine

Status: SCAFFOLD / 2026-09-30
Authority: TAKY `OS/CHARACTER_ASSET_BEHAVIOR_PIPELINE.md` + `MASTER/DESIGN_UI_ASSET_SOURCE_PROTOCOL.md`.

## 1. Boundary

`ASSET GENERATION ENGINE != CHARACTER BEHAVIOR ENGINE`.

This repository owns approved reusable visual binaries, derivatives, metadata and registries.
It does not decide live character behavior, relationship progression, dialogue, rewards or scene logic.

## 2. Sub-pipelines

- USER CHARACTER: photo intake derivative -> candidate -> Character Master -> derivatives -> registry
- GUIDE / COMPANION: approved Visual ID source -> derivative set -> registry
- BADGE: approved motif/source -> reusable layer set -> badge registry
- BACKGROUND: approved scene master -> layered/optimized derivatives -> registry
- UI ILLUSTRATION: approved UI visual -> reusable layers/variants -> registry

All outputs must preserve approved source identity and provenance.## 3. Canonical flow

`SOURCE -> PRESERVE/CHANGE/NEW DECISION -> GENERATE/EDIT -> VALIDATE -> SHA256 -> VERSION -> REGISTRY -> CONSUMER POINTER -> BUILD COPY`.

Production completion requires actual binary presence when a binary is expected.
Manifest-only entries do not count as finished assets.

## 4. Runtime rule

App runtimes consume approved registry entries or verified build copies.
A runtime asset gap must use an approved fallback or report a gap.
It must not silently create a new canonical visual.

## 5. Privacy / child source boundary

Raw child photos are private intake and are not stored in a public deployment path.
Only consented release-safe derivatives may be registered for app use.

## 6. Directory roles

- `characters/users/` — approved user Character Masters and derivatives
- `characters/guides/` — approved Guide/companion assets and derivatives
- `badges/` — badge masters, motifs and reusable layers
- `backgrounds/` — background masters and layered derivatives
- `ui/` — UI illustration assets
- `registry/` — canonical asset/character/badge registries
- `schemas/` — registry schemas and validation contracts

END