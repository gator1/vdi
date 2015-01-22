# Copyright (c) 2014 Huawei Inc.
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

import six

from vdiclient.api import base
# from vdiclient.nova import base


class Pools(base.Resource):
    resource_name = 'Pools'


class PoolManager(base.ResourceManager):
    resource_class = Pools

    def _assert_variables(self, **kwargs):
        for var_name, var_value in six.iteritems(kwargs):
            if var_value is None:
                raise base.APIException('Pool is missing field "%s"' %
                                        var_name)

    def create(self, domain_id, name, description):
        data = {'domain_id': domain_id,
                'name': name,
                'description': description}
        return self._create('/pools', data, 'pool')

    def list(self):
        return self._list('/pools', 'pools')

    def get(self, pool_id):
        return self._get('/pools/%s' % pool_id, 'pool')

    def update(self, pool_id, data):
        return self._update('/pools/%s' % pool_id, data, 'pool')

    def delete(self, pool_id):
        self._delete('/pools/%s' % pool_id)

    def get_image(self, pool_id):
        return self._list('/images?group_id=%s' % pool_id, 'images')

    def list_group_pools(self, group_id):
        return self._list('/groups/%s/pools' % group_id, 'pools')

    def list_domain_pools(self, domain_id):
        return self._list('/domains/%s/pools' % domain_id, 'pools')