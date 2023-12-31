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

import copy

import unittest2

from vdi.conductor import resource as r
from vdi.utils import types


SAMPLE_DICT = {
    'first': [1, 2],
    'second': {'a': 1, 'b': 2}
}

SAMPLE_NESTED_LISTS_DICT = {
    'a': [[{'b': 123}]]
}

SAMPLE_CLUSTER_DICT = {
    'name': 'test-cluster',
    'cluster_configs': {
        'general': {
            'some_overridden_config': 'somevalue'
        }
    },
    'node_groups': [
        {
            'name': 'master',
        },
        {
            'name': 'worker',
            'node_processes': ['tasktracker', 'datanode'],
            'node_configs': {},
            'instances': [
                {
                    'name': 'test-cluster-001',
                    'ip': '1.1.1.1'
                }
            ]
        }
    ]
}


SAMPLE_JOB_BINARY_DICT = {
    "created_at": "2014-02-14 16:26:08.895897",
    "description": "a job",
    "extra": {
        "password": "password",
        "user": "user"
    },
    "id": "c0caf119-f380-4fab-a46e-0f28ebd23b5c",
    "name": "bob",
    "tenant_id": "6b859fb8d1f44e8eafdfb91f21309b5f",
    "updated_at": "null",
    "url": "swift-internal://bob.vdi/job"
}


SAMPLE_DATA_SOURCE = {
    'name': 'input',
    'description': 'some input',
    'type': 'swift',
    'url': 'swift://tmckay.vdi',
    'credentials': {
        'username': 'me',
        'password': 'password'
    }
}


class TestResource(unittest2.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_resource_creation(self):
        res = r.Resource(SAMPLE_DICT)

        self.assertIsInstance(res.first, list)
        self.assertEqual(res.first, [1, 2])
        self.assertIsInstance(res.second, r.Resource)
        self.assertEqual(res.second.a, 1)
        self.assertEqual(res.second.b, 2)

    def test_resource_immutability(self):
        res = r.Resource(SAMPLE_DICT)

        with self.assertRaises(types.FrozenClassError):
            res.first.append(123)

        with self.assertRaises(types.FrozenClassError):
            res.first = 123

        with self.assertRaises(types.FrozenClassError):
            res.second.a = 123

    def test_nested_lists(self):
        res = r.Resource(SAMPLE_NESTED_LISTS_DICT)
        self.assertEqual(res.a[0][0].b, 123)

    def test_cluster_resource(self):
        cluster = r.ClusterResource(SAMPLE_CLUSTER_DICT)

        self.assertEqual(cluster.name, 'test-cluster')

        self.assertEqual(cluster.node_groups[0].name, 'master')
        self.assertIsInstance(cluster.node_groups[0], r.NodeGroupResource)
        self.assertEqual(cluster.node_groups[0].cluster.name, 'test-cluster')

        self.assertEqual(cluster.node_groups[1].instances[0].name,
                         'test-cluster-001')
        self.assertIsInstance(cluster.node_groups[1].instances[0],
                              r.InstanceResource)
        self.assertEqual(
            cluster.node_groups[1].instances[0].node_group.name,
            'worker')

    def test_to_dict(self):
        cluster = r.ClusterResource(SAMPLE_CLUSTER_DICT)
        self.assertEqual(cluster.to_dict(), SAMPLE_CLUSTER_DICT)

    def test_to_dict_filtering(self):
        cluster_dict = copy.deepcopy(SAMPLE_CLUSTER_DICT)
        cluster_dict['management_private_key'] = 'abacaba'
        cluster_dict['node_groups'][0]['id'] = 'some_id'

        cluster = r.ClusterResource(cluster_dict)
        self.assertEqual(cluster.to_dict(), SAMPLE_CLUSTER_DICT)

    def test_to_wrapped_dict(self):
        cluster = r.ClusterResource(SAMPLE_CLUSTER_DICT)
        wrapped_dict = cluster.to_wrapped_dict()
        self.assertEqual(len(wrapped_dict), 1)
        self.assertEqual(wrapped_dict['cluster'], SAMPLE_CLUSTER_DICT)

    def test_job_binary_filter_extra(self):
        job_binary = r.JobBinary(SAMPLE_JOB_BINARY_DICT)
        wrapped_dict = job_binary.to_wrapped_dict()
        self.assertNotIn('extra', wrapped_dict)

    def test_data_source_filter_credentials(self):
        data_source = r.DataSource(SAMPLE_DATA_SOURCE)
        wrapped_dict = data_source.to_wrapped_dict()
        self.assertNotIn('credentials', wrapped_dict)
