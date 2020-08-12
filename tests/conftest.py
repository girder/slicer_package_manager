import os

import pytest

from shutil import copyfile

from . import ExternalData


@pytest.fixture
def external_data(request, tmpdir):
    """A pytest fixture to define a 'tmpdir' containing files or directories
    specified with a 'external_data' mark.
    """
    entry_list = []
    for mark in request.node.iter_markers('external_data'):
        entry_list.extend(mark.args)

    # Collect externals in map where keys are "fileName" and values are "(<algo>, <checksum>)"
    externals = {}
    for entry in entry_list:
        ext_not_found = []
        for ext in ['sha256', 'sha512', 'md5']:
            external = entry + "." + ext
            if os.path.exists(external):
                break
            else:
                ext_not_found.append(ext)
                external = None
        if external is None:
            raise ValueError("{}.{} not found".format(entry, ", ".join(ext_not_found)))
        with open(external) as content:
            hashsum = content.read().strip()
        externals[os.path.basename(entry)] = (ext, hashsum)

    external_data_dir = os.environ.get(
        'GIRDER_TEST_DATA_PREFIX', os.path.join(os.path.dirname(__file__), ".external_data"))

    # Download files
    downloaded_files = []
    for fileName, value in externals.items():
        algo, checksum = value
        print("fileName [%s] algo [%s] checksum [%s]" % (fileName, algo, checksum))
        downloaded_files.append(
            ExternalData(external_data_dir).download(
                uri="https://data.kitware.com/api/v1/file/hashsum/{}/{}/download".format(algo, checksum),
                fileName=fileName,
                checksum="{}:{}".format(algo.upper(), checksum)
            )
        )

    # Copy download files to temporary directory
    for downloaded_file in downloaded_files:
        copyfile(downloaded_file, tmpdir.join(os.path.basename(downloaded_file)))

    return tmpdir
