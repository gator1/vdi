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

"""Defines interface for DB access.

Functions in this module are imported into the vdi.db namespace. Call these
functions from vdi.db namespace, not the vdi.db.api namespace.

All functions in this module return objects that implement a dictionary-like
interface.

**Related Flags**

:db_backend:  string to lookup in the list of LazyPluggable backends.
              `sqlalchemy` is the only supported backend right now.

:sql_connection:  string specifying the sqlalchemy connection to use, like:
                  `sqlite:///var/lib/vdi/vdi.sqlite`.

"""

from oslo.config import cfg

from vdi.openstack.common.db import api as db_api
from vdi.openstack.common import log as logging


CONF = cfg.CONF

_BACKEND_MAPPING = {
    'sqlalchemy': 'vdi.db.sqlalchemy.api',
}

IMPL = db_api.DBAPI(backend_mapping=_BACKEND_MAPPING)
LOG = logging.getLogger(__name__)


def setup_db():
    """Set up database, create tables, etc.

    Return True on success, False otherwise
    """
    return IMPL.setup_db()


def drop_db():
    """Drop database.

    Return True on success, False otherwise
    """
    return IMPL.drop_db()


## Helpers for building constraints / equality checks


def constraint(**conditions):
    """Return a constraint object suitable for use with some updates."""
    return IMPL.constraint(**conditions)


def equal_any(*values):
    """Return an equality condition object suitable for use in a constraint.

    Equal_any conditions require that a model object's attribute equal any
    one of the given values.
    """
    return IMPL.equal_any(*values)


def not_equal(*values):
    """Return an inequality condition object suitable for use in a constraint.

    Not_equal conditions require that a model object's attribute differs from
    all of the given values.
    """
    return IMPL.not_equal(*values)


def to_dict(func):
    def decorator(*args, **kwargs):
        res = func(*args, **kwargs)

        if isinstance(res, list):
            return [item.to_dict() for item in res]

        if res:
            return res.to_dict()
        else:
            return None

    return decorator


## Group ops

@to_dict
def group_get(context, group):
    """Return the group or None if it does not exist."""
    return IMPL.group_get(context, group)


@to_dict
def group_get_all(context, **kwargs):
    """Get all groups filtered by **kwargs  e.g.
         group_get_all(group_name='test', tenant_name='test')
    """
    return IMPL.group_get_all(context, **kwargs)


@to_dict
def group_create(context, values):
    """Create a group from the values dictionary."""
    return IMPL.group_create(context, values)


@to_dict
def group_update(context, group, values):
    """Set the given properties on group and update it."""
    return IMPL.group_update(context, group, values)


def group_destroy(context, group):
    """Destroy the group or raise if it does not exist."""
    IMPL.group_destroy(context, group)


## Group assignment ops

# @to_dict
# def group_get(context, group):
#     """Return the group or None if it does not exist."""
#     return IMPL.group_get(context, group)
#
#
# @to_dict
# def group_get_all(context, **kwargs):
#     """Get all groups filtered by **kwargs  e.g.
#          group_get_all(group_name='test', tenant_name='test')
#     """
#     return IMPL.group_get_all(context, **kwargs)


@to_dict
def assignment_create(context, values):
    """Create a group from the values dictionary."""
    return IMPL.assignment_create(context, values)


# @to_dict
# def group_update(context, group, values):
#     """Set the given properties on group and update it."""
#     return IMPL.group_update(context, group, values)
#
#
# def group_destroy(context, group):
#     """Destroy the group or raise if it does not exist."""
#     IMPL.group_destroy(context, group)


## Group membership ops

@to_dict
def group_membership_get_all(context, **kwargs):
    """Get all group memberships filtered by **kwargs  e.g.
         group_membership_get_all(group_name='test', tenant_name='test')
    """
    return IMPL.group_membership_get_all(context, **kwargs)


@to_dict
def group_membership_create(context, values):
    """Create a group from the values dictionary."""
    return IMPL.group_membership_create(context, values)


# @to_dict
# def group_update(context, group, values):
#     """Set the given properties on group and update it."""
#     return IMPL.group_update(context, group, values)
#
#
# def group_destroy(context, group):
#     """Destroy the group or raise if it does not exist."""
#     IMPL.group_destroy(context, group)


## Image ops

@to_dict
def image_get(context, image):
    """Return the image or None if it does not exist."""
    return IMPL.image_get(context, image)


@to_dict
def image_get_all(context, **kwargs):
    """Get all images filtered by **kwargs  e.g.
         image_get_all(image_name='test', tenant_name='test')
    """
    return IMPL.image_get_all(context, **kwargs)


@to_dict
def image_create(context, values):
    """Create an image from the values dictionary."""
    return IMPL.image_create(context, values)


@to_dict
def image_update(context, image, values):
    """Set the given properties on image and update it."""
    return IMPL.image_update(context, image, values)


def image_destroy(context, image):
    """Destroy the group or raise if it does not exist."""
    IMPL.image_destroy(context, image)


## Pool ops

