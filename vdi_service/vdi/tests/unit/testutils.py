# Copyright (c) 2014 Mirantis Inc.
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


from vdi.conductor import resource as r


def create_cluster(name, tenant, plugin, version, node_groups, **kwargs):
    dct = {'name': name, 'tenant_id': tenant, 'plugin_name': plugin,
           'hadoop_version': version, 'node_groups': node_groups}
    dct.update(kwargs)
    return r.ClusterResource(dct)


def make_ng_dict(name, flavor, processes, count, instances=[], **kwargs):
    dct = {'name': name, 'flavor_id': flavor, 'node_processes': processes,
           'count': count, 'instances': instances}
    dct.update(kwargs)
    return dct


def make_inst_dict(inst_id, inst_name):
    return {'instance_id': inst_id, 'instance_name': inst_name}
