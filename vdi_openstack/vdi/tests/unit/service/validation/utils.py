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
import novaclient.exceptions as nova_ex
import unittest2

from vdi.conductor import resource as r
from vdi.plugins.vanilla import plugin
import vdi.service.validation as v
from vdi.tests.unit import testutils as tu


m = {}

_types_checks = {
    "string": [1, (), {}],
    "integer": ["a", (), {}],
    "uuid": ["z550e8400-e29b-41d4-a716-446655440000", 1, "a", (), {}],
    "array": [{}, 'a', 1]
}


def _update_data(data, update):
    data.update(update)
    return data


def _get_plugins():
    vanilla = plugin.VanillaProvider
    vanilla.name = 'vanilla'
    return [vanilla]


def _get_plugin(name):
    if name == 'vanilla':
        vanilla = plugin.VanillaProvider
        vanilla.name = 'vanilla'
        return vanilla
    return None


def _get_keypair(name):
    if name != "test_keypair":
        raise nova_ex.NotFound("")


def _get_network(**kwargs):
    if 'id' in kwargs and (
            kwargs['id'] != "d9a3bebc-f788-4b81-9a93-aa048022c1ca"):
        raise nova_ex.NotFound("")
    return 'OK'


def _get_heat_stack_list():
    return [FakeStack('test-heat')]


class FakeStack(object):
    def __init__(self, name):
        self.stack_name = name


class FakeFlavor(object):
    def __init__(self, id):
        self.id = id


def _get_flavors_list():
    return [FakeFlavor("42")]


def start_patch(patch_templates=True):
    get_clusters_p = mock.patch("vdi.service.api.get_clusters")
    get_cluster_p = mock.patch("vdi.service.api.get_cluster")
    if patch_templates:
        get_ng_templates_p = \
            mock.patch("vdi.service.api.get_node_group_templates")
        get_ng_template_p = \
            mock.patch("vdi.service.api.get_node_group_template")
    get_plugins_p = mock.patch("vdi.service.api.get_plugins")
    get_plugin_p = \
        mock.patch("vdi.plugins.base.PluginManager.get_plugin")
    if patch_templates:
        get_cl_templates_p = \
            mock.patch("vdi.service.api.get_cluster_templates")
        get_cl_template_p = \
            mock.patch("vdi.service.api.get_cluster_template")
    nova_p = mock.patch("vdi.utils.openstack.nova.client")
    keystone_p = mock.patch("vdi.utils.openstack.keystone.client")
    heat_p = mock.patch("vdi.utils.openstack.heat.client")
    get_image_p = mock.patch("vdi.service.api.get_image")

    get_image = get_image_p.start()
    get_clusters = get_clusters_p.start()
    get_cluster = get_cluster_p.start()
    if patch_templates:
        get_ng_templates = get_ng_templates_p.start()
        get_ng_template = get_ng_template_p.start()
    get_plugins = get_plugins_p.start()
    get_plugin = get_plugin_p.start()
    if patch_templates:
        get_cl_templates = get_cl_templates_p.start()
        get_cl_template_p.start()

    nova = nova_p.start()
    keystone = keystone_p.start()

    if patch_templates:
        get_cl_templates.return_value = []

    nova().flavors.list.side_effect = _get_flavors_list
    nova().keypairs.get.side_effect = _get_keypair
    nova().networks.find.side_effect = _get_network

    heat = heat_p.start()
    heat().stacks.list.side_effect = _get_heat_stack_list

    class Service:
        @property
        def name(self):
            return 'cinder'

    def _services_list():
        return [Service()]

    keystone().services.list.side_effect = _services_list

    class Image:
        def __init__(self, name='test'):
            self.name = name

        @property
        def id(self):
            if self.name == 'test':
                return '550e8400-e29b-41d4-a716-446655440000'
            else:
                return '813fe450-40d2-4acc-ade5-ea753a1bd5bc'

        @property
        def tags(self):
            if self.name == 'test':
                return ['vanilla', '1.2.1']
            else:
                return ['wrong_tag']

    def _get_image(id):
        if id == '550e8400-e29b-41d4-a716-446655440000':
            return Image()
        else:
            return Image('wrong_test')

    get_image.side_effect = _get_image
    nova().images.list_registered.return_value = [Image(),
                                                  Image(name='wrong_name')]
    ng_dict = tu.make_ng_dict('ng', '42', ['namenode'], 1)
    cluster = tu.create_cluster('test', 't', 'vanilla', '1.2.1', [ng_dict],
                                id=1, status='Active')
    # stub clusters list
    get_clusters.return_value = [cluster]
    get_cluster.return_value = cluster

    # stub node templates
    if patch_templates:
        ngt_dict = {'name': 'test', 'tenant_id': 't', 'flavor_id': '42',
                    'plugin_name': 'vanilla', 'hadoop_version': '1.2.1',
                    #'id': '1234321',
                    'id': '550e8400-e29b-41d4-a716-446655440000',
                    'node_processes': ['namenode']}

        get_ng_templates.return_value = [r.NodeGroupTemplateResource(ngt_dict)]

        ct_dict = {'name': 'test', 'tenant_id': 't',
                   'plugin_name': 'vanilla', 'hadoop_version': '1.2.1'}

        get_cl_templates.return_value = [r.ClusterTemplateResource(ct_dict)]

    vanilla = plugin.VanillaProvider()
    vanilla.name = 'vanilla'
    get_plugins.return_value = [vanilla]

    def _get_ng_template(id):
        for template in get_ng_templates():
            if template.id == id:
                return template
        return None

    def _get_plugin(name):
        if name == 'vanilla':
            return vanilla
        return None

    get_plugin.side_effect = _get_plugin
    if patch_templates:
        get_ng_template.side_effect = _get_ng_template
    # request data to validate
    patchers = [get_clusters_p, get_plugins_p, get_plugin_p,
                nova_p, keystone_p, get_image_p, heat_p]
    if patch_templates:
        patchers.extend([get_ng_template_p, get_ng_templates_p,
                         get_cl_template_p, get_cl_templates_p])
    return patchers