@to_dict
def pool_get(context, pool):
    """Return the pool or None if it does not exist."""
    return IMPL.pool_get(context, pool)


@to_dict
def pool_get_all(context, **kwargs):
    """Get all pools filtered by **kwargs  e.g.
         pool_get_all(pool_name='test', tenant_name='test')
    """
    return IMPL.pool_get_all(context, **kwargs)


@to_dict
def pool_create(context, values):
    """Create a pool from the values dictionary."""

    # print context, values
    # raw_input("db-api-pool-create")

    return IMPL.pool_create(context, values)


@to_dict
def pool_update(context, pool, values):
    """Set the given properties on pool and update it."""

    # print pool, values
    # raw_input("vdi-db-pool-update")

    return IMPL.pool_update(context, pool, values)


def pool_destroy(context, pool):
    """Destroy the pool or raise if it does not exist."""
    IMPL.pool_destroy(context, pool)


## Cluster ops

@to_dict
def cluster_get(context, cluster):
    """Return the cluster or None if it does not exist."""
    return IMPL.cluster_get(context, cluster)


@to_dict
def cluster_get_all(context, **kwargs):
    """Get all clusters filtered by **kwargs  e.g.
         cluster_get_all(plugin_name='vanilla', hadoop_version='1.1')
    """
    return IMPL.cluster_get_all(context, **kwargs)


@to_dict
def cluster_create(context, values):
    """Create a cluster from the values dictionary."""
    return IMPL.cluster_create(context, values)


@to_dict
def cluster_update(context, cluster, values):
    """Set the given properties on cluster and update it."""
    return IMPL.cluster_update(context, cluster, values)


def cluster_destroy(context, cluster):
    """Destroy the cluster or raise if it does not exist."""
    IMPL.cluster_destroy(context, cluster)


## Node Group ops

def node_group_add(context, cluster, values):
    """Create a Node Group from the values dictionary."""
    return IMPL.node_group_add(context, cluster, values)


def node_group_update(context, node_group, values):
    """Set the given properties on node_group and update it."""
    IMPL.node_group_update(context, node_group, values)


def node_group_remove(context, node_group):
    """Destroy the node_group or raise if it does not exist."""
    IMPL.node_group_remove(context, node_group)


## Instance ops

def instance_add(context, node_group, values):
    """Create an Instance from the values dictionary."""
    return IMPL.instance_add(context, node_group, values)


def instance_update(context, instance, values):
    """Set the given properties on Instance and update it."""
    IMPL.instance_update(context, instance, values)


def instance_remove(context, instance):
    """Destroy the Instance or raise if it does not exist."""
    IMPL.instance_remove(context, instance)


## Volumes ops

def append_volume(context, instance, volume_id):
    """Append volume_id to instance."""
    IMPL.append_volume(context, instance, volume_id)


def remove_volume(context, instance, volume_id):
    """Remove volume_id in instance."""
    IMPL.remove_volume(context, instance, volume_id)


## Cluster Template ops

@to_dict
def cluster_template_get(context, cluster_template):
    """Return the cluster_template or None if it does not exist."""
    return IMPL.cluster_template_get(context, cluster_template)


@to_dict
def cluster_template_get_all(context):
    """Get all cluster_templates."""
    return IMPL.cluster_template_get_all(context)


@to_dict
def cluster_template_create(context, values):
    """Create a cluster_template from the values dictionary."""
    return IMPL.cluster_template_create(context, values)


def cluster_template_destroy(context, cluster_template):
    """Destroy the cluster_template or raise if it does not exist."""
    IMPL.cluster_template_destroy(context, cluster_template)


## Node Group Template ops

@to_dict
def node_group_template_get(context, node_group_template):
    """Return the Node Group Template or None if it does not exist."""
    return IMPL.node_group_template_get(context, node_group_template)


@to_dict
def node_group_template_get_all(context):
    """Get all Node Group Templates."""
    return IMPL.node_group_template_get_all(context)


@to_dict
def node_group_template_create(context, values):
    """Create a Node Group Template from the values dictionary."""
    return IMPL.node_group_template_create(context, values)


def node_group_template_destroy(context, node_group_template):
    """Destroy the Node Group Template or raise if it does not exist."""
    IMPL.node_group_template_destroy(context, node_group_template)


## Data Source ops

@to_dict
def data_source_get(context, data_source):
    """Return the Data Source or None if it does not exist."""
    return IMPL.data_source_get(context, data_source)


@to_dict
def data_source_get_all(context):
    """Get all Data Sources."""
    return IMPL.data_source_get_all(context)


@to_dict
def data_source_create(context, values):
    """Create a Data Source from the values dictionary."""
    return IMPL.data_source_create(context, values)


def data_source_destroy(context, data_source):
    """Destroy the Data Source or raise if it does not exist."""
    IMPL.data_source_destroy(context, data_source)


## JobExecutions ops

@to_dict
def job_execution_get(context, job_execution):
    """Return the JobExecution or None if it does not exist."""
    return IMPL.job_execution_get(context, job_execution)


