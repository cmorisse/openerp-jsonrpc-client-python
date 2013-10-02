# coding: utf8
import random
import unittest
import requests
from openerp_jsonrpc_client import *

OE_BASE_SERVER_URL = 'http://localhost:8069'


class TestDatasetService(unittest.TestCase):

    def setUp(self):
        self.server = OpenERPJSONRPCClient(OE_BASE_SERVER_URL)

    def test_010_setup_db(self):
        """search then read a set of objects"""
        # TODO: Use db_list to chech db_exists before droppping it
        db_list = self.server.db_get_list()
        if 'test_dataset' in db_list:
            result = self.server.db_drop("admin", "test_dataset")

        self.server.db_create("admin", "test_dataset", False, "Fr_fr", "admin")

        session_info = self.server.session_authenticate("test_dataset", "admin", "admin")
        module_obj = self.server.get_model('ir.module.module')
        module_ids = module_obj.search([('name', '=', 'sale')])
        module = module_obj.read(module_ids[0])

        self.assertFalse(module['state'] == 'installed', "Sales module is already installed")
        module_obj.button_immediate_install([module_ids[0]])

        module = module_obj.read(module_ids[0])
        self.assertTrue(module['state'] == 'installed', "Sales module installation failed")


    def test_020_search_read(self):
        """test search_read()"""
        result = self.server.session_authenticate("test_dataset", "admin", "admin")
        print result

        # Search then load all ir.ui.view
        result = self.server.dataset_search_read("ir.ui.view")
        print result

    def test_030_load(self):
        """test load()"""
        result = self.server.session_authenticate("test_dataset", "admin", "admin")
        print result

        result = self.server.dataset_load("ir.ui.view", 1)
        print result

    def test_040_call_kw_read_direct(self):
        """test dataset/call_kw"""
        try:
            result = self.server.session_authenticate('test_dataset', 'admin', 'admin', OE_BASE_SERVER_URL)
            self.assertTrue(result, "Failed to authenticate against db_test_dataset database")

            result = self.server.dataset_call_kw('res.users', 'read', [1], fields=['login', 'password'], context={})
            self.assertTrue(result, "call_kw failed")
            print "call_kw() => %s" % result

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    def test_050_call_kw_read_via_model_proxy(self):
        """test dataset/call_kw via Model proxy"""
        try:
            result = self.server.session_authenticate('test_dataset', 'admin', 'admin', OE_BASE_SERVER_URL)
            self.assertTrue(result, "Failed to authenticate against db_test_session database")

            res_partner_obj = self.server.get_model('res.users')

            # call with args only
            result = res_partner_obj.read([1], ['login', 'password'])
            self.assertTrue(result, "call_kw failed")
            print "call_kw() via model_proxy => %s" % result

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    def NOtest_060_exec_workflow(self):
        """test exec_workflow via Model proxy"""

        # To use this test, you must create a valid sale.order and define sale_order_id below
        sale_order_id = 2
        # TODO: Programmatically setup a sale order

        try:
            result = self.server.session_authenticate('test_dataset', 'admin', 'admin', OE_BASE_SERVER_URL)
            self.assertTrue(result, "Failed to authenticate against test_dataset database")

            result = self.server.dataset_exec_workflow('sale.order', 2, 'order_confirm')
            # self.assertTrue(result, "exec_workflow failed because it requires a draft sale order")
            # TODO: check why exec_workflow always return false

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc


if __name__ == '__main__':
    unittest.main()


