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

import vdi.exceptions as ex
import vdi.service.api as api
import vdi.service.validations.base as b
import vdi.service.validations.cluster_templates as cl_tmpl


def _build_cluster_schema():
    cluster_schema = copy.deepcopy(cl_tmpl.CLUSTER_TEMPLATE_SCHEMA)
    cluster_schema['properties'].update({
        "is_transient": {
            "type": "boolean"
        },
        "user_keypair_id": {
            "type": "string",
            "format": "valid_name",
        },
        "cluster_template_id": {
            "type": "string",
            "format": "uuid",
        }})
    return cluster_schema


CLUSTER_SCHEMA = _build_cluster_schema()


def check_group_create(data, **kwargs):
    b.check_group_unique_name(data['name'])
    # b.check_plugin_name_exists(data['plugin_name'])
    # b.check_plugin_supports_version(data['plugin_name'],
    #                                 data['hadoop_version'])
    # if data.get('cluster_template_id'):
    #     ct_id = data['cluster_template_id']
    #     b.check_cluster_template_exists(ct_id)
    #     if not data.get('node_groups'):
    #         b.check_node_groups_in_cluster_templates(data['plugin_name'],
    #                                                  data['hadoop_version'],
    #                                                  ct_id)

    # if data.get('user_keypair_id'):
    #     b.check_keypair_exists(data['user_keypair_id'])

    # default_image_id = _get_cluster_field(data, 'default_image_id')
    # if default_image_id:
    #     b.check_image_registered(default_image_id)
    #     b.check_required_image_tags(data['plugin_name'],
    #                                 data['hadoop_version'],
    #                                 default_image_id)
    # else:
    #     raise ex.NotFoundException('default_image_id',
    #                                "'%s' field is not found")

    # b.check_all_configurations(data)

    # if data.get('anti_affinity'):
    #     b.check_node_processes(data['plugin_name'], data['hadoop_version'],
    #                            data['anti_affinity'])

    # if data.get('node_groups'):
    #     b.check_network_config(data['node_groups'])

    # neutron_net_id = _get_cluster_field(data, 'neutron_management_network')
    # if neutron_net_id:
    #     b.check_network_exists(neutron_net_id)


def check_cluster_create(data, **kwargs):
    b.check_cluster_unique_name(data['name'])
    b.check_plugin_name_exists(data['plugin_name'])
    b.check_plugin_supports_version(data['plugin_name'],
                                    data['hadoop_version'])
    if data.get('cluster_template_id'):
        ct_id = data['cluster_template_id']
        b.check_cluster_template_exists(ct_id)
        if not data.get('node_groups'):
            b.check_node_groups_in_cluster_templates(data['plugin_name'],
                                                     data['hadoop_version'],
                                                     ct_id)

    if data.get('user_keypair_id'):
        b.check_keypair_exists(data['user_keypair_id'])

    default_image_id = _get_cluster_field(data, 'default_image_id')
    if default_image_id:
        b.check_image_registered(default_image_id)
        b.check_required_image_tags(data['plugin_name'],
                                    data['hadoop_version'],
                                    default_image_id)
    else:
        raise ex.NotFoundException('default_image_id',
                                   "'%s' field is not found")

    b.check_all_configurations(data)

    if data.get('anti_affinity'):
        b.check_node_processes(data['plugin_name'], data['hadoop_version'],
                               data['anti_affinity'])

    if data.get('node_groups'):
        b.check_network_config(data['node_groups'])

    neutron_net_id = _get_cluster_field(data, 'neutron_management_network')
    if neutron_net_id:
        b.check_network_exists(neutron_net_id)


def _get_cluster_field(cluster, field):
    if cluster.get(field):
        return cluster[field]

    if cluster.get('cluster_template_id'):
        cluster_template = api.get_cluster_template(
            id=cluster['cluster_template_id'])

        if cluster_template.get(field):
            return cluster_template[field]

    return None
