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

from oslo.config import cfg
from six.moves.urllib import parse as urlparse

from vdi import conductor as c
from vdi import context
from vdi.openstack.common import excutils
from vdi.openstack.common import log as logging
from vdi.plugins import base as plugin_base
from vdi.plugins import provisioning
from vdi.service.edp import job_manager as jm
from vdi.service import trusts
from vdi.utils import general as g
from vdi.utils.openstack import nova


conductor = c.API
CONF = cfg.CONF
LOG = logging.getLogger(__name__)


INFRA = None


def setup_service_api(engine):
    global INFRA

    INFRA = engine


## Group ops

def get_groups():
    return conductor.group_get_all(context.ctx())


def get_group(id):
    return conductor.group_get(context.ctx(), id)


def update_group(id, data):
    ctx = context.ctx()
    group = conductor.group_get(ctx, id)

    try:
        group = conductor.group_update(ctx, group, data)
        #group = conductor.group_update(ctx, group, {"status": "Validating", "name": "Test1111"})
        LOG.info(g.format_group_status(group))
    except Exception:
        with excutils.save_and_reraise_exception():
            group = conductor.group_update(ctx, group, {"status": "Active"})
            LOG.info(g.format_group_status(group))

    return conductor.group_get(ctx, id)


def create_group(values):
    ctx = context.ctx()
    group = conductor.group_create(ctx, values)

    # validating group
    try:
        group = conductor.group_update(ctx, group, {"status": "Active"})
        # group = conductor.group_update(ctx, group, {"status": "Validating"})
        LOG.info(g.format_group_status(group))
    except Exception as e:
        with excutils.save_and_reraise_exception():
            group = conductor.group_update(ctx, group,
                                               {"status": "Error",
                                                "status_description": str(e)})
            LOG.info(g.format_group_status(group))

    # context.spawn("group-creating-%s" % group.id,
    #               _provision_group, group.id)
    # if CONF.use_identity_api_v3 and cluster.is_transient:
    #     trusts.create_trust(cluster)

    return conductor.group_get(ctx, group.id)


def terminate_group(id):
    ctx = context.ctx()
    group = conductor.group_get(ctx, id)

    # group = conductor.group_update(ctx, group, {"status": "Deleting"})
    # LOG.info(g.format_group_status(group))

    # plugin = plugin_base.PLUGINS.get_plugin(cluster.plugin_name)
    # plugin.on_terminate_cluster(cluster)
    # INFRA.shutdown_cluster(cluster)
    # if CONF.use_identity_api_v3:
    #     trusts.delete_trust(group)
    conductor.group_destroy(ctx, group)


def group_update(id, data):
    ctx = context.ctx()
    group = conductor.group_get(ctx, id)

    try:
        group = conductor.group_update(ctx, group,
                                          {"status": "Validating"})
        LOG.info(g.format_group_status(group))
    except Exception:
        with excutils.save_and_reraise_exception():
            #g.clean_cluster_from_empty_ng(cluster)
            group = conductor.group_update(ctx, group, {"status": "Active"})
            LOG.info(g.format_group_status(group))

    return conductor.group_get(ctx, id)


def group_assignment(id, data):
    ctx = context.ctx()
    tenant_id = ctx.tenant_id
    group = conductor.group_get(ctx, id)

    data['group_id'] = group.id
    data['target_id'] = tenant_id

    # LOG.info("data = %s", data)
    # raw_input("group_assignment")

    assignment = conductor.assignment_create(ctx, data)

    # LOG.info("tenant_id = %s", tenant_id)
    # LOG.info("group = %s", group)
    #
    # raw_input("group_assignment")

    # try:
    #     group = conductor.assignmnet_create(ctx, group,
    #                                       {"status": "Validating"})
    #     LOG.info(g.format_group_status(group))
    # except Exception:
    #     with excutils.save_and_reraise_exception():
    #         #g.clean_cluster_from_empty_ng(cluster)
    #         group = conductor.group_update(ctx, group, {"status": "Active"})
    #         LOG.info(g.format_group_status(group))

    # return conductor.assignment_get(ctx, id)
    return assignment


def get_group_pools(group_id):
    all_pools = get_pools()
    pools = []
    for pool in all_pools:
        if group_id in pool.vdi_group:
            pools.append(pool)
    return pools


