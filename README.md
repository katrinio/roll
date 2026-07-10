## `roll`

[//]: # (<div align="center">)
[//]: # (  <img src="docs/images/roll.png" width="310"/>)
[//]: # (</div>)

A small CLI for managing a film photography archive.

`roll` follows a roll of film from the moment it is loaded into a camera until it becomes part of the archive.

---

## Why

I don't shoot film often enough to remember everything months later.

`roll` helps answer questions like:

- Which films do I still have?
- What's currently loaded?
- Where is that roll I took with Kir?
- Which camera, film and lab was it?

The goal is to keep this information next to the archive instead of in my head.

---

## What it does

Use `roll` to:

- keep film stock in one place;
- record when a film was loaded and into which camera;
- mark a roll as processed or failed;
- add features and tags later, when the memory is still fresh;
- search the archive by film, camera, status, year, or a short text query;
- normalize archive metadata without moving the archive into a separate system.

It is a CLI for small, durable records around the archive, not for managing the photos themselves.

---

## Principles

`roll` doesn't try to replace your photo archive.

Your archive stays an ordinary folder. `roll` only keeps the information that would be difficult to reconstruct later.

Some principles behind the project:

- the archive belongs to the user;
- data lives inside the archive;
- everything is stored as plain text;
- removing the application never removes your data;
- the user only enters what cannot be detected automatically.

---

## Installation

`brew install katrinio/tap/roll`

Alternative install methods: `uv tool install git+https://github.com/katrinio/roll.git`, `pip install git+https://github.com/katrinio/roll.git`.

Tap details: [docs/homebrew.md](docs/homebrew.md).

---

## Main flow

| Status | Command | Description |
|--------|----------|-------------|
| — | `rl init` | Initialize an archive |
| `stock` | `rl stock add` | Add film to stock |
| `stock → loaded` | `rl load` | Load a film into a camera |
| `loaded → processed` | `rl stock process` | Mark the roll as finished |
| `loaded → failed` | `rl stock failed` | Mark the roll as failed |
| `processed` | `rl tags add` | Add keywords and features |
| `processed` | `rl search` | Search the archive |
| `processed` | `rl normalize` | Normalize folder names |

Typical use:

```bash
rl init ~/Pictures/plenka
rl stock add
rl load
rl stock process
rl search balcony
```

---

## Storage

```text
<archive>
├── .roll
│   ├── stock.toml
│   └── vocabulary/
│       ├── films.txt
│       ├── cameras.txt
│       ├── features.txt
│       └── keywords.txt
└── 2026/
    └── 05-12-e02775/
        └── roll.toml
```

- `stock.toml` — film stock
- `vocabulary/` — autocomplete dictionaries
- `roll.toml` — metadata for a single roll

Everything lives inside the archive. The application can be removed or reinstalled without affecting your data.

---

## Documentation

- `docs/index.md` — start here
- `docs/getting-started.md` — project scope and first flows
- `docs/architecture.md` — file map and command effects
- `docs/reference.md` — terminology and exact rules
- `docs/development.md` — setup and checks
