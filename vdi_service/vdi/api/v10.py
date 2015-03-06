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

import flask

import vdi.api.base as b
from vdi.openstack.common import log as logging
from vdi.service import api
from vdi.service import validation as v
from vdi.service.validations import cluster_templates as v_ct
from vdi.service.validations import clusters as v_c
from vdi.service.validations import clusters_scaling as v_c_s
from vdi.service.validations import images as v_images
from vdi.service.validations import node_group_templates as v_ngt
from vdi.service.validations import plugins as v_p
import vdi.utils.api as u


LOG = logging.getLogger(__name__)

rest = u.Rest('v10', __name__)


# @rest.get('/list')
# def list_():
#     user_list = ["user1", "user2"]
#     print 'v10 list'
#     return u.render(list=user_list)


## VM ops

# @rest.get('/vms')
# def VMs_list():
#     # return u.render(vms=[v.to_dict() for v in api.get_VMs()])
#     return u.render(test = "get VMs OK!")

# @rest.post('/vms')
# def VM_create(data):
#     # LOG.debug("post_VMs called!")
#     return u.render(test = "post VMs OK!")

    # return u.render(api.create_VM(data).to_wrapped_dict())

# how do I add a VM to a group, how to start, pause, reboot, shutdown one?


## site ops
# a VDI site might have multiple web sites for different groups, for now let's first assume just one site
# @rest.get('/sites')
# def sites_list():
#     # return u.render(sites = [v.to_dict() for v in api.get_sites()])
#     return u.render(test = "get sites OK!")
#
# @rest.post('/sites')
# def site_create(data):
#     # LOG.debug("post_VMs called!")
#     # return u.render(api.create_site(data).to_wrapped_dict())
#     return u.render(test = "post sites OK!")


## user ops
# a VDI site might have multiple web sites for different groups, for now let's first assume just one site
# @rest.get('/users')
# def users_list():
#     # return u.render(users = [v.to_dict() for v in api.get_users()])
#     return u.render(test = "get users OK!")
#
#
# @rest.post('/users')
# def user_create(data):
#     # return u.render(api.create_user(data).to_wrapped_dict())
#     return u.render(test = "post users OK!")


## Group ops

@rest.get('/groups')
def groups_list():
    return u.render(groups=[g.to_dict() for g in api.get_groups()])


@rest.post('/groups')
# @v.validate(v_c.GROUP_SCHEMA, v_c.check_group_create)
def groups_create(data):
    return u.render(api.create_group(data).to_wrapped_dict())


@rest.put('/groups/<group_id>')
@v.check_exists(api.get_group, 'group_id')
# @v.validate(v_c_s.CLUSTER_SCALING_SCHEMA, v_c_s.check_cluster_scaling)
def groups_update(group_id, data):
    return u.render(api.update_group(group_id, data).to_wrapped_dict())


@rest.get('/groups/<group_id>')
@v.check_exists(api.get_group, 'group_id')
def groups_get(group_id):
    return u.render(api.get_group(group_id).to_wrapped_dict())


@rest.delete('/groups/<group_id>')
@v.check_exists(api.get_group, 'group_id')
def groups_delete(group_id):
    api.terminate_group(group_id)
    return u.render()


@rest.put('/groups/<group_id>')
@v.check_exists(api.get_group, 'group_id')
def group_update(group_id, data):
    return u.render(api.group_update(group_id, data).to_wrapped_dict())


@rest.put('/users/<user_id>/groups/<group_id>')
@v.check_exists(api.get_group, 'group_id')
def create_membership(user_id, group_id, data):
    # LOG.info("user_id = %s", user_id)
    # LOG.info("group_id = %s", group_id)
    # import pdb; pdb.set_trace()
    data = {'user_id': user_id,
            'group_id': group_id}
    return u.render(api.group_membership(data).to_wrapped_dict())


