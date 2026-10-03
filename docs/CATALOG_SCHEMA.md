# Catalog schema

The catalog is a normalized lookup layer over private development-reference material.

## Core provenance chain

`appearanceId → appearanceClass → frameGroup → pattern → spriteId → sourceSheet → source file`

Catalog records must distinguish verified source facts from inferred/candidate semantic roles.

## Primary indexes

- appearances
- sprites / sprite sheets
- creatures
- outfits
- items / objects
- tiles / map objects
- effects
- missiles
- HUD/reference images
- minimap/map sectors

## Rules

1. Preserve source identifiers; filenames alone are never canonical identity.
2. Record source gaps instead of silently guessing.
3. Keep gameplay semantics separate from visual/reference metadata.
4. Catalog data must never make browser/client assets authoritative for simulation.
5. Raw/reference material remains isolated from the production build/release graph.
