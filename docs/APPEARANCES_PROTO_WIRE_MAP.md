# Appearances catalog wire map

The supplied `appearances-*.dat` is a Protocol Buffers wire-format payload. The catalog tooling parses only fields observed in the supplied source and preserves unknown fields.

## Top-level repeated messages

| field | class | observed count |
|---|---|---:|
| 1 | object | 39,221 |
| 2 | outfit | 1,375 |
| 3 | effect | 179 |
| 4 | missile | 60 |

Field 5 is present once and is preserved as unknown metadata.

## Appearance message

Observed useful fields:

- field 1: numeric appearance id;
- field 2: repeated frame-group message;
- field 3: flags/properties payload;
- field 4: UTF-8 display/source name when present.

## Frame-group message

Observed fields:

- field 1: source frame-group category;
- field 2: source frame-group id;
- field 3: sprite-info payload.

## Sprite-info payload

Observed fields include pattern width, height, depth, layers, repeated sprite ids, animation metadata, bounding square and bounding-box records. The parser does not convert unknown fields into gameplay truth.

The catalog joins every observed sprite id against `catalog-content.json` sprite ranges to resolve the source sprite-sheet filename, sheet type, first sprite id, last sprite id and area.

This is a reference/provenance catalog only. No value extracted here becomes authoritative collision, combat, movement, loot or other gameplay data without an explicit verified mapping.
