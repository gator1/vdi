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

"""Provides means to wrap dicts coming from DB layer in objects.

The Conductor can fetch only values represented by JSON.
That limitation comes from Oslo RPC implementation.
This module provides means to wrap a fetched value, always
dictionary, into an immutable Resource object. A descendant of
Resource class might provide back references to parent objects
and helper methods.
"""

import datetime

import six

from vdi.conductor import objects
from vdi.utils import types


def wrap(resource_class):
    """A decorator which wraps dict returned by a given function into
    a Resource.
    """

    def decorator(func):
        def handle(*args, **kwargs):
            ret = func(*args, **kwargs)
            if isinstance(ret, list):
                return [resource_class(el) for el in ret]
            elif ret:
                return resource_class(ret)
            else:
                return None

        return handle

    return decorator


class Resource(types.FrozenDict):
    """Represents dictionary as an immutable object, enhancing it with
    back references and helper methods.

    For instance, the following dictionary:
    {'first': {'a': 1, 'b': 2}, 'second': [1,2,3]}

    after wrapping with Resource will look like an object, let it be
    'res' with the following fields:
    res.first
    res.second

    'res.first' will in turn be wrapped into Resource with two fields:
    res.first.a == 1
    res.first.b == 2

    'res.second', which is a list, will be transformed into a tuple
    for immutability:
    res.second == (1,2,3)

    Additional helper methods could be specified in descendant
    classes. '_children' specifies children of that specific Resource
    in the following format: {refname: (child_class, backref_name)}
    Back reference is a reference to parent object which is
    injected into a Resource during wrapping.
    """

    _resource_name = 'resource'
    _children = {}
    _filter_fields = []

    def __init__(self, dct):
        super(Resource, self).__setattr__('_initial_dict', dct)
        newdct = dict()
        for refname, entity in dct.iteritems():
            newdct[refname] = self._wrap_entity(refname, entity)

        super(Resource, self).__init__(newdct)

    def to_dict(self):
        """Return dictionary representing the Resource for REST API.

        On the way filter out fields which shouldn't be exposed.
        """
        return self._to_dict(None)

    def to_wrapped_dict(self):
        return {self._resource_name: self.to_dict()}

    # Construction

    def _wrap_entity(self, refname, entity):
        if isinstance(entity, Resource):
            # that is a back reference
            return entity
        elif isinstance(entity, list):
            return self._wrap_list(refname, entity)
        elif isinstance(entity, dict):
            return self._wrap_dict(refname, entity)
        elif self._is_passthrough_type(entity):
            return entity
        else:
            raise TypeError("Unsupported type: %s" % type(entity).__name__)

    def _wrap_list(self, refname, lst):
        newlst = [self._wrap_entity(refname, entity) for entity in lst]

        return types.FrozenList(newlst)

    def _wrap_dict(self, refname, dct):
        if refname in self._children:
            dct = dict(dct)
            child_class = self._children[refname][0]
            backref_name = self._children[refname][1]
            if backref_name:
                dct[backref_name] = self
            return child_class(dct)
        else:
            return Resource(dct)

    def _is_passthrough_type(self, entity):
        return (entity is None or
                isinstance(entity,
                           (six.integer_types, float,
                            datetime.datetime, six.string_types)))

    # Conversion to dict

    def _to_dict(self, backref):
        dct = dict()
        for refname, entity in self.iteritems():
            if refname != backref and refname not in self._filter_fields:
                childs_backref = None
                if refname in self._children:
                    childs_backref = self._children[refname][1]
                dct[refname] = self._entity_to_dict(entity, childs_backref)

        return dct

    def _entity_to_dict(self, entity, childs_backref):
        if isinstance(entity, Resource):
            return entity._to_dict(childs_backref)
        elif isinstance(entity, list):
            return self._list_to_dict(entity, childs_backref)
        elif entity is not None:
            return entity

    def _list_to_dict(self, lst, childs_backref):
        return [self._entity_to_dict(entity, childs_backref) for entity in lst]

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, *args):
        raise types.FrozenClassError(self)


class GroupResource(Resource, objects.Group):
    _resource_name = 'group'

    # _children = {
    #     'node_groups': (NodeGroupResource, 'cluster'),
    #     'cluster_template': (ClusterTemplateResource, None)
    # }

    # _filter_fields = ['management_private_key', 'extra']


class AssignmentResource(Resource, objects.Group):
    _resource_name = 'assignment'

    # _children = {
    #     'node_groups': (NodeGroupResource, 'cluster'),
    #     'cluster_template': (ClusterTemplateResource, None)
    # }

    # _filter_fields = ['management_private_key', 'extra']


class GroupMembershipResource(Resource, objects.Group):
    _resource_name = 'group_membership'

    # _children = {
    #     'node_groups': (NodeGroupResource, 'cluster'),
    #     'cluster_template': (ClusterTemplateResource, None)
    # }

    # _filter_fields = ['management_private_key', 'extra']


class ImageResource(Resource, objects.Image):
    _resource_name = 'image'

    # _children = {
    #     'node_groups': (NodeGroupResource, 'cluster'),
    #     'cluster_template': (ClusterTemplateResource, None)
    # }

    # _filter_fields = ['management_private_key', 'extra']


class PoolResource(Resource, objects.Pool):
    _resource_name = 'pool'

    # _children = {
    #     'node_groups': (NodeGroupResource, 'cluster'),
    #     'cluster_template': (ClusterTemplateResource, None)
    # }

    # _filter_fields = ['management_private_key', 'extra']


class NodeGroupTemplateResource(Resource, objects.NodeGroupTemplate):
    _resource_name = 'node_group_template'


class InstanceResource(Resource, objects.Instance):
    _filter_fields = ['tenant_id', 'node_group_id']


class NodeGroupResource(Resource, objects.NodeGroup):
    _children = {
        'instances': (InstanceResource, 'node_group'),
        'node_group_template': (NodeGroupTemplateResource, None)
    }

    _filter_fields = ['id', 'tenant_id', 'cluster_id', 'cluster_template_id',
                      'image_username']


class ClusterTemplateResource(Resource, objects.ClusterTemplate):
    _resource_name = 'cluster_template'

    _children = {
        'node_groups': (NodeGroupResource, 'cluster_template')
    }


class ClusterResource(Resource, objects.Cluster):
    _resource_name = 'cluster'

    _children = {
        'node_groups': (NodeGroupResource, 'cluster'),
        'cluster_template': (ClusterTemplateResource, None)
    }

    _filter_fields = ['management_private_key', 'extra']


##EDP Resources

class DataSource(Resource, objects.DataSource):
    _resource_name = "data_source"
    _filter_fields = ['credentials']


class JobExecution(Resource, objects.JobExecution):
    _resource_name = "job_execution"


class Job(Resource, objects.Job):
    _resource_name = "job"


class JobBinary(Resource, objects.JobBinary):
    _resource_name = "job_binary"
    _filter_fields = ['extra']


class JobBinaryInternal(Resource, objects.JobBinaryInternal):
    _resource_name = "job_binary_internal"


class VMResource(Resource, objects.VM):
    _resource_name = 'VM'


    # _filter_fields = ['management_private_key', 'extra']

class SiteResource(Resource, objects.Site):
        _resource_name = 'Site'


        # _filter_fields = ['management_private_key', 'extra']

class UserResource(Resource, objects.User):
        _resource_name = 'User'


        # _filter_fields = ['management_private_key', 'extra']
