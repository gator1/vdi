# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 OpenStack Foundation
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import six.moves.urllib.parse as urlparse

from keystoneclient import exceptions as keystone_exceptions

from openstack_auth import backend
from openstack_auth import utils as auth_utils

from horizon import exceptions
from horizon import messages
from horizon.utils import functions as utils

from openstack_dashboard.api import base


LOG = logging.getLogger(__name__)
DEFAULT_ROLE = None


# Set up our data structure for managing Identity API versions, and
# add a couple utility methods to it.
class IdentityAPIVersionManager(base.APIVersionManager):
    def upgrade_v2_user(self, user):
        if getattr(user, "project_id", None) is None:
            user.project_id = getattr(user, "tenantId", None)
        return user

    def get_project_manager(self, *args, **kwargs):
        if VERSIONS.active < 3:
            manager = keystoneclient(*args, **kwargs).tenants
        else:
            manager = keystoneclient(*args, **kwargs).projects
        return manager


VERSIONS = IdentityAPIVersionManager(
    "identity", preferred_version=auth_utils.get_keystone_version())


# Import from oldest to newest so that "preferred" takes correct precedence.
try:
    from keystoneclient.v2_0 import client as keystone_client_v2
    VERSIONS.load_supported_version(2.0, {"client": keystone_client_v2})
except ImportError:
    pass

try:
    from keystoneclient.v3 import client as keystone_client_v3
    VERSIONS.load_supported_version(3, {"client": keystone_client_v3})
except ImportError:
    pass


class Service(base.APIDictWrapper):
    """Wrapper for a dict based on the service data from keystone."""
    _attrs = ['id', 'type', 'name']

    def __init__(self, service, region, *args, **kwargs):
        super(Service, self).__init__(service, *args, **kwargs)
        self.public_url = base.get_url_for_service(service, region,
                                                   'publicURL')
        self.url = base.get_url_for_service(service, region, 'internalURL')
        if self.url:
            self.host = urlparse.urlparse(self.url).hostname
        else:
            self.host = None
        self.disabled = None
        self.region = region

    def __unicode__(self):
        if(self.type == "identity"):
            return _("%(type)s (%(backend)s backend)") \
                % {"type": self.type, "backend": keystone_backend_name()}
        else:
            return self.type

    def __repr__(self):
        return "<Service: %s>" % unicode(self)


def _get_endpoint_url(request, endpoint_type, catalog=None):
    if getattr(request.user, "service_catalog", None):
        url = base.url_for(request,
                           service_type='identity',
                           endpoint_type=endpoint_type)
    else:
        auth_url = getattr(settings, 'OPENSTACK_KEYSTONE_URL')
        url = request.session.get('region_endpoint', auth_url)

    # TODO(gabriel): When the Service Catalog no longer contains API versions
    # in the endpoints this can be removed.
    bits = urlparse.urlparse(url)
    root = "://".join((bits.scheme, bits.netloc))
    url = "%s/v%s" % (root, VERSIONS.active)

    return url


def keystoneclient(request, admin=False):
    """Returns a client connected to the Keystone backend.

    Several forms of authentication are supported:

        * Username + password -> Unscoped authentication
        * Username + password + tenant id -> Scoped authentication
        * Unscoped token -> Unscoped authentication
        * Unscoped token + tenant id -> Scoped authentication
        * Scoped token -> Scoped authentication

    Available services and data from the backend will vary depending on
    whether the authentication was scoped or unscoped.

    Lazy authentication if an ``endpoint`` parameter is provided.

    Calls requiring the admin endpoint should have ``admin=True`` passed in
    as a keyword argument.

    The client is cached so that subsequent API calls during the same
    request/response cycle don't have to be re-authenticated.
    """
    user = request.user

    if admin:
        # if not user.is_superuser:
        #     raise exceptions.NotAuthorized
        endpoint_type = 'adminURL'
    else:
        endpoint_type = getattr(settings,
                                'OPENSTACK_ENDPOINT_TYPE',
                                'internalURL')

    api_version = VERSIONS.get_active_version()

    # Take care of client connection caching/fetching a new client.
    # Admin vs. non-admin clients are cached separately for token matching.
    cache_attr = "_keystoneclient_admin" if admin \
        else backend.KEYSTONE_CLIENT_ATTR
    if hasattr(request, cache_attr) and (not user.token.id
            or getattr(request, cache_attr).auth_token == user.token.id):
        LOG.debug("Using cached client for token: %s" % user.token.id)
        conn = getattr(request, cache_attr)
    else:
        endpoint = _get_endpoint_url(request, endpoint_type)
        insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
        cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
        LOG.debug("Creating a new keystoneclient connection to %s." % endpoint)
        remote_addr = request.environ.get('REMOTE_ADDR', '')
        conn = api_version['client'].Client(token=user.token.id,
                                            endpoint=endpoint,
                                            original_ip=remote_addr,
                                            insecure=insecure,
                                            cacert=cacert,
                                            auth_url=endpoint,
                                            debug=settings.DEBUG)
        setattr(request, cache_attr, conn)
    return conn


