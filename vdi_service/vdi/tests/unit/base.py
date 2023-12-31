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

import os
import tempfile

import unittest2

from vdi import context
from vdi.db import api as db_api
from vdi import main
from vdi.openstack.common.db.sqlalchemy import session


class SaharaTestCase(unittest2.TestCase):

    def setUp(self):
        super(SaharaTestCase, self).setUp()

        self.maxDiff = None
        self.setup_context()

    def setup_context(self, username="test_user", tenant_id="tenant_1",
                      token="test_auth_token", tenant_name='test_tenant',
                      **kwargs):
        self.addCleanup(context.set_ctx,
                        context.ctx() if context.has_ctx() else None)
        context.set_ctx(context.Context(
            username=username, tenant_id=tenant_id,
            token=token, service_catalog={},
            tenant_name=tenant_name, **kwargs))

    def override_config(self, name, override, group=None):
        main.CONF.set_override(name, override, group)
        self.addCleanup(main.CONF.clear_override, name, group)


class SaharaWithDbTestCase(SaharaTestCase):
    def setUp(self):
        super(SaharaWithDbTestCase, self).setUp()
        self.setup_db()

    def setup_db(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        session.set_defaults('sqlite:///' + self.db_path, self.db_path)
        db_api.setup_db()
        self.addCleanup(self._drop_db)

    def _drop_db(self):
        db_api.drop_db()
        os.close(self.db_fd)
        os.unlink(self.db_path)
