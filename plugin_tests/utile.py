# -*- coding: utf-8 -*-

extensions = {
    'extension1': {
        'meta': {
            'os': 'linux',
            'arch': 'i386',
            'baseName': 'Ext1',
            'repository_type': 'git',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '35333',
            'app_revision': '0005',
            'packagetype': 'installer',
            'codebase': 'SL4',
            'description': 'Extension for Slicer 4'
        }
    },
    'extension2': {
        'meta': {
            'os': 'win',
            'arch': 'i386',
            'baseName': 'Ext2',
            'repository_type': 'git',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '54342',
            'app_revision': '0000',
            'packagetype': 'installer',
            'codebase': 'SL4',
            'description': 'Extension for Slicer 4 new version'
        }
    },
    'extension3': {
        'meta': {
            'os': 'linux',
            'arch': 'amd64',
            'baseName': 'Ext3',
            'repository_type': 'gitlab',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '542',
            'app_revision': '0001',
            'packagetype': 'zip',
            'codebase': 'SL434334',
            'description': 'Extension for Slicer 4 new version'
        }
    },
    'extension4': {
        'meta': {
            'os': 'macosx',
            'arch': 'amd64',
            'baseName': 'Ext3',
            'repository_type': 'gitlab',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '542',
            'app_revision': '0001',
            'packagetype': 'zip',
            'codebase': 'SL434334',
            'description': 'Extension for Slicer 4 new version'
        }
    },
    'extension5': {
        'meta': {
            'os': 'macosx',
            'arch': 'i386',
            'baseName': 'Ext3',
            'repository_type': 'gitlab',
            'repository_url': 'http://slicer.com/extension/Ext',
            'revision': '542',
            'app_revision': '0001',
            'packagetype': 'zip',
            'codebase': 'SL434334',
            'description': 'Extension for Slicer 4 new version'
        }
    }
}

packages = {
    'package1': {
        'meta': {
            'os': 'macosx',
            'arch': 'amd64',
            'baseName': 'pkg1',
            'repository_type': 'gitlab',
            'repository_url': 'https://slicer4.com',
            'revision': '0005',
        }
    },

    'package2': {
        'meta': {
            'os': 'win',
            'arch': 'i386',
            'baseName': 'pkg2',
            'repository_type': 'gitlab',
            'repository_url': 'https://slicer4.com',
            'revision': '0000',
        }
    },

    'package3': {
        'meta': {
            'os': 'linux',
            'arch': 'amd64',
            'baseName': 'pkg3',
            'repository_type': 'git',
            'repository_url': 'git://slicer4.com',
            'revision': '0000',
        }
    }

}

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
            'Ext2': {
                'win': {
                    'i386': 1
                }
            }
        }
    },
    '0001': {
        'extensions': {
            'Ext3': {
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
            'Ext1': {
                'linux': {
                    'i386': 1
                }
            }
        }
    }
}
