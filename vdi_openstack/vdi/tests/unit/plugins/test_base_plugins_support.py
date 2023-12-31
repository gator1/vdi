# Copyright (c) 2014 Huawei Technologies.
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

from vdi.plugins import base as pb


class BasePluginsSupportTest(unittest2.TestCase):

    def setUp(self):
        pb.setup_plugins()

    def test_plugins_loaded(self):
        plugins = [p.name for p in pb.PLUGINS.get_plugins(pb.PluginInterface)]
        self.assertIn('vanilla', plugins)
        self.assertIn('hdp', plugins)
