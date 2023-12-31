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

from vdi.plugins import provisioning as p


class ProvisioningPluginBaseTest(unittest2.TestCase):
    def test__map_to_user_inputs_success(self):
        c1, c2, c3, plugin = _build_configs_and_plugin()

        user_inputs = plugin._map_to_user_inputs(None, {
            'at-1': {
                'n-1': 'v-1',
                'n-3': 'v-3',
            },
            'at-2': {
                'n-2': 'v-2',
            },
        })

        self.assertEqual(user_inputs, [
            p.UserInput(c3, 'v-3'),
            p.UserInput(c1, 'v-1'),
            p.UserInput(c2, 'v-2'),
        ])

    def test__map_to_user_inputs_failure(self):
        c1, c2, c3, plugin = _build_configs_and_plugin()

        with self.assertRaises(RuntimeError):
            plugin._map_to_user_inputs(None, {
                'at-X': {
                    'n-1': 'v-1',
                },
            })

        with self.assertRaises(RuntimeError):
            plugin._map_to_user_inputs(None, {
                'at-1': {
                    'n-X': 'v-1',
                },
            })


def _build_configs_and_plugin():
    c1 = p.Config('n-1', 'at-1', 'cluster')
    c2 = p.Config('n-2', 'at-2', 'cluster')
    c3 = p.Config('n-3', 'at-1', 'node')

    class TestPlugin(TestEmptyPlugin):
        def get_configs(self, hadoop_version):
            return [c1, c2, c3]

    return c1, c2, c3, TestPlugin()


class TestEmptyPlugin(p.ProvisioningPluginBase):
    def get_title(self):
        pass

    def get_versions(self):
        pass

    def get_configs(self, hadoop_version):
        pass

    def get_node_processes(self, hadoop_version):
        pass

    def configure_cluster(self, cluster):
        pass

    def start_cluster(self, cluster):
        pass
