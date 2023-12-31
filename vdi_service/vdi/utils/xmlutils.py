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

import re
import xml.dom.minidom as xml

import pkg_resources as pkg

from vdi import version


## hadoop.xml related utils

def load_hadoop_xml_defaults(file_name):
    doc = load_xml_document(file_name)
    configs = []
    prop = doc.getElementsByTagName('property')
    for elements in prop:
        configs.append({
            "name": _get_text_from_node(elements, 'name'),
            "value": _adjust_field(_get_text_from_node(elements, 'value')),
            "description": _adjust_field(
                _get_text_from_node(elements, 'description'))
        })
    return configs


def load_hadoop_xml_defaults_with_type_and_locale(file_name):
    doc = load_xml_document(file_name)
    configs = []
    prop = doc.getElementsByTagName('property')
    for elements in prop:
        configs.append({
            'name': _get_text_from_node(elements, 'name'),
            'value': _get_text_from_node(elements, 'value'),
            'type': _get_text_from_node(elements, 'valuetype'),
            'description': _adjust_field(
                _get_text_from_node(
                    _get_node_element(elements, 'description'), 'en'))
        })
    return configs


def _get_node_element(element, name):
    element = element.getElementsByTagName(name)
    return element[0] if element and element[0].hasChildNodes() else None


def create_hadoop_xml(configs, config_filter=None):
    doc = xml.Document()

    pi = doc.createProcessingInstruction('xml-stylesheet',
                                         'type="text/xsl" '
                                         'href="configuration.xsl"')
    doc.insertBefore(pi, doc.firstChild)

    # Create the <configuration> base element
    configuration = doc.createElement('configuration')
    doc.appendChild(configuration)

    default_configs = []
    if config_filter is not None:
        default_configs = [cfg['name'] for cfg in config_filter]

    for name, value in configs.items():
        if name in default_configs or config_filter is None:
            add_property_to_configuration(doc, name, value)

    # Return newly created XML
    return doc.toprettyxml(indent="  ")


## basic utils

def load_xml_document(file_name, strip=False):
    fname = pkg.resource_filename(
        version.version_info.package, file_name)
    if strip:
        with open(fname, "r") as f:
            doc = "".join(line.strip() for line in f)
            return xml.parseString(doc)
    else:
        return xml.parse(fname)


def _get_text_from_node(element, name):
    element = element.getElementsByTagName(name) if element else None
    return element[0].firstChild.nodeValue if (
        element and element[0].hasChildNodes()) else ''


def _adjust_field(text):
    return re.sub(r"\n *|\t", "", str(text))


def add_property_to_configuration(doc, name, value):
    prop = add_child(doc, 'configuration', 'property')
    add_text_element_to_element(doc, prop, 'name', name)
    add_text_element_to_element(doc, prop, 'value', value)


def add_properties_to_configuration(doc, parent_for_conf, configs):
    get_and_create_if_not_exist(doc, parent_for_conf, 'configuration')
    for n, v in configs.items():
        if n:
            add_property_to_configuration(doc, n, v)


def add_child(doc, parent, tag_to_add):
    actions = doc.getElementsByTagName(parent)
    actions[0].appendChild(doc.createElement(tag_to_add))
    return actions[0].lastChild


def add_element(doc, parent, element):
    actions = doc.getElementsByTagName(parent)
    actions[0].appendChild(element)
    return actions[0].lastChild


def get_and_create_if_not_exist(doc, parent, element):
    prop = doc.getElementsByTagName(element)
    if len(prop) != 0:
        return prop[0]
    return add_child(doc, parent, element)


def add_text_element_to_tag(doc, parent_tag, element, value):
    prop = add_child(doc, parent_tag, element)
    prop.appendChild(doc.createTextNode(str(value)))


def add_text_element_to_element(doc, parent, element, value):
    parent.appendChild(doc.createElement(element))
    parent.lastChild.appendChild(doc.createTextNode(str(value)))


def add_equal_separated_dict(doc, parent_tag, each_elem_tag, value):
    for k, v in value.items():
        if k:
            add_text_element_to_tag(doc, parent_tag, each_elem_tag,
                                    "%s=%s" % (k, v))


def add_tagged_list(doc, parent_tag, each_elem_tag, values):
    for v in values:
        add_text_element_to_tag(doc, parent_tag, each_elem_tag, v)
