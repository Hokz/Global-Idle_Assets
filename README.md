# Global Idle — Asset Reference

Development-reference repository for Global Idle source assets, catalogs, manifests and map/HUD references.

> PRIVATE DEVELOPMENT REFERENCE — NOT FOR DISTRIBUTION

This repository is intentionally separate from `Hokz/Global-Idle`. It must never become a production/release input for the game.

## Intended structure

- `catalog/` — normalized, searchable semantic catalogs.
- `indexes/` — machine-readable lookup indexes.
- `manifests/` — source-package hashes, provenance and ingestion metadata.
- `docs/` — catalog schema and ingestion notes.
- `raw/` — reserved for approved binary/LFS source-reference material.

Raw client-derived material must not be copied into the distributable Global Idle repository.
