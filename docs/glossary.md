# Glossary

Project concepts. File structure, code layout, and the full command list — see [model.md](model.md).

---

## Archive

A folder with a film archive: years of rolls + `.roll/` (workspace). `roll` doesn't store archive data in code — it only knows where the archive is.

---

## Workspace

`.roll/` inside the archive: config, [[Stock]], and vocabularies. Should stay portable together with the archive.

---

## Stock

Film that hasn't been loaded into a camera yet. Stored in `stock.toml`, separate from `roll.toml`: while a film is in stock, it isn't a [[Roll]] yet and doesn't take up a folder in the archive. `rl load` decreases stock by one; `rl load --manual` creates a roll bypassing stock.

---

## Roll

One exposed roll of film. Fields and their requirements — see [model.md](model.md#roll). `features`/`keywords` always start empty and get filled in later by separate commands.

---

## Status

`loaded → processed | failed`. The transition is manual and one-way, never back. See [model.md](model.md#roll-lifecycle).

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

Brings folder names to a consistent shape: builds a plan → asks for confirmation, doesn't touch `roll.toml`. With `--tags` — brings `keywords` to uppercase in both `roll.toml` and the vocabulary.

---

## Doctor

Integrity check: global config, archives, `.roll/` and vocabularies, whether `roll.toml` files are readable, mismatches with vocabularies, suspicious and unindexed folders. `--fix` only applies safe renames, `-v` shows the full list of fixes.

---

## Principle

The user only enters what can't be figured out automatically. Everything else comes from the filesystem or is computed.

## Language

UI language stored in the global config. Use `rl config lang` to inspect it and `rl config lang EN` / `rl config lang RU` to change it.

Code, tests, and CI — see [docs/development.md](development.md).
