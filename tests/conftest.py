import pytest

from . import downloadExternals


@pytest.fixture
def external_data(request, tmpdir):
    """A pytest fixture to define a 'tmpdir' containing files or directories
    specified with a 'external_data' mark.
    """
    entry_list = []
    for mark in request.node.iter_markers('external_data'):
        entry_list.extend(mark.args)

    return downloadExternals(entry_list, tmpdir)
