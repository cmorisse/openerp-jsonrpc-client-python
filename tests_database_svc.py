# coding: utf8
import random
import unittest
from openerp_jsonrpc_client import *

OE_BASE_SERVER_URL = 'http://localhost:8069'


class TestDatabaseService(unittest.TestCase):

    # setup() is called before each test method invocation
    def setUp(self):
        self.server = OpenERPJSONRPCClient(OE_BASE_SERVER_URL)

    def test_010_get_list(self):
        """Test database/create"""
        # make sure the shuffled sequence does not lose any elements
        #db_list = self.database_svc.get_list()
        db_list = self.server.db_get_list(context={'key': 'value'})
        print "database list = %s" % db_list
        if 'db_test_01' in db_list:
            result = self.server.db_drop("admin", "db_test_01")
        if 'db_test_01_bis' in db_list:
            result = self.server.db_drop("admin", "db_test_01_bis")

    def test_020_create(self):
        """Test database/create"""
        try:
            #result = self.database_svc.create("admin", "db_test_01", False, 'FR_fr', 'admin', context={'key': 'value'})
            result = self.server.db_create("admin", "db_test_01", False, 'FR_fr', 'admin')
            print "  result: %s" % result

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    def test_030_duplicate(self):
        """Test database/duplicate"""
        try:
            result = self.server.db_duplicate("admin", "db_test_01", 'db_test_01_bis')
            self.assertTrue(result, "Duplicate failed")

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    def test_040_change_password(self):
        """Test database/change_password (admin password)"""
        print "Change Password"
        try:
            result = self.server.db_change_password("admin", "admin_new")
            print "  result: %s" % result

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    def test_050_drop(self):
        """Test database/drop"""
        print "Drop database"
        try:
            result = self.server.db_drop("admin_new", "db_test_01")
            result = self.server.db_drop("admin_new", "db_test_01_bis")
            result = self.server.db_change_password("admin_new", "admin")
            print "  result: %s" % result

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

if __name__ == '__main__':
    unittest.main()


