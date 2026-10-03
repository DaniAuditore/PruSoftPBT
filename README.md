# PruSoftPBT

A small, executable CRUD laboratory for an in-memory book catalog. Python keeps
the domain visible; pytest and Hypothesis verify general properties rather than
only hand-picked examples. No database, web server, or GUI is required.

## Run the laboratory

Run these commands from the repository root in Windows PowerShell. Python 3.12
must be installed and available through the `py` launcher. Activation is optional;
using the virtual environment executable avoids PATH and execution-policy issues.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m ruff format catalog.py demo.py tests
.\.venv\Scripts\python.exe -m ruff check catalog.py demo.py tests
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe demo.py
```

The demo creates, reads, updates, and deletes a book, confirms that a deleted ID
is missing, and checks that a later creation does not reuse that ID. Tests include
generated properties for each CRUD operation.

## Domain contract

| Operation / field | Contract |
| --- | --- |
| `create(title, pages)` | Returns an immutable `Book`; assigns the next positive integer ID. |
| `read(book_id)` | Returns the matching immutable record without changing the catalog. |
| `update(book_id, title, pages)` | Full replacement of editable fields; preserves ID and other records. |
| `delete(book_id)` | Removes and returns exactly the matching record. |
| `list_books()` | Returns an immutable tuple snapshot in creation/ID order. |
| Title | String, stripped of surrounding whitespace; normalized length 1–120 Unicode code points. Interior whitespace is preserved. |
| Pages | Exact `int` (not `bool`), between 1 and 10,000 inclusive. |
| ID | Exact positive `int` (not `bool`); invalid IDs raise `ValueError`. |
| Missing ID | `read`, `update`, and `delete` raise `KeyError`; no state changes. |
| Validation failure | Raises `ValueError`; no partial mutation and no consumed ID. |

IDs are unique and never reused **within one catalog instance**, including after
deletion. Separate instances start at 1. Titles need not be unique. Updates first
validate and look up the ID, then validate replacement fields. A missing ID thus
takes precedence over invalid replacement fields. Frozen records and tuple
snapshots prevent accidental mutation through the public API; updates cannot
change an earlier snapshot. Python reflection/private-field access is not a
security boundary. Storage is transient and single-threaded.

## Criteria and executable properties

| Criterion | Generated test / invariant |
| --- | --- |
| Create | `test_create_adds_one_unique_normalized_record`: cardinality +1, correct values, increasing unique IDs, previous records preserved. |
| Read | `test_read_is_pure_and_snapshots_are_immutable`: round trip, unchanged state, frozen records, historical snapshots unaffected by update. |
| Update | `test_update_preserves_identity_cardinality_and_other_records`: same ID and size; only target fields change. |
| Delete | `test_delete_removes_only_target_and_never_reuses_id`: cardinality -1, target missing, other records preserved, subsequent ID strictly higher. |
| Invalid fields | `test_invalid_fields_do_not_mutate_or_consume_ids`: rejected create/update leave all records and next ID unchanged. |
| Invalid / absent IDs | `test_invalid_ids_are_rejected_without_mutation`, `test_missing_ids_do_not_mutate`: generated failures for read/update/delete are atomic. |

Strategies generate bounded lists of books, Unicode titles, page counts, record
positions, malformed fields, and missing/invalid IDs. Invalid fields are built
directly (including whitespace-only and overlong titles, booleans, floats, and
out-of-range pages); tests do not discard most examples using broad filters.
These are bounded experiments, not a mathematical proof or a
concurrency/persistence test.

## Investigated PBT approach and reproduction

The official Hypothesis documentation was consulted through Context7 before
implementation: `@given` generates inputs from strategies. Each property runs up
to 100 examples. A deterministic CI profile and pinned dependencies make the
baseline reproducible without disabling shrinking.

When a property fails, Hypothesis shrinks the input toward
a smaller failing example. pytest displays the falsifying example. Local examples
are cached in `.hypothesis/` (ignored by Git); they are useful for exploration,
but are not part of the source deliverable. Failures also print a reproduction
blob because `print_blob=True`. Paste the suggested `@reproduce_failure(...)`
decorator temporarily onto the failing property with the same Hypothesis version.
For a repeatable exploratory run, use an explicit seed:

```powershell
.\.venv\Scripts\python.exe -m pytest --hypothesis-profile=explore --hypothesis-seed=20261002
```

After fixing a discovered defect, keep a regression test/example and rerun the
whole suite; a seed or blob is a debugging aid, not the invariant itself.

Official references:
- [Hypothesis quick start: generated properties](https://hypothesis.readthedocs.io/en/latest/quickstart.html)
- [Reproducing failures](https://hypothesis.readthedocs.io/en/latest/reproducing.html)

## Review and scope

Read `catalog.py`, then `tests/test_catalog.py`.
`demo.py` is the runtime entry point. `requirements-dev.txt` pins the test and
formatting tools; `pyproject.toml` sets test discovery and formatting conventions.
There are no runtime third-party dependencies. Generated environments, caches,
and the pre-existing `.atl/` directory are not laboratory source and must not be
staged.
