# Editing

`roll` has two write paths:

- `rl tags add` and `rl features add` update one roll at a time;
- `rl batch` applies one change to many rolls.

Use `rl search` to preview a set before `rl batch`.

## Boundaries

| Command | Scope | Typical use |
|---|---|---|
| `rl tags add` / `rl features add` | one roll | add or correct roll metadata |
| `rl batch` | many rolls | repeated update across a filtered set |
| `rl search` | many rolls | structured lookup, optionally with free text |
| `rl normalize` | archive structure | folder shape, keywords normalization, photo import |
| `rl doctor` | integrity | report problems, safe fixes only |

---

## Single-roll metadata updates

Use `rl tags add` or `rl features add` to update one roll.

What they do:

- selects a single roll;
- updates either `keywords` or `features`;
- writes new values to the roll and the matching vocabulary;
- skips duplicates.

Best for:

- correcting one record;
- refining features or keywords on a single roll;
- adding new vocabulary values during normal use.

Not for:

- mass changes across many rolls;
- camera changes across many rolls;
- repeated status updates.

---

## `rl batch`

Use this when you want to apply the same change to many rolls.

What it does:

- selects rolls by filters;
- shows a preview of the target set;
- applies one change to the whole selection;
- asks for confirmation before writing.

Selection is based on filters such as:

- year;
- film name;
- camera;
- status.

Within one filter, comma-separated values mean "match any of these".
Across filters, the selection is cumulative.

Best for:

- changing a camera on many rolls;
- moving a group of rolls to a new status;
- adding the same feature or tag to a batch;
- cleaning up a whole year or a film family.

Not for:

- one-off manual corrections;
- browsing a single record in detail;
- workflows that need per-field judgment on each roll.

---

## Boundary

Use this rule:

- one roll, tags or features only -> `rl tags add` or `rl features add`;
- many rolls, one repeated operation -> `rl batch`.

## `rl search`

Use this when you want to find rolls with the same filter language as `rl batch`, but without writing anything.

What it does:

- accepts the same structured filters as `rl batch`;
- keeps free-text search for ad hoc lookup;
- shows matching rolls and their basic metadata.

Selection is based on the same filters:

- year;
- film name;
- camera;
- status.

Within one filter, comma-separated values mean "match any of these".
Across filters, the selection is cumulative.

Best for:

- finding rolls by year and status;
- narrowing by film family before a batch update;
- looking up tags or camera names;
- searching by a short free-text fragment when you do not need a structured filter.

Not for:

- changing metadata;
- structural normalization;
- integrity repair.

If you need both at different times, start with `rl search` to preview the set, then run `rl batch`.

---

## Examples

```bash
rl search --year 2025 --status loaded
```

```bash
rl search --film "Kodak Gold 200, Ilford HP5 Plus" balcony
```

```bash
rl tags add
```

```bash
rl features add
```

```bash
rl batch --year 2025 --film "Kodak Gold 200, Ilford HP5 Plus" --set-camera "Pentax K1000"
```

```bash
rl batch --year 2025 --set-status processed
```

```bash
rl batch --film "Kodak Gold 200" --add-tag "summer,belgrade"
```

## Related

- [Getting Started](getting-started.md)
- [Architecture](architecture.md)
- [Reference](reference.md)