@rest.get('/users/<user_id>/groups')
def user_groups_list(user_id):
    return u.render(groups=[g.to_dict() for g in api.get_user_groups(user_id)])
    # return u.render(groups=[g.to_dict() for g in api.get_group_memberships()])


@rest.get('/domains/<domain_id>/groups')
def domain_groups_list(domain_id):
    return u.render(groups=[g.to_dict() for g in api.get_domain_groups(domain_id)])


## Image ops

@rest.get('/images')
def images_list():
    # 06-12-2014 - Ching Sun, extract querying string for group_id
    group_id = flask.request.args.get("group_id", None)
    LOG.debug("group_id = %s", group_id)
    return u.render(images=[i.to_dict() for i in api.get_images(group_id)])


@rest.post('/images')
# @v.validate(v_c.GROUP_SCHEMA, v_c.check_group_create)
def images_create(data):
    return u.render(api.create_image(data).to_wrapped_dict())


@rest.put('/images/<group_id>')
@v.check_exists(api.get_group, 'group_id')
# @v.validate(v_c_s.CLUSTER_SCALING_SCHEMA, v_c_s.check_cluster_scaling)
def images_update(image_id, data):
    return u.render(api.update_image(image_id, data).to_wrapped_dict())


@rest.get('/images/<image_id>')
@v.check_exists(api.get_group, 'image_id')
def images_get(image_id):
    return u.render(api.get_image(image_id).to_wrapped_dict())


@rest.delete('/images/<image_id>')
@v.check_exists(api.get_image, 'image_id')
def images_delete(image_id):
    api.delete_image(image_id)
    return u.render()


@rest.put('/images/<image_id>')
@v.check_exists(api.get_image, 'image_id')
def image_update(image_id, data):
    return u.render(api.group_update(image_id, data).to_wrapped_dict())


## Pool ops

@rest.get('/pools')
def pools_list():
    return u.render(pools=[g.to_dict() for g in api.get_pools()])


@rest.post('/pools')
def pools_create(data):
    return u.render(api.create_pool(data).to_wrapped_dict())


@rest.put('/pools/<pool_id>')
@v.check_exists(api.get_pool, 'pool_id')
def pools_update(pool_id, data):
    return u.render(api.update_pool(pool_id, data).to_wrapped_dict())


@rest.get('/pools/<pool_id>')
@v.check_exists(api.get_pool, 'pool_id')
def pools_get(pool_id):
    return u.render(api.get_pool(pool_id).to_wrapped_dict())


@rest.delete('/pools/<pool_id>')
@v.check_exists(api.get_pool, 'pool_id')
def pools_delete(pool_id):
    api.terminate_pool(pool_id)
    return u.render()


@rest.put('/pools/<pool_id>')
@v.check_exists(api.get_pool, 'pool_id')
def pool_update(pool_id, data):
  return u.render(api.pool_update(pool_id, data).to_wrapped_dict())


@rest.get('/groups/<group_id>/pools')
def group_pools_list(group_id):
    return u.render(pools=[p.to_dict() for p in api.get_group_pools(group_id)])


@rest.get('/domains/<domain_id>/pools')
def domain_pools_list(domain_id):
    return u.render(pools=[p.to_dict() for p in api.get_domain_pools(domain_id)])


## Cluster ops

# @rest.get('/clusters')
# def clusters_list():
#     return u.render(clusters=[c.to_dict() for c in api.get_clusters()])
#
#
# @rest.post('/clusters')
# @v.validate(v_c.CLUSTER_SCHEMA, v_c.check_cluster_create)
# def clusters_create(data):
#     LOG.debug("post_clusters")
#     return u.render(api.create_cluster(data).to_wrapped_dict())
#
#
# @rest.put('/clusters/<cluster_id>')
# @v.check_exists(api.get_cluster, 'cluster_id')
# @v.validate(v_c_s.CLUSTER_SCALING_SCHEMA, v_c_s.check_cluster_scaling)
# def clusters_scale(cluster_id, data):
#     return u.render(api.scale_cluster(cluster_id, data).to_wrapped_dict())
#
#
# @rest.get('/clusters/<cluster_id>')
# @v.check_exists(api.get_cluster, 'cluster_id')
# def clusters_get(cluster_id):
#     return u.render(api.get_cluster(cluster_id).to_wrapped_dict())
#
#
# @rest.delete('/clusters/<cluster_id>')
# @v.check_exists(api.get_cluster, 'cluster_id')
# def clusters_delete(cluster_id):
#     api.terminate_cluster(cluster_id)
#     return u.render()