def get_domain_pools(domain_id):
    all_pools = get_pools()
    pools = []
    for pool in all_pools:
        if pool.domain_id:
            if pool.domain_id in domain_id :
                pools.append(pool)
    return pools


## Group Membership ops

def get_group_memberships():
    return conductor.group_membership_get_all(context.ctx())


def group_membership(values):

    # LOG.info("value = %s", values)

    ctx = context.ctx()
    membership = conductor.group_membership_create(ctx, values)

    # # validating image
    # try:
    #     image = conductor.image_update(ctx, image, {"status": "Active"})
    #     # group = conductor.group_update(ctx, group, {"status": "Validating"})
    #     LOG.info(g.format_image_status(image))
    # except Exception as e:
    #     with excutils.save_and_reraise_exception():
    #         image = conductor.image_update(ctx, image,
    #                                        {"status": "Error",
    #                                        "status_description": str(e)})
    #         LOG.info(g.format_image_status(image))

    # return conductor.image_get(ctx, image.id)
    return membership


def get_user_groups(user_id):
    memberships = conductor.group_membership_get_all(context.ctx(), user_id=user_id)
    all_groups = get_groups()
    group_ids = [m.group_id for m in memberships]
    groups = []
    for group in all_groups:
        if group.id in group_ids:
            groups.append(group)
    return groups


def get_domain_groups(domain_id):
    all_groups = get_groups()
    groups = []
    for group in all_groups:
        if  group.domain_id:
            if group.domain_id in domain_id:
                groups.append(group)
    return groups


## Image ops

def get_images(group_id):
    # LOG.debug("get_groups called.")
    # 06-12-2014 - Ching Sun, add querying string for group_id
    if group_id:
        kwargs = {"group_id": group_id}
        return conductor.image_get_all(context.ctx(), **kwargs)
    else:
        return conductor.image_get_all(context.ctx())


def get_image(id):
    # LOG.debug("get_groups(id) called.")
    return conductor.image_get(context.ctx(), id)


def update_image(id, data):
    ctx = context.ctx()
    image = conductor.image_get(ctx, id)

    try:
        image = conductor.group_image(ctx, image, data)
        #group = conductor.group_update(ctx, group, {"status": "Validating", "name": "Test1111"})
        LOG.info(g.format_image_status(image))
    except Exception:
        with excutils.save_and_reraise_exception():
            image = conductor.image_update(ctx, image, {"status": "Active"})
            LOG.info(g.format_image_status(image))

    return conductor.image_get(ctx, id)


def create_image(values):
    ctx = context.ctx()
    image = conductor.image_create(ctx, values)

    # validating image
    try:
        image = conductor.image_update(ctx, image, {"status": "Active"})
        # group = conductor.group_update(ctx, group, {"status": "Validating"})
        LOG.info(g.format_image_status(image))
    except Exception as e:
        with excutils.save_and_reraise_exception():
            image = conductor.image_update(ctx, image,
                                           {"status": "Error",
                                           "status_description": str(e)})
            LOG.info(g.format_image_status(image))

    return conductor.image_get(ctx, image.id)


def delete_image(id):
    ctx = context.ctx()
    image = conductor.image_get(ctx, id)

    # group = conductor.group_update(ctx, group, {"status": "Deleting"})
    # LOG.info(g.format_group_status(group))

    # plugin = plugin_base.PLUGINS.get_plugin(cluster.plugin_name)
    # plugin.on_terminate_cluster(cluster)
    # INFRA.shutdown_cluster(cluster)
    # if CONF.use_identity_api_v3:
    #     trusts.delete_trust(group)
    conductor.image_destroy(ctx, image)


def image_update(id, data):
   ctx = context.ctx()

   image = conductor.image_get(ctx, id)

   try:
       image = conductor.group_update(ctx, image,
                                          {"status": "Validating"})
       LOG.info(g.format_image_status(image))
   except Exception:
       with excutils.save_and_reraise_exception():
           #g.clean_cluster_from_empty_ng(cluster)
           image = conductor.group_update(ctx, image,
                                              {"status": "Active"})
           LOG.info(g.format_group_status(image))

   return conductor.image_get(ctx, id)


