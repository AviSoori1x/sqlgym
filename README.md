# SQLGym Text-to-SQL Corpus

A scaffold for generating a 50‑subdomain corpus of realistic, efficiency-aware
SQLite databases paired with multi-turn text-to-SQL tasks. Guardrails verify
index usage with `EXPLAIN QUERY PLAN` and rely on SQLite's JSON1 extension for
portable evidence lookups.

## Quickstart
```bash
make scaffold   # create subdomain folders from domains.yaml
make build      # generate schemas and populate data
make check      # run sanity checks and guardrails
python3 scripts/index_dbs.py  # index built datasets
```
Use `DOMAIN=<topdomain>` to limit `build` or `check` to a top-level domain.

### Prereqs
Efficiency guards rely on `EXPLAIN QUERY PLAN` against built SQLite databases
and the JSON1 extension for evidence queries. Ensure your SQLite build includes
JSON1 and run `make build` locally before invoking guards.

## Consumers' Guide
After building locally:
```bash
git lfs install
git add **/*_normalized.db **/*_denormalized.db DATASET_INDEX.md datasets.json
git commit -m "Add built SQLite datasets and index (LFS)"
```
Consumers can retrieve datasets via:
```bash
git lfs pull
sqlite3 finance/payments_acquiring/payments_acquiring_normalized.db
.read finance/payments_acquiring/sanity_checks.sql
```
Example query:
```sql
SELECT COUNT(*) FROM card_transactions WHERE merchant_id=1;
```

## Guardrail errors
Guard scripts expect normalized databases and fast/slow query pairs. If you run
`make check` before building, you may see errors like `missing db; build first`
or `No fast/slow pairs`. Efficiency checks will fail until you build local
databases via `make build DOMAIN=<topdomain>` then rerun checks.

SQLite requires foreign keys to be enabled per connection via
`PRAGMA foreign_keys=ON;` — see the [SQLite docs](https://www.sqlite.org/pragma.html#pragma_foreign_keys).

## How to Extend
1. Add a new subdomain under the appropriate top domain in `domains.yaml`.
2. `make scaffold DOMAIN=<topdomain>` to create stub files.
3. Implement schema, populators, tasks, evidence and checks.
4. `make build DOMAIN=<topdomain>` and `make check DOMAIN=<topdomain>`.
5. Commit changes and dataset artifacts via Git LFS as shown above.

## Beyond WikiSQL/Spider
- **Multi-turn dialogue**: tasks contain clarifications and context carry-over.
- **Efficiency planning**: `EXPLAIN QUERY PLAN` guard ensures indexed access vs scans.
- **Evidence grounded**: tasks reference small policy/knowledge files validated by `evidence_schema.py`.
- **Workflows**: top-level `workflow_tasks.md` files describe multi-SQL sequences verified by `workflow_guard.py`.
These features move the corpus beyond single-question benchmarks toward
realistic, plan-aware interactions.
