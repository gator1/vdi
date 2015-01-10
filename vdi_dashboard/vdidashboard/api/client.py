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

import logging

from horizon import exceptions

from vdiclient.api import base as api_base
from vdiclient import client as api_client
from openstack_dashboard.dashboards.vdi.utils import importutils


# horizon.api is for backward compatibility with folsom
base = importutils.import_any('openstack_dashboard.api.base',
                              'horizon.api.base')

keystone = importutils.import_any('openstack_dashboard.api.keystone',
                                  'horizon.api.keystone')

LOG = logging.getLogger(__name__)


def get_horizon_parameter(name, default_value):
    import openstack_dashboard.settings

    if hasattr(openstack_dashboard.settings, name):
        return getattr(openstack_dashboard.settings, name)
    else:
        logging.info('Parameter %s is not found in local_settings.py, '
                     'using default "%s"' % (name, default_value))
        return default_value


# These parameters should be defined in Horizon's local_settings.py
# Example SAHARA_URL - http://localhost:9000/v1.0
VDI_URL = get_horizon_parameter('VDI_URL', None)
# "type" of Sahara service registered in keystone
VDI_SERVICE = get_horizon_parameter('VDI_SERVICE', 'data_processing')
# hint to generate additional Neutron network field
VDI_USE_NEUTRON = get_horizon_parameter('VDI_USE_NEUTRON', False)

AUTO_ASSIGNMENT_ENABLED = get_horizon_parameter('AUTO_ASSIGNMENT_ENABLED',
                                                True)

exceptions.RECOVERABLE += (api_base.APIException,)


def get_vdi_url(request):
    if VDI_URL is not None:
        url = VDI_URL.rstrip('/')
        if url.split('/')[-1] in ['v1.0', 'v1.1']:
            url = VDI_URL + '/' + request.user.tenant_id
        return url

    return base.url_for(request, VDI_SERVICE)


def client(request):
    endpoint_type = get_horizon_parameter('OPENSTACK_ENDPOINT_TYPE',
                                          'internalURL')
    auth_url = keystone._get_endpoint_url(request, endpoint_type)

    # print "http://" + get_sahara_url(request)
    # raw_input("client-api-client.py")

    return api_client.Client('1.0', vdi_url="http://" + get_vdi_url(request),
                             service_type=VDI_SERVICE,
                             project_id=request.user.tenant_id,
                             input_auth_token=request.user.token.id,
                             auth_url=auth_url)
