# coding: utf8
import random
import unittest
from openerp_jsonrpc_client import *

OE_BASE_SERVER_URL = 'http://localhost:8069'


class TestDatasetService(unittest.TestCase):

    def setUp(self):
        self.server = OpenERPJSONRPCClient(OE_BASE_SERVER_URL)

    def no_test_010_setup_db(self):
        """search then read a set of objects"""
        self.server.db_drop("admin", "test_dataset")
        self.server.db_create("admin", "test_dataset", False, "Fr_fr", "admin")

    def test_020_search_read(self):
        """test search_read()"""
        result = self.server.session_authenticate("test_dataset", "admin", "admin")
        print result

        result = self.server.dataset_search_read("ir.ui.view")
        print result

    def test_030_load(self):
        """test search_read()"""
        result = self.server.session_authenticate("test_dataset", "admin", "admin")
        print result

        result = self.server.dataset_load("ir.ui.view", 1)
        print result

    def test_040_call_kw_read_direct(self):
        """test dataset/call_kw"""
        try:
            result = self.server.session_authenticate('db_test_session', 'admin', 'admin', OE_BASE_SERVER_URL)
            self.assertTrue(result, "Failed to authenticate against db_test_session database")

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
            result = self.server.session_authenticate('db_test_session', 'admin', 'admin', OE_BASE_SERVER_URL)
            self.assertTrue(result, "Failed to authenticate against db_test_session database")

            res_partner_obj = self.server.get_model('res.users')
            result = res_partner_obj.read([1], fields=['login', 'password'])
            self.assertTrue(result, "call_kw failed")
            print "call_kw() via model_proxy => %s" % result

            # we check that args, varargs combination is ok
            result = res_partner_obj.read([1], ['login', 'password'])
            self.assertTrue(result, "call_kw failed")
            print "call_kw() via model_proxy => %s" % result

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc



if __name__ == '__main__':
    unittest.main()


