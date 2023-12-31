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

import webob.exc as ex

from vdi.openstack.common import log as logging
import vdi.openstack.commons as commons


LOG = logging.getLogger(__name__)


class AuthValidator:
    """Handles token auth results and tenants."""

    def __init__(self, app, conf):
        self.app = app
        self.conf = conf

    def __call__(self, env, start_response):
        """Ensures that tenants in url and token are equal.

        Handle incoming request by checking tenant info prom the headers and
        url ({tenant_id} url attribute).

        Pass request downstream on success.
        Reject request if tenant_id from headers not equals to tenant_id from
        url.
        """
        token_domain = env['HTTP_X_USER_DOMAIN_ID']
        if not token_domain:
            LOG.warn("Can't get domain_id from env")
            resp = ex.HTTPServiceUnavailable()
            return resp(env, start_response)

        # token_tenant = env['HTTP_X_TENANT_ID']
        # if not token_tenant:
        #     LOG.warn("Can't get tenant_id from env")
        #     resp = ex.HTTPServiceUnavailable()
        #     return resp(env, start_response)

        path = env['PATH_INFO']
        if path not in ['/', '/api/help']:
            version, url_target, rest = commons.split_path(path, 3, 3, True)
            if not version or not url_target or not rest:
                LOG.info("Incorrect path: %s", path)
                resp = ex.HTTPNotFound("Incorrect path")
                return resp(env, start_response)

            if token_domain != url_target:
                LOG.debug("Unauthorized: token domain != requested domain")
                resp = ex.HTTPUnauthorized('Token domain != requested domain')
                return resp(env, start_response)

            # if token_tenant != url_target:
            #     LOG.debug("Unauthorized: token tenant != requested tenant")
            #     resp = ex.HTTPUnauthorized('Token tenant != requested tenant')
            #     return resp(env, start_response)

        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_filter(app):
        return AuthValidator(app, conf)

    return auth_filter