## ClusterTemplate ops

# @rest.get('/cluster-templates')
# def cluster_templates_list():
#     return u.render(
#         cluster_templates=[t.to_dict() for t in api.get_cluster_templates()])
#
#
# @rest.post('/cluster-templates')
# @v.validate(v_ct.CLUSTER_TEMPLATE_SCHEMA, v_ct.check_cluster_template_create)
# def cluster_templates_create(data):
#     return u.render(api.create_cluster_template(data).to_wrapped_dict())
#
#
# @rest.get('/cluster-templates/<cluster_template_id>')
# @v.check_exists(api.get_cluster_template, 'cluster_template_id')
# def cluster_templates_get(cluster_template_id):
#     return u.render(
#         api.get_cluster_template(cluster_template_id).to_wrapped_dict())
#
#
# @rest.put('/cluster-templates/<cluster_template_id>')
# @v.check_exists(api.get_cluster_template, 'cluster_template_id')
# def cluster_templates_update(cluster_template_id, data):
#     return b.not_implemented()
#
#
# @rest.delete('/cluster-templates/<cluster_template_id>')
# @v.check_exists(api.get_cluster_template, 'cluster_template_id')
# @v.validate(None, v_ct.check_cluster_template_usage)
# def cluster_templates_delete(cluster_template_id):
#     api.terminate_cluster_template(cluster_template_id)
#     return u.render()


## NodeGroupTemplate ops

# @rest.get('/node-group-templates')
# def node_group_templates_list():
#     return u.render(
#         node_group_templates=[t.to_dict()
#                               for t in api.get_node_group_templates()])
#
#
# @rest.post('/node-group-templates')
# @v.validate(v_ngt.NODE_GROUP_TEMPLATE_SCHEMA,
#             v_ngt.check_node_group_template_create)
# def node_group_templates_create(data):
#     return u.render(api.create_node_group_template(data).to_wrapped_dict())
#
#
# @rest.get('/node-group-templates/<node_group_template_id>')
# @v.check_exists(api.get_node_group_template, 'node_group_template_id')
# def node_group_templates_get(node_group_template_id):
#     return u.render(
#         api.get_node_group_template(node_group_template_id).to_wrapped_dict())
#
#
# @rest.put('/node-group-templates/<node_group_template_id>')
# @v.check_exists(api.get_node_group_template, 'node_group_template_id')
# def node_group_templates_update(node_group_template_id, data):
#     return b.not_implemented()
#
#
# @rest.delete('/node-group-templates/<node_group_template_id>')
# @v.check_exists(api.get_node_group_template, 'node_group_template_id')
# @v.validate(None, v_ngt.check_node_group_template_usage)
# def node_group_templates_delete(node_group_template_id):
#     api.terminate_node_group_template(node_group_template_id)
#     return u.render()


## Plugins ops

# @rest.get('/plugins')
# def plugins_list():
#     return u.render(plugins=[p.dict for p in api.get_plugins()])
#
#
# @rest.get('/plugins/<plugin_name>')
# @v.check_exists(api.get_plugin, plugin_name='plugin_name')
# def plugins_get(plugin_name):
#     return u.render(api.get_plugin(plugin_name).wrapped_dict)
#
#
# @rest.get('/plugins/<plugin_name>/<version>')
# @v.check_exists(api.get_plugin, plugin_name='plugin_name', version='version')
# def plugins_get_version(plugin_name, version):
#     return u.render(api.get_plugin(plugin_name, version).wrapped_dict)
#
#
# @rest.post_file('/plugins/<plugin_name>/<version>/convert-config/<name>')
# @v.check_exists(api.get_plugin, plugin_name='plugin_name', version='version')
# @v.validate(v_p.CONVERT_TO_TEMPLATE_SCHEMA, v_p.check_convert_to_template)
# def plugins_convert_to_cluster_template(plugin_name, version, name, data):
#     return u.render(api.convert_to_cluster_template(plugin_name,
#                                                     version,
#                                                     name,
#                                                     data).to_wrapped_dict())


