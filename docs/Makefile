# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = SlicerPackageManager
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets specific to this project
docs-only:
	rm -f developer_guide/slicer_package_manager.api.rst
	rm -f developer_guide/slicer_package_manager.models.rst
	rm -rf _build/
	sphinx-apidoc -o ./developer_guide/ --no-toc --module-first ../slicer_package_manager/
	sphinx-apidoc -o ./developer_guide/ --no-toc --module-first ../python_client/slicer_package_manager_client/
	$(MAKE) clean
	$(MAKE) html

docs: docs-only
	open _build/html/index.html || xdg-open _build/html/index.html

.PHONY: docs docs-only
