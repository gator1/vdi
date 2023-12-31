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

from vdi.service import api
from vdi.service.validations.edp import job_binary as b
from vdi.swift import utils as su
from vdi.tests.unit.service.validation import utils as u


class TestJobBinaryValidation(u.ValidationTestCase):
    def setUp(self):
        self._create_object_fun = b.check_job_binary
        self.scheme = b.JOB_BINARY_SCHEMA
        api.plugin_base.setup_plugins()

    def test_creation(self):
        data = {
            "name": "main.jar",
            "url": "internal-db://3e4651a5-1f08-4880-94c4-596372b37c64",
            "extra": {
            "user": "user",
            "password": "password"
            },
            "description": "long description"
        }
        self._assert_types(data)

    def test_job_binary_create_swift(self):
        self._assert_create_object_validation(
            data={
                "name": "j_o_w",
                "url": su.SWIFT_INTERNAL_PREFIX+"o.vdi/k"
            },
            bad_req_i=(1, "BAD_JOB_BINARY",
                       "To work with JobBinary located in internal "
                       "swift add 'user' and 'password' to extra"))

    # TODO(mattf): remove support for OLD_SWIFT_INTERNAL_PREFIX
    def test_job_binary_create_swift_with_old_prefix(self):
        self._assert_create_object_validation(
            data={
                "name": "j_o_w",
                "url": su.OLD_SWIFT_INTERNAL_PREFIX+"o.vdi/k"
            },
            bad_req_i=(1, "BAD_JOB_BINARY",
                       "To work with JobBinary located in internal "
                       "swift add 'user' and 'password' to extra"))

    def test_job_binary_create_internal(self):
        self._assert_create_object_validation(
            data={
                "name": "main.jar",
                "url": "internal-db://abacaba",
            },
            bad_req_i=(1, "VALIDATION_ERROR",
                       "'internal-db://abacaba' is not a "
                       "'valid_job_location'"))
