# Model

The project has three levels: global config → archive workspace → roll.

```
~/.config/roll/config.toml         1. global config — list of archives
        │
        ▼
~/Pictures/plenka/                  archive
├── .roll/                         2. workspace
│   ├── config.toml
│   ├── stock.toml                    film stock, separate from roll.toml
│   └── vocabulary/
│       ├── films.txt
│       ├── cameras.txt
│       ├── features.txt
│       └── keywords.txt
└── 2026/
    └── 07-03/                     3. roll
        └── roll.toml
```

| Level | Where | Knows about |
|---|---|---|
| Global config | `~/.config/roll/config.toml` | list of archives |
| Workspace | `<archive>/.roll/` | config, stock, vocabularies |
| Roll | `<archive>/YYYY/MM-DD/roll.toml` | one film roll |

`stock.toml` and `vocabulary/*.txt` solve different problems: stock tracks what you physically have on hand, vocabularies hold canonical values for autocomplete.

## Code layout

| Path | Area |
|---|---|
| `filesystem.py` | low-level operations on the archive's file structure |
| `app/workspace/` | workspace, vocabularies, stock/roll storage |
| `app/flows/` | interactive scenarios (`stock.py`: load/process/failed) |
| `app/archive/` | search, stats, batch, normalization + rendering |
| `app/diagnostics/` | doctor |
| `messages/` | user-facing strings, grouped by area |

## Roll

`roll.toml`:

| Field | Required | Notes |
|---|---|---|
| `status` | yes | `loaded` \| `processed` \| `failed` |
| `film` | yes | |
| `camera` | yes | |
| `loaded_at` | yes | determines the roll's folder name |
| `features` | no | filled in via `rl features add` |
| `keywords` | no | filled in via `rl tags add` (called "tags" in the CLI) |

### Roll lifecycle

```
[ stock ]  --rl stock add-->  sits in stock.toml
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

## Commands

| Area | Command |
|---|---|
| Setup | `rl init` |
| Stock | `rl stock add`, `rl stock list` |
| Roll | `rl load` (`--manual` — without stock), `rl stock process`, `rl stock failed` |
| Fill in | `rl features add`, `rl tags add` |
| Find / view | `rl search`, `rl scan`, `rl status`, `rl stats [-v]`, `rl vocab` |
| Archive hygiene | `rl doctor [--fix] [-v]`, `rl normalize [--tags]` |
| Batch | `rl batch process` |

## Principles

- the archive is self-contained; the app can be removed without losing data;
- vocabularies are edited as plain text and grow automatically as you type;
- normalization (`rl normalize`, `rl doctor --fix`) always builds a plan before asking for confirmation;
- a roll starts as `loaded`, then ends as `processed`/`failed` — it never goes back.

Environment setup and CI — see [docs/development.md](development.md).
