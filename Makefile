.RECIPEPREFIX := >
.PHONY: scaffold build check clean regen

scaffold:
> python3 scripts/scaffold.py $(if $(DOMAIN),--domain $(DOMAIN),)

build:
> python3 scripts/build_all.py $(if $(DOMAIN),--domain $(DOMAIN),)

check:
> python3 scripts/diversity_guard.py
> python3 scripts/workflow_guard.py
> python3 scripts/evidence_schema.py
> python3 scripts/run_checks.py $(if $(DOMAIN),--domain $(DOMAIN),)
> python3 scripts/efficiency_guard.py

clean:
> python3 scripts/clean.py

regen: clean scaffold build