@to_dict
def job_execution_get_all(context, **kwargs):
    """Get all JobExecutions filtered by **kwargs  e.g.
        job_execution_get_all(cluster_id=12, input_id=123)
    """
    return IMPL.job_execution_get_all(context, **kwargs)


def job_execution_count(context, **kwargs):
    """Count number of JobExecutions filtered by **kwargs  e.g.
        job_execution_count(cluster_id=12, input_id=123)
    """
    return IMPL.job_execution_count(context, **kwargs)


@to_dict
def job_execution_create(context, values):
    """Create a JobExecution from the values dictionary."""
    return IMPL.job_execution_create(context, values)


@to_dict
def job_execution_update(context, job_execution, values):
    """Create a JobExecution from the values dictionary."""
    return IMPL.job_execution_update(context, job_execution, values)


def job_execution_destroy(context, job_execution):
    """Destroy the JobExecution or raise if it does not exist."""
    IMPL.job_execution_destroy(context, job_execution)


## Job ops

@to_dict
def job_get(context, job):
    """Return the Job or None if it does not exist."""
    return IMPL.job_get(context, job)


@to_dict
def job_get_all(context):
    """Get all Jobs."""
    return IMPL.job_get_all(context)


@to_dict
def job_create(context, values):
    """Create a Job from the values dictionary."""
    return IMPL.job_create(context, values)


def job_update(context, job, values):
    """Update a Job from the values dictionary."""
    return IMPL.job_update(context, job, values)


def job_destroy(context, job):
    """Destroy the Job or raise if it does not exist."""
    IMPL.job_destroy(context, job)


@to_dict
def job_binary_get_all(context):
    """Get all JobBinarys."""
    return IMPL.job_binary_get_all(context)


@to_dict
def job_binary_get(context, job_binary):
    """Return the JobBinary or None if it does not exist."""
    return IMPL.job_binary_get(context, job_binary)


@to_dict
def job_binary_create(context, values):
    """Create a JobBinary from the values dictionary."""
    return IMPL.job_binary_create(context, values)


def job_binary_destroy(context, job_binary):
    """Destroy the JobBinary or raise if it does not exist."""
    IMPL.job_binary_destroy(context, job_binary)


@to_dict
def job_binary_internal_get_all(context):
    """Get all JobBinaryInternals."""
    return IMPL.job_binary_internal_get_all(context)


@to_dict
def job_binary_internal_get(context, job_binary_internal):
    """Return the JobBinaryInternal or None if it does not exist."""
    return IMPL.job_binary_internal_get(context, job_binary_internal)


@to_dict
def job_binary_internal_create(context, values):
    """Create a JobBinaryInternal from the values dictionary."""
    return IMPL.job_binary_internal_create(context, values)


def job_binary_internal_destroy(context, job_binary_internal):
    """Destroy the JobBinaryInternal or raise if it does not exist."""
    IMPL.job_binary_internal_destroy(context, job_binary_internal)


def job_binary_internal_get_raw_data(context, job_binary_internal_id):
    """Return the binary data field from the specified JobBinaryInternal."""
    return IMPL.job_binary_internal_get_raw_data(context,
                                                 job_binary_internal_id)

## VM ops

@to_dict
def VM_get(context, VM):
    """Return the VM or None if it does not exist."""
    return IMPL.VM_get(context, VM)


@to_dict
def VM_get_all(context, **kwargs):
    """Get all VM filtered by **kwargs  e.g.
       VM_get_all(group_name='test', tenant_name='test')
    """
    return IMPL.VM_get_all(context, **kwargs)


@to_dict
def VM_create(context, values):
    """Create a VM from the values dictionary."""
    return IMPL.VM_create(context, values)


@to_dict
def VM_update(context, vm, values):
    """Set the given properties on group and update it."""
    return IMPL.VM_update(context, vm, values)


## Site ops

@to_dict
def Site_get(context, Site):
   """Return the Site or None if it does not exist."""
   return IMPL.Site_get(context, Site)


@to_dict
def Site_get_all(context, **kwargs):
   """Get all Site filtered by **kwargs  e.g.
     Site_get_all(group_name='test', tenant_name='test')
   """
   return IMPL.Site_get_all(context, **kwargs)


@to_dict
def Site_create(context, values):
   """Create a VM from the values dictionary."""
   return IMPL.Site_create(context, values)


@to_dict
def Site_update(context, Site, values):
   """Set the given properties on group and update it."""
   return IMPL.Site_update(context, Site, values)


  ## User ops

@to_dict
def User_get(context, User):
   """Return the Site or None if it does not exist."""
   return IMPL.User_get(context, Site)


@to_dict
def User_get_all(context, **kwargs):
   """Get all User filtered by **kwargs  e.g.
    User_get_all(group_name='test', tenant_name='test')
   """
   return IMPL.User_get_all(context, **kwargs)


@to_dict
def User_create(context, values):
   """Create a VM from the values dictionary."""
   return IMPL.User_create(context, values)


@to_dict
def User_update(context, User, values):
   """Set the given properties on group and update it."""
   return IMPL.User_update(context, User, values)

