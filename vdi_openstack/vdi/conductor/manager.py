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

"""Handles database requests from other Vdi services."""

import copy

from vdi.db import base as db_base
from vdi.utils import configs
from vdi.utils import crypto


ASSIGNMENT_DEFAULTS = {
    # "info": {}
}

GROUP_DEFAULTS = {
    # "info": {}
}

GROUP_MEMBERSHIP_DEFAULTS = {
    # "info": {}
}

IMAGE_DEFAULTS = {
    # "info": {}
}

POOL_DEFAULTS = {
    # "info": {}
}

CLUSTER_DEFAULTS = {
    "cluster_configs": {},
    "status": "undefined",
    "anti_affinity": [],
    "status_description": "",
    "info": {},
}

NODE_GROUP_DEFAULTS = {
    "node_processes": [],
    "node_configs": {},
    "volumes_per_node": 0,
    "volumes_size": 0,
    "volume_mount_prefix": "/volumes/disk",
    "floating_ip_pool": None
}

INSTANCE_DEFAULTS = {
    "volumes": []
}

DATA_SOURCE_DEFAULTS = {
    "credentials": {}
}

VM_DEFAULTS = {
    # "info": {}
}

def _apply_defaults(values, defaults):
    new_values = copy.deepcopy(defaults)
    new_values.update(values)
    return new_values