## Pool ops

def get_pools():
    return conductor.pool_get_all(context.ctx())


def get_pool(id):
    return conductor.pool_get(context.ctx(), id)


def update_pool(id, data):
    ctx = context.ctx()
    pool = conductor.pool_get(ctx, id)

    try:
        pool = conductor.pool_update(ctx, pool, data)
        LOG.info(g.format_pool_status(pool))
    except Exception:
        with excutils.save_and_reraise_exception():
            pool = conductor.pool_update(ctx, pool, {"status": "Active"})
            LOG.info(g.format_pool_status(pool))

    return conductor.pool_get(ctx, id)


def create_pool(values):
    ctx = context.ctx()
    pool = conductor.pool_create(ctx, values)

    # print pool, ctx
    # raw_input("service-api-create-pool")

    # validating pool
    try:
        pool = conductor.pool_update(ctx, pool, {"status": "Active"})
        # group = conductor.group_update(ctx, group, {"status": "Validating"})
        LOG.info(g.format_pool_status(pool))
    except Exception as e:
        with excutils.save_and_reraise_exception():
            pool = conductor.pool_update(ctx, pool,
                                               {"status": "Error",
                                                "status_description": str(e)})
            LOG.info(g.format_pool_status(pool))

    return conductor.pool_get(ctx, pool.id)


def terminate_pool(id):
    ctx = context.ctx()
    pool = conductor.pool_get(ctx, id)

    # group = conductor.group_update(ctx, group, {"status": "Deleting"})
    # LOG.info(g.format_group_status(group))

    # plugin = plugin_base.PLUGINS.get_plugin(cluster.plugin_name)
    # plugin.on_terminate_cluster(cluster)
    # INFRA.shutdown_cluster(cluster)
    # if CONF.use_identity_api_v3:
    #     trusts.delete_trust(group)
    conductor.pool_destroy(ctx, pool)


def pool_update(id, data):
    ctx = context.ctx()
    pool = conductor.pool_get(ctx, id)

    try:
        pool = conductor.group_update(ctx, pool,
                                          {"status": "Validating"})
        LOG.info(g.format_pool_status(pool))
    except Exception:
        with excutils.save_and_reraise_exception():
            #g.clean_cluster_from_empty_ng(cluster)
            pool = conductor.pool_update(ctx, pool, {"status": "Active"})
            LOG.info(g.format_pool_status(pool))

    return conductor.pool_get(ctx, id)


## Cluster ops

def get_clusters():
    return conductor.cluster_get_all(context.ctx())


def get_cluster(id):
    return conductor.cluster_get(context.ctx(), id)


def scale_cluster(id, data):
    ctx = context.ctx()

    cluster = conductor.cluster_get(ctx, id)
    plugin = plugin_base.PLUGINS.get_plugin(cluster.plugin_name)
    existing_node_groups = data.get('resize_node_groups', [])
    additional_node_groups = data.get('add_node_groups', [])

    #the next map is the main object we will work with
    #to_be_enlarged : {node_group_id: desired_amount_of_instances}
    to_be_enlarged = {}
    for ng in existing_node_groups:
        ng_id = g.find(cluster.node_groups, name=ng['name'])['id']
        to_be_enlarged.update({ng_id: ng['count']})

    additional = construct_ngs_for_scaling(cluster, additional_node_groups)
    cluster = conductor.cluster_get(ctx, cluster)

    # update nodegroup image usernames
    for nodegroup in cluster.node_groups:
        if additional.get(nodegroup.id):
            image_username = INFRA.get_node_group_image_username(nodegroup)
            conductor.node_group_update(
                ctx, nodegroup, {"image_username": image_username})
    cluster = conductor.cluster_get(ctx, cluster)

    try:
        cluster = conductor.cluster_update(ctx, cluster,
                                           {"status": "Validating"})
        LOG.info(g.format_cluster_status(cluster))
        plugin.validate_scaling(cluster, to_be_enlarged, additional)
    except Exception:
        with excutils.save_and_reraise_exception():
            g.clean_cluster_from_empty_ng(cluster)
            cluster = conductor.cluster_update(ctx, cluster,
                                               {"status": "Active"})
            LOG.info(g.format_cluster_status(cluster))

    # If we are here validation is successful.
    # So let's update to_be_enlarged map:
    to_be_enlarged.update(additional)

    for node_group in cluster.node_groups:
        if node_group.id not in to_be_enlarged:
            to_be_enlarged[node_group.id] = node_group.count

    context.spawn("cluster-scaling-%s" % id,
                  _provision_scaled_cluster, id, to_be_enlarged)
    return conductor.cluster_get(ctx, id)


