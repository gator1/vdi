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

from oslo.config import cfg
import swiftclient

import vdi.exceptions as ex
from vdi.swift import utils as su
from vdi.utils.openstack import base


CONF = cfg.CONF


def _get_conn(user, password):
    return swiftclient.Connection(base.retrieve_auth_url(),
                                  user,
                                  password,
                                  tenant_name=CONF.os_admin_tenant_name,
                                  auth_version="2.0")


def get_raw_data(context, job_binary):

    user = job_binary.extra["user"]
    password = job_binary.extra["password"]

    conn = _get_conn(user, password)

    # TODO(mattf): remove support for OLD_SWIFT_INTERNAL_PREFIX
    if not (job_binary.url.startswith(su.SWIFT_INTERNAL_PREFIX) or
            job_binary.url.startswith(su.OLD_SWIFT_INTERNAL_PREFIX)):
        # This should have been guaranteed already,
        # but we'll check just in case.
        raise ex.BadJobBinaryException("Url for binary in internal swift "
                                       "must start with %s"
                                       % su.SWIFT_INTERNAL_PREFIX)

    names = job_binary.url[job_binary.url.index("://")+3:].split("/", 1)
    if len(names) == 1:
        # We are getting a whole container, return as a dictionary.
        container = names[0]

        # First check the size...
        try:
            headers = conn.head_container(container)
            total_KB = int(headers.get('x-container-bytes-used', 0)) / 1024.0
            if total_KB > CONF.job_binary_max_KB:
                raise ex.DataTooBigException(round(total_KB, 1),
                                             CONF.job_binary_max_KB,
                                             "Size of swift container (%sKB) "
                                             "is greater than maximum (%sKB)")

            body = {}
            headers, objects = conn.get_container(names[0])
            for item in objects:
                headers, obj = conn.get_object(names[0], item["name"])
                body[item["name"]] = obj
        except swiftclient.ClientException as e:
            raise ex.SwiftClientException(e.message)

    else:
        container, obj = names
        try:
            # First check the size
            headers = conn.head_object(container, obj)
            total_KB = int(headers.get('content-length', 0)) / 1024.0
            if total_KB > CONF.job_binary_max_KB:
                raise ex.DataTooBigException(round(total_KB, 1),
                                             CONF.job_binary_max_KB,
                                             "Size of swift object (%sKB) "
                                             "is greater than maximum (%sKB)")

            headers, body = conn.get_object(container, obj)
        except swiftclient.ClientException as e:
            raise ex.SwiftClientException(e.message)

    return body
