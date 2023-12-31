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

import novaclient.exceptions as nova_ex
from oslo.config import cfg

from vdi import conductor as cond
from vdi import context
import vdi.exceptions as ex
import vdi.plugins.base as plugin_base
import vdi.service.api as api
import vdi.utils.openstack.heat as heat
import vdi.utils.openstack.keystone as keystone
import vdi.utils.openstack.nova as nova


CONF = cfg.CONF
conductor = cond.API


def _get_plugin_configs(plugin_name, hadoop_version, scope=None):
    pl_confs = {}
    for config in plugin_base.PLUGINS.get_plugin(
            plugin_name).get_configs(hadoop_version):
        if pl_confs.get(config.applicable_target):
            pl_confs[config.applicable_target].append(config.name)
        else:
            pl_confs[config.applicable_target] = [config.name]
    return pl_confs


## Common validation checks

def check_plugin_name_exists(name):
    if name not in [p.name for p in api.get_plugins()]:
        raise ex.InvalidException("Sahara doesn't contain plugin with name "
                                  "'%s'" % name)


def check_plugin_supports_version(p_name, version):
    if version not in plugin_base.PLUGINS.get_plugin(p_name).get_versions():
        raise ex.InvalidException("Requested plugin '%s' doesn't support"
                                  " version '%s'" % (p_name, version))


def check_image_registered(image_id):
    if image_id not in [i.id for i in nova.client().images.list_registered()]:
        raise ex.InvalidException("Requested image '%s' is not registered"
                                  % image_id)


def check_node_group_configs(plugin_name, hadoop_version, ng_configs,
                             plugin_configs=None):
    # TODO(aignatov): Should have scope and config type validations
    pl_confs = plugin_configs or _get_plugin_configs(plugin_name,
                                                     hadoop_version)
    for app_target, configs in ng_configs.items():
        if app_target not in pl_confs:
            raise ex.InvalidException("Plugin doesn't contain applicable "
                                      "target '%s'" % app_target)
        for name, values in configs.items():
            if name not in pl_confs[app_target]:
                raise ex.InvalidException("Plugin's applicable target '%s' "
                                          "doesn't contain config with name "
                                          "'%s'" % (app_target, name))


def check_all_configurations(data):
    pl_confs = _get_plugin_configs(data['plugin_name'], data['hadoop_version'])

    if data.get('cluster_configs'):
        check_node_group_configs(data['plugin_name'], data['hadoop_version'],
                                 data['cluster_configs'],
                                 plugin_configs=pl_confs)

    if data.get('node_groups'):
        check_duplicates_node_groups_names(data['node_groups'])
        for ng in data['node_groups']:
            check_node_group_basic_fields(data['plugin_name'],
                                          data['hadoop_version'],
                                          ng, pl_confs)

## NodeGroup related checks


def check_node_group_basic_fields(plugin_name, hadoop_version, ng,
                                  plugin_configs=None):

    if ng.get('node_group_template_id'):
        ng_tmpl_id = ng['node_group_template_id']
        check_node_group_template_exists(ng_tmpl_id)
        ng_tmpl = api.get_node_group_template(ng_tmpl_id).to_wrapped_dict()
        check_node_group_basic_fields(plugin_name, hadoop_version,
                                      ng_tmpl['node_group_template'],
                                      plugin_configs)

    if ng.get('node_configs'):
        check_node_group_configs(plugin_name, hadoop_version,
                                 ng['node_configs'], plugin_configs)
    if ng.get('flavor_id'):
        check_flavor_exists(ng['flavor_id'])

    if ng.get('node_processes'):
        check_node_processes(plugin_name, hadoop_version, ng['node_processes'])

    if ng.get('image_id'):
        check_image_registered(ng['image_id'])

    if ng.get('volumes_per_node'):
        check_cinder_exists()

    if ng.get('floating_ip_pool'):
        check_floatingip_pool_exists(ng['name'], ng['floating_ip_pool'])


def check_flavor_exists(flavor_id):
    flavor_list = nova.client().flavors.list()
    if flavor_id not in [flavor.id for flavor in flavor_list]:
        raise ex.InvalidException("Requested flavor '%s' not found"
                                  % flavor_id)


def check_floatingip_pool_exists(ng_name, pool_id):
    if not nova.get_network(id=pool_id):
        raise ex.InvalidException("Floating IP pool %s for node group "
                                  "'%s' not found" % (pool_id, ng_name))


def check_node_processes(plugin_name, version, node_processes):
    if len(set(node_processes)) != len(node_processes):
        raise ex.InvalidException("Duplicates in node processes "
                                  "have been detected")
    plugin_procesess = []
    for process in plugin_base.PLUGINS.get_plugin(
            plugin_name).get_node_processes(version).values():
        plugin_procesess += process

    if not set(node_processes).issubset(set(plugin_procesess)):
        raise ex.InvalidException("Plugin supports the following "
                                  "node procesess: %s" % plugin_procesess)


def check_duplicates_node_groups_names(node_groups):
    ng_names = [ng['name'] for ng in node_groups]
    if len(set(ng_names)) < len(node_groups):
        raise ex.InvalidException("Duplicates in node group names "
                                  "are detected")


## Group creation related checks

def check_group_unique_name(name):
    if name in [group.name for group in api.get_groups()]:
        raise ex.NameAlreadyExistsException("Group with name '%s' already"
                                            " exists" % name)
    # check_heat_stack_name(name)


