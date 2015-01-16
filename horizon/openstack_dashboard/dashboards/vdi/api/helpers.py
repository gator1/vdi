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

from vdidashboard.utils import workflow_helpers as work_helpers


class Helpers(object):
    def __init__(self, vdi_client):
        self.vdi = vdi_client
        self.plugins = self.vdi.plugins

    def _get_node_processes(self, plugin):
        processes = []
        for proc_lst in plugin.node_processes.values():
            processes += proc_lst

        return [(proc_name, proc_name) for proc_name in processes]

    def get_node_processes(self, plugin_name, vdi_version):
        plugin = self.plugins.get_version_details(plugin_name, vdi_version)

        return self._get_node_processes(plugin)

    def _extract_parameters(self, configs, scope, applicable_target):
        parameters = []
        for config in configs:
            if (config['scope'] == scope and
                    config['applicable_target'] == applicable_target):

                parameters.append(work_helpers.Parameter(config))

        return parameters

    def get_general_node_group_configs(self, plugin_name, vdi_version):
        plugin = self.plugins.get_version_details(plugin_name, vdi_version)

        return self._extract_parameters(plugin.configs, 'node', 'general')

    def get_targeted_node_group_configs(self, plugin_name, vdi_version):
        plugin = self.plugins.get_version_details(plugin_name, vdi_version)

        parameters = {}

        for service in plugin.node_processes.keys():
            parameters[service] = self._extract_parameters(plugin.configs,
                                                           'node', service)

        return parameters

    