# Getting Started

> Find the right roll from memory: a person, a place, an event, a mood - months later.

## Main Flow

```bash
rl init ~/Pictures/plenka   # once
rl stock add                # bought a film → into stock
rl load                     # loaded the camera → roll created, asks for tags/features
rl stock process            # or: rl stock failed
rl search kir balcony       # half a year later — found it
```

## What This Covers

| Flow | Command |
|---|---|
| Start | `rl init`, `rl config lang` |
| Film stock | `rl stock add`, `rl stock list` |
| Roll creation | `rl load`, `rl load --manual` |
| Status update | `rl stock process`, `rl stock failed` |
| Fill in a roll | `rl features add`, `rl tags add` |
| Find / inspect | `rl search`, `rl scan`, `rl status`, `rl stats [-v]`, `rl vocab` |
| Integrity | `rl doctor`, `rl doctor --fix`, `rl normalize --tags` |
| Batch | `rl batch process` |

## Out of Scope

sync between machines · cloud · web UI · migrating old formats · image processing

The CLI defaults to English in the global config and `rl config lang` changes it.

## Rule

If it doesn't help find a roll from memory faster — it's out of scope.

Architecture and exact behavior — see [docs/architecture.md](architecture.md). Terms and exact rules — see [docs/reference.md](reference.md). Development setup — see [docs/development.md](development.md).
