# Copyright (c) 2013 Hortonworks, Inc.
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

import unittest2

from vdi.plugins.hdp.versions import versionhandlerfactory


class VersionManagerFactoryTest(unittest2.TestCase):

    def test_get_versions(self):
        factory = versionhandlerfactory.VersionHandlerFactory.get_instance()
        versions = factory.get_versions()

        self.assertEqual(2, len(versions))
        self.assertIn('1.3.2', versions)
        self.assertIn('2.0.6', versions)

    def test_get_version_handlers(self):
        factory = versionhandlerfactory.VersionHandlerFactory.get_instance()
        versions = factory.get_versions()
        for version in versions:
            handler = factory.get_version_handler(version)
            self.assertIsNotNone(handler)
            self.assertEqual(version, handler.get_version())
