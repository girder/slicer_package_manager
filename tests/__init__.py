import os


FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data',
    )


EXTENSIONS = [
    {
        'meta': {
            'os': 'linux',
            'arch': 'i386',
            'baseName': 'Ext0',
            'repository_type': 'git',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '35333',
            'app_revision': '0005',
            'packagetype': 'installer',
            'codebase': 'SL4',
            'description': 'Extension for Slicer 4'
        }
    },
    {
        'meta': {
            'os': 'win',
            'arch': 'i386',
            'baseName': 'Ext1',
            'repository_type': 'git',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '54342',
            'app_revision': '0000',
            'packagetype': 'installer',
            'codebase': 'SL4',
            'description': 'Extension for Slicer 4 new version'
        }
    },
    {
        'meta': {
            'os': 'linux',
            'arch': 'amd64',
            'baseName': 'Ext2',
            'repository_type': 'gitlab',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '542',
            'app_revision': '0001',
            'packagetype': 'zip',
            'codebase': 'SL434334',
            'description': 'Extension for Slicer 4 new version'
        }
    },
    {
        'meta': {
            'os': 'macosx',
            'arch': 'amd64',
            'baseName': 'Ext2',
            'repository_type': 'gitlab',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '542',
            'app_revision': '0001',
            'packagetype': 'zip',
            'codebase': 'SL434334',
            'description': 'Extension for Slicer 4 new version'
        }
    },
    {
        'meta': {
            'os': 'macosx',
            'arch': 'i386',
            'baseName': 'Ext2',
            'repository_type': 'gitlab',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '542',
            'app_revision': '0001',
            'packagetype': 'zip',
            'codebase': 'SL434334',
            'description': 'Extension for Slicer 4 new version'
        }
    }
]

PACKAGES = [
    {
        'meta': {
            'os': 'macosx',
            'arch': 'amd64',
            'baseName': 'pkg0',
            'repository_type': 'gitlab',
            'repository_url': 'https://slicer4.com',
            'revision': '0005',
            'version': '0.1.0',
        }
    },
    {
        'meta': {
            'os': 'win',
            'arch': 'i386',
            'baseName': 'pkg1',
            'repository_type': 'gitlab',
            'repository_url': 'https://slicer4.com',
            'revision': '0000',
            'version': '0.2.0',
        }
    },
    {
        'meta': {
            'os': 'linux',
            'arch': 'amd64',
            'baseName': 'pkg2',
            'repository_type': 'git',
            'repository_url': 'git://slicer4.com',
            'revision': '0000',
            'version': '0.3.0',
        }
    }
]

expectedDownloadStats = {
    '0000': {
        'applications': {
            'win': {
                'i386': 1
            },
            'linux': {
                'amd64': 1
            }
        },
        'extensions': {
            'Ext1': {
                'win': {
                    'i386': 1
                }
            }
        }
    },
    '0001': {
        'extensions': {
            'Ext2': {
                'linux': {
                    'amd64': 1
                },
                'macosx': {
                    'amd64': 1,
                    'i386': 1
                }
            }
        }
    },
    '0005': {
        'applications': {
            'macosx': {
                'amd64': 1
            }
        },
        'extensions': {
            'Ext0': {
                'linux': {
                    'i386': 1
                }
            }
        }
    }
}


def computeContentChecksum(algo, content):
    """Compute digest of ``content`` using ``algo``.

    Supported hashing algorithms are SHA256, SHA512, and MD5.

    :raises ValueError: if algo is unknown.
    """
    import hashlib

    if algo not in ['SHA256', 'SHA512', 'MD5']:
        raise ValueError("unsupported hashing algorithm %s" % algo)

    hash = hashlib.new(algo)
    hash.update(content)
    return hash.hexdigest()


def computeFileChecksum(algo, filePath):
    """Compute digest of ``filePath`` using ``algo``.

    Supported hashing algorithms are SHA256, SHA512, and MD5.
    It internally reads the file by chunk of 8192 bytes.

    :raises ValueError: if algo is unknown.
    :raises IOError: if filePath does not exist.
    """
    import hashlib

    if algo not in ['SHA256', 'SHA512', 'MD5']:
        raise ValueError("unsupported hashing algorithm %s" % algo)

    with open(filePath, 'rb') as content:
        hash = hashlib.new(algo)
        while True:
            chunk = content.read(8192)
            if not chunk:
                break
            hash.update(chunk)
        return hash.hexdigest()