def domain_create(request, name, description=None, enabled=None):
    manager = keystoneclient(request, admin=True).domains
    return manager.create(name,
                          description=description,
                          enabled=enabled)


def domain_get(request, domain_id):
    manager = keystoneclient(request, admin=True).domains
    return manager.get(domain_id)


def domain_delete(request, domain_id):
    manager = keystoneclient(request, admin=True).domains
    return manager.delete(domain_id)


def domain_list(request):
    manager = keystoneclient(request, admin=True).domains
    return manager.list()


def domain_update(request, domain_id, name=None, description=None,
                  enabled=None):
    manager = keystoneclient(request, admin=True).domains
    return manager.update(domain_id, name, description, enabled)


def tenant_create(request, name, description=None, enabled=None,
                  domain=None, **kwargs):
    manager = VERSIONS.get_project_manager(request, admin=True)
    if VERSIONS.active < 3:
        return manager.create(name, description, enabled, **kwargs)
    else:
        return manager.create(name, domain,
                              description=description,
                              enabled=enabled, **kwargs)


def get_default_domain(request):
    """Gets the default domain object to use when creating Identity object.
    Returns the domain context if is set, otherwise return the domain
    of the logon user.
    """
    domain_id = request.session.get("domain_context", None)
    domain_name = request.session.get("domain_context_name", None)
    # if running in Keystone V3 or later
    if VERSIONS.active >= 3 and not domain_id:
        # if no domain context set, default to users' domain
        domain_id = request.user.user_domain_id
        try:
            domain = domain_get(request, domain_id)
            domain_name = domain.name
        except Exception:
            LOG.warning("Unable to retrieve Domain: %s" % domain_id)
    domain = base.APIDictWrapper({"id": domain_id,
                                  "name": domain_name})
    return domain


# TODO(gabriel): Is there ever a valid case for admin to be false here?
# A quick search through the codebase reveals that it's always called with
# admin=true so I suspect we could eliminate it entirely as with the other
# tenant commands.
def tenant_get(request, project, admin=True):
    manager = VERSIONS.get_project_manager(request, admin=admin)
    return manager.get(project)


def tenant_delete(request, project):
    manager = VERSIONS.get_project_manager(request, admin=True)
    return manager.delete(project)


def tenant_list(request, paginate=False, marker=None, domain=None, user=None):
    manager = VERSIONS.get_project_manager(request, admin=True)
    page_size = utils.get_page_size(request)

    limit = None
    if paginate:
        limit = page_size + 1

    has_more_data = False
    if VERSIONS.active < 3:
        tenants = manager.list(limit, marker)
        if paginate and len(tenants) > page_size:
            tenants.pop(-1)
            has_more_data = True
    else:
        tenants = manager.list(domain=domain, user=user)
    return (tenants, has_more_data)


def tenant_update(request, project, name=None, description=None,
                  enabled=None, domain=None, **kwargs):
    manager = VERSIONS.get_project_manager(request, admin=True)
    if VERSIONS.active < 3:
        return manager.update(project, name, description, enabled, **kwargs)
    else:
        return manager.update(project, name=name, description=description,
                              enabled=enabled, domain=domain, **kwargs)


def user_list(request, project=None, domain=None, group=None):
    if VERSIONS.active < 3:
        kwargs = {"tenant_id": project}
    else:
        kwargs = {
            "project": project,
            "domain": domain,
            "group": group
        }

    # print "request.user=", request.user
    # print "kwargs=", kwargs
    # raw_input("user_list-horizon")

    users = keystoneclient(request, admin=True).users.list(**kwargs)
    return [VERSIONS.upgrade_v2_user(user) for user in users]


def user_create(request, name=None, email=None, password=None, project=None,
                enabled=None, domain=None):
    manager = keystoneclient(request, admin=True).users
    if VERSIONS.active < 3:
        user = manager.create(name, password, email, project, enabled)
        return VERSIONS.upgrade_v2_user(user)
    else:
        return manager.create(name, password=password, email=email,
                              project=project, enabled=enabled, domain=domain)


def user_delete(request, user_id):
    return keystoneclient(request, admin=True).users.delete(user_id)


def user_get(request, user_id, admin=True):
    user = keystoneclient(request, admin=admin).users.get(user_id)
    return VERSIONS.upgrade_v2_user(user)


