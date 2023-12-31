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

"""This module contains description of objects returned by the
conductor.

The actual objects returned are located in resource.py, which aim
is to hide some necessary magic. Current module describes objects
fields via docstrings and contains implementation of helper methods.
"""

from oslo.config import cfg

from vdi.utils import configs
from vdi.utils import remote


CONF = cfg.CONF
CONF.import_opt('node_domain', 'vdi.config')


class Group(object):
    """An object representing Group.

    id
    name
    description
    tenant_id
    trust_id
    is_transient
    plugin_name
    cluster_configs - configs dict converted to object,
                      see the docs for details
    default_image_id
    anti_affinity
    management_private_key
    management_public_key
    user_keypair_id
    status
    status_description
    info
    extra
    """


class Assignment(object):
    """An object representing Assignment.

    type
    actor_id
    target_id
    group_id
    inherited
    """


class Image(object):
    """An object representing Group.

    id
    name
    description
    tenant_id
    trust_id
    is_transient
    plugin_name
    cluster_configs - configs dict converted to object,
                      see the docs for details
    default_image_id
    anti_affinity
    management_private_key
    management_public_key
    user_keypair_id
    status
    status_description
    info
    extra
    """


class Pool(object):
    """An object representing Pool.

    id
    name
    description
    tenant_id
    trust_id
    is_transient
    plugin_name
    cluster_configs - configs dict converted to object,
                      see the docs for details
    default_image_id
    anti_affinity
    management_private_key
    management_public_key
    user_keypair_id
    status
    status_description
    info
    extra
    """


class Cluster(object):
    """An object representing Cluster.

    id
    name
    description
    tenant_id
    trust_id
    is_transient
    plugin_name
    hadoop_version
    cluster_configs - configs dict converted to object,
                      see the docs for details
    default_image_id
    anti_affinity
    management_private_key
    management_public_key
    user_keypair_id
    status
    status_description
    info
    extra
    node_groups - list of NodeGroup objects
    cluster_template_id
    cluster_template - ClusterTemplate object
    """


class NodeGroup(object):
    """An object representing Node Group.

    id
    name
    flavor_id
    image_id
    image_username
    node_processes - list of node processes
    node_configs - configs dict converted to object,
                   see the docs for details
    volumes_per_node
    volumes_size
    volume_mount_prefix
    floating_ip_pool - Floating IP Pool name used to assign Floating IPs to
                        instances in this Node Group
    count
    instances - list of Instance objects
    node_group_template_id
    node_group_template - NodeGroupTemplate object

    If node group belongs to cluster:
    cluster_id - parent Cluster ID
    cluster - parent Cluster object

    If node group belongs to cluster template:
    cluster_template_id - parent ClusterTemplate ID
    cluster_template - parent ClusterTemplate object
    """

    def configuration(self):
        return configs.merge_configs(self.cluster.cluster_configs,
                                     self.node_configs)

    def storage_paths(self):
        mp = []
        for idx in range(1, self.volumes_per_node + 1):
            mp.append(self.volume_mount_prefix + str(idx))

        # Here we assume that NG's instances use ephemeral
        # drives for storage if volumes_per_node == 0
        if not mp:
            mp = ['/mnt']

        return mp

    def get_image_id(self):
        return self.image_id or self.cluster.default_image_id


class Instance(object):
    """An object representing Instance.

    id
    node_group_id - parent NodeGroup ID
    node_group - parent NodeGroup object
    instance_id - Nova instance ID
    instance_name
    internal_ip
    management_ip
    volumes
    """

    def hostname(self):
        return self.instance_name

    def fqdn(self):
        return self.instance_name + '.' + CONF.node_domain

    def remote(self):
        return remote.get_remote(self)


class ClusterTemplate(object):
    """An object representing Cluster Template.

    id
    name
    description
    cluster_configs - configs dict converted to object,
                      see the docs for details
    default_image_id
    anti_affinity
    tenant_id
    plugin_name
    hadoop_version
    node_groups - list of NodeGroup objects
    """


class NodeGroupTemplate(object):
    """An object representing Node Group Template.

    id
    name
    description
    tenant_id
    flavor_id
    image_id
    plugin_name
    hadoop_version
    node_processes - list of node processes
    node_configs - configs dict converted to object,
                   see the docs for details
    volumes_per_node
    volumes_size
    volume_mount_prefix
    floating_ip_pool
    """


##EDP Objects

class DataSource(object):
    """An object representing Data Source.

    id
    tenant_id
    name
    description
    type
    url
    credentials
    """


class JobExecution(object):
    """An object representing JobExecution

    id
    tenant_id
    job_id
    input_id
    output_id
    start_time
    end_time
    cluster_id
    info
    progress
    oozie_job_id
    return_code
    """


class Job(object):
    """An object representing Job

    id
    tenant_id
    name
    description
    type
    mains
    libs
    """


class JobBinary(object):
    """An object representing JobBinary

    id
    tenant_id
    name
    description
    url -  URLs may be the following: internal-db://URL, swift://
    extra - extra may contain not only user-password but e.g. auth-token
    """


class JobBinaryInternal(object):
    """An object representing JobBinaryInternal

    Note that the 'data' field is not returned. It uses deferred
    loading and must be requested explicitly with the
    job_binary_get_raw_data() conductor method.

    id
    tenant_id
    name
    datasize
    """

class VM(object):
    """An object representing VM.

    id
    name
    description
    tenant_id # do we still need it
    group_id
    default_image_id
    anti_affinity
    management_private_key
    management_public_key
    user_keypair_id
    status
    status_description
    info
    extra
    """

class Site(object):
    """An object representing Site.

    id
    name
    description
    tenant_id 
    anti_affinity
    management_private_key
    management_public_key
    user_keypair_id
    status
    status_description
    info
    extra
    """

class User(object):
    """An object representing User.

    id
    name
    description
    tenant_id 
    group_id
    vm_id
    anti_affinity
    management_private_key
    management_public_key
    user_keypair_id
    status
    status_description
    info
    extra
    """


