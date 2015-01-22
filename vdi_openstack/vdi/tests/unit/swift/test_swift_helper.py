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

import mock

from vdi.swift import swift_helper as h
from vdi.tests.unit import base


GENERAL_PREFIX = "fs.swift."
SERVICE_PREFIX = "service.vdi."

GENERAL = ["impl", "connect.timeout", "socket.timeout",
           "connect.retry.count", "connect.throttle.delay",
           "blocksize", "partsize", "requestsize"]

SERVICE_SPECIFIC = ["auth.url", "tenant",
                    "username", "password", "http.port",
                    "https.port", "public", "location-aware",
                    "region", "apikey"]


class SwiftIntegrationTestCase(base.VdiTestCase):

    @mock.patch('vdi.utils.openstack.base.url_for')
    def test_get_swift_configs(self, authUrlConfig):
        self.setup_context(tenant_name='test_tenant')
        self.override_config("os_auth_protocol", 'http')
        self.override_config("os_auth_port", '8080')
        authUrlConfig.return_value = "http://localhost:8080/v2.0/"

        result = h.get_swift_configs()
        self.assertEqual(7, len(result))
        self.assertIn({'name': "fs.swift.service.vdi.tenant",
                       'value': 'test_tenant', 'description': ''}, result)
        self.assertIn({'name': "fs.swift.service.vdi.http.port",
                       'value': '8080', 'description': ''}, result)
