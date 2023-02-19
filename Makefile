.PHONY: help docs serve_docs install test deploy_docs

DOCS_DIR = docs

.git/hooks/pre-commit:  .pre-commit-config.yaml 
	echo $(COLOR)"Adding pre-commit hook to avoid committing notebook outputs"$(NC)
	pre-commit install

init: .git/hooks/pre-commit

help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "  install     to install the datascience package locally"
	@echo "  test        to run the tests"
	@echo "  docs        to build the docs"
	@echo "  clean_docs  to remove the doc files"
	@echo "  serve_docs  to serve the docs from a local Python server"
	@echo "  deploy_docs to deploy the docs to Github Pages"

install:
	python3 setup.py develop

test:
	python3 tests.py

docs:
	cd $(DOCS_DIR) ; make html

clean_docs:
	cd $(DOCS_DIR) ; make clean

serve_docs:
	cd $(DOCS_DIR)/_build/html ; python -m http.server
