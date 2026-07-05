# Editing

`roll` has two editing surfaces:

- `rl stock edit` for one roll at a time;
- `rl batch` for many rolls at once.

They solve different problems and should stay separate.

## Boundaries

| Command | Scope | Typical use |
|---|---|---|
| `rl stock edit` | one roll | manual correction, field-by-field judgment |
| `rl batch` | many rolls | repeated update across a filtered set |
| `rl search` | many rolls | structured lookup, optionally with free text |
| `rl normalize` | archive structure | folder shape, keywords normalization, photo import |
| `rl doctor` | integrity | report problems, safe fixes only |

---

## `rl stock edit`

Use this when you want to inspect and adjust one roll by hand.

What it does:

- selects a single roll;
- edits its metadata fields directly;
- keeps the current values available in the prompts;
- applies changes only after you confirm each value in the interactive flow.

Best for:

- correcting one record;
- changing a camera on one roll;
- refining features or keywords on a single roll;
- adjusting the origin fields on one roll.

Not for:

- mass changes across many rolls;
- filtering by year or film name;
- bulk status updates.

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
- status;
- tags or keywords when needed.

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

- one roll, manual judgment, many fields -> `rl stock edit`;
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
- status;
- tags or keywords.

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

If you need both at different times, start with `stock edit` for the outlier and use `batch` for the rest.

---

## Examples

```bash
rl search --year 2025 --status loaded
```

```bash
rl search --film "Kodak Gold 200, Ilford HP5 Plus" --query balcony
```

```bash
rl stock edit
```

```bash
rl batch --year 2025 --film "Kodak Gold 200, Ilford HP5 Plus" --set camera="Pentax K1000"
```

```bash
rl batch --year 2025 --set status=processed
```

```bash
rl batch --film "Kodak Gold 200" --add-tag "summer,belgrade"
```

## Related

- [Getting Started](getting-started.md)
- [Architecture](architecture.md)
- [Reference](reference.md)
