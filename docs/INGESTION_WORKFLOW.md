# Ingestion workflow

## Public-safe stage

While this repository is public, commit only tooling, schemas and source-agnostic metadata examples. Do **not** publish raw client-derived binaries or detailed extracted client catalogs.

## Private stage

After the repository is private:

1. extract the approved source package outside the production repository;
2. place raw binary reference material under `raw/` using Git LFS;
3. run `python tools/build_catalog.py <extracted-root>`;
4. validate hashes/counts and exclude local Character data from semantic cataloging;
5. extend semantic indexes from verified source manifests only;
6. record gaps/candidates explicitly instead of guessing gameplay roles;
7. keep `Hokz/Global-Idle` release-isolation rules unchanged.

## Separation rule

This repository is a development/reference source. It is never imported by production code or copied into the distributable web build.
