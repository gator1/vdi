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

import random
import string
import time
import uuid

from vdi.openstack.common import excutils
from vdi.tests.integration.tests import base
from vdi.utils import edp


class EDPTest(base.ITestCase):

    def _create_data_source(self, name, data_type, url, description=''):
        return self.vdi.data_sources.create(
            name, description, data_type, url, self.common_config.OS_USERNAME,
            self.common_config.OS_PASSWORD).id

    def _create_job_binary_internals(self, name, data):
        return self.vdi.job_binary_internals.create(name, data).id

    def _create_job_binary(self, name, url):
        return self.vdi.job_binaries.create(name, url,
                                               description='', extra={}).id

    def _create_job(self, name, job_type, mains, libs):
        return self.vdi.jobs.create(name, job_type, mains, libs,
                                       description='').id

    def _await_job_execution(self, job):
        timeout = self.common_config.JOB_LAUNCH_TIMEOUT * 60
        status = self.vdi.job_executions.get(job.id).info['status']
        while status != 'SUCCEEDED':
            if status == 'KILLED':
                self.fail('Job status == \'KILLED\'.')
            if timeout <= 0:
                self.fail(
                    'Job did not return to \'SUCCEEDED\' status within '
                    '%d minute(s).' % self.common_config.JOB_LAUNCH_TIMEOUT
                )
            status = self.vdi.job_executions.get(job.id).info['status']
            time.sleep(10)
            timeout -= 10

    def _create_job_binaries(self, job_data_list, job_binary_internal_list,
                             job_binary_list):
        for job_data in job_data_list:
            name = 'binary_job-%s' % str(uuid.uuid4())[:8]
            if isinstance(job_data, dict):
                for key, value in job_data.items():
                        name = 'binary_job-%s.%s' % (
                            str(uuid.uuid4())[:8], key)
                        data = value

            else:
                data = job_data
            job_binary_internal_list.append(
                self._create_job_binary_internals(name, data))
            job_binary_list.append(
                self._create_job_binary(
                    name, 'internal-db://%s' % job_binary_internal_list[-1]))

    def _delete_job(self, execution_job, job_id, job_binary_list,
                    job_binary_internal_list, input_id, output_id):
        if execution_job:
            self.vdi.job_executions.delete(execution_job.id)
        if job_id:
            self.vdi.jobs.delete(job_id)
        if job_binary_list:
            for job_binary_id in job_binary_list:
                self.vdi.job_binaries.delete(job_binary_id)
        if job_binary_internal_list:
            for internal_id in job_binary_internal_list:
                self.vdi.job_binary_internals.delete(internal_id)
        if input_id:
            self.vdi.data_sources.delete(input_id)
        if output_id:
            self.vdi.data_sources.delete(output_id)

    def _add_swift_configs(self, configs):
        swift_user = "fs.swift.service.vdi.username"
        swift_passw = "fs.swift.service.vdi.password"

        if "configs" not in configs:
            configs["configs"] = {}

        if swift_user not in configs["configs"]:
            configs["configs"][swift_user] = self.common_config.OS_USERNAME
        if swift_passw not in configs["configs"]:
            configs["configs"][swift_passw] = self.common_config.OS_PASSWORD

    @base.skip_test('SKIP_EDP_TEST',
                    'Test for EDP was skipped.')
    def edp_testing(self, job_type, job_data_list, lib_data_list=None,
                    configs=None, pass_input_output_args=False):
        try:
            swift = self.connect_to_swift()
            container_name = 'Edp-test-%s' % str(uuid.uuid4())[:8]
            swift.put_container(container_name)
            swift.put_object(
                container_name, 'input', ''.join(
                    random.choice(':' + ' ' + '\n' + string.ascii_lowercase)
                    for x in range(10000)
                )
            )

        except Exception as e:
            with excutils.save_and_reraise_exception():
                self.delete_swift_container(swift, container_name)
                print(str(e))
        input_id = None
        output_id = None
        job_id = None
        job_execution = None
        try:
            job_binary_list = []
            lib_binary_list = []
            job_binary_internal_list = []

            swift_input_url = 'swift://%s.vdi/input' % container_name
            swift_output_url = 'swift://%s.vdi/output' % container_name

            # Java jobs don't use data sources.  Input/output paths must
            # be passed as args with corresponding username/password configs
            if not edp.compare_job_type(job_type, "Java"):
                input_id = self._create_data_source(
                    'input-%s' % str(uuid.uuid4())[:8], 'swift',
                    swift_input_url)
                output_id = self._create_data_source(
                    'output-%s' % str(uuid.uuid4())[:8], 'swift',
                    swift_output_url)

            if job_data_list:
                self._create_job_binaries(
                    job_data_list, job_binary_internal_list, job_binary_list
                )
            if lib_data_list:
                self._create_job_binaries(
                    lib_data_list, job_binary_internal_list, lib_binary_list
                )
            job_id = self._create_job(
                'Edp-test-job-%s' % str(uuid.uuid4())[:8], job_type,
                job_binary_list, lib_binary_list)
            if not configs:
                configs = {}

            # Append the input/output paths with the swift configs
            # if the caller has requested it...
            if edp.compare_job_type(job_type,
                                    "Java") and pass_input_output_args:
                self._add_swift_configs(configs)
                if "args" in configs:
                    configs["args"].extend([swift_input_url,
                                            swift_output_url])
                else:
                    configs["args"] = [swift_input_url,
                                       swift_output_url]

            job_execution = self.vdi.job_executions.create(
                job_id, self.cluster_id, input_id, output_id,
                configs=configs)

            if job_execution:
                self._await_job_execution(job_execution)

        except Exception as e:
            with excutils.save_and_reraise_exception():
                print(str(e))

        finally:
            self.delete_swift_container(swift, container_name)
            self._delete_job(
                job_execution, job_id, job_binary_list+lib_binary_list,
                job_binary_internal_list, input_id, output_id
            )
