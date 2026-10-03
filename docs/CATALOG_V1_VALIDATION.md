# Catalog v1 validation — 2026-10-03

Source package SHA-256: `f5ceaaae4736b389ca885b6f1fb832a2dbe2ec857d9ba5f32ed8a65933934bc1`

The Director parsed the supplied source package and validated the first catalog pass:

- 39,221 object appearances;
- 1,375 outfit appearances;
- 179 effects;
- 60 missiles;
- 8,482 appearances expose a source name;
- 5,334 sprite sheets/ranges;
- 295,960 appearance sprite references;
- **0 unresolved sprite → source-sheet references**;
- 2,116 minimap PNG sectors parsed from source coordinates;
- Z range 0–15.

A local searchable catalog build was also produced with JSON indexes and SQLite tables for appearances, frame groups, sprite references/sheets and minimap sectors. The canonical generator is `tools/build_catalog.py`; generated outputs will be committed by the Builder together with raw ingestion so their provenance is reproducible from repository source.
