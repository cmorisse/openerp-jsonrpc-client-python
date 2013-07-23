# coding: utf8
import requests
import json


class OpenERPJSONRPCClientMethodNotFoundError(BaseException):
    pass

class OpenERPJSONRPCClientServiceNotFoundError(BaseException):
    pass


class OpenERPJSONRPCClientException(BaseException):
    """
    Raised when jsonrpc() returns an error response
    """
    def __init__(self, code, message, data, json_response):
        self.code = code
        self.message = message
        self.data = data
        self.json_response = json_response


class OpenERPServiceProxy(object):
    """
    A proxy to a generic OpenERP Service (eg. db).
    """
    def __init__(self, json_rpc_client, service_name):
        self._json_rpc_client = json_rpc_client
        self.service_name = service_name

    def __getattr__(self, method):
        """
        Returns a wrapper method ready for OpenERPJSONRPCClient calls.
        """
        def proxy(*args, **kwargs):
            # TODO: extract description = kw.pop('description', None) for funkload
            return self._json_rpc_client.call(self.service_name, method, *args, **kwargs)
        return proxy


class OpenERPModelProxy(object):
    """
    A proxy to a dataset model which allow to call methods on models using call_kw.
    """
    def __init__(self, json_rpc_client, model_name):
        self._json_rpc_client = json_rpc_client
        self.model_name = model_name

    def __getattr__(self, method):
        """
        On a model, method are called using call_kw
        Returns a wrapper method ready for a call to dataset.call_kw()
        """
        def proxy(*args, **kwargs):
            # TODO: extract description = kw.pop('description', None) for funkload
            return self._json_rpc_client.call('dataset', 'call_kw', method, self.model_name, *args, **kwargs)
        return proxy


