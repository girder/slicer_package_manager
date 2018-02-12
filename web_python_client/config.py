#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

from girder_client import GirderClient

if __name__ == "__main__":
    gc = GirderClient(apiUrl='http://localhost:8080/api/v1')

    gc.createUser(
        login='admin',
        email='admin@admin.com',
        firstName='admin',
        lastName='admin',
        password='adminadmin',
        admin=True
    )
