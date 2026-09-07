PYTHON_INTERPRETER ?= .venv/bin/python
export GCAM_EMISSIONS_HOME ?= $(CURDIR)

.PHONY: help install validate inventory factors scrape-capss emissions spatial format lint test check clean

help:
	@grep -E '^[a-zA-Z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install:  ## Create the venv and install the package with dev extras
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"

validate:  ## Check the packaged reference tables agree with each other
	$(PYTHON_INTERPRETER) -m gcam_emissions.inventory --validate-only
	$(PYTHON_INTERPRETER) -m gcam_emissions.factors.catalog --validate-only

inventory:  ## Build the sector inventory and its diagnostics
	$(PYTHON_INTERPRETER) -m gcam_emissions.inventory

factors:  ## Build and validate the emission-factor catalog
	$(PYTHON_INTERPRETER) -m gcam_emissions.factors.catalog

scrape-capss:  ## Extract factor candidates from the CAPSS Handbook VII PDF
	$(PYTHON_INTERPRETER) -m gcam_emissions.factors.capss_handbook

emissions:  ## Map GCAM activity through the factor catalog to annual mass
	$(PYTHON_INTERPRETER) -m gcam_emissions.native

spatial:  ## Allocate national mass to administrative shares and coordinates
	$(PYTHON_INTERPRETER) -m gcam_emissions.spatial

format:  ## Apply the formatter
	$(PYTHON_INTERPRETER) -m ruff format src tests

lint:  ## Lint and check import ordering
	$(PYTHON_INTERPRETER) -m ruff check src tests

test:  ## Run the test suite
	$(PYTHON_INTERPRETER) -m pytest -q

check: format lint test  ## Everything that must pass before a commit

clean:  ## Remove caches and build artifacts
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
