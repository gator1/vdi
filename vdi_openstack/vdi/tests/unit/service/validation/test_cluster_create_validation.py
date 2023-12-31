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

import mock

from vdi import exceptions
from vdi import main
from vdi.service import api
from vdi.service.validations import clusters as c
from vdi.tests.unit import base
from vdi.tests.unit.service.validation import utils as u


class TestClusterCreateValidation(u.ValidationTestCase):
    def setUp(self):
        self._create_object_fun = c.check_cluster_create
        self.scheme = c.CLUSTER_SCHEMA
        api.plugin_base.setup_plugins()

    def test_cluster_create_v_plugin_vers(self):
        self._assert_create_object_validation(
            data={
                'name': 'testname',
                'plugin_name': 'vanilla',
                'hadoop_version': '1'
            },
            bad_req_i=(1, "INVALID_REFERENCE",
                       "Requested plugin 'vanilla' "
                       "doesn't support version '1'"),
        )

    def test_cluster_create_v_required(self):
        self._assert_create_object_validation(
            data={},
            bad_req_i=(1, "VALIDATION_ERROR",
                       u"'name' is a required property")
        )
        self._assert_create_object_validation(
            data={
                'name': 'test-name'
            },
            bad_req_i=(1, "VALIDATION_ERROR",
                       u"'plugin_name' is a required property")
        )
        self._assert_create_object_validation(
            data={
                'name': 'testname',
                'plugin_name': 'vanilla'
            },
            bad_req_i=(1, "VALIDATION_ERROR",
                       u"'hadoop_version' is a required property")
        )

    def test_cluster_create_v_types(self):
        data = {
            'name': "testname",
            'plugin_name': "vanilla",
            'hadoop_version': "1.2.1"
        }
        self._assert_types(data)

    def test_cluster_create_v_name_base(self):
        data = {
            'name': "testname",
            'plugin_name': "vanilla",
            'hadoop_version': "1.2.1"
        }
        self._assert_valid_name_hostname_validation(data)

    def test_cluster_create_v_unique_cl(self):
        data = {
            'name': 'test',
            'plugin_name': 'vanilla',
            'hadoop_version': '1.2.1'
        }
        self._assert_create_object_validation(
            data=data,
            bad_req_i=(1, 'NAME_ALREADY_EXISTS',
                       "Cluster with name 'test' already exists")
        )

    def test_cluster_create_with_heat_stack_exists(self):
        main.CONF.set_override('infrastructure_engine', 'heat')
        self.addCleanup(main.CONF.clear_override, 'infrastructure_engine')
        data = {
            'name': 'test-heat',
            'plugin_name': 'vanilla',
            'hadoop_version': '1.2.1'
        }
        self._assert_create_object_validation(
            data=data,
            bad_req_i=(1, 'NAME_ALREADY_EXISTS',
                       "Cluster name 'test-heat' is already "
                       "used as Heat stack name")
        )

    def test_cluster_create_v_keypair_exists(self):
        self._assert_create_object_validation(
            data={
                'name': "testname",
                'plugin_name': "vanilla",
                'hadoop_version': "1.2.1",
                'user_keypair_id': 'wrong_keypair'
            },
            bad_req_i=(1, 'INVALID_REFERENCE',
                       "Requested keypair 'wrong_keypair' not found")
        )

    def test_cluster_create_v_keypair_type(self):
        self._assert_create_object_validation(
            data={
                'name': "test-name",
                'plugin_name': "vanilla",
                'hadoop_version': "1.2.1",
                'user_keypair_id': '1'
            },
            bad_req_i=(1, 'VALIDATION_ERROR',
                       "'1' is not a 'valid_name'")
        )
        self._assert_create_object_validation(
            data={
                'name': "test-name",
                'plugin_name': "vanilla",
                'hadoop_version': "1.2.1",
                'user_keypair_id': '!'},
            bad_req_i=(1, 'VALIDATION_ERROR',
                       "'!' is not a 'valid_name'")
        )

    def test_cluster_create_v_image_exists(self):
        self._assert_create_object_validation(
            data={
                'name': "test-name",
                'plugin_name': "vanilla",
                'hadoop_version': "1.2.1",
                'default_image_id': '550e8400-e29b-41d4-a616-446655440000'
            },
            bad_req_i=(1, 'INVALID_REFERENCE',
                       "Requested image '550e8400-e29b-41d4-a616-446655440000'"
                       " is not registered")
        )

    def test_cluster_create_v_plugin_name_exists(self):
        self._assert_create_object_validation(
            data={
                'name': "test-name",
                'plugin_name': "wrong_plugin",
                'hadoop_version': "1.2.1",
            },
            bad_req_i=(1, 'INVALID_REFERENCE',
                       "Sahara doesn't contain plugin "
                       "with name 'wrong_plugin'")
        )

    def test_cluster_create_v_wrong_network(self):
        self._assert_create_object_validation(
            data={
                'name': "test-name",
                'plugin_name': "vanilla",
                'hadoop_version': "1.2.1",
                'default_image_id': '550e8400-e29b-41d4-a716-446655440000',
                'neutron_management_network': '53a36917-ab9f-4589-'
                                              '94ce-b6df85a68332'
            },
            bad_req_i=(1, 'INVALID_REFERENCE', "Network 53a36917-ab9f-4589-"
                                               "94ce-b6df85a68332 not found")
        )

    def test_cluster_create_v_cluster_configs(self):
        self._assert_cluster_configs_validation(True)

    def test_cluster_create_v_right_data(self):
        self._assert_create_object_validation(
            data={
                'name': "testname",
                'plugin_name': "vanilla",
                'hadoop_version': "1.2.1",
                'user_keypair_id': 'test_keypair',
                'cluster_configs': {
                    'HDFS': {
                        u'hadoop.tmp.dir': '/temp/'
                    }
                },
                'default_image_id': '550e8400-e29b-41d4-a716-446655440000',
                'neutron_management_network': 'd9a3bebc-f788-4b81-'
                                              '9a93-aa048022c1ca'
            }
        )

    def test_cluster_create_v_default_image_required_tags(self):
        self._assert_cluster_default_image_tags_validation()


