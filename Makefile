.PHONY: clean-pyc clean-build clean-skbuild docs clean

help:
	@echo "$(MAKE) [target]"
	@echo
	@echo "  targets:"
	@echo "    docs        - generate Sphinx HTML documentation, including API docs"
	@echo "    docs-only   - generate Sphinx HTML documentation, including API docs"
	@echo

docs-only:
	rm -f docs/server.api.rst
	rm -f docs/server.models.rst
	rm -rf docs/_build/
	sphinx-apidoc -o docs/ --module-first server
	sphinx-apidoc -o docs/ --module-first python_client/slicer_package_manager_client/
	rm -f docs/modules.rst
	rm -f docs/setup.rst
	rm -f docs/slicer_package_manager_client.rst
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

docs: docs-only
	open docs/_build/html/index.html || xdg-open docs/_build/html/index.html

