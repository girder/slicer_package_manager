import os
import pytest


@pytest.fixture
def files():

    filenames = ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']

    for idx, filename in enumerate(filenames, start=1):
        with open(filename, 'w+') as file:
            file.write('Content of the file number %s' % idx)

    yield filenames

    for filename in filenames:
        os.remove(filename)