## Image Registry ops

# @rest.get('/images')
# def images_list():
#     tags = u.get_request_args().getlist('tags')
#     return u.render(images=[i.dict for i in api.get_images(tags)])
#
#
# @rest.get('/images/<image_id>')
# @v.check_exists(api.get_image, id='image_id')
# def images_get(image_id):
#     return u.render(api.get_image(id=image_id).wrapped_dict)
#
#
# @rest.post('/images/<image_id>')
# @v.check_exists(api.get_image, id='image_id')
# @v.validate(v_images.image_register_schema, v_images.check_image_register)
# def images_set(image_id, data):
#     return u.render(api.register_image(image_id, **data).wrapped_dict)
#
#
# @rest.delete('/images/<image_id>')
# @v.check_exists(api.get_image, id='image_id')
# def images_unset(image_id):
#     api.unregister_image(image_id)
#     return u.render()
#
#
# @rest.post('/images/<image_id>/tag')
# @v.check_exists(api.get_image, id='image_id')
# @v.validate(v_images.image_tags_schema, v_images.check_tags)
# def image_tags_add(image_id, data):
#     return u.render(api.add_image_tags(image_id, **data).wrapped_dict)
#
#
# @rest.post('/images/<image_id>/untag')
# @v.check_exists(api.get_image, id='image_id')
# @v.validate(v_images.image_tags_schema)
# def image_tags_delete(image_id, data):
#     return u.render(api.remove_image_tags(image_id, **data).wrapped_dict)


## VM ops

@rest.get('/VMs')
def VMs_list():
    return u.render(vms=[v.to_dict() for v in api.get_VMs()])


@rest.post('/VMs')
def VM_create(data):
    return u.render(api.create_VM(data).to_wrapped_dict())


# how do I add a VM to a group, how to start, pause, reboot, shutdown one?
@rest.put('/VMs/<VM_id>')
@v.check_exists(api.get_VM, 'VM_id')
def VM_update(VM_id, data):
  return u.render(api.VM_update(VM_id, data).to_wrapped_dict())


    ## site ops
    # a VDI site might have multiple web sites for different groups, for now let's first assume just one site
@rest.get('/Sites')
def Sites_list():
    return u.render(sites = [v.to_dict() for v in api.get_sites()])


@rest.post('/Sites')
def Site_create(data):
    # LOG.debug("post_Lists called!")
    return u.render(api.create_site(data).to_wrapped_dict())


@rest.put('/Sites/<Site_id>')
@v.check_exists(api.get_Site, 'Site_id')
def Site_update(Site_id, data):
   return u.render(api.Site_update(Site_id, data).to_wrapped_dict())


    ## user ops
    # a VDI site might have multiple web sites for different groups, for now let's first assume just one site
@rest.get('/Users')
def Users_list():
    return u.render(users = [v.to_dict() for v in api.get_Users()])


@rest.post('/Users')
def User_create(data):
    return u.render(api.create_user(data).to_wrapped_dict())


@rest.put('/Users/<User_id>')
@v.check_exists(api.get_User, 'User_id')
def User_update(User_id, data):
   return u.render(api.User_update(User_id, data).to_wrapped_dict())

# Roles, a user is desinated as full admin, tenant admin, or a site admin
# How do we do it?
# do I need to make role part of user or seperate?


# Security Group
# a security group or template that allows different sites or VMs. 

