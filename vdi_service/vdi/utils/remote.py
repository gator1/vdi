# Copyright (c) 2014 Huawei Technologies.
# Copyright (c) 2013 Hortonworks, Inc.
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

import abc

from oslo.config import cfg
import six


# These options are for SSH remote only
ssh_opts = [
    cfg.IntOpt('global_remote_threshold', default=100,
               help='Maximum number of remote operations that will '
                    'be running at the same time. Note that each '
                    'remote operation requires its own process to '
                    'run.'),
    cfg.IntOpt('cluster_remote_threshold', default=70,
               help='The same as global_remote_threshold, but for '
                    'a single cluster.'),
]

# These options are for Agent remote only
agent_opts = [
    cfg.StrOpt('rpc_server_host',
               help='A server to which guest agent running on a VM '
                    'should connect to. The parameter is needed only if '
                    'agent remote is enabled.'),
]


CONF = cfg.CONF
CONF.register_opts(ssh_opts)
CONF.register_opts(agent_opts)


DRIVER = None


@six.add_metaclass(abc.ABCMeta)
class RemoteDriver(object):
    @abc.abstractmethod
    def setup_remote(self, engine):
        """Performs driver initialization."""

    @abc.abstractmethod
    def get_remote(self, instance):
        """Returns driver specific Remote."""

    @abc.abstractmethod
    def get_userdata_template(self):
        """Returns userdata template preparing instance to work with driver."""


@six.add_metaclass(abc.ABCMeta)
class Remote(object):
    @abc.abstractmethod
    def get_neutron_info(self):
        """Returns dict which later could be passed to get_http_client."""

    @abc.abstractmethod
    def get_http_client(self, port, info=None):
        """Returns HTTP client for a given instance's port."""

    @abc.abstractmethod
    def close_http_sessions(self):
        """Closes all cached HTTP sessions."""

    @abc.abstractmethod
    def execute_command(self, cmd, run_as_root=False, get_stderr=False,
                        raise_when_error=True, timeout=300):
        """Execute specified command remotely using existing ssh connection.

        Return exit code, stdout data and stderr data of the executed command.
        """

    @abc.abstractmethod
    def write_file_to(self, remote_file, data, run_as_root=False, timeout=120):
        """Create remote file using existing ssh connection and write the given
        data to it.
        """

    @abc.abstractmethod
    def write_files_to(self, files, run_as_root=False, timeout=120):
        """Copy file->data dictionary in a single ssh connection.
        """

    @abc.abstractmethod
    def read_file_from(self, remote_file, run_as_root=False, timeout=120):
        """Read remote file from the specified host and return given data."""

    @abc.abstractmethod
    def replace_remote_string(self, remote_file, old_str, new_str,
                              timeout=120):
        """Replaces strings in remote file using sed command."""


def setup_remote(driver, engine):
    global DRIVER

    DRIVER = driver
    DRIVER.setup_remote(engine)


def get_remote(instance):
    """Returns Remote for a given instance."""
    return DRIVER.get_remote(instance)


def get_userdata_template():
    """Returns userdata template as a string."""
    return DRIVER.get_userdata_template()
