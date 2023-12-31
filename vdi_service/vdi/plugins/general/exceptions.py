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

import vdi.exceptions as e


class NodeGroupCannotBeScaled(e.VDIException):
    def __init__(self, ng_name, reason):
        self.message = ("Chosen node group %s cannot be scaled : "
                        "%s" % (ng_name, reason))
        self.code = "NODE_GROUP_CANNOT_BE_SCALED"


class ClusterCannotBeScaled(e.VDIException):
    def __init__(self, cluster_name, reason):
        self.message = ("Cluster %s cannot be scaled : "
                        "%s" % (cluster_name, reason))
        self.code = "CLUSTER_CANNOT_BE_SCALED"


class RequiredServiceMissingException(e.VDIException):
    """A validation exception indicating that a required service
       has not been deployed
    """

    def __init__(self, service_name, required_by=None):
        self.message = 'Cluster is missing a service: %s'\
                       % service_name
        if required_by:
            self.message = '%s, required by service: %s'\
                % (self.message, required_by)

        self.code = 'MISSING_SERVICE'

        super(RequiredServiceMissingException, self).__init__()


class InvalidComponentCountException(e.VDIException):
    """A validation exception indicating that an invalid number of
       components are being deployed in a cluster
    """

    def __init__(self, component, expected_count, count):
        self.message = ("Hadoop cluster should contain {0} {1} components."
                        " Actual {1} count is {2}".format(
                        expected_count, component, count))
        self.code = "INVALID_COMPONENT_COUNT"

        super(InvalidComponentCountException, self).__init__()


class HadoopProvisionError(e.VDIException):
    """Exception indicating that cluster provisioning failed.

    A message indicating the reason for failure must be provided.
    """

    base_message = "Failed to Provision Hadoop Cluster: %s"

    def __init__(self, message):
        self.code = "HADOOP_PROVISION_FAILED"
        self.message = self.base_message % message

        super(HadoopProvisionError, self).__init__()
