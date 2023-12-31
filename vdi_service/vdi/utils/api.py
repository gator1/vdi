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

import traceback

import flask
from werkzeug import datastructures

from vdi import context
from vdi import exceptions as ex
from vdi.openstack.common import log as logging
from vdi.openstack.common import wsgi


LOG = logging.getLogger(__name__)


class Rest(flask.Blueprint):
    def get(self, rule, status_code=200):
        return self._mroute('GET', rule, status_code)

    def post(self, rule, status_code=202):
        return self._mroute('POST', rule, status_code)

    def post_file(self, rule, status_code=202):
        return self._mroute('POST', rule, status_code, file_upload=True)

    def put(self, rule, status_code=202):
        return self._mroute('PUT', rule, status_code)

    def put_file(self, rule, status_code=202):
        return self._mroute('PUT', rule, status_code, file_upload=True)

    def delete(self, rule, status_code=204):
        return self._mroute('DELETE', rule, status_code)

    def _mroute(self, methods, rule, status_code=None, **kw):
        if type(methods) is str:
            methods = [methods]
        return self.route(rule, methods=methods, status_code=status_code, **kw)

    def route(self, rule, **options):
        status = options.pop('status_code', None)
        file_upload = options.pop('file_upload', False)

        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)

            def handler(**kwargs):
                context.set_ctx(None)

                _init_resp_type(file_upload)

                # update status code
                if status:
                    flask.request.status_code = status
                kwargs.pop("tenant_id")

                ctx = context.Context(
                    flask.request.headers['X-User-Id'],
                    flask.request.headers['X-User-Domain-Id'],
                    flask.request.headers['X-Tenant-Id'],
                    flask.request.headers['X-Auth-Token'],
                    flask.request.headers['X-Service-Catalog'],
                    flask.request.headers['X-User-Name'],
                    flask.request.headers['X-User-Domain-Name'],
                    flask.request.headers['X-Tenant-Name'],
                    flask.request.headers['X-Roles'].split(','),
                    flask.request.headers['X-Role'])
                context.set_ctx(ctx)

                if flask.request.method in ['POST', 'PUT']:
                    kwargs['data'] = request_data()

                try:
                    return func(**kwargs)
                except ex.VDIException as e:
                    return bad_request(e)
                except Exception as e:
                    return internal_error(500, 'Internal Server Error', e)

            f_rule = "/<tenant_id>" + rule
            self.add_url_rule(f_rule, endpoint, handler, **options)
            self.add_url_rule(f_rule + '.json', endpoint, handler, **options)
            self.add_url_rule(f_rule + '.xml', endpoint, handler, **options)

            return func

        return decorator


RT_JSON = datastructures.MIMEAccept([("application/json", 1)])
RT_XML = datastructures.MIMEAccept([("application/xml", 1)])


def _init_resp_type(file_upload):
    """Extracts response content type."""

    # get content type from Accept header
    resp_type = flask.request.accept_mimetypes

    # url /foo.xml
    if flask.request.path.endswith('.xml'):
        resp_type = RT_XML

    # url /foo.json
    if flask.request.path.endswith('.json'):
        resp_type = RT_JSON

    flask.request.resp_type = resp_type

    # set file upload flag
    flask.request.file_upload = file_upload


def render(res=None, resp_type=None, status=None, **kwargs):
    if not res:
        res = {}
    if type(res) is dict:
        res.update(kwargs)
    elif kwargs:
        # can't merge kwargs into the non-dict res
        abort_and_log(500, "Non-dict and non-empty kwargs passed to render")

    status_code = getattr(flask.request, 'status_code', None)
    if status:
        status_code = status
    if not status_code:
        status_code = 200

    if not resp_type:
        resp_type = getattr(flask.request, 'resp_type', RT_JSON)

    if not resp_type:
        resp_type = RT_JSON

    serializer = None
    if "application/json" in resp_type:
        resp_type = RT_JSON
        serializer = wsgi.JSONDictSerializer()
    elif "application/xml" in resp_type:
        resp_type = RT_XML
        serializer = wsgi.XMLDictSerializer()
    else:
        abort_and_log(400, "Content type '%s' isn't supported" % resp_type)

    body = serializer.serialize(res)
    resp_type = str(resp_type)

    return flask.Response(response=body, status=status_code,
                          mimetype=resp_type)


def request_data():
    if hasattr(flask.request, 'parsed_data'):
        return flask.request.parsed_data

    if not flask.request.content_length > 0:
        LOG.debug("Empty body provided in request")
        return dict()

    if flask.request.file_upload:
        return flask.request.data

    deserializer = None
    content_type = flask.request.mimetype
    if not content_type or content_type in RT_JSON:
        deserializer = wsgi.JSONDeserializer()
    elif content_type in RT_XML:
        abort_and_log(400, "XML requests are not supported yet")
        # deserializer = XMLDeserializer()
    else:
        abort_and_log(400, "Content type '%s' isn't supported" % content_type)

    # parsed request data to avoid unwanted re-parsings
    parsed_data = deserializer.deserialize(flask.request.data)['body']
    flask.request.parsed_data = parsed_data

    return flask.request.parsed_data


def get_request_args():
    return flask.request.args


def abort_and_log(status_code, descr, exc=None):
    LOG.error("Request aborted with status code %s and message '%s'",
              status_code, descr)

    if exc is not None:
        LOG.error(traceback.format_exc())

    flask.abort(status_code, description=descr)


def render_error_message(error_code, error_message, error_name):
    message = {
        "error_code": error_code,
        "error_message": error_message,
        "error_name": error_name
    }

    resp = render(message)
    resp.status_code = error_code

    return resp


def internal_error(status_code, descr, exc=None):
    LOG.error("Request aborted with status code %s and message '%s'",
              status_code, descr)

    if exc is not None:
        LOG.error(traceback.format_exc())

    error_code = "INTERNAL_SERVER_ERROR"
    if status_code == 501:
        error_code = "NOT_IMPLEMENTED_ERROR"

    return render_error_message(status_code, descr, error_code)


def bad_request(error):
    error_code = 400

    LOG.debug("Validation Error occurred: "
              "error_code=%s, error_message=%s, error_name=%s",
              error_code, error.message, error.code)

    return render_error_message(error_code, error.message, error.code)


def not_found(error):
    error_code = 404

    LOG.debug("Not Found exception occurred: "
              "error_code=%s, error_message=%s, error_name=%s",
              error_code, error.message, error.code)

    return render_error_message(error_code, error.message, error.code)
