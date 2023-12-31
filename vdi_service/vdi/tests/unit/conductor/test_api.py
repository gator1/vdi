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

from vdi import conductor
from vdi import context
from vdi.tests.unit import base


SAMPLE_CLUSTER = {
    'plugin_name': 'test_plugin',
    'hadoop_version': 'test_version',
    'tenant_id': 'tenant_1',
    'name': 'test_cluster',
    'user_keypair_id': 'my_keypair',
    'node_groups': [
        {
            'name': 'ng_1',
            'flavor_id': '42',
            'node_processes': ['p1', 'p2'],
            'count': 1
        },
        {
            'name': 'ng_2',
            'flavor_id': '42',
            'node_processes': ['p3', 'p4'],
            'count': 3
        }
    ],
    'cluster_configs': {
        'service_1': {
            'config_2': 'value_2'
        },
        'service_2': {
            'config_1': 'value_1'
        }
    },
}

SAMPLE_NODE_GROUP = {
    'name': 'ng_3',
    'flavor_id': '42',
    'node_processes': ['p5', 'p6'],
    'count': 5
}

SAMPLE_INSTANCE = {
    'instance_name': 'test-name',
    'instance_id': '123456',
    'management_ip': '1.2.3.1'
}


class TestConductorClusterApi(base.SaharaWithDbTestCase):
    def setUp(self):
        super(TestConductorClusterApi, self).setUp()
        self.api = conductor.API

    def _make_sample(self):
        ctx = context.ctx()
        cluster = self.api.cluster_create(ctx, SAMPLE_CLUSTER)
        return ctx, cluster

    def _get_by_id(self, lst, id):
        for obj in lst:
            if obj.id == id:
                return obj

        raise RuntimeError('No such object with id %s' % id)

    def test_update_by_id(self):
        ctx, cluster = self._make_sample()

        self.api.cluster_update(ctx, cluster.id, {'name': 'changed'})

        updated_cluster = self.api.cluster_get(ctx, cluster.id)
        self.assertEqual(updated_cluster['name'], 'changed')

        self.api.cluster_destroy(ctx, updated_cluster.id)
        cluster_list = self.api.cluster_get_all(ctx)
        self.assertEqual(len(cluster_list), 0)

    def test_add_node_group_to_cluster_id(self):
        ctx, cluster = self._make_sample()
        ng_id = self.api.node_group_add(ctx, cluster.id, SAMPLE_NODE_GROUP)
        self.assertTrue(ng_id)

    def test_update_node_group_by_id(self):
        ctx, cluster = self._make_sample()
        ng_id = cluster.node_groups[0].id
        self.api.node_group_update(ctx, ng_id, {'name': 'changed_ng'})
        cluster = self.api.cluster_get(ctx, cluster.id)

        ng = self._get_by_id(cluster.node_groups, ng_id)
        self.assertEqual(ng.name, 'changed_ng')

    def test_add_instance_to_node_group_id(self):
        ctx, cluster = self._make_sample()
        inst_id = self.api.instance_add(ctx, cluster.node_groups[0].id,
                                        SAMPLE_INSTANCE)
        self.assertTrue(inst_id)

    def test_update_instance_by_id(self):
        ctx, cluster = self._make_sample()
        ng_id = cluster.node_groups[0].id
        inst_id = self.api.instance_add(ctx, ng_id, SAMPLE_INSTANCE)

        self.api.instance_update(ctx, inst_id, {'instance_name': 'tst123'})
        cluster = self.api.cluster_get(ctx, cluster.id)

        ng = self._get_by_id(cluster.node_groups, ng_id)
        self.assertEqual(ng.instances[0].instance_name, 'tst123')
