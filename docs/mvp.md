# MVP

> Find the right roll from memory: a person, a place, an event, a mood - months later.

## Scenario

```bash
rl init ~/Pictures/plenka   # once
rl stock add                # bought a film → into stock
rl load                     # loaded the camera → roll created, asks for tags/features
rl stock process            # or: rl stock failed
rl search kir balcony       # half a year later — found it
```

## Commands

| Task | Command |
|---|---|
| Film stock | `stock add`, `stock list` |
| Roll | `load` (`--manual` — without stock), `stock process`, `stock failed` |
| Fill in a roll | `features add`, `tags add` |
| Find / view | `search`, `scan`, `status`, `stats [-v]`, `vocab` |
| Archive hygiene | `doctor [--fix] [-v]`, `normalize [--tags]` |
| Batch | `batch process` |

## Out of MVP scope

sync between machines · cloud · web UI · migrating old formats · image processing

First thing right after MVP: localization. The CLI defaults to English in the global config and the language is controlled with `rl config lang`.

## Rule

If it doesn't help find a roll from memory faster — it's out of MVP.
