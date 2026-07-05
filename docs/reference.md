# Reference

Project concepts and exact rules. File structure, command effects, and flows — see [docs/architecture.md](architecture.md).

---

## Archive

A folder with a film archive: years of rolls plus `.roll/` (workspace). `roll` does not store archive data in code — it only knows where the archive is.

---

## Workspace

`.roll/` inside the archive: workspace config, [[Stock]], and vocabularies. It should stay portable together with the archive.

---

## Stock

Film that has not been loaded into a camera yet. Stored in `stock.toml`, separate from `roll.toml`: while a film is in stock, it is not a [[Roll]] yet and does not take up a folder in the archive.

---

## Roll

One exposed roll of film. Fields and their requirements — see [docs/architecture.md](architecture.md#lifecycle). `features` and `keywords` start empty and are filled in later.

---

## Status

`loaded → processed | failed`. The transition is manual and one-way, never back. See [docs/architecture.md](architecture.md#lifecycle).

---

## Camera

The camera a film was loaded into.

---

## Film

The film stock type. Lives in the `vocabulary/films.txt` dictionary — used for autocomplete, grows with new values after confirmation.

Examples:
- Kodak Gold 200
- Kodak ColorPlus 200
- Ilford HP5 Plus
- Fujifilm 400

---

## Features

Short, reusable characteristics of a shoot that narrow down a search. Entered comma-separated (`rl features add`), autocomplete per value, duplicates aren't written, `_` is allowed inside a value.

Examples: `redscale`, `push +1`, `push +2`, `expired`.

---

## Keywords

Called "tags" in the CLI. Keywords for finding a roll from memory: short, no long descriptions, written the way you'd later search for them. Entered comma-separated (`rl tags add`), stored in uppercase.

Examples: `pizza`, `balcony`, `evening`, `belgrade`.

---

## Loaded at

The date a film was loaded into the camera.

This is the base date that the folder name and part of normalization are built from.

---

## Normalize

Brings folder names to a consistent shape: builds a plan, asks for confirmation, and does not touch `roll.toml`. With `--tags` it brings `keywords` to uppercase in both `roll.toml` and the vocabulary.

---

## Doctor

Integrity check: global config, workspaces, stock, roll metadata, vocabularies, suspicious and unindexed folders. Diagnostics stay in English. `--fix` applies safe fixes and prints them in a separate block; `-v` shows the full list of fixes.

---

## Principle

The user only enters what can't be figured out automatically. Everything else comes from the filesystem or is computed.

## Language

UI language stored in the global config. Use `rl config lang` to inspect it and `rl config lang EN` / `rl config lang RU` to change it. Missing or invalid values fall back to `EN`.

Code, tests, and CI — see [docs/development.md](development.md).
