# logos — reproducible entry points. `make test-unit` passes in a bare checkout (no DB, no
# licensed corpora, no GPU); `make test-full` runs everything against a configured environment.
.PHONY: help install install-full test-unit test-full test-integration schema

help:
	@echo "install       - core deps (numpy, scipy)"
	@echo "install-full  - core + db + morph + neural + dev"
	@echo "test-unit     - DB-free / data-free unit suite (default CI lane)"
	@echo "test-full     - the whole suite (needs .env + licensed corpora + optional GPU)"
	@echo "schema        - apply schema.sql to the configured DB"

install:
	python3 -m pip install -e .

install-full:
	python3 -m pip install -e ".[full]"

# Unit lane: exclude the marked integration/licensed/gpu tests; the rest either run pure or skipif
# out cleanly in a bare checkout. PYTHONPATH=. so the scripts package is importable in-place.
test-unit:
	PYTHONPATH=. OMP_NUM_THREADS=1 python3 -m pytest tests/ -q -p no:cacheprovider \
		-m "not integration and not licensed_data and not gpu and not external_asset"

test-full:
	PYTHONPATH=. OMP_NUM_THREADS=1 python3 -m pytest tests/ -q -p no:cacheprovider

test-integration:
	PYTHONPATH=. python3 -m pytest tests/ -q -p no:cacheprovider -m integration

schema:
	@test -f .env || (echo "no .env (copy .env.example)"; exit 1)
	mysql < schema/schema.sql
