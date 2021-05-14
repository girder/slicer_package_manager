import os
import pytest


@pytest.fixture
def files():
    with open('file1.txt', 'w+') as file:
        file.write('Content of the file number 1')

    with open('file2.txt', 'w+') as file:
        file.write('Content of the file number 2')

    with open('file3.txt', 'w+') as file:
        file.write('Content of the file number 3')

    yield ['file1.txt', 'file2.txt', 'file3.txt']

    os.remove('file1.txt')
    os.remove('file2.txt')
    os.remove('file3.txt')