def create_cluster(values):
    ctx = context.ctx()
    cluster = conductor.cluster_create(ctx, values)
    plugin = plugin_base.PLUGINS.get_plugin(cluster.plugin_name)

    # update nodegroup image usernames
    for nodegroup in cluster.node_groups:
        conductor.node_group_update(
            ctx, nodegroup,
            {"image_username": INFRA.get_node_group_image_username(nodegroup)})
    cluster = conductor.cluster_get(ctx, cluster)

    # validating cluster
    try:
        cluster = conductor.cluster_update(ctx, cluster,
                                           {"status": "Validating"})
        LOG.info(g.format_cluster_status(cluster))

        plugin.validate(cluster)
    except Exception as e:
        with excutils.save_and_reraise_exception():
            cluster = conductor.cluster_update(ctx, cluster,
                                               {"status": "Error",
                                                "status_description": str(e)})
            LOG.info(g.format_cluster_status(cluster))

    context.spawn("cluster-creating-%s" % cluster.id,
                  _provision_cluster, cluster.id)
    if CONF.use_identity_api_v3 and cluster.is_transient:
        trusts.create_trust(cluster)

    return conductor.cluster_get(ctx, cluster.id)


def _provision_scaled_cluster(id, node_group_id_map):
    ctx = context.ctx()
    cluster = conductor.cluster_get(ctx, id)
    plugin = plugin_base.PLUGINS.get_plugin(cluster.plugin_name)

    # Decommissioning surplus nodes with the plugin

    cluster = conductor.cluster_update(ctx, cluster,
                                       {"status": "Decommissioning"})
    LOG.info(g.format_cluster_status(cluster))

    instances_to_delete = []

    for node_group in cluster.node_groups:
        new_count = node_group_id_map[node_group.id]
        if new_count < node_group.count:
            instances_to_delete += node_group.instances[new_count:
                                                        node_group.count]

    if instances_to_delete:
        plugin.decommission_nodes(cluster, instances_to_delete)

    # Scaling infrastructure
    cluster = conductor.cluster_update(ctx, cluster, {"status": "Scaling"})
    LOG.info(g.format_cluster_status(cluster))

    instances = INFRA.scale_cluster(cluster, node_group_id_map)

    # Setting up new nodes with the plugin

    if instances:
        cluster = conductor.cluster_update(ctx, cluster,
                                           {"status": "Configuring"})
        LOG.info(g.format_cluster_status(cluster))
        try:
            instances = g.get_instances(cluster, instances)
            plugin.scale_cluster(cluster, instances)
        except Exception as ex:
            LOG.exception("Can't scale cluster '%s' (reason: %s)",
                          cluster.name, ex)
            cluster = conductor.cluster_update(ctx, cluster,
                                               {"status": "Error"})
            LOG.info(g.format_cluster_status(cluster))
            return

    cluster = conductor.cluster_update(ctx, cluster, {"status": "Active"})
    LOG.info(g.format_cluster_status(cluster))