def user_update(request, user, **data):
    manager = keystoneclient(request, admin=True).users
    error = None

    if not keystone_can_edit_user():
        raise keystone_exceptions.ClientException(405, _("Identity service "
                                    "does not allow editing user data."))

    # The v2 API updates user model, password and default project separately
    if VERSIONS.active < 3:
        password = data.pop('password')
        project = data.pop('project')

        # Update user details
        try:
            user = manager.update(user, **data)
        except Exception:
            error = exceptions.handle(request, ignore=True)

        # Update default tenant
        try:
            user_update_tenant(request, user, project)
            user.tenantId = project
        except Exception:
            error = exceptions.handle(request, ignore=True)

        # Check for existing roles
        # Show a warning if no role exists for the project
        user_roles = roles_for_user(request, user, project)
        if not user_roles:
            messages.warning(request,
                             _('User %s has no role defined for '
                               'that project.')
                             % data.get('name', None))

        # If present, update password
        # FIXME(gabriel): password change should be its own form + view
        if password:
            try:
                user_update_password(request, user, password)
                if user.id == request.user.id:
                    return utils.logout_with_message(
                        request,
                        _("Password changed. Please log in again to continue.")
                    )
            except Exception:
                error = exceptions.handle(request, ignore=True)

        if error is not None:
            raise error

    # v3 API is so much simpler...
    else:
        if not data['password']:
            data.pop('password')
        user = manager.update(user, **data)
        if data.get('password') and user.id == request.user.id:
            return utils.logout_with_message(
                request,
                _("Password changed. Please log in again to continue.")
            )


def user_update_enabled(request, user, enabled):
    manager = keystoneclient(request, admin=True).users
    if VERSIONS.active < 3:
        return manager.update_enabled(user, enabled)
    else:
        return manager.update(user, enabled=enabled)


def user_update_password(request, user, password, admin=True):
    manager = keystoneclient(request, admin=admin).users
    if VERSIONS.active < 3:
        return manager.update_password(user, password)
    else:
        return manager.update(user, password=password)


def user_update_own_password(request, origpassword, password):
    client = keystoneclient(request, admin=False)
    client.user_id = request.user.id
    if VERSIONS.active < 3:
        return client.users.update_own_password(origpassword, password)
    else:
        return client.users.update_password(origpassword, password)


def user_update_tenant(request, user, project, admin=True):
    manager = keystoneclient(request, admin=admin).users
    if VERSIONS.active < 3:
        return manager.update_tenant(user, project)
    else:
        return manager.update(user, project=project)


def group_create(request, domain_id, name, description=None):
    manager = keystoneclient(request, admin=True).groups
    return manager.create(domain=domain_id,
                          name=name,
                          description=description)


def group_get(request, group_id, admin=True):
    manager = keystoneclient(request, admin=admin).groups
    return manager.get(group_id)


def group_delete(request, group_id):
    manager = keystoneclient(request, admin=True).groups
    return manager.delete(group_id)


def group_list(request, domain=None, project=None, user=None):
    manager = keystoneclient(request, admin=True).groups
    groups = manager.list(user=user)
    # TODO(dklyle): once keystoneclient supports filtering by
    # domain change this to use that cleaner implementation
    if domain:
        domain_groups = []
        for group in groups:
            if group.domain_id == domain:
                domain_groups.append(group)
        groups = domain_groups

    if project:
        project_groups = []
        for group in groups:
            roles = roles_for_group(request, group=group.id, project=project)
            if roles and len(roles) > 0:
                project_groups.append(group)
        groups = project_groups

    return groups


def group_update(request, group_id, name=None, description=None):
    manager = keystoneclient(request, admin=True).groups
    return manager.update(group=group_id,
                          name=name,
                          description=description)


def add_group_user(request, group_id, user_id):
    manager = keystoneclient(request, admin=True).users
    return manager.add_to_group(group=group_id, user=user_id)


def remove_group_user(request, group_id, user_id):
    manager = keystoneclient(request, admin=True).users
    return manager.remove_from_group(group=group_id, user=user_id)


def role_create(request, name):
    manager = keystoneclient(request, admin=True).roles
    return manager.create(name)


def role_get(request, role_id):
    manager = keystoneclient(request, admin=True).roles
    return manager.get(role_id)


def role_update(request, role_id, name=None):
    manager = keystoneclient(request, admin=True).roles
    return manager.update(role_id, name)


def role_delete(request, role_id):
    manager = keystoneclient(request, admin=True).roles
    return manager.delete(role_id)


def role_list(request):
    """Returns a global list of available roles."""
    return keystoneclient(request, admin=True).roles.list()


def roles_for_user(request, user, project):
    manager = keystoneclient(request, admin=True).roles
    if VERSIONS.active < 3:
        return manager.roles_for_user(user, project)
    else:
        return manager.list(user=user, project=project)


