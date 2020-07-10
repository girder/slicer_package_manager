# -*- coding: utf-8 -*-

from girder_client import GirderClient

if __name__ == "__main__":
    login = 'admin'
    password = 'adminadmin'

    gc = GirderClient(apiUrl='http://localhost:8080/api/v1')

    # Create an admin user & authenticate
    gc.createUser(
        login=login,
        email='admin@admin.com',
        firstName='admin',
        lastName='admin',
        password=password,
        admin=True
    )
    gc.authenticate(username=login, password=password)

    # Create an assetstore
    gc.post('assetstore', parameters={
        'name': 'TestAssetstore',
        'type': 0,
        'root': '/home/circleci/project/assetstore'
    })

    # Enable the 'slicer_package_manager' plugin
    gc.put('system/plugins', parameters={
        "plugins": '["slicer_package_manager"]'
    })

    # Restart the server
    gc.put('system/restart')
