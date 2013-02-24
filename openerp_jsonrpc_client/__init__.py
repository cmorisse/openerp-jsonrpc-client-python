# coding: utf8
import requests
import json


class OpenERPJSONRPCClientMethodNotFound(BaseException):
    pass


class OpenERPJSONRPCClientException(BaseException):
    """
    Raised when jsonrpc() returns an error response
    """
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data


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
        self._cookies = None
        self._session_id = None
        self.last_response_exception = None

        # We call get_session_info() to retreive a werkzeug cookie
        # and an openerp session_id
        first_connection = self.jsonrpc('session', 'get_session_info')
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
            params = kwargs

        post_data = {
            'json-rpc': "2.0",
            'method': 'call',
            'params': params,
            'id': self._rid,
        }

        if self._session_id:
            post_data['params']['session_id'] = self._session_id

        server_response = requests.post(self._url_for_method(service, method), json.dumps(post_data),
                                        cookies=self._cookies)
        self._rid += 1
        return server_response

    def call(self, service, method, *args, **kwargs):
        """
        is a jsonrpc() wrapper which returns jsonrpc.result as a dict
        or raise an error based on jsonrpc.error
        """
        #: :type: requests.Response
        response = self.jsonrpc(service, method, *args, **kwargs)
        if response.status_code != 200:
            raise OpenERPJSONRPCClientMethodNotFound("%s is not a valid URL."
                                                     % (self._url_for_method(service, method),))
        if response.json().get('result', False):
            self.last_response_exception = None
            return response.json()['result']

        # jsonrpc returns error as response containg an error
        # we raise an Exception based on this response content
        error_dict = response.json()['error']
        self.last_response_exception = OpenERPJSONRPCClientException(error_dict['code'],
                                                                     error_dict['message'],
                                                                     error_dict['data'])
        raise self.last_response_exception

    def get_available_services(self):
        return OpenERPJSONRPCClient.OE_SERVICES

    def get_service(self, service_name):
        if service_name in OpenERPJSONRPCClient.OE_SERVICES:
            return OpenERPServiceProxy(self, service_name)

    def get_model(self, model_name):
        return OpenERPModelProxy(self, model_name)