# def check_heat_stack_name(cluster_name):
#     if CONF.infrastructure_engine == 'heat':
#         for stack in heat.client().stacks.list():
#             if stack.stack_name == cluster_name:
#                 raise ex.NameAlreadyExistsException(
#                     "Cluster name '%s' is already used as Heat stack name"
#                     % cluster_name)


def check_group_exists(id):
    if not api.get_group(id):
        raise ex.InvalidException("Group with id '%s'"
                                  " doesn't exist" % id)


# def check_keypair_exists(keypair):
#     try:
#         nova.client().keypairs.get(keypair)
#     except nova_ex.NotFound:
#         raise ex.InvalidException("Requested keypair '%s' not found" % keypair)


## Cluster creation related checks

def check_cluster_unique_name(name):
    if name in [cluster.name for cluster in api.get_clusters()]:
        raise ex.NameAlreadyExistsException("Cluster with name '%s' already"
                                            " exists" % name)
    check_heat_stack_name(name)


def check_heat_stack_name(cluster_name):
    if CONF.infrastructure_engine == 'heat':
        for stack in heat.client().stacks.list():
            if stack.stack_name == cluster_name:
                raise ex.NameAlreadyExistsException(
                    "Cluster name '%s' is already used as Heat stack name"
                    % cluster_name)


def check_cluster_exists(id):
    if not api.get_cluster(id):
        raise ex.InvalidException("Cluster with id '%s'"
                                  " doesn't exist" % id)


def check_keypair_exists(keypair):
    try:
        nova.client().keypairs.get(keypair)
    except nova_ex.NotFound:
        raise ex.InvalidException("Requested keypair '%s' not found" % keypair)


def check_network_exists(net_id):
    if not nova.get_network(id=net_id):
        raise ex.InvalidException("Network %s not found" % net_id)


## Cluster templates related checks

def check_cluster_template_unique_name(name):
    if name in [t.name for t in api.get_cluster_templates()]:
        raise ex.NameAlreadyExistsException("Cluster template with name '%s'"
                                            " already exists" % name)


def check_cluster_template_exists(cluster_template_id):
    if not api.get_cluster_template(id=cluster_template_id):
        raise ex.InvalidException("Cluster template with id '%s'"
                                  " doesn't exist" % cluster_template_id)


def check_node_groups_in_cluster_templates(plugin_name, hadoop_version,
                                           cluster_template_id):
    c_t = api.get_cluster_template(id=cluster_template_id)
    n_groups = c_t.to_wrapped_dict()['cluster_template']['node_groups']
    check_network_config(n_groups)
    for node_group in n_groups:
        check_node_group_basic_fields(plugin_name, hadoop_version, node_group)

## NodeGroup templates related checks


def check_node_group_template_unique_name(name):
    if name in [t.name for t in api.get_node_group_templates()]:
        raise ex.NameAlreadyExistsException("NodeGroup template with name '%s'"
                                            " already exists" % name)


def check_node_group_template_exists(ng_tmpl_id):
    if not api.get_node_group_template(id=ng_tmpl_id):
        raise ex.InvalidException("NodeGroup template with id '%s'"
                                  " doesn't exist" % ng_tmpl_id)


def check_network_config(node_groups):
    if CONF.use_floating_ips and CONF.use_neutron:
        for ng in node_groups:
            if not _get_floating_ip_pool(ng):
                raise ex.MissingFloatingNetworkException(ng.get('name'))


def _get_floating_ip_pool(node_group):
    if node_group.get('floating_ip_pool'):
        return node_group['floating_ip_pool']

    if node_group.get('node_group_template_id'):
        ctx = context.ctx()
        ngt = conductor.node_group_template_get(
            ctx,
            node_group['node_group_template_id'])
        if ngt.get('floating_ip_pool'):
            return ngt['floating_ip_pool']

    return None


## Cluster scaling

def check_resize(cluster, r_node_groups):
    cluster_ng_names = [ng.name for ng in cluster.node_groups]

    check_duplicates_node_groups_names(r_node_groups)

    for ng in r_node_groups:
        if ng['name'] not in cluster_ng_names:
            raise ex.InvalidException("Cluster doesn't contain node group "
                                      "with name '%s'" % ng['name'])


def check_add_node_groups(cluster, add_node_groups):
    cluster_ng_names = [ng.name for ng in cluster.node_groups]

    check_duplicates_node_groups_names(add_node_groups)

    pl_confs = _get_plugin_configs(cluster.plugin_name, cluster.hadoop_version)

    for ng in add_node_groups:
        if ng['name'] in cluster_ng_names:
            raise ex.InvalidException("Can't add new nodegroup. Cluster "
                                      "already has nodegroup with name '%s'"
                                      % ng['name'])

        check_node_group_basic_fields(cluster.plugin_name,
                                      cluster.hadoop_version, ng, pl_confs)


## Cinder

def check_cinder_exists():
    services = [service.name for service in
                keystone.client().services.list()]
    if 'cinder' not in services:
        raise ex.InvalidException("Cinder is not supported")


##Tags


def check_required_image_tags(plugin_name, hadoop_version, image_id):
    image = api.get_image(id=image_id)
    plugin = plugin_base.PLUGINS.get_plugin(plugin_name)
    req_tags = set(plugin.get_required_image_tags(hadoop_version))
    if not req_tags.issubset(set(image.tags)):
            raise ex.InvalidException("Tags of requested image '%s' don't "
                                      "contain required tags "
                                      "['%s', '%s']" %
                                      (image_id,
                                       plugin_name,
                                       hadoop_version))
