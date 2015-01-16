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

import logging
import os
import time
import traceback

import selenium.common.exceptions as selenim_except
from selenium import webdriver
import selenium.webdriver.common.by as by
from swiftclient import client as swift_client
import unittest2

import vdidashboard.tests.configs.config as cfg


logger = logging.getLogger('swiftclient')
logger.setLevel(logging.WARNING)


class UITestCase(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.ifFail = False
            cls.driver = webdriver.Firefox()
            cls.driver.get(cfg.common.base_url + "/")
            cls.find_clear_send(by.By.ID, "id_username", cfg.common.user)
            cls.find_clear_send(by.By.ID, "id_password", cfg.common.password)
            cls.driver.find_element_by_xpath(
                "//button[@type='submit']").click()
        except Exception:
            traceback.print_exc()
            cls.ifFail = True
            pass

    def setUp(self):
        if self.ifFail:
            self.fail("setUpClass method is fail")
        self.await_element(by.By.CLASS_NAME, 'clearfix',
                           'authorization failed')

    
    

#-------------------------helpers_methods--------------------------------------

    @staticmethod
    def connect_to_swift():
        return swift_client.Connection(
            authurl=cfg.common.keystone_url,
            user=cfg.common.user,
            key=cfg.common.password,
            tenant_name=cfg.common.tenant,
            auth_version=2
        )

    @staticmethod
    def delete_swift_container(swift, container):

        objects = [obj['name'] for obj in swift.get_container(container)[1]]
        for obj in objects:

            swift.delete_object(container, obj)

        swift.delete_container(container)

    @classmethod
    def find_clear_send(cls, by_find, find_element, send):
        cls.driver.find_element(by=by_find, value=find_element).clear()
        cls.driver.find_element(by=by_find, value=find_element).send_keys(send)

    def click_visible_key(self, xpath):
        keys = self.driver.find_elements_by_xpath(xpath)
        for key in keys:
            if key.is_displayed():
                key.click()

    def delete_and_validate(self, url, delete_button_id, names, undelete_names,
                            finally_delete,
                            succes_msg='Success: Deleted Template',
                            error_msg='Error: Unable to delete template',
                            info_msg='Info: Deleted Template'):
        driver = self.driver
        driver.refresh()
        driver.get(cfg.common.base_url + url)
        self.await_element(by.By.ID, delete_button_id)
        for name in names:
            # choose checkbox for this element
            try:
                driver.find_element_by_link_text("%s" % name).\
                    find_element_by_xpath("../../td[1]/input").click()
            except selenim_except.NoSuchElementException as e:
                if finally_delete:
                    pass
                else:
                    print ('element with name %s not found for delete' % name)
                    raise e
        # click deletebutton
        driver.find_element_by_id(delete_button_id).click()
        # wait window to confirm the deletion
        self.await_element(by.By.CLASS_NAME, "btn-primary")
        # confirm the deletion
        driver.find_element_by_class_name("btn-primary").click()
        exp_del_obj = list(set(names).symmetric_difference(set(
            undelete_names if undelete_names else [])))
        if not undelete_names:
            if len(names) > 1:
                succes_msg += "s"
            succes_msg += ": "
            self.check_alert("alert-success", succes_msg, names, deleted=True)
        elif not exp_del_obj:
            if len(undelete_names) > 1:
                error_msg += "s"
            error_msg += ": "
            self.check_alert("alert-error", error_msg, undelete_names,
                             deleted=False)
        else:
            if len(undelete_names) > 1:
                error_msg += "s"
            error_msg += ": "
            if len(exp_del_obj) > 1:
                info_msg += "s"
            info_msg += ": "
            self.check_alert("alert-error", error_msg, undelete_names,
                             deleted=False)
            self.check_alert("alert-info", info_msg, exp_del_obj, deleted=True)
        driver.refresh()

    def error_helper(self, message):
        driver = self.driver
        messages = message.split(", ")
        self.await_element(by.By.CLASS_NAME, "error")
        errors = driver.find_elements_by_class_name("error")
        for message in messages:
            mes = message.split(":")
            if len(mes) > 1:
                # if word count for error mesage > 1, then error message
                #  can be on the open tab or on another
                if len(mes) > 2:
                    # if word count for error mesage > 2, then error message
                    #  on another tab
                    # Click the tab indicated in the message
                    driver.find_element_by_link_text(mes.pop(0)).click()
                error = errors.pop(0).text.split("\n")
                self.assertEqual(mes[0], error[0])
                self.assertEqual(mes[1], error[1])
            else:
                self.assertEqual(mes[0], errors.pop(0).text)
        self.assertEqual(errors, [])
        driver.refresh()

    def config_helper(self, config_list):
        driver = self.driver
        for pair in config_list:
            for par, value in pair.iteritems():
                if len(par.split(":")) > 1:
                    driver.find_element_by_link_text(par.split(":")[0]).click()
                    config_id = "id_CONF:%s" % par.split(":")[0].split(" ")[0]
                    if config_id == "id_CONF:General":
                        config_id = "id_CONF:general"
                    par = par.split(":")[1]
                if par == "Show_param":
                    if value:

                        self.waiting_element_in_visible_state(
                            by.By.LINK_TEXT, "Show full configuration")
                        driver.find_element_by_link_text(
                            "Show full configuration").click()
                        self.waiting_element_in_visible_state(
                            by.By.LINK_TEXT, "Hide full configuration")
                    else:
                        self.waiting_element_in_visible_state(
                            by.By.LINK_TEXT, "Hide full configuration")
                        driver.find_element_by_link_text(
                            "Hide full configuration").click()
                        self.waiting_element_in_visible_state(
                            by.By.LINK_TEXT, "Show full configuration")
                elif par == "Filter":
                    self.find_clear_send(
                        by.By.XPATH, "//input[@class='field-filter']", value)
                else:
                    self.waiting_element_in_visible_state(
                        by.By.ID, "%s:%s" % (config_id, par))
                    if isinstance(value, bool):
                        if driver.find_element_by_id(
                                "%s:%s" % (config_id,
                                           par)).is_selected() != value:
                            driver.find_element_by_id(
                                "%s:%s" % (config_id, par)).click()
                    else:
                        self.find_clear_send(
                            by.By.ID, "%s:%s" % (config_id, par), value)

    def image_registry_helper(self, image_name, user_name, description,
                              tags_to_add, tags_to_remove, positive,
                              close_window, message, operation):
        driver = self.driver
        list_for_check_tags = []
        driver.get(cfg.common.base_url + "/vdi/image_registry/")
        self.await_element(by.By.ID, "image_registry__action_register")
        if operation == 'Registry':
            driver.find_element_by_id(
                "image_registry__action_register").click()
        else:
            #Add existing tags in the list
            list_for_check_tags = driver.\
                find_element(by=by.By.LINK_TEXT, value=image_name).\
                find_element_by_xpath('../../td[3]').text.split('\n')
            # Click "Edit Tags"
            driver.find_element(by=by.By.LINK_TEXT, value=image_name).\
                find_element_by_xpath('../../td[4]').\
                find_element(by=by.By.LINK_TEXT, value='Edit Tags').click()
        self.await_element(by.By.ID, 'id_user_name')
        if operation == 'Registry':
            driver.find_element_by_xpath("//select[@id='id_image_id']"
                                         "/option[text()='%s']"
                                         % image_name).click()
        if user_name:
            self.find_clear_send(by.By.ID, 'id_user_name', user_name)
        if description:
            self.find_clear_send(by.By.ID, 'id_description', user_name)
        if tags_to_add:
            for tag in tags_to_add:
                for first, second in tag.iteritems():
                    if first in ["vanilla", 'hdp']:
                        driver.find_element_by_xpath(
                            "//select[@id='plugin_select']/option[text()='%s']"
                            % first).click()
                        driver.find_element_by_xpath(
                            "//select[@id='vdi_version_%s']"
                            "/option[text()='%s']" % (first, second)).click()
                        driver.find_element_by_id('add_all_btn').click()
                        if first not in list_for_check_tags:
                            list_for_check_tags.append(first)
                        if second not in list_for_check_tags:
                            list_for_check_tags.append(second)
                    elif first == 'custom_tag':
                        self.find_clear_send(by.By.ID, '_vdi_image_tag',
                                             second)
                        driver.find_element_by_id('add_tag_btn').click()
                        if second not in list_for_check_tags:
                            list_for_check_tags.append(second)
                    else:
                        self.fail("Tag:%s, %s is unknown" % (first, second))
        if tags_to_remove:
            for tag in tags_to_remove:
                #click "x" in tag
                driver.find_element_by_xpath(
                    "//div[@id='image_tags_list']//span[contains(.,'%s')]//i"
                    % tag).click()
                if tag in list_for_check_tags:
                    list_for_check_tags.remove(tag)
        driver.find_element_by_id('edit_image_tags_btn').click()
        if positive:
            self.check_create_object(image_name, positive, message,
                                     [{3: list_for_check_tags}])
        else:
            if not close_window:
                self.error_helper(message)
            else:
                self.check_create_object(image_name, positive, message)

    def choose_plugin_name(self, plugin_name, vdi_version, name,
                           description, id_name):
        self.await_element(by.By.XPATH, "//*[@id='modal_wrapper']"
                                        "/div/form/div[3]/input")
        self.driver.find_element_by_xpath(
            "//select[@id='id_plugin_name']/option[text()='%s']" %
            plugin_name).click()
        if plugin_name == "Hortonworks Data Platform":
            version_id = "id_hdp_version"
        elif plugin_name == "Vanilla Apache Vdi":
            version_id = "id_vanilla_version"
        else:
            self.fail("plugin_name:%s is wrong" % plugin_name)
        self.driver.find_element_by_id(version_id).find_element_by_xpath(
            "option[text()='%s']" % vdi_version).click()
        self.driver.find_element_by_xpath("//input[@value='Create']").click()
        self.await_element(by.By.ID, id_name)
        self.find_clear_send(by.By.ID, id_name, name)
        if description:
            self.find_clear_send(by.By.ID, "id_description", description)

    def check_alert(self, alert, expected_message, list_obj, deleted=True):
        self.await_element(by.By.CLASS_NAME, alert)
        actual_message = self.find_alert_message(
            alert, first_character=2, last_character=len(expected_message)+2)
        self.assertEqual(actual_message, expected_message)
        not_expected_objs = list(set(self.find_alert_message(
            alert, first_character=len(expected_message)+2).split(
                ", ")).symmetric_difference(set(list_obj)))
        if not_expected_objs:
            self.fail("have deleted objects: %s" % not_expected_objs)
        for name in list_obj:
            if self.does_element_present(by.By.LINK_TEXT, name) == deleted:
                if deleted:
                    errmsg = "object with name:%s is not deleted" % name
                else:
                    errmsg = "object with name:%s is deleted" % name
                self.fail(errmsg)

    def find_alert_message(self, name, first_character=None,
                           last_character=None):
        driver = self.driver
        return str(driver.find_element_by_class_name("%s" % name).text[
                   first_character:last_character])

    def search_id_processes(self, process, plugin):
        return plugin.processes[process]

    def waiting_element_in_visible_state(self, how, what):
        for i in range(cfg.common.await_element):
            if self.driver.find_element(by=how, value=what).is_displayed():
                break
            time.sleep(1)
        else:
            self.fail("time out for await visible: %s , %s" % (how, what))

    def does_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except Exception as e:
            print(e.message)
            return False
        return True

    def await_element(self, by, value, message=""):
        for i in range(cfg.common.await_element):
            if self.does_element_present(by, value):
                break
            time.sleep(1)
        else:
            if not message:
                message = "time out for await: %s , %s" % (by, value)
            self.fail(message)

    def check_create_object(self, name, positive, expected_message,
                            check_columns=None, check_create_element=True):
        driver = self.driver
        expected_alert = "alert-error"
        unexpected_alert = "alert-success"
        if positive:
            expected_alert = "alert-success"
            unexpected_alert = "alert-error"
        for i in range(cfg.common.await_element):
            if self.does_element_present(by.By.CLASS_NAME, expected_alert):
                break
            elif self.does_element_present(by.By.CLASS_NAME, unexpected_alert):
                fail_mesg = self.driver.find_element(
                    by=by.By.CLASS_NAME, value=unexpected_alert).text[2:]
                self.fail("Result of creation %s is not expected: %s != %s"
                          % (name, expected_message, fail_mesg))
            time.sleep(1)
        else:
            self.fail("alert check:%s time out" % expected_alert)
        actual_message = self.driver.find_element(
            by=by.By.CLASS_NAME, value=expected_alert).text[2:]
        if check_create_element and positive:
            self.assertEqual(expected_message, str(actual_message))
            if not self.does_element_present(by.By.LINK_TEXT, name):
                self.fail("object with name:%s not found" % name)
            if check_columns:
                for column in check_columns:
                    for column_number, expected_values in column.iteritems():
                        actual_values = driver.\
                            find_element_by_link_text(name).\
                            find_element_by_xpath(
                                '../../td[%d]' % column_number).\
                            text.split('\n')
                        self.assertItemsEqual(actual_values, expected_values)
        else:
            if expected_message:
                self.assertEqual(expected_message, str(actual_message))
        self.driver.refresh()

    

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