class ExternalData:

    def __init__(self, objectStorePath):
        self._downloadPercent = 0
        self._objectStorePath = objectStorePath

    @staticmethod
    def _humanFormatSize(size):
        """Convert size in bytes to human readable string including unit suffix.

        Adapted from
        https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
        """
        for x in ['bytes', 'KB', 'MB', 'GB']:
            if -1024.0 < size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0
        return "%3.1f %s" % (size, 'TB')

    @staticmethod
    def _extractAlgoAndDigest(checksum):
        """Given a checksum string formatted as ``<algo>:<digest>`` returns the tuple ``(algo, digest)``.

        ``<algo>`` is expected to be `SHA256`, `SHA512`, or `MD5`.
        ``<digest>`` is expected to be the full length hexdecimal digest.

        :raises ValueError: if checksum is incorrectly formatted.
        """
        if checksum is None:
            return None, None
        if len(checksum.split(':')) != 2:
            raise ValueError("invalid checksum '%s'. Expected format is '<algo>:<digest>'." % checksum)
        (algo, digest) = checksum.split(':')
        expected_algos = ['SHA256', 'SHA512', 'MD5']
        if algo not in expected_algos:
            raise ValueError("invalid algo '%s'. Algo must be one of %s" % (algo, ", ".join(expected_algos)))
        expected_digest_length = {'SHA256': 64, 'SHA512': 128, 'MD5': 32}
        if len(digest) != expected_digest_length[algo]:
            raise ValueError("invalid digest length %d. Expected digest length for %s is %d" % (
                len(digest), algo, expected_digest_length[algo]))
        return algo, digest

    def _reportHook(self, blocksSoFar, blockSize, totalSize):
        # we clamp to 100% because the blockSize might be larger than the file itself
        percent = min(int((100. * blocksSoFar * blockSize) / totalSize), 100)
        if percent == 100 or (percent - self._downloadPercent >= 10):
            # we clamp to totalSize when blockSize is larger than totalSize
            humanSizeSoFar = self._humanFormatSize(min(blocksSoFar * blockSize, totalSize))
            humanSizeTotal = self._humanFormatSize(totalSize)
            print('Downloaded %s (%d%% of %s)...' % (humanSizeSoFar, percent, humanSizeTotal))
            self._downloadPercent = percent

    def _downloadFile(self, uri, name, checksum):
        """
        :param uri: Download URL.
        :param name: File name that will be downloaded.
        :param checksum: Checksum formatted as ``<algo>:<digest>`` to verify the downloaded file.
            For example, ``SHA256:cc211f0dfd9a05ca3841ce1141b292898b2dd2d3f08286affadf823a7e58df93``.
        """
        self._downloadPercent = 0
        filePath = self._objectStorePath + '/' + name
        (algo, digest) = self._extractAlgoAndDigest(checksum)
        if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
            import urllib.error
            import urllib.parse
            import urllib.request
            print('Requesting download %s from %s ...' % (name, uri))
            try:
                urllib.request.urlretrieve(uri, filePath, self._reportHook)
                print('Download finished')
            except IOError as exc:
                raise ValueError(f"Failed to download {uri} to {filePath}: %s" % exc)

            if algo is not None:
                print('Verifying checksum')
                current_digest = computeFileChecksum(algo, filePath)
                if current_digest != digest:
                    print(
                        'Checksum verification failed. Computed checksum %s different from expected checksum %s' % (
                            current_digest, digest))
                    os.remove(filePath)
                else:
                    self._downloadPercent = 100
                    print('Checksum OK')
        else:
            if algo is not None:
                print('Verifying checksum')
                current_digest = computeFileChecksum(algo, filePath)
                if current_digest != digest:
                    print('File already exists in cache but checksum is different - re-downloading it.')
                    os.remove(filePath)
                    return self._downloadFile(uri, name, checksum)
                else:
                    self._downloadPercent = 100
                    print('File already exists and checksum is OK - reusing it.')
            else:
                self._downloadPercent = 100
                print('File already exists in cache - reusing it.')
        return filePath

    def download(self, uri, fileName, checksum):
        """Download data into storage directory.

        :param uri: Download URL.
        :param fileName: File name that will be downloaded.
        :param checksum: Checksum formatted as ``<algo>:<digest>`` to verify the downloaded file.
            For example, ``SHA256:cc211f0dfd9a05ca3841ce1141b292898b2dd2d3f08286affadf823a7e58df93``.
        """
        if not os.access(self._objectStorePath, os.W_OK):
            os.makedirs(self._objectStorePath, exist_ok=True)
            assert os.access(self._objectStorePath, os.W_OK)
        maximumAttemptsCount = 3
        errors = set()
        for _attemptsCount in range(maximumAttemptsCount):
            try:
                return self._downloadFile(uri, fileName, checksum)
            except ValueError as exc:
                errors.add(str(exc))
                continue
        raise RuntimeError('Download of %s failed for %d attempts\n  uri: %s\n  errors: %s' % (
            fileName, maximumAttemptsCount, uri, ", ".join(errors)
        ))
