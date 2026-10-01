# Makefile — the developer's entry points, copied to the PROJECT root (templates/ci/Makefile; references/agent-ops.md §8). Every heavy
# command goes through the one job pool (scripts/jobs.sh: slot semaphore sized cores / 4, nice, memory / load gate, wall + RSS log); the
# record round runs under ONE lock, once per batch of commits, never per agent. `make check` is the PR entry point ({{PROJECT_CHECK_CMD}}).
PY      ?= .venv/bin/python
JOBS    ?= scripts/jobs.sh
LOCK    ?= $(or $(TMPDIR),/tmp)/hwfs_record_round.lock
PRESETS ?= $(shell $(PY) scripts/project.py get print_targets 2>/dev/null | sed -n 's/^\([a-z_]*\):.*/\1/p')

.PHONY: check gates case slice renders pdf record-round status

check:            ## the adopt gates + the clone gate (read-only; the PR check)
	scripts/adopt_gates.sh

gates:            ## the adopt gates without the clone gate
	scripts/adopt_gates.sh --no-clone

# gen/*.py are the PROJECT's generators (contracts: SKILL.md §10, references/release-and-cut.md §7); a target whose generator is absent says so and skips.
gen = @test -f $(1) && $(JOBS) --tag $(2) -- $(PY) $(1) $(3) || echo "skip: $(1) is not in this project (project-side generator)"

case:             ## geometry chain: every body regenerated (no geometry cache with a fast engine; the old md5 is a determinism check); one heavy slot
	$(call gen,gen/case.py,case,)

slice:            ## slicer: one process per plate, plates whose STL md5 or settings md5 changed (sidecar); never parallel plates
	$(call gen,gen/plates.py,slice,--only-changed)

renders:          ## previews regenerated with the geometry (seconds with --preview); the collector re-grades every copy
	$(JOBS) --tag renders -- $(PY) scripts/collect_renders.py

pdf:              ## PDF render of the documents whose source md5 changed, one headless browser instance reused
	$(call gen,gen/render_pdf.py,pdf,--only-changed)

record-round:     ## the one-round record chain (references/release-and-cut.md §3.1), serialized: one lock on the machine, once per batch
	@mkdir "$(LOCK)" 2>/dev/null || { echo "record round already running (lock $(LOCK))"; exit 1; }
	@trap 'rmdir "$(LOCK)"' EXIT; set -e; \
	$(PY) scripts/known_issues.py; \
	if $(PY) scripts/project.py record | grep -q MISSING; then echo "skip: no record of record yet (collect_renders)"; else $(JOBS) --tag records -- $(PY) scripts/collect_renders.py; fi; \
	$(PY) scripts/release_report.py; \
	if ! $(PY) scripts/traceability.py --check >/dev/null 2>&1; then $(PY) scripts/traceability.py; $(PY) scripts/release_report.py; fi; \
	test -f gen/analysis_index.py && $(PY) gen/analysis_index.py || echo "skip: gen/analysis_index.py"; \
	test -f gen/render_pdf.py && $(JOBS) --tag pdf -- $(PY) gen/render_pdf.py --only-changed || echo "skip: gen/render_pdf.py"; \
	test -f gen/production_cut.py && $(PY) gen/production_cut.py build || echo "skip: gen/production_cut.py (the cut generator is project-side; SKILL.md §10)"

status:           ## the pool: slots in use, free memory, load
	$(JOBS) --status