class OpenERPJSONRPCClient():
    # List of OpenERP v7.0 Available Services
    # can be found in openerp/addons/web/controllers/main.py
    OE_SERVICES = (
        'webclient', 'proxy', 'database', 'session',
        'menu', 'dataset', 'view', 'treeview', 'binary',
        'action', 'export', 'export/csv', 'export/xls',
        'report',
    )

    def __init__(self, base_url):
        self._rid = 0
        self._base_url = base_url
        self._cookies = dict()
        self._session_id = None

        # We call get_session_info() to retreive a werkzeug cookie
        # and an openerp session_id
        first_connection = self.jsonrpc('session', 'get_session_info')
        if first_connection.cookies.get('sid', False):
            self._cookies = dict(sid=first_connection.cookies['sid'])
        self._session_id = first_connection.json()['result']['session_id']

    def _url_for_method(self, service_name, method_name):
        return self._base_url + '/web/' + service_name + '/' + method_name

    def jsonrpc(self, service, method, *args, **kwargs):
        """
        Executes jsonrpc calls

        :param service: OpenERP Service to call (cf. openerp/addons/web/controllers/main.py)
        :param method: OpenERP jsonrequest method to call
        :param args: args to pass (only used for call_kw)
        :param kwargs:
        :return: result of the call
        """
        params = {}

        # For call_kw we need to inject args in an args key
        # and method and model
        if method == 'call_kw':
            params['method'] = args[0]
            params['model'] = args[1]
            params['args'] = args[2:]
            params['kwargs'] = kwargs
        else:
            # ok this is pure call, so params is a list
            if len(kwargs):
                params = {'fields': [{'name': k, 'value': v} for (k, v) in kwargs.items()]}
            else:
                params = args

        post_data = {
            'json-rpc': "2.0",
            'method': 'call',
            'params': params,
            'id': self._rid,
        }

        # we pass session_id as a cookie
        if self._session_id:
            post_data['params']['session_id'] = self._session_id

        server_response = requests.post(self._url_for_method(service, method), json.dumps(post_data),
                                        cookies=self._cookies)
        self._rid += 1
        return server_response

    def call(self, service, method, *args, **kwargs):
        """
        is a jsonrpc() wrapper which returns jsonrpc.result as a dict
        or return the whole json response in case of error
        """
        #: :type: requests.Response
        response = self.jsonrpc(service, method, *args, **kwargs)
        if response.status_code != 200:
            raise OpenERPJSONRPCClientMethodNotFoundError("%s is not a valid URL." %
                                                          (self._url_for_method(service, method),))
        json_response = response.json()
        if json_response.get('result', False):
            return json_response['result']

        # jsonrpc returns an error. So we raise an OpenERPJSONRPCClientException
        # based on the (error) response content.
        raise OpenERPJSONRPCClientException(json_response['error']['code'],
                                            json_response['error']['message'],
                                            json_response['error']['data'], json_response)

    def oe_jsonrpc(self, url, method, params={}):
        """
        Executes jsonrpc calls

        :param url: OpenERP Service/request/ to call (cf. openerp/addons/web/controllers/main.py)
        :type  url: str
        :param method: JSON-RPC method name. with OE it's always call or call_kw
        :type  method: str
        :param params: content of the JSON-RPC params dict. Must be a dict !
        :type  params: dict
        :return: result of the call
        :rtype: dict
        """
        post_data = {
            'json-rpc': "2.0",
            'method': method,
            'params': params,
            'id': self._rid,
        }
        self._rid += 1

        # we pass session_id as a cookie
        if self._session_id:
            post_data['params']['session_id'] = self._session_id

        server_response = requests.post(url, json.dumps(post_data), cookies=self._cookies)
        if server_response.status_code != 200:
            raise OpenERPJSONRPCClientMethodNotFoundError("%s is not a valid URL." % url)

        json_response = server_response.json()
        if json_response.get('result', False):
            return json_response['result']

        # jsonrpc returns an error. So we raise an OpenERPJSONRPCClientException
        # based on the (error) response content.
        raise OpenERPJSONRPCClientException(json_response['error']['code'],
                                            json_response['error']['message'],
                                            json_response['error']['data'], json_response)

    def call_with_named_arguments(self, service, method, *args, **kwargs):
        """
        use JSON-RPC named arguments style.
        each named arg is mapped to a key in the param dict()
        eg. authenticate(db='db_name', login='admin', password='admin', base_location='http://localhost:8069')
        is called with:
        {
            "jsonrpc":"2.0",
            "method":"call",
            "params": {
                "db": "db_name",
                "login": "admin",
                "password":"admin",
                "base_location":"http://localhost:8069",
                "session_id":"6fd6928ec15a48ea9a604e1d44238788",
                "context":{}
            },
            "id":"r6"
        }

        Returns jsonrpc.result as a dict
        or return the whole json response in case of error
        """
        #: :type: requests.Response
        url = self._url_for_method(service, method)
        params = kwargs
        response = self.oe_jsonrpc(url, "call", params)
        return response

    def call_with_fields_arguments(self, service, method, *args, **kwargs):
        """
        use JSON-RPC named arguments style.
        each named arg is mapped to a key in the param dict()
        eg. authenticate(db='db_name', login='admin', password='admin', base_location='http://localhost:8069')
        is called with:
        {
            "jsonrpc":"2.0",
            "method":"call",
            "params": {
                "db": "db_name",
                "login": "admin",
                "password":"admin",
                "base_location":"http://localhost:8069",
                "session_id":"6fd6928ec15a48ea9a604e1d44238788",
                "context":{}
            },
            "id":"r6"
        }

        Returns jsonrpc.result as a dict
        or return the whole json response in case of error
        """
        #: :type: requests.Response
        url = self._url_for_method(service, method)
        params = {'fields': [{'name': k, 'value': v} for (k, v) in kwargs.items()]}
        response = self.oe_jsonrpc(url, "call", params)
        return response


    def get_available_services(self):
        return OpenERPJSONRPCClient.OE_SERVICES

    def get_service(self, service_name):
        if service_name in OpenERPJSONRPCClient.OE_SERVICES:
            return OpenERPServiceProxy(self, service_name)
        raise OpenERPJSONRPCClientServiceNotFoundError()

    def get_model(self, model_name):
        return OpenERPModelProxy(self, model_name)

    #
    # database service
    #
    def db_get_list(self):
        """
        :return: list of database on server (beware of any filter in server config)
        :rtype: list
        """
        return self.call_with_named_arguments('database', 'get_list'),

    def db_create(self, super_admin_pwd, database_name, demo_data, language, user_admin_password):
        """
        Create a new database
        :param super_admin_pwd: OpenERP admin password.
        :type super_admin_pwd: str
        :param database_name: Name of the database to create?
        :type database_name: str
        :param demo_data: Shall we load "demo" data in the crated database ?"
        :type demo_data: bool
        :param language: "Translation to load (eg. Fr_fr)
        :type language: str
        :param user_admin_password: Password of the admin user of the created database
        :type user_admin_password: str
        :return:
        :rtype:
        """
        return self.call_with_fields_arguments('database', 'create',
                                               super_admin_pwd=super_admin_pwd,
                                               db_name=database_name,
                                               demo_data=demo_data,
                                               db_lang=language,
                                               create_admin_pwd=user_admin_password)

    def db_duplicate(self, super_admin_pwd, source_database_name, duplicated_database_name):
        """
        Create a new database
        :param super_admin_pwd: OpenERP admin password.
        :type super_admin_pwd: str
        :param source_database_name: Name of the database use as duplication source
        :type source_database_name: str
        :param duplicated_database_name: Name of the duplicated (destination) database
        :type duplicated_database_name: str
        :return:
        :rtype:
        """
        return self.call_with_fields_arguments('database', 'duplicate',
                                               super_admin_pwd=super_admin_pwd,
                                               db_original_name=source_database_name,
                                               db_name=duplicated_database_name)

    def db_drop(self, super_admin_pwd, database_name):
        """
        Create a new database
        :param super_admin_pwd: OpenERP admin password.
        :type super_admin_pwd: str
        :param database_name: Name of the database to delete
        :type database_name: str
        :return:
        :rtype:
        """
        return self.call_with_fields_arguments('database', 'drop',
                                               drop_pwd=super_admin_pwd,
                                               drop_db=database_name)


    #####( session service )#####
    def authenticate(self, database, user_login, user_password, server_base_location=""):
        """
        Authenticate against OpenERP and returns session_info
        :param database: database name to authenticate the user against
        :type database: str
        :param user_login: user login
        :type user_login: str
        :param user_password: user password
        :type user_password: str
        :param server_base_location: server base url ( http://host:port )
        :type server_base_location: str
        :return: session_info
        :rtype: dict
        """
        return self.call_with_named_arguments('session',
                                              'authenticate',
                                              db=database,
                                              login=user_login,
                                              password=user_password,
                                              base_location=server_base_location)