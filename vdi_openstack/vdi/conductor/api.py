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

"""Handles all requests to the conductor service."""

from oslo.config import cfg

from vdi.conductor import manager
from vdi.conductor import resource as r
from vdi.openstack.common import log as logging


conductor_opts = [
    cfg.BoolOpt('use_local',
                default=True,
                help='Perform vdi-conductor operations locally.'),
]

conductor_group = cfg.OptGroup(name='conductor',
                               title='Conductor Options')

CONF = cfg.CONF
CONF.register_group(conductor_group)
CONF.register_opts(conductor_opts, conductor_group)

LOG = logging.getLogger(__name__)


def _get_id(obj):
    """Return object id.

    Allows usage of both an object or an object's ID as a parameter when
    dealing with relationships.
    """
    try:
        return obj.id
    except AttributeError:
        return obj


class LocalApi(object):
    """A local version of the conductor API that does database updates
    locally instead of via RPC.
    """

    def __init__(self):
        self._manager = manager.ConductorManager()

    ## Group ops

    @r.wrap(r.GroupResource)
    def group_get(self, context, group):
        """Return the group or None if it does not exist."""
        return self._manager.group_get(context, _get_id(group))

    @r.wrap(r.GroupResource)
    def group_get_all(self, context, **kwargs):
        """Get all groups filtered by **kwargs  e.g.
            group_get_all(group_name='test', tenant_name='test')
        """
        return self._manager.group_get_all(context, **kwargs)

    @r.wrap(r.GroupResource)
    def group_create(self, context, values):
        """Create a group from the values dictionary.
        Return the created group.
        """
        return self._manager.group_create(context, values)

    @r.wrap(r.GroupResource)
    def group_update(self, context, group, values):
        """Update the group with the given values dictionary.
        Return the updated group.
        """
        return self._manager.group_update(context, _get_id(group), values)

    def group_destroy(self, context, group):
        """Destroy the cluster or raise if it does not exist.
        Return None.
        """
        self._manager.group_destroy(context, _get_id(group))

    ## Assignment ops

    # @r.wrap(r.AssignmentResource)
    # def group_get(self, context, group):
    #     """Return the group or None if it does not exist."""
    #     return self._manager.group_get(context, _get_id(group))
    #
    # @r.wrap(r.GroupResource)
    # def group_get_all(self, context, **kwargs):
    #     """Get all groups filtered by **kwargs  e.g.
    #         group_get_all(group_name='test', tenant_name='test')
    #     """
    #     return self._manager.group_get_all(context, **kwargs)

    @r.wrap(r.AssignmentResource)
    def assignment_create(self, context, values):
        """Create a group from the values dictionary.
        Return the created group.
        """
        return self._manager.assignment_create(context, values)

    # @r.wrap(r.GroupResource)
    # def group_update(self, context, group, values):
    #     """Update the group with the given values dictionary.
    #     Return the updated group.
    #     """
    #     return self._manager.group_update(context, _get_id(group), values)
    #
    # def group_destroy(self, context, group):
    #     """Destroy the cluster or raise if it does not exist.
    #     Return None.
    #     """
    #     self._manager.group_destroy(context, _get_id(group))

    ## Group Membership ops

    @r.wrap(r.GroupMembershipResource)
    def group_membership_create(self, context, values):
        """Create a group membership from the values dictionary.
        Return the created group membership.
        """
        return self._manager.group_membership_create(context, values)


    @r.wrap(r.GroupMembershipResource)
    def group_membership_get_all(self, context, **kwargs):
        """Get all group memberships filtered by **kwargs  e.g.
            group_membership_get_all(group_name='test', tenant_name='test')
        """
        return self._manager.group_membership_get_all(context, **kwargs)


    # @r.wrap(r.GroupResource)
    # def group_update(self, context, group, values):
    #     """Update the group with the given values dictionary.
    #     Return the updated group.
    #     """
    #     return self._manager.group_update(context, _get_id(group), values)
    #
    # def group_destroy(self, context, group):
    #     """Destroy the cluster or raise if it does not exist.
    #     Return None.
    #     """
    #     self._manager.group_destroy(context, _get_id(group))

    ## Image ops

    @r.wrap(r.ImageResource)
    def image_get(self, context, image):
        """Return the group or None if it does not exist."""
        return self._manager.image_get(context, _get_id(image))

    @r.wrap(r.ImageResource)
    def image_get_all(self, context, **kwargs):
        """Get all groups filtered by **kwargs  e.g.
            group_get_all(group_name='test', tenant_name='test')
        """
        return self._manager.image_get_all(context, **kwargs)

    @r.wrap(r.ImageResource)
    def image_create(self, context, values):
        """Create a group from the values dictionary.
        Return the created group.
        """
        return self._manager.image_create(context, values)

    @r.wrap(r.ImageResource)
    def image_update(self, context, image, values):
        """Update the group with the given values dictionary.
        Return the updated group.
        """
        return self._manager.image_update(context, _get_id(image), values)

    def image_destroy(self, context, image):
        """Destroy the cluster or raise if it does not exist.
        Return None.
        """
        self._manager.image_destroy(context, _get_id(image))

    ## Pool ops

    @r.wrap(r.PoolResource)
    def pool_get(self, context, pool):
        """Return the pool or None if it does not exist."""
        return self._manager.pool_get(context, _get_id(pool))

    @r.wrap(r.PoolResource)
    def pool_get_all(self, context, **kwargs):
        """Get all pools filtered by **kwargs  e.g.
            pool_get_all(pool_name='test', tenant_name='test')
        """
        return self._manager.pool_get_all(context, **kwargs)

    @r.wrap(r.PoolResource)
    def pool_create(self, context, values):
        """Create a pool from the values dictionary.
            Return the created pool.
        """
        return self._manager.pool_create(context, values)

    @r.wrap(r.PoolResource)
    def pool_update(self, context, pool, values):
        """Update the pool with the given values dictionary.
        Return the updated pool.
        """
        return self._manager.pool_update(context, _get_id(pool), values)

    def pool_destroy(self, context, pool):
        """Destroy the cluster or raise if it does not exist.
        Return None.
        """
        self._manager.pool_destroy(context, _get_id(pool))

    ## Cluster ops

    @r.wrap(r.ClusterResource)
    def cluster_get(self, context, cluster):
        """Return the cluster or None if it does not exist."""
        return self._manager.cluster_get(context, _get_id(cluster))

    @r.wrap(r.ClusterResource)
    def cluster_get_all(self, context, **kwargs):
        """Get all clusters filtered by **kwargs  e.g.
            cluster_get_all(plugin_name='vanilla', hadoop_version='1.1')
        """
        return self._manager.cluster_get_all(context, **kwargs)

    @r.wrap(r.ClusterResource)
    def cluster_create(self, context, values):
        """Create a cluster from the values dictionary.
        Return the created cluster.
        """
        return self._manager.cluster_create(context, values)

    @r.wrap(r.ClusterResource)
    def cluster_update(self, context, cluster, values):
        """Update the cluster with the given values dictionary.
        Return the updated cluster.
        """
        return self._manager.cluster_update(context, _get_id(cluster),
                                            values)

    def cluster_destroy(self, context, cluster):
        """Destroy the cluster or raise if it does not exist.
        Return None.
        """
        self._manager.cluster_destroy(context, _get_id(cluster))

    ## Node Group ops

    def node_group_add(self, context, cluster, values):
        """Create a node group from the values dictionary.
        Return ID of the created node group.
        """
        return self._manager.node_group_add(context, _get_id(cluster), values)

    def node_group_update(self, context, node_group, values):
        """Update the node group with the given values dictionary.
        Return None.
        """
        self._manager.node_group_update(context, _get_id(node_group), values)

    def node_group_remove(self, context, node_group):
        """Destroy the node group or raise if it does not exist.
        Return None.
        """
        self._manager.node_group_remove(context, _get_id(node_group))

    ## Instance ops

    def instance_add(self, context, node_group, values):
        """Create an instance from the values dictionary.
        Return ID of the created instance.
        """
        return self._manager.instance_add(context, _get_id(node_group), values)

    def instance_update(self, context, instance, values):
        """Update the instance with the given values dictionary.
        Return None.
        """
        self._manager.instance_update(context, _get_id(instance), values)

    def instance_remove(self, context, instance):
        """Destroy the instance or raise if it does not exist.
        Return None.
        """
        self._manager.instance_remove(context, _get_id(instance))

    ## Volumes ops

    def append_volume(self, context, instance, volume_id):
        """Append volume_id to instance."""
        self._manager.append_volume(context, _get_id(instance), volume_id)

    def remove_volume(self, context, instance, volume_id):
        """Remove volume_id in instance."""
        self._manager.remove_volume(context, _get_id(instance), volume_id)

    ## Cluster Template ops

    @r.wrap(r.ClusterTemplateResource)
    def cluster_template_get(self, context, cluster_template):
        """Return the cluster template or None if it does not exist."""
        return self._manager.cluster_template_get(context,
                                                  _get_id(cluster_template))

    @r.wrap(r.ClusterTemplateResource)
    def cluster_template_get_all(self, context):
        """Get all cluster templates."""
        return self._manager.cluster_template_get_all(context)

    @r.wrap(r.ClusterTemplateResource)
    def cluster_template_create(self, context, values):
        """Create a cluster template from the values dictionary.
        Return the created cluster template
        """
        return self._manager.cluster_template_create(context, values)

    def cluster_template_destroy(self, context, cluster_template):
        """Destroy the cluster template or raise if it does not exist.
        Return None
        """
        self._manager.cluster_template_destroy(context,
                                               _get_id(cluster_template))

    ## Node Group Template ops

    @r.wrap(r.NodeGroupTemplateResource)
    def node_group_template_get(self, context, node_group_template):
        """Return the node group template or None if it does not exist."""
        return self._manager.node_group_template_get(
            context, _get_id(node_group_template))

    @r.wrap(r.NodeGroupTemplateResource)
    def node_group_template_get_all(self, context):
        """Get all node group templates."""
        return self._manager.node_group_template_get_all(context)

    @r.wrap(r.NodeGroupTemplateResource)
    def node_group_template_create(self, context, values):
        """Create a node group template from the values dictionary.
        Return the created node group template
        """
        return self._manager.node_group_template_create(context, values)

    def node_group_template_destroy(self, context, node_group_template):
        """Destroy the node group template or raise if it does not exist.
        Return None
        """
        self._manager.node_group_template_destroy(context,
                                                  _get_id(node_group_template))

    ## Data Source ops

    @r.wrap(r.DataSource)
    def data_source_get(self, context, data_source):
        """Return the Data Source or None if it does not exist."""
        return self._manager.data_source_get(context, _get_id(data_source))

    @r.wrap(r.DataSource)
    def data_source_get_all(self, context):
        """Get all Data Sources."""
        return self._manager.data_source_get_all(context)

    @r.wrap(r.DataSource)
    def data_source_create(self, context, values):
        """Create a Data Source from the values dictionary."""
        return self._manager.data_source_create(context, values)

    def data_source_destroy(self, context, data_source):
        """Destroy the Data Source or raise if it does not exist."""
        self._manager.data_source_destroy(context, _get_id(data_source))

    ## JobExecution ops

    @r.wrap(r.JobExecution)
    def job_execution_get(self, context, job_execution):
        """Return the JobExecution or None if it does not exist."""
        return self._manager.job_execution_get(context,
                                               _get_id(job_execution))

    @r.wrap(r.JobExecution)
    def job_execution_get_all(self, context, **kwargs):
        """Get all JobExecutions filtered by **kwargs  e.g.
            job_execution_get_all(cluster_id=12, input_id=123)
        """
        return self._manager.job_execution_get_all(context, **kwargs)

    def job_execution_count(self, context, **kwargs):
        """Count number of JobExecutions filtered by **kwargs  e.g.
            job_execution_count(cluster_id=12, input_id=123)
        """
        return self._manager.job_execution_count(context, **kwargs)

    @r.wrap(r.JobExecution)
    def job_execution_create(self, context, values):
        """Create a JobExecution from the values dictionary."""
        return self._manager.job_execution_create(context, values)

    @r.wrap(r.JobExecution)
    def job_execution_update(self, context, job_execution, values):
        """Update the JobExecution or raise if it does not exist."""
        return self._manager.job_execution_update(context,
                                                  _get_id(job_execution),
                                                  values)

    def job_execution_destroy(self, context, job_execution):
        """Destroy the JobExecution or raise if it does not exist."""
        self._manager.job_execution_destroy(context, _get_id(job_execution))

    ## Job ops

    @r.wrap(r.Job)
    def job_get(self, context, job):
        """Return the Job or None if it does not exist."""
        return self._manager.job_get(context, _get_id(job))

    @r.wrap(r.Job)
    def job_get_all(self, context):
        """Get all Jobs."""
        return self._manager.job_get_all(context)

    @r.wrap(r.Job)
    def job_create(self, context, values):
        """Create a Job from the values dictionary."""
        return self._manager.job_create(context, values)

    def job_update(self, context, job, values):
        """Update the Job or raise if it does not exist."""
        return self._manager.job_update(context, _get_id(job),
                                        values)

    def job_destroy(self, context, job):
        """Destroy the Job or raise if it does not exist."""
        self._manager.job_destroy(context, _get_id(job))

    def job_main_name(self, context, job):
        """Return the name of the first main JobBinary or None

        At present the 'mains' element is expected to contain a single element.
        In the future if 'mains' contains more than one element we will need
        a scheme or convention for retrieving a name from the list of binaries.

        :param job: This is expected to be a Job object
        """
        if job.mains:
            binary = self.job_binary_get(context, job.mains[0])
            if binary is not None:
                return binary["name"]
        return None

    ## JobBinary ops

    @r.wrap(r.JobBinary)
    def job_binary_get_all(self, context):
        """Get all JobBinarys."""
        return self._manager.job_binary_get_all(context)

    @r.wrap(r.JobBinary)
    def job_binary_get(self, context, job_binary):
        """Return the JobBinary or None if it does not exist."""
        return self._manager.job_binary_get(context, _get_id(job_binary))

    @r.wrap(r.JobBinary)
    def job_binary_create(self, context, values):
        """Create a JobBinary from the values dictionary."""
        return self._manager.job_binary_create(context, values)

    def job_binary_destroy(self, context, job_binary):
        """Destroy the JobBinary or raise if it does not exist."""
        self._manager.job_binary_destroy(context, _get_id(job_binary))

    ## JobBinaryInternal ops

    @r.wrap(r.JobBinaryInternal)
    def job_binary_internal_get_all(self, context):
        """Get all JobBinaryInternals."""
        return self._manager.job_binary_internal_get_all(context)

    @r.wrap(r.JobBinaryInternal)
    def job_binary_internal_get(self, context, job_binary_internal):
        """Return the JobBinaryInternal or None if it does not exist."""
        return self._manager.job_binary_internal_get(
            context,
            _get_id(job_binary_internal))

    @r.wrap(r.JobBinaryInternal)
    def job_binary_internal_create(self, context, values):
        """Create a JobBinaryInternal from the values dictionary."""
        return self._manager.job_binary_internal_create(context, values)

    def job_binary_internal_destroy(self, context, job_binary_internal_id):
        """Destroy the JobBinaryInternal or raise if it does not exist."""
        self._manager.job_binary_internal_destroy(
            context,
            _get_id(job_binary_internal_id))

    def job_binary_internal_get_raw_data(self, context,
                                         job_binary_internal_id):
        """Return the binary data field from a JobBinaryInternal."""
        return self._manager.job_binary_internal_get_raw_data(
            context,
            job_binary_internal_id)


    ## VMs ops

    @r.wrap(r.VMResource)
    def VM_get(self, context, VM):
        """Return the VM or None if it does not exist."""
        return self._manager.VM_get(context, _get_id(VM))

    @r.wrap(r.VMResource)
    def VM_create(self, context, values):
        """Create a VM from the values dictionary.
        Return ID of the created VM.
        """
        # return self._manager.VM_create(context, _get_id(VM), values)
        return self._manager.VM_create(context, values)

    @r.wrap(r.VMResource)
    def VM_update(self, context, vm, values):
        """Update the node VM with the given values dictionary.
        Return None.
        """
        return self._manager.VM_update(context, _get_id(vm), values)

    @r.wrap(r.VMResource)
    def VM_remove(self, context, VM):
        """Destroy the node group or raise if it does not exist.
        Return None.
        """
        self._manager.VM_remove(context, _get_id(VM))
   
    @r.wrap(r.VMResource)
    def VM_get_all(self, context, **kwargs):
        """Get all VMs filtered by **kwargs  e.g.
            VM_get_all(VM_name='test', tenant_name='test')
        """
        return self._manager.VM_get_all(context, **kwargs)


    ## Sites ops

    @r.wrap(r.SiteResource)
    def site_create(self, context, Site, values):
        """Create a Site from the values dictionary.
        Return ID of the created Site.
        """
        #return self._manager.Site_create(context, _get_id(Site), values)
        return self._manager.Site_create(context, values)

    @r.wrap(r.SiteResource)
    def Site_update(self, context, Site, values):
        """Update the site with the given values dictionary.
        Return None.
        """
        self._manager.Site_update(context, _get_id(Site), values)

    @r.wrap(r.SiteResource)
    def Site_remove(self, context, Site):
        """Destroy the node group or raise if it does not exist.
        Return None.
        """
        self._manager.Site_remove(context, _get_id(Site))

    @r.wrap(r.SiteResource)
    def Site_get_all(self, context, **kwargs):
        """Get all Sites filtered by **kwargs  e.g.
             Site_get_all(Site_name='test', tenant_name='test')
        """
        return self._manager.Site_get_all(context, **kwargs)


        ## Users ops

    @r.wrap(r.UserResource)
    def user_create(self, context, values):
        """Create a User from the values dictionary.
        Return ID of the created User.
        """
        # what about user ID?
        #return self._manager.User_add(context, _get_id(User), values)
        # 0 for now
        return self._manager.User_create(context, 0, values) 

    @r.wrap(r.UserResource)
    def User_update(self, context, User, values):
        """Update the user with the given values dictionary.
        Return None.
        """
        self._manager.User_update(context, _get_id(User), values)

    @r.wrap(r.UserResource)
    def User_remove(self, context, User):
        """Destroy the node group or raise if it does not exist.
        Return None.
        """
        self._manager.User_remove(context, _get_id(User))

    @r.wrap(r.UserResource)
    def User_get_all(self, context, **kwargs):
        """Get all Users filtered by **kwargs  e.g.
             Site_get_all(User_name='test', tenant_name='test')
        """
        return self._manager.User_get_all(context, **kwargs)


class RemoteApi(LocalApi):
    """Conductor API that does updates via RPC to the ConductorManager."""

    # TODO(slukjanov): it should override _manager and only necessary functions
