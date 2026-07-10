# Architecture

This is a file-first tool. The main question is always: which files are read, which are written, and what can be fixed automatically.

## File Map

| Layer | Path | Purpose |
|---|---|---|
| Global config | `~/.config/roll/config.toml` | archive list, UI language |
| Workspace | `<archive>/.roll/` | workspace config, stock, vocabularies |
| Roll | `<archive>/YYYY/MM-DD/roll.toml` | one film roll |

```
~/.config/roll/config.toml
        │
        ▼
~/Pictures/plenka/
├── .roll/
│   ├── config.toml
│   ├── stock.toml
│   └── vocabulary/
│       ├── films.txt
│       ├── cameras.txt
│       ├── features.txt
│       └── keywords.txt
└── 2026/
    └── 07-03/
        └── roll.toml
```

`config.toml` is the only root config file. `lang` defaults to `EN` when missing or invalid.

```toml
lang = "EN"
archives = ["/path/to/archive"]
```

`stock.toml` tracks unused film. `vocabulary/*.txt` tracks canonical autocomplete values. They solve different problems and are intentionally separate.

## Command Effects

| Command | Reads | Writes | Auto-fix | Scope |
|---|---|---|---|---|
| `rl --version` | package metadata, git tag | no | no | meta |
| `rl init` | filesystem | global config, workspace | no | setup |
| `rl config` | global config | no | no | config |
| `rl config lang` | global config | global config | yes, with `rl doctor --fix` | config |
| `rl update` | no | no | no | meta |
| `rl stock add` | global config, workspace, vocabulary, stock | stock | no | workspace |
| `rl load` | global config, stock, vocabulary | stock, roll | no | roll creation |
| `rl load --manual` | global config, vocabulary | roll | no | roll creation |
| `rl stock process` / `rl stock failed` | global config, workspace, roll | roll | no | roll status |
| `rl batch process` | global config, workspace, roll | roll | no | roll status |
| `rl features add` / `rl tags add` | global config, workspace, vocabulary, roll | roll, vocabulary | no | roll editing |
| `rl search` / `rl scan` / `rl status` / `rl stats` / `rl vocab` | global config, workspace, roll, vocabulary | no | no | read-only |
| `rl doctor` | global config, workspace, stock, roll, vocabulary | no | yes with `--fix` | integrity |
| `rl normalize` | current archive workspace, roll, vocabulary | roll, vocabulary | yes | normalization |
| `rl normalize --photos` | photo folders in current archive workspace | archive folders | yes | photo import |
| `rl batch` | global config, workspace, roll | roll | no | batch update |

These scopes are deliberate:

- `rl tags add` and `rl features add` update one roll at a time;
- `rl batch` is the bulk editor;
- `rl search` shares the same filter language as `rl batch`, but never writes;
- `rl normalize` is for structural cleanup and normalization;
- `rl doctor` is for diagnostics and safe repair.

## Lifecycle

```
[ stock ]  --rl stock add-->  stock.toml
              │
           rl load
              ▼
[ loaded ]   roll.toml created
              │
       ┌──────┴──────┐
  rl stock       rl stock
  process          failed
       ▼              ▼
[ processed ]    [ failed ]
```

The transition is manual and one-way: a roll never goes back to `loaded`.

## Scenarios

### First setup

```bash
rl init ~/Pictures/plenka
rl config lang EN
```

### Film workflow

```bash
rl stock add
rl load
rl stock process
```

### Later lookup

```bash
rl search kir balcony
rl status
rl stats --verbose
```

### Integrity pass

```bash
rl doctor
rl doctor --fix
```

## Code Layout

| Path | Area |
|---|---|
| `filesystem.py` | archive tree and file discovery |
| `app/workspace/` | config, stock, roll storage, vocabularies |
| `app/flows/` | interactive flows |
| `app/archive/` | search, stats, batch, selection, normalization |
| `app/diagnostics/` | doctor |
| `messages/` | localized user-facing text |

## Principles

- the archive is self-contained;
- user edits only what the filesystem cannot infer;
- normalization and doctor fixes build a plan before changing anything;
- `doctor` reports issues first and lists safe fixes in a separate block;
- vocabularies stay plain text and grow automatically;
- dev-facing diagnostics stay in English; only user-facing UI is localized;
- English is the default UI language.

Quick start — see [docs/getting-started.md](getting-started.md). Environment setup and CI — see [docs/development.md](development.md). Terms and exact command behavior — see [docs/reference.md](reference.md).
Editing flows — see [docs/editing.md](editing.md).
