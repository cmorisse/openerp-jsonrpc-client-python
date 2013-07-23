# coding: utf8
# TODO: Tester toutes les fonctions du service database
import random
import unittest
from openerp_jsonrpc_client import *

OE_BASE_SERVER_URL = 'http://localhost:8069'

# TODO: client instanciation, sets-up werkzeug session (sid cookie) and openerp session (session_id)


class TestDatabaseService(unittest.TestCase):

    # setup() is called before each test method invocation
    def setUp(self):
        self.server = OpenERPJSONRPCClient(OE_BASE_SERVER_URL)

    def test_000_get_list(self):
        print "in test_000_get_list()"
        # make sure the shuffled sequence does not lose any elements
        db_list = self.server.db_get_list()
        print "database list=%s" % db_list

    def test_010_create(self):
        print "in test_100_create()"
        try:
            result = self.server.db_create('OpenAT&R=2013', "db_test_01", False, 'FR_fr', 'admin')
            print "  result: %s" % result
        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    def test_020_duplicate(self):
        """
        Test database/duplicate
        :return:
        :rtype:
        """
        try:
            result = self.server.db_duplicate('OpenAT&R=2013', "db_test_01", 'db_test_01_bis')
            print "  result: %s" % result
        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    def test_030_drop(self):
        """
        Test database/ddrop
        :return:
        :rtype:
        """
        try:
            result = self.server.db_drop('OpenAT&R=2013', "db_test_01")
            result = self.server.db_drop('OpenAT&R=2013', "db_test_01_bis")
            print "  result: %s" % result
        except OpenERPJSONRPCClientException as exc:
            print "message: %s" % exc.message
            print "data: %s" % exc.data
            print "data.type: %s" % exc.data['type']
            print "data.fault_code: %s" % exc.data['fault_code']
            raise exc

    #TODO: implement chnage_password
    # @openerpweb.jsonrequest
    # def change_password(self, req, fields):
    #     old_password, new_password = operator.itemgetter(
    #         'old_pwd', 'new_pwd')(
    #             dict(map(operator.itemgetter('name', 'value'), fields)))
    #     try:
    #         return req.session.proxy("db").change_admin_password(old_password, new_password)
    #     except xmlrpclib.Fault, e:
    #         if e.faultCode and e.faultCode.split(':')[0] == 'AccessDenied':
    #             return {'error': e.faultCode, 'title': _('Change Password')}
    #     return {'error': _('Error, password not changed !'), 'title': _('Change Password')}





if __name__ == '__main__':
    unittest.main()