def add_tenant_user_role(request, project=None, user=None, role=None,
                         group=None, domain=None):
    """Adds a role for a user on a tenant."""
    manager = keystoneclient(request, admin=True).roles
    if VERSIONS.active < 3:
        return manager.add_user_role(user, role, project)
    else:
        return manager.grant(role, user=user, project=project,
                             group=group, domain=domain)


def remove_tenant_user_role(request, project=None, user=None, role=None,
                            group=None, domain=None):
    """Removes a given single role for a user from a tenant."""
    manager = keystoneclient(request, admin=True).roles
    if VERSIONS.active < 3:
        return manager.remove_user_role(user, role, project)
    else:
        return manager.revoke(role, user=user, project=project,
                              group=group, domain=domain)


def remove_tenant_user(request, project=None, user=None, domain=None):
    """Removes all roles from a user on a tenant, removing them from it."""
    client = keystoneclient(request, admin=True)
    roles = client.roles.roles_for_user(user, project)
    for role in roles:
        remove_tenant_user_role(request, user=user, role=role.id,
                                project=project, domain=domain)


def roles_for_group(request, group, domain=None, project=None):
    manager = keystoneclient(request, admin=True).roles
    return manager.list(group=group, domain=domain, project=project)


def add_group_role(request, role, group, domain=None, project=None):
    """Adds a role for a group on a domain or project."""
    manager = keystoneclient(request, admin=True).roles
    return manager.grant(role=role, group=group, domain=domain,
                         project=project)


def remove_group_role(request, role, group, domain=None, project=None):
    """Removes a given single role for a group from a domain or project."""
    manager = keystoneclient(request, admin=True).roles
    return manager.revoke(role=role, group=group, project=project,
                          domain=domain)


def remove_group_roles(request, group, domain=None, project=None):
    """Removes all roles from a group on a domain or project,
    removing them from it.
    """
    client = keystoneclient(request, admin=True)
    roles = client.roles.list(group=group, domain=domain, project=project)
    for role in roles:
        remove_group_role(request, role=role.id, group=group,
                          domain=domain, project=project)


def get_default_role(request):
    """Gets the default role object from Keystone and saves it as a global
    since this is configured in settings and should not change from request
    to request. Supports lookup by name or id.
    """
    global DEFAULT_ROLE
    default = getattr(settings, "OPENSTACK_KEYSTONE_DEFAULT_ROLE", None)
    if default and DEFAULT_ROLE is None:
        try:
            roles = keystoneclient(request, admin=True).roles.list()
        except Exception:
            roles = []
            exceptions.handle(request)
        for role in roles:
            if role.id == default or role.name == default:
                DEFAULT_ROLE = role
                break
    return DEFAULT_ROLE


def ec2_manager(request):
    client = keystoneclient(request)
    if hasattr(client, 'ec2'):
        return client.ec2

    # Keystoneclient 4.0 was released without the ec2 creds manager.
    from keystoneclient.v2_0 import ec2
    return ec2.CredentialsManager(client)


def list_ec2_credentials(request, user_id):
    return ec2_manager(request).list(user_id)


def create_ec2_credentials(request, user_id, tenant_id):
    return ec2_manager(request).create(user_id, tenant_id)


def get_user_ec2_credentials(request, user_id, access_token):
    return ec2_manager(request).get(user_id, access_token)


def keystone_can_edit_domain():
    backend_settings = getattr(settings, "OPENSTACK_KEYSTONE_BACKEND", {})
    can_edit_domain = backend_settings.get('can_edit_domain', True)
    multi_domain_support = getattr(settings,
                                   'OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT',
                                   False)
    return can_edit_domain and multi_domain_support


def keystone_can_edit_user():
    backend_settings = getattr(settings, "OPENSTACK_KEYSTONE_BACKEND", {})
    return backend_settings.get('can_edit_user', True)


def keystone_can_edit_project():
    backend_settings = getattr(settings, "OPENSTACK_KEYSTONE_BACKEND", {})
    return backend_settings.get('can_edit_project', True)


def keystone_can_edit_group():
    backend_settings = getattr(settings, "OPENSTACK_KEYSTONE_BACKEND", {})
    return backend_settings.get('can_edit_group', True)


def keystone_can_edit_role():
    backend_settings = getattr(settings, "OPENSTACK_KEYSTONE_BACKEND", {})
    return backend_settings.get('can_edit_role', True)


def keystone_backend_name():
    if hasattr(settings, "OPENSTACK_KEYSTONE_BACKEND"):
        return settings.OPENSTACK_KEYSTONE_BACKEND['name']
    else:
        return 'unknown'
