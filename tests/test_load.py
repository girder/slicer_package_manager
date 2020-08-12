import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('slicer_package_manager')
def test_import(server):
    assert 'slicer_package_manager' in loadedPlugins()
