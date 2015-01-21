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


class VM_class(base.Resource):
    resource_name = 'VM'


# class VMManager(base.BootingManagerWithFind):
class VMManager(base.ResourceManager):
    resource_class = VM_class

    def _assert_variables(self, **kwargs):
        for var_name, var_value in six.iteritems(kwargs):
            if var_value is None:
                raise base.APIException('VM is missing field "%s"' %
                                        var_name)

    # def create(self, name, plugin_name, hadoop_version,
    #            cluster_template_id=None, default_image_id=None,
    #            is_transient=None, description=None, cluster_configs=None,
    #            node_groups=None, user_keypair_id=None,
    #            anti_affinity=None, net_id=None):
    def create(self, name, imageRef, flavorRef,
               max_count=1, min_count=1):

        data = {
            'name': name,
            'imageRef': imageRef,
            'flavorRef': flavorRef,
        }

        # data = {
        #     "server": {
        #         "name": "Test2",
        #         "imageRef": "d8051872-07b1-48ad-8717-1754d1822b6a",
        #         "flavorRef": "1",
        #         "max_count": 1,
        #         "min_count": 1
        #     }
        # }

        # if cluster_template_id is None:
        #     self._assert_variables(default_image_id=default_image_id,
        #                            cluster_configs=cluster_configs,
        #                            node_groups=node_groups)

        # self._copy_if_defined(data,
        #                       cluster_template_id=cluster_template_id,
        #                       is_transient=is_transient,
        #                       default_image_id=default_image_id,
        #                       description=description,
        #                       cluster_configs=cluster_configs,
        #                       node_groups=node_groups,
        #                       user_keypair_id=user_keypair_id,
        #                       anti_affinity=anti_affinity,
        #                       neutron_management_network=net_id)
        self._copy_if_defined(data,
                              min_count=min_count,
                              max_count=max_count)

        # print data
        # raw_input("vm-create")

        return self._create('/servers', {'server': data})
        # return self._boot('/servers',
        #                   1,
        #                   "Test",
        #                   "d8051872-07b1-48ad-8717-1754d1822b6a",
        #                   1)

    # def scale(self, cluster_id, scale_object):
    #     return self._update('/clusters/%s' % cluster_id, scale_object)
    #
    # def list(self):
    #     return self._list('/clusters', 'clusters')
    #
    # def get(self, cluster_id):
    #     return self._get('/clusters/%s' % cluster_id, 'cluster')
    #
    # def delete(self, cluster_id):
    #     self._delete('/clusters/%s' % cluster_id)
