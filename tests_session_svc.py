# coding: utf8
import random
import unittest
from openerp_jsonrpc_client import *

OE_BASE_SERVER_URL = 'http://localhost:8069'


class TestSessionService(unittest.TestCase):

    def setUp(self):
        self.server = OpenERPJSONRPCClient(OE_BASE_SERVER_URL)

    def test_010_get_session_info(self):
        """Retrieve session info dict
        Note that returned content is different wether you're logged or not
        """
        session_info = self.server.session_get_info()
        print "session_info = %s" % session_info

    def test_020_authenticate(self):
        """Authenticate against a database"""
        try:
            session_info = self.server.session_get_info()
            print "session_info = %s" % session_info

            result = self.server.db_drop("admin", "db_test_session")

            result = self.server.db_create("admin", 'db_test_session', False, 'FR_fr', 'admin')
            self.assertTrue(result, "Failed to create db_test_session database" )

            result = self.server.session_authenticate('db_test_session', 'admin', 'admin', OE_BASE_SERVER_URL)
            self.assertTrue(result, "Failed to authenticate against db_test_session database")

            session_info = self.server.session_get_info()
            print "session_info = %s" % session_info

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    def test_030_sc_list(self):
        """Test session/sc_list"""
        try:
            result = self.server.session_authenticate('db_test_session', 'admin', 'admin', OE_BASE_SERVER_URL)
            self.assertTrue(result, "Failed to authenticate against db_test_session database")

            result = self.server.session_sc_list(context={'key': 'value'})
            print "sc_list = %s" % result
            self.assertTrue(result, "sc_list failed")

        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc


if __name__ == '__main__':
    unittest.main()


