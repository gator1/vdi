# Copyright (c) 2014 Intel Corporation
# Copyright (c) 2014 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re


class VersionFactory():
    versions = None
    modules = None
    initialized = False

    @staticmethod
    def get_instance():
        if not VersionFactory.initialized:
            src_dir = os.path.join(os.path.dirname(__file__), '')
            VersionFactory.versions = (
                [name[1:].replace('_', '.')
                 for name in os.listdir(src_dir)
                 if (os.path.isdir(os.path.join(src_dir, name))
                     and re.match(r'^v\d+_\d+_\d+$', name))])
            VersionFactory.modules = {}
            for version in VersionFactory.versions:
                module_name = 'vdi.plugins.intel.v{0}.'\
                              'versionhandler'.format(
                              version.replace('.', '_'))
                module_class = getattr(
                    __import__(module_name, fromlist=['vdi']),
                    'VersionHandler')
                module = module_class()
                key = version.replace('_', '.')
                VersionFactory.modules[key] = module

            VersionFactory.initialized = True

        return VersionFactory()

    def get_versions(self):
        return VersionFactory.versions

    def get_version_handler(self, version):
        return VersionFactory.modules[version]
