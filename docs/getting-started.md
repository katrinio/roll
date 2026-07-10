# Getting Started

Track film stock, loaded rolls, and archive metadata.

## Main Flow

```bash
rl init ~/Pictures/plenka   # once
rl stock add                # bought a film → into stock
rl load                     # loaded the camera → roll created, asks for tags/features
rl stock process            # or: rl stock failed
rl search kir balcony       # half a year later — found it
```

## Command Groups

| Area | Commands |
|---|---|
| Setup | `rl init`, `rl config`, `rl config lang` |
| Film stock | `rl stock add`, `rl stock list` |
| Roll creation | `rl load`, `rl load --manual` |
| Status update | `rl stock process`, `rl stock failed`, `rl batch process` |
| Metadata | `rl features add`, `rl tags add`, `rl batch` |
| Find / inspect | `rl search`, `rl scan`, `rl status`, `rl stats [-v]`, `rl vocab` |
| Integrity | `rl doctor`, `rl doctor --fix`, `rl normalize --tags` |
| Photo import | `rl normalize --photos` |

## Out of Scope

sync between machines · cloud · web UI · migrating old formats · image processing

## Notes

- Run `rl config lang EN` or `rl config lang RU` to set the UI language.
- Run `rl --version` to print the current version.
- Run `rl update` to print package manager update guidance.
- Run `rl normalize --photos` in the current archive to sort raw photo folders by dominant photo date.

## Rule

If it doesn't help find a roll from memory faster — it's out of scope.

Architecture and exact behavior — see [docs/architecture.md](architecture.md). Editing flows — see [docs/editing.md](editing.md). Terms and exact rules — see [docs/reference.md](reference.md). Development setup — see [docs/development.md](development.md).