def stop_patch(patchers):
    for patcher in patchers:
        patcher.stop()


class ValidationTestCase(unittest2.TestCase):
    def setUp(self):
        self._create_object_fun = None
        self.scheme = None

    def tearDown(self):
        self._create_object_fun = None

    def _assert_calls(self, mock, call_info):
        if not call_info:
            self.assertEqual(mock.call_count, 0)
        else:
            self.assertEqual(mock.call_count, call_info[0])
            self.assertEqual(mock.call_args[0][0].code, call_info[1])
            self.assertEqual(mock.call_args[0][0].message, call_info[2])

    @mock.patch("vdi.utils.api.request_data")
    @mock.patch("vdi.utils.api.bad_request")
    def _assert_create_object_validation(
            self, bad_req=None, request_data=None,
            data=None, bad_req_i=None):

        request_data.return_value = data
        # mock function that should be validated
        patchers = start_patch()
        m_func = mock.Mock()
        m_func.__name__ = "m_func"
        v.validate(self.scheme, self._create_object_fun)(m_func)(data=data)

        self.assertEqual(request_data.call_count, 1)
        self._assert_calls(bad_req, bad_req_i)
        stop_patch(patchers)

    def _assert_valid_name_hostname_validation(self, data):

        data.update({'name': None})
        self._assert_create_object_validation(
            data=data,
            bad_req_i=(1, "VALIDATION_ERROR",
                       u"None is not of type 'string'")
        )
        data.update({'name': ""})
        self._assert_create_object_validation(
            data=data,
            bad_req_i=(1, "VALIDATION_ERROR",
                       u"'' is too short")
        )
        data.update({'name': ('a' * 51)})
        self._assert_create_object_validation(
            data=data,
            bad_req_i=(1, "VALIDATION_ERROR",
                       u"'%s' is too long" % ('a' * 51))
        )
        data.update({'name': 'a-!'})
        self._assert_create_object_validation(
            data=data,
            bad_req_i=(1, "VALIDATION_ERROR",
                       u"'a-!' is not a 'valid_name_hostname'")
        )

    def _assert_types(self, default_data):
        for p_name in self.scheme['properties']:
            prop = self.scheme['properties'][p_name]
            if prop["type"] in _types_checks:
                for type_ex in _types_checks[prop["type"]]:
                    data = default_data.copy()
                    value = type_ex
                    value_str = str(value)
                    if isinstance(value, str):
                        value_str = "'%s'" % value_str
                    data.update({p_name: value})
                    if "enum" in prop:
                        self._assert_create_object_validation(
                            data=data,
                            bad_req_i=(1, 'VALIDATION_ERROR',
                                       u"%s is not one of %s"
                                       % (value_str, prop["enum"]))
                        )
                    else:
                        self._assert_create_object_validation(
                            data=data,
                            bad_req_i=(1, 'VALIDATION_ERROR',
                                       u"%s is not of type '%s'"
                                       % (value_str, prop["type"]))
                        )

    def _assert_cluster_configs_validation(self, require_image_id=False):
        data = {
            'name': 'test-cluster',
            'plugin_name': 'vanilla',
            'hadoop_version': '1.2.1',
            'cluster_configs': {
                'HDFS': {
                    u'hadoop.tmp.dir': '/temp/'
                }
            },
            'default_image_id': '550e8400-e29b-41d4-a716-446655440000'
        }
        if require_image_id:
            data_without_image = data.copy()
            data_without_image.pop('default_image_id')
            self._assert_create_object_validation(
                data=data_without_image,
                bad_req_i=(1, 'NOT_FOUND',
                           "'default_image_id' field is not found")
            )
        self._assert_create_object_validation(
            data=_update_data(data.copy(), {
                'cluster_configs': {
                    'wrong_target': {
                        u'hadoop.tmp.dir': '/temp/'
                    }
                }}),
            bad_req_i=(1, 'INVALID_REFERENCE',
                       "Plugin doesn't contain applicable "
                       "target 'wrong_target'")
        )
        self._assert_create_object_validation(
            data=_update_data(data.copy(), {
                'cluster_configs': {
                    'HDFS': {
                        u's': '/temp/'
                    }
                }
            }),
            bad_req_i=(1, 'INVALID_REFERENCE',
                       "Plugin's applicable target 'HDFS' doesn't "
                       "contain config with name 's'")
        )

    def _assert_cluster_default_image_tags_validation(self):
        data = {
            'name': 'test-cluster',
            'plugin_name': 'vanilla',
            'hadoop_version': '1.2.1',
            'default_image_id': '550e8400-e29b-41d4-a716-446655440000'
        }
        self._assert_create_object_validation(data=data)
        data = {
            'name': 'test-cluster',
            'plugin_name': 'vanilla',
            'hadoop_version': '1.2.1',
            'default_image_id': '813fe450-40d2-4acc-ade5-ea753a1bd5bc'
        }
        self._assert_create_object_validation(
            data=data,
            bad_req_i=(1, 'INVALID_REFERENCE',
                       "Tags of requested image "
                       "'813fe450-40d2-4acc-ade5-ea753a1bd5bc' "
                       "don't contain required tags "
                       "['vanilla', '1.2.1']"))