def _provision_cluster(cluster_id):
    ctx = context.ctx()
    cluster = conductor.cluster_get(ctx, cluster_id)
    plugin = plugin_base.PLUGINS.get_plugin(cluster.plugin_name)

    # updating cluster infra
    cluster = conductor.cluster_update(ctx, cluster,
                                       {"status": "InfraUpdating"})
    LOG.info(g.format_cluster_status(cluster))
    plugin.update_infra(cluster)

    # creating instances and configuring them
    cluster = conductor.cluster_get(ctx, cluster_id)
    INFRA.create_cluster(cluster)

    # configure cluster
    cluster = conductor.cluster_update(ctx, cluster, {"status": "Configuring"})
    LOG.info(g.format_cluster_status(cluster))
    try:
        plugin.configure_cluster(cluster)
    except Exception as ex:
        LOG.exception("Can't configure cluster '%s' (reason: %s)",
                      cluster.name, ex)
        cluster = conductor.cluster_update(ctx, cluster, {"status": "Error"})
        LOG.info(g.format_cluster_status(cluster))
        return

    # starting prepared and configured cluster
    cluster = conductor.cluster_update(ctx, cluster, {"status": "Starting"})
    LOG.info(g.format_cluster_status(cluster))
    try:
        plugin.start_cluster(cluster)
    except Exception as ex:
        LOG.exception("Can't start services for cluster '%s' (reason: %s)",
                      cluster.name, ex)
        cluster = conductor.cluster_update(ctx, cluster, {"status": "Error"})
        LOG.info(g.format_cluster_status(cluster))
        return

    # cluster is now up and ready
    cluster = conductor.cluster_update(ctx, cluster, {"status": "Active"})
    LOG.info(g.format_cluster_status(cluster))

    # schedule execution pending job for cluster
    for je in conductor.job_execution_get_all(ctx, cluster_id=cluster.id):
        jm.run_job(je)


def terminate_cluster(id):
    ctx = context.ctx()
    cluster = conductor.cluster_get(ctx, id)

    cluster = conductor.cluster_update(ctx, cluster, {"status": "Deleting"})
    LOG.info(g.format_cluster_status(cluster))

    plugin = plugin_base.PLUGINS.get_plugin(cluster.plugin_name)
    plugin.on_terminate_cluster(cluster)
    INFRA.shutdown_cluster(cluster)
    if CONF.use_identity_api_v3:
        trusts.delete_trust(cluster)
    conductor.cluster_destroy(ctx, cluster)


## ClusterTemplate ops

def get_cluster_templates():
    return conductor.cluster_template_get_all(context.ctx())


def get_cluster_template(id):
    return conductor.cluster_template_get(context.ctx(), id)


def create_cluster_template(values):
    return conductor.cluster_template_create(context.ctx(), values)


def terminate_cluster_template(id):
    return conductor.cluster_template_destroy(context.ctx(), id)


## NodeGroupTemplate ops

def get_node_group_templates():
    return conductor.node_group_template_get_all(context.ctx())


def get_node_group_template(id):
    return conductor.node_group_template_get(context.ctx(), id)


def create_node_group_template(values):
    return conductor.node_group_template_create(context.ctx(), values)


def terminate_node_group_template(id):
    return conductor.node_group_template_destroy(context.ctx(), id)


## Plugins ops

def get_plugins():
    return plugin_base.PLUGINS.get_plugins(
        base=provisioning.ProvisioningPluginBase)


def get_plugin(plugin_name, version=None):
    plugin = plugin_base.PLUGINS.get_plugin(plugin_name)
    if plugin:
        res = plugin.as_resource()
        if version:
            if version in plugin.get_versions():
                configs = plugin.get_configs(version)
                res._info['configs'] = [c.dict for c in configs]
                processes = plugin.get_node_processes(version)
                res._info['node_processes'] = processes
                required_image_tags = plugin.get_required_image_tags(version)
                res._info['required_image_tags'] = required_image_tags
            else:
                return None
        return res


def convert_to_cluster_template(plugin_name, version, template_name,
                                config_file):
    plugin = plugin_base.PLUGINS.get_plugin(plugin_name)
    return plugin.convert(config_file, plugin_name, version,
                          urlparse.unquote(template_name),
                          conductor.cluster_template_create)


def construct_ngs_for_scaling(cluster, additional_node_groups):
    ctx = context.ctx()
    additional = {}
    for ng in additional_node_groups:
        count = ng['count']
        ng['count'] = 0
        ng_id = conductor.node_group_add(ctx, cluster, ng)
        additional.update({ng_id: count})
    return additional

## Image Registry