class ConductorManager(db_base.Base):
    """This class aimed to conduct things.

    The methods in the base API for vdi-conductor are various proxy
    operations that allows other services to get specific work done without
    locally accessing the database.

    Additionally it performs some template-to-object copying magic.
    """

    def __init__(self):
        super(ConductorManager, self).__init__()

    ## Common helpers

    def _populate_node_groups(self, context, cluster):
        node_groups = cluster.get('node_groups')
        if not node_groups:
            return []

        populated_node_groups = []
        for node_group in node_groups:
            populated_node_group = self._populate_node_group(context,
                                                             node_group)
            self._cleanup_node_group(populated_node_group)
            populated_node_group["tenant_id"] = context.tenant_id
            populated_node_groups.append(
                populated_node_group)

        return populated_node_groups

    def _cleanup_node_group(self, node_group):
        node_group.pop('id', None)
        node_group.pop('created_at', None)
        node_group.pop('updated_at', None)

    def _populate_node_group(self, context, node_group):
        node_group_merged = copy.deepcopy(NODE_GROUP_DEFAULTS)

        ng_tmpl_id = node_group.get('node_group_template_id')
        ng_tmpl = None
        if ng_tmpl_id:
            ng_tmpl = self.node_group_template_get(context, ng_tmpl_id)

            self._cleanup_node_group(ng_tmpl)
            node_group_merged.update(ng_tmpl)

        node_group_merged.update(node_group)

        if ng_tmpl:
            node_group_merged['node_configs'] = configs.merge_configs(
                ng_tmpl.get('node_configs'),
                node_group.get('node_configs'))

        return node_group_merged

    ## Assignment ops

    # def group_get(self, context, group):
    #     """Return the group or None if it does not exist."""
    #     return self.db.group_get(context, group)
    #
    # def group_get_all(self, context, **kwargs):
    #     """Get all groups filtered by **kwargs  e.g.
    #         group_get_all(group_name='test', tenant_name='test')
    #         """
    #     return self.db.group_get_all(context, **kwargs)

    def assignment_create(self, context, values):
        """Create an assignment from the values dictionary."""

        #loading defaults
        merged_values = copy.deepcopy(ASSIGNMENT_DEFAULTS)
        # values['group_id'] = group_id
        # values['actor_id'] = context.user_id
        #
        # private_key, public_key = crypto.generate_key_pair()
        # merged_values['management_private_key'] = private_key
        # merged_values['management_public_key'] = public_key

        # cluster_template_id = values.get('cluster_template_id')
        # c_tmpl = None

        # if cluster_template_id:
        #     c_tmpl = self.cluster_template_get(context, cluster_template_id)
        #
        #     del c_tmpl['created_at']
        #     del c_tmpl['updated_at']
        #     del c_tmpl['id']
        #
        #     #updating with cluster_template values
        #     merged_values.update(c_tmpl)

        #updating with values provided in request
        merged_values.update(values)

        # if c_tmpl:
        #     merged_values['cluster_configs'] = configs.merge_configs(
        #         c_tmpl.get('cluster_configs'),
        #         values.get('cluster_configs'))
        #
        # merged_values['node_groups'] = \
        #     self._populate_node_groups(context, merged_values)

        # print("merged_values = {0}".format(merged_values))
        # print self.db.group_create(context, merged_values)
        # raw_input("conductor_manager - group_create.")

        # self.db.assignment_create(context, merged_values)
        return self.db.assignment_create(context, merged_values)
        # return {"Test": "OK"}

    # def group_update(self, context, group, values):
    #     """Set the given properties on group and update it."""
    #     values = copy.deepcopy(values)
    #     return self.db.group_update(context, group, values)
    #
    # def group_destroy(self, context, group):
    #     """Destroy the group or raise if it does not exist."""
    #     self.db.group_destroy(context, group)

    ## Group ops

    def group_get(self, context, group):
        """Return the group or None if it does not exist."""
        return self.db.group_get(context, group)

    def group_get_all(self, context, **kwargs):
        """Get all groups filtered by **kwargs  e.g.
            group_get_all(group_name='test', tenant_name='test')
            """
        return self.db.group_get_all(context, **kwargs)

    def group_create(self, context, values):
        """Create a group from the values dictionary."""

        #loading defaults
        merged_values = copy.deepcopy(GROUP_DEFAULTS)
        # merged_values['domain_id'] = context.domain_id
        merged_values['project_id'] = context.tenant_id

        private_key, public_key = crypto.generate_key_pair()
        merged_values['management_private_key'] = private_key
        merged_values['management_public_key'] = public_key

        # cluster_template_id = values.get('cluster_template_id')
        # c_tmpl = None

        # if cluster_template_id:
        #     c_tmpl = self.cluster_template_get(context, cluster_template_id)
        #
        #     del c_tmpl['created_at']
        #     del c_tmpl['updated_at']
        #     del c_tmpl['id']
        #
        #     #updating with cluster_template values
        #     merged_values.update(c_tmpl)

        #updating with values provided in request
        merged_values.update(values)

        # if c_tmpl:
        #     merged_values['cluster_configs'] = configs.merge_configs(
        #         c_tmpl.get('cluster_configs'),
        #         values.get('cluster_configs'))
        #
        # merged_values['node_groups'] = \
        #     self._populate_node_groups(context, merged_values)

        # print("merged_values = {0}".format(merged_values))
        # print self.db.group_create(context, merged_values)
        # raw_input("conductor_manager - group_create.")

        return self.db.group_create(context, merged_values)

    def group_update(self, context, group, values):
        """Set the given properties on group and update it."""
        values = copy.deepcopy(values)
        return self.db.group_update(context, group, values)

    def group_destroy(self, context, group):
        """Destroy the group or raise if it does not exist."""
        self.db.group_destroy(context, group)


    ## Group Membership ops

    def group_membership_create(self, context, values):
        #loading defaults
        merged_values = copy.deepcopy(GROUP_MEMBERSHIP_DEFAULTS)

        #updating with values provided in request
        merged_values.update(values)

        return self.db.group_membership_create(context, merged_values)

    def group_membership_get_all(self, context, **kwargs):
        """Get all group membership filtered by **kwargs  e.g.
            group_membership_get_all(group_name='test', tenant_name='test')
            """
        return self.db.group_membership_get_all(context, **kwargs)


    ## Image ops

    def image_get(self, context, image):
        """Return the group or None if it does not exist."""
        return self.db.image_get(context, image)

    def image_get_all(self, context, **kwargs):
        """Get all groups filtered by **kwargs  e.g.
            group_get_all(group_name='test', tenant_name='test')
            """
        return self.db.image_get_all(context, **kwargs)

    def image_create(self, context, values):
        """Create a group from the values dictionary."""

        #loading defaults
        merged_values = copy.deepcopy(IMAGE_DEFAULTS)
        merged_values['tenant_id'] = context.tenant_id

        private_key, public_key = crypto.generate_key_pair()
        merged_values['management_private_key'] = private_key
        merged_values['management_public_key'] = public_key

        #updating with values provided in request
        merged_values.update(values)

        return self.db.image_create(context, merged_values)

    def image_update(self, context, image, values):
        """Set the given properties on group and update it."""
        values = copy.deepcopy(values)
        return self.db.image_update(context, image, values)

    def image_destroy(self, context, image):
        """Destroy the group or raise if it does not exist."""
        self.db.image_destroy(context, image)

    ## Pool ops

    def pool_get(self, context, pool):
        """Return the pool or None if it does not exist."""
        return self.db.pool_get(context, pool)

    def pool_get_all(self, context, **kwargs):
        """Get all pool filtered by **kwargs  e.g.
            pool_get_all(pool_name='test', tenant_name='test')
        """
        return self.db.pool_get_all(context, **kwargs)

    def pool_create(self, context, values):
        """Create a pool from the values dictionary."""

        #loading defaults
        merged_values = copy.deepcopy(POOL_DEFAULTS)
        merged_values['tenant_id'] = context.tenant_id

        private_key, public_key = crypto.generate_key_pair()
        merged_values['management_private_key'] = private_key
        merged_values['management_public_key'] = public_key

        # cluster_template_id = values.get('cluster_template_id')
        # c_tmpl = None

        # if cluster_template_id:
        #     c_tmpl = self.cluster_template_get(context, cluster_template_id)
        #
        #     del c_tmpl['created_at']
        #     del c_tmpl['updated_at']
        #     del c_tmpl['id']
        #
        #     #updating with cluster_template values
        #     merged_values.update(c_tmpl)

        #updating with values provided in request
        merged_values.update(values)

        # if c_tmpl:
        #     merged_values['cluster_configs'] = configs.merge_configs(
        #         c_tmpl.get('cluster_configs'),
        #         values.get('cluster_configs'))
        #
        # merged_values['node_groups'] = \
        #     self._populate_node_groups(context, merged_values)

        # print("merged_values = {0}".format(merged_values))
        # raw_input("conductor_manager - pool_create.")

        return self.db.pool_create(context, merged_values)

    def pool_update(self, context, pool, values):
        """Set the given properties on group and update it."""
        values = copy.deepcopy(values)

        # print pool, values
        # raw_input("conductor-manager-pool-update")

        return self.db.pool_update(context, pool, values)

    def pool_destroy(self, context, pool):
        """Destroy the group or raise if it does not exist."""
        self.db.pool_destroy(context, pool)

    ## Cluster ops

    def cluster_get(self, context, cluster):
        """Return the cluster or None if it does not exist."""
        return self.db.cluster_get(context, cluster)

    def cluster_get_all(self, context, **kwargs):
        """Get all clusters filtered by **kwargs  e.g.
            cluster_get_all(plugin_name='vanilla', hadoop_version='1.1')
            """
        return self.db.cluster_get_all(context, **kwargs)

    def cluster_create(self, context, values):
        """Create a cluster from the values dictionary."""

        #loading defaults
        merged_values = copy.deepcopy(CLUSTER_DEFAULTS)
        merged_values['tenant_id'] = context.tenant_id

        private_key, public_key = crypto.generate_key_pair()
        merged_values['management_private_key'] = private_key
        merged_values['management_public_key'] = public_key

        cluster_template_id = values.get('cluster_template_id')
        c_tmpl = None

        if cluster_template_id:
            c_tmpl = self.cluster_template_get(context, cluster_template_id)

            del c_tmpl['created_at']
            del c_tmpl['updated_at']
            del c_tmpl['id']

            #updating with cluster_template values
            merged_values.update(c_tmpl)

        #updating with values provided in request
        merged_values.update(values)

        if c_tmpl:
            merged_values['cluster_configs'] = configs.merge_configs(
                c_tmpl.get('cluster_configs'),
                values.get('cluster_configs'))

        merged_values['node_groups'] = \
            self._populate_node_groups(context, merged_values)

        return self.db.cluster_create(context, merged_values)

    def cluster_update(self, context, cluster, values):
        """Set the given properties on cluster and update it."""
        values = copy.deepcopy(values)
        return self.db.cluster_update(context, cluster, values)

    def cluster_destroy(self, context, cluster):
        """Destroy the cluster or raise if it does not exist."""
        self.db.cluster_destroy(context, cluster)

    ## Node Group ops

    def node_group_add(self, context, cluster, values):
        """Create a Node Group from the values dictionary."""
        values = copy.deepcopy(values)
        values = self._populate_node_group(context, values)
        values['tenant_id'] = context.tenant_id
        return self.db.node_group_add(context, cluster, values)

    def node_group_update(self, context, node_group, values):
        """Set the given properties on node_group and update it."""
        values = copy.deepcopy(values)
        self.db.node_group_update(context, node_group, values)

    def node_group_remove(self, context, node_group):
        """Destroy the node_group or raise if it does not exist."""
        self.db.node_group_remove(context, node_group)

    ## Instance ops

    def instance_add(self, context, node_group, values):
        """Create an Instance from the values dictionary."""
        values = copy.deepcopy(values)
        values = _apply_defaults(values, INSTANCE_DEFAULTS)
        values['tenant_id'] = context.tenant_id
        return self.db.instance_add(context, node_group, values)

    def instance_update(self, context, instance, values):
        """Set the given properties on Instance and update it."""
        values = copy.deepcopy(values)
        self.db.instance_update(context, instance, values)

    def instance_remove(self, context, instance):
        """Destroy the Instance or raise if it does not exist."""
        self.db.instance_remove(context, instance)

    ## Volumes ops

    def append_volume(self, context, instance, volume_id):
        """Append volume_id to instance."""
        self.db.append_volume(context, instance, volume_id)

    def remove_volume(self, context, instance, volume_id):
        """Remove volume_id in instance."""
        self.db.remove_volume(context, instance, volume_id)

    ## Cluster Template ops

    def cluster_template_get(self, context, cluster_template):
        """Return the cluster_template or None if it does not exist."""
        return self.db.cluster_template_get(context, cluster_template)

    def cluster_template_get_all(self, context):
        """Get all cluster_templates."""
        return self.db.cluster_template_get_all(context)

    def cluster_template_create(self, context, values):
        """Create a cluster_template from the values dictionary."""
        values = copy.deepcopy(values)
        values = _apply_defaults(values, CLUSTER_DEFAULTS)
        values['tenant_id'] = context.tenant_id

        values['node_groups'] = self._populate_node_groups(context, values)

        return self.db.cluster_template_create(context, values)

    def cluster_template_destroy(self, context, cluster_template):
        """Destroy the cluster_template or raise if it does not exist."""
        self.db.cluster_template_destroy(context, cluster_template)

    ##JobExecution ops

    def job_execution_get(self, context, job_execution):
        """Return the JobExecution or None if it does not exist."""
        return self.db.job_execution_get(context, job_execution)

    def job_execution_get_all(self, context, **kwargs):
        """Get all JobExecutions filtered by **kwargs  e.g.
            job_execution_get_all(cluster_id=12, input_id=123)
        """
        return self.db.job_execution_get_all(context, **kwargs)

    def job_execution_count(self, context, **kwargs):
        """Count number of JobExecutions filtered by **kwargs  e.g.
            job_execution_count(cluster_id=12, input_id=123)
        """
        return self.db.job_execution_count(context, **kwargs)

    def job_execution_create(self, context, values):
        """Create a JobExecution from the values dictionary."""
        values = copy.deepcopy(values)
        values['tenant_id'] = context.tenant_id
        return self.db.job_execution_create(context, values)

    def job_execution_update(self, context, job_execution, values):
        """Updates a JobExecution from the values dictionary."""
        return self.db.job_execution_update(context, job_execution, values)

    def job_execution_destroy(self, context, job_execution):
        """Destroy the JobExecution or raise if it does not exist."""
        return self.db.job_execution_destroy(context, job_execution)

    ## Job ops

    def job_get(self, context, job):
        """Return the Job or None if it does not exist."""
        return self.db.job_get(context, job)

    def job_get_all(self, context):
        """Get all Jobs."""
        return self.db.job_get_all(context)

    def job_create(self, context, values):
        """Create a Job from the values dictionary."""
        values = copy.deepcopy(values)
        values['tenant_id'] = context.tenant_id
        return self.db.job_create(context, values)

    def job_update(self, context, job, values):
        """Updates a Job from the values dictionary."""
        return self.db.job_update(context, job, values)

    def job_destroy(self, context, job):
        """Destroy the Job or raise if it does not exist."""
        self.db.job_destroy(context, job)

    ## JobBinary ops

    def job_binary_get_all(self, context):
        """Get all JobBinaries."""
        return self.db.job_binary_get_all(context)

    def job_binary_get(self, context, job_binary_id):
        """Return the JobBinary or None if it does not exist."""
        return self.db.job_binary_get(context, job_binary_id)

    def job_binary_create(self, context, values):
        """Create a JobBinary from the values dictionary."""

        values = copy.deepcopy(values)
        values['tenant_id'] = context.tenant_id
        return self.db.job_binary_create(context, values)

    def job_binary_destroy(self, context, job_binary):
        """Destroy the JobBinary or raise if it does not exist."""
        self.db.job_binary_destroy(context, job_binary)

    ## JobBinaryInternal ops

    def job_binary_internal_get_all(self, context):
        """Get all JobBinaryInternals

        The JobBinaryInternals returned do not contain a data field.
        """
        return self.db.job_binary_internal_get_all(context)

    def job_binary_internal_get(self, context, job_binary_internal_id):
        """Return the JobBinaryInternal or None if it does not exist

        The JobBinaryInternal returned does not contain a data field.
        """
        return self.db.job_binary_internal_get(context, job_binary_internal_id)

    def job_binary_internal_create(self, context, values):
        """Create a JobBinaryInternal from the values dictionary."""

        # Since values["data"] is (should be) encoded as a string
        # here the deepcopy of values only incs a reference count on data.
        # This is nice, since data could be big...
        values = copy.deepcopy(values)
        values['tenant_id'] = context.tenant_id
        return self.db.job_binary_internal_create(context, values)

    def job_binary_internal_destroy(self, context, job_binary_internal):
        """Destroy the JobBinaryInternal or raise if it does not exist."""
        self.db.job_binary_internal_destroy(context, job_binary_internal)

    def job_binary_internal_get_raw_data(self,
                                         context, job_binary_internal_id):
        """Return the binary data field from a JobBinaryInternal."""
        return self.db.job_binary_internal_get_raw_data(
            context,
            job_binary_internal_id)


    ## VM ops

    def VM_get(self, context, VM):
        """Return the VM or None if it does not exist."""
        return self.db.VM_get(context, VM)

    def VM_get_all(self, context, **kwargs):
        """Get all VMs filtered by **kwargs  e.g.
            """
        return self.db.VM_get_all(context, **kwargs)

    def VM_create(self, context, values):
        """Create a VM from the values dictionary."""

        #loading defaults
        merged_values = copy.deepcopy(VM_DEFAULTS)
        merged_values['tenant_id'] = context.tenant_id
        # merged_values['group_id'] = context.group_id #we need this

        private_key, public_key = crypto.generate_key_pair()
        merged_values['management_private_key'] = private_key
        merged_values['management_public_key'] = public_key


        #updating with values provided in request
        merged_values.update(values)

        return self.db.VM_create(context, merged_values)

    def VM_update(self, context, vm, values):
        """Set the given properties on cluster and update it."""
        values = copy.deepcopy(values)
        return self.db.VM_update(context, vm, values)


        ## User ops

    def User_get(self, context, User):
        """Return the User or None if it does not exist."""
        return self.db.User_get(context, User)

    def User_get_all(self, context, **kwargs):
        """Get all User filtered by **kwargs  e.g.
            """
        return self.db.User_get_all(context, **kwargs)

    def User_create(self, context, user_id, values):
        """Create a User from the values dictionary."""

        #loading defaults
        print 'User_create calls db.User_create'

        return self.db.User_create(context, user_id)  # this may not work, we need to work with Keystone

    def User_update(self, context, User, values):
        """Set the given properties on cluster and update it."""
        values = copy.deepcopy(values)
        return self.db.Site_update(context, User, values)
