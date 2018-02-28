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

# This gets us basic linting tests
add_standard_plugin_tests(NO_CLIENT_TESTS)

add_python_test(
  PLUGIN slicer_extension_manager
  EXTERNAL_DATA
  # Data are downloaded from https://data.kitware.com/#user/59c409558d777f7d33e9d5c1/folder/59c409558d777f7d33e9d5c2
  # The Public folder of 'pierreassemat'
  plugins/slicer_extension_manager/extension1.tar.gz
  plugins/slicer_extension_manager/extension2.tar.gz
  plugins/slicer_extension_manager/extension3.tar.gz
  plugins/slicer_extension_manager/extension4.tar.gz
  plugins/slicer_extension_manager/extension5.tar.gz
)