class TestClusterCreateFlavorValidation(base.SaharaWithDbTestCase):
    """Tests for valid flavor on cluster create.

    The following use cases for flavors during cluster create are validated:
      * Flavor id defined in a node group template and used in a cluster
        template.
      * Flavor id defined in node groups on cluster create.
      * Both node groups and cluster template defined on cluster create.
      * Node groups with node group template defined on cluster create.
    """

    def setUp(self):
        super(TestClusterCreateFlavorValidation, self).setUp()
        modules = [
            "vdi.service.validations.base.check_plugin_name_exists",
            "vdi.service.validations.base.check_plugin_supports_version",
            "vdi.service.validations.base._get_plugin_configs",
            "vdi.service.validations.base.check_node_processes",
            "vdi.utils.openstack.nova.client",
        ]
        self.patchers = []
        for module in modules:
            patch = mock.patch(module)
            patch.start()
            self.patchers.append(patch)

        nova_p = mock.patch("vdi.utils.openstack.nova.client")
        nova = nova_p.start()
        self.patchers.append(nova_p)
        nova().flavors.list.side_effect = u._get_flavors_list
        api.plugin_base.setup_plugins()

    def tearDown(self):
        u.stop_patch(self.patchers)
        super(TestClusterCreateFlavorValidation, self).tearDown()

    def _create_node_group_template(self, flavor='42'):
        ng_tmpl = {
            "plugin_name": "vanilla",
            "hadoop_version": "1.2.1",
            "node_processes": ["namenode"],
            "name": "master",
            "flavor_id": flavor
        }
        return api.create_node_group_template(ng_tmpl).id

    def _create_cluster_template(self, ng_id):
        cl_tmpl = {
            "plugin_name": "vanilla",
            "hadoop_version": "1.2.1",
            "node_groups": [
                {"name": "master",
                 "count": 1,
                 "node_group_template_id": "%s" % ng_id}
            ],
            "name": "test-template"
        }
        return api.create_cluster_template(cl_tmpl).id

    def test_cluster_create_v_correct_flavor(self):
        ng_id = self._create_node_group_template(flavor='42')
        ctmpl_id = self._create_cluster_template(ng_id)

        data = {
            "name": "testname",
            "plugin_name": "vanilla",
            "hadoop_version": "1.2.1",
            "cluster_template_id": '%s' % ctmpl_id,
            'default_image_id': '550e8400-e29b-41d4-a716-446655440000'
        }
        patchers = u.start_patch(False)
        c.check_cluster_create(data)
        u.stop_patch(patchers)

        data1 = {
            "name": "testwithnodegroups",
            "plugin_name": "vanilla",
            "hadoop_version": "1.2.1",
            "node_groups": [
                {
                    "name": "allinone",
                    "count": 1,
                    "flavor_id": "42",
                    "node_processes": [
                        "namenode",
                        "jobtracker",
                        "datanode",
                        "tasktracker"
                    ]
                }
            ],
            'default_image_id': '550e8400-e29b-41d4-a716-446655440000'
        }
        patchers = u.start_patch(False)
        c.check_cluster_create(data1)
        u.stop_patch(patchers)

    def test_cluster_create_v_invalid_flavor(self):
        ng_id = self._create_node_group_template(flavor='10')
        ctmpl_id = self._create_cluster_template(ng_id)

        data = {
            "name": "testname",
            "plugin_name": "vanilla",
            "hadoop_version": "1.2.1",
            "cluster_template_id": '%s' % ctmpl_id,
            'default_image_id': '550e8400-e29b-41d4-a716-446655440000'
        }
        data1 = {
            "name": "testwithnodegroups",
            "plugin_name": "vanilla",
            "hadoop_version": "1.2.1",
            "node_groups": [
                {
                    "name": "allinone",
                    "count": 1,
                    "flavor_id": "10",
                    "node_processes": [
                        "namenode",
                        "jobtracker",
                        "datanode",
                        "tasktracker"
                    ]
                }
            ],
            'default_image_id': '550e8400-e29b-41d4-a716-446655440000'
        }
        for values in [data, data1]:
            with self.assertRaises(exceptions.InvalidException):
                try:
                    patchers = u.start_patch(False)
                    c.check_cluster_create(values)
                    u.stop_patch(patchers)
                except exceptions.InvalidException as e:
                    self.assertEqual("Requested flavor '10' not found",
                                     e.message)
                    raise e

    def test_cluster_create_cluster_tmpl_node_group_mixin(self):
        ng_id = self._create_node_group_template(flavor='10')
        ctmpl_id = self._create_cluster_template(ng_id)

        data = {
            "name": "testtmplnodegroups",
            "plugin_name": "vanilla",
            "hadoop_version": "1.2.1",
            "cluster_template_id": '%s' % ctmpl_id,
            'default_image_id': '550e8400-e29b-41d4-a716-446655440000',
            "node_groups": [
                {
                    "name": "allinone",
                    "count": 1,
                    "flavor_id": "42",
                    "node_processes": [
                        "namenode",
                        "jobtracker",
                        "datanode",
                        "tasktracker"
                    ]
                }
            ]
        }
        patchers = u.start_patch(False)
        c.check_cluster_create(data)
        u.stop_patch(patchers)

    def test_cluster_create_node_group_tmpl_mixin(self):
        ng_id = self._create_node_group_template(flavor='23')
        data = {
            "name": "testtmplnodegroups",
            "plugin_name": "vanilla",
            "hadoop_version": "1.2.1",
            "node_groups": [
                {
                    "node_group_template_id": '%s' % ng_id,
                    "name": "allinone",
                    "count": 1,
                    "flavor_id": "42",
                    "node_processes": [
                        "namenode",
                        "jobtracker",
                        "datanode",
                        "tasktracker"
                    ]
                },
            ],
            'default_image_id': '550e8400-e29b-41d4-a716-446655440000'
        }
        with self.assertRaises(exceptions.InvalidException):
            try:
                patchers = u.start_patch(False)
                c.check_cluster_create(data)
                u.stop_patch(patchers)
            except exceptions.InvalidException as e:
                self.assertEqual("Requested flavor '23' not found",
                                 e.message)
                raise e
