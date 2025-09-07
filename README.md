# SQLGym Text-to-SQL Corpus

A scaffold for generating a 50‑subdomain corpus of realistic, efficiency-aware
SQLite databases paired with multi-turn text-to-SQL tasks.

## Quickstart
```bash
make scaffold   # create subdomain folders from domains.yaml
make build      # generate schemas and populate data (disabled in this repo)
make check      # run sanity checks and guardrails
python3 scripts/index_dbs.py  # index built datasets
```
Use `DOMAIN=<topdomain>` to limit `build` or `check` to a top-level domain.

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