# def get_images(tags):
#     return nova.client().images.list_registered(tags)
#
#
# def get_image(**kwargs):
#     if len(kwargs) == 1 and 'id' in kwargs:
#         return nova.client().images.get(kwargs['id'])
#     else:
#         return nova.client().images.find(**kwargs)
#
#
# def register_image(image_id, username, description=None):
#     client = nova.client()
#     client.images.set_description(image_id, username, description)
#     return client.images.get(image_id)
#
#
# def unregister_image(image_id):
#     client = nova.client()
#     client.images.unset_description(image_id)
#     return client.images.get(image_id)
#
#
# def add_image_tags(image_id, tags):
#     client = nova.client()
#     client.images.tag(image_id, tags)
#     return client.images.get(image_id)
#
#
# def remove_image_tags(image_id, tags):
#     client = nova.client()
#     client.images.untag(image_id, tags)
#     return client.images.get(image_id)


    ## VMs

def get_VMs():
    return conductor.VM_get_all(context.ctx())
        
def get_VM(id):
        LOG.debug("get_vm(id) called.")
        pass


def create_VM(values):
    ctx = context.ctx()
    vm = conductor.VM_create(ctx, values)

    # validating VM
    try:
        vm = conductor.VM_update(ctx, vm, {"status": "Active"})
        LOG.info(g.format_VM_status(vm))
    except Exception as e:
        with excutils.save_and_reraise_exception():
            vm = conductor.VM_update(ctx, vm, {"status": "Error",
                                               "status_description": str(e)})

    return conductor.VM_get(ctx, vm.id)


def update_VM(id, data):
    ctx = context.ctx()
    vm = conductor.VM_get(ctx, id)
   
    try:
        vm = conductor.VM_update(ctx, vm, data)
        LOG.info(g.format_VM_status(vm))
    except Exception:
        with excutils.save_and_reraise_exception():
            vm = conductor.VM_update(ctx, vm, {"status": "Active"})
            LOG.info(g.format_VM_status(vm))

    return conductor.VM_get(ctx, id)


    # Sites

def get_sites():
    LOG.debug("get_Sites called.")
    return conductor.Site_get_all(context.ctx())
        
def get_Site(id):
        LOG.debug("get_site(id) called.")
        pass


def create_site(values):
    # LOG.debug("create_site called. values = %s", values)

    ctx = context.ctx()
    Site = conductor.site_create(ctx, 0, values) # need to provide site id ???

    # validating Site
    try:
        site = conductor.site_update(ctx, Site, {"status": "Validating"})
    except Exception as e:
        with excutils.save_and_reraise_exception():
            Site = conductor.site_update(ctx, site,
                                    {"status": "Error",
                                    "status_description": str(e)})

    LOG.debug("create_site - conductor=%s", conductor)

    return conductor.site_get(ctx, Site.id)



def site_update(id, data):
   ctx = context.ctx()

   site = conductor.Site_get(ctx, id)
   
   try:
       site = conductor.Site_update(ctx, site,
                                          {"status": "Validating"})
       LOG.info(g.format_site_status(site))
   except Exception:
       with excutils.save_and_reraise_exception():
           #g.clean_cluster_from_empty_ng(cluster)
           Site = conductor.Site_update(ctx, site,
                                              {"status": "Active"})
           LOG.info(g.format_site_status(Site))

   return conductor.Site_get(ctx, id)

    # Users

def get_Users():
    LOG.debug("get_Users called.")
    return conductor.User_get_all(context.ctx())
        
def get_User(id):
        LOG.debug("get_user(id) called.")
        pass


def create_user(values):
    # LOG.debug("create_User called. values = %s", values)
    # this needs to call into Keystone

    ctx = context.ctx()
    User = conductor.user_create(ctx, values)

    # validating User
    try:
        User = conductor.user_update(ctx, User, {"status": "Validating"})
    except Exception as e:
        with excutils.save_and_reraise_exception():
            User = conductor.user_update(ctx, User,
                                    {"status": "Error",
                                    "status_description": str(e)})

    LOG.debug("create_User - conductor=%s", conductor)

    return conductor.User_get(ctx, User.id)



def user_update(id, data):
   ctx = context.ctx()

   user = conductor.User_get(ctx, id)
   
   try:
       user = conductor.User_update(ctx, user,
                                          {"status": "Validating"})
       LOG.info(g.format_User_status(user))
   except Exception:
       with excutils.save_and_reraise_exception():
           #g.clean_cluster_from_empty_ng(cluster)
           User = conductor.User_update(ctx, user,
                                              {"status": "Active"})
           LOG.info(g.format_user_status(User))

   return conductor.User_get(ctx, id)
