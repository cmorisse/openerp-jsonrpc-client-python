# coding: utf8

#    Copyright (c) 2013, Cyril MORISSE ( @cmorisse )
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# TODO: Add a shortcut to ir.model.data.get_object_reference('module', identifier')
# TODO: Add a complete example of OpenERP configuration with wizard and settings to enable exec_workflow test
# TODO: By default, reinject in every call, the context got by authenticate
# TODO: coverage ?
# TODO: publish on pypi

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
            return self._json_rpc_client.dataset_call_kw(self.model_name, method, *args, **kwargs)

        return proxy


class OpenERPJSONRPCClient():
    # List of OpenERP v7.0 Available Services
    # can be found in openerp/addons/web/controllers/main.py
    OE_SERVICES = (
        'webclient', 'proxy', 'session', 'database',
        'menu', 'dataset', 'view', 'treeview', 'binary',
        'action', 'export', 'export/csv', 'export/xls',
        'report',
    )

    def __init__(self, base_url):
        self._rid = 0  # a unique request id incremented at each request
        self._base_url = base_url
        self._cookies = dict()
        self._session_id = None
        self.user_context = None

        # We call get_session_info() to retreive a werkzeug cookie
        # and an OpenERP session_id
        first_connection = self.jsonrpc(self._url_for_method('session', 'get_session_info'),
                                        'call',
                                        session_id=None,
                                        context={})
        if first_connection.cookies.get('sid', False):
            self._cookies = dict(sid=first_connection.cookies['sid'])
        self._session_id = first_connection.json()['result']['session_id']

    def _url_for_method(self, service_name, method_name):
        return self._base_url + '/web/' + service_name + '/' + method_name

    def jsonrpc(self, url, method, *args, **kwargs):
        """
        Executes a "standard" JSON-RPC calls

        :param url: url of the end point to call
        :param method: JSONRPC method to call
        :param args: positional args if any
        :param kwargs: keyword args if any
        :return: result of the call
        """

        # JSONRPC do not allow to mix positional and keyword arguments
        # If args are defined we use them, else we try with keywords args then fallback to None
        params = args or kwargs

        post_data = {
            'json-rpc': "2.0",
            'method': method,
            'params': params,
            'id': self._rid,
        }

        server_response = requests.post(url, json.dumps(post_data), cookies=self._cookies)
        self._rid += 1
        return server_response

    def oe_jsonrpc(self, url, method, params={}):
        """
        Executes an OpenERP flavored JSON-RPC calls :
        - pass OpenERP _session_id along each request
        - return the result key of the Call Response dict or raise an Exception

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

        # We pass OpenERP _session_id at each request
        if self._session_id:
            post_data['params']['session_id'] = self._session_id

        server_response = requests.post(url, json.dumps(post_data), cookies=self._cookies)
        if server_response.status_code != 200:
            raise OpenERPJSONRPCClientMethodNotFoundError("%s is not a valid URL." % url)

        json_response = server_response.json()

        try:
            return json_response['result']
        except KeyError:
            pass

        # JSON-RPC returns an error. So we raise an OpenERPJSONRPCClientException
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
        use JSON-RPC named arguments style but all OpenERP args are stored in a dict under a "fields" named parameter
        eg. authenticate(db='db_name', login='admin', password='admin', base_location='http://localhost:8069')
        is called with:
        {
            "jsonrpc":"2.0",
            "method":"call",
            "params": {
                'fields': {
                    "db": "db_name",
                    "login": "admin",
                    "password":"admin",
                    "base_location":"http://localhost:8069",
                },
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

        # we extract context which must not be encoded as a "field" and remain a param
        context = kwargs['context']
        del kwargs['context']

        # let's add all kwargs as fields items
        params = {'fields': [{'name': k, 'value': v} for (k, v) in kwargs.items()]}

        # we re-inject context at the same level as "fields"
        params['context'] = context

        response = self.oe_jsonrpc(url, "call", params)
        return response

    @property
    def get_available_services(self):
        return OpenERPJSONRPCClient.OE_SERVICES

    def get_service(self, service_name):
        if service_name in OpenERPJSONRPCClient.OE_SERVICES:
            return OpenERPServiceProxy(self, service_name)
        raise OpenERPJSONRPCClientServiceNotFoundError()

    def get_model(self, model_name):
        """OpenERP self.pool.get(...) equivalent"""
        return OpenERPModelProxy(self, model_name)

    #
    # database service
    #
    def db_get_list(self, context={}):
        """
        :return: list of database on server (beware of any filter in server config)
        :rtype: list
        """
        return self.call_with_named_arguments('database', 'get_list', context=context)

    def db_create(self, super_admin_pwd, database_name, demo_data, language, user_admin_password, context={}):
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
                                               create_admin_pwd=user_admin_password,
                                               context=context)

    def db_duplicate(self, super_admin_pwd, source_database_name, duplicated_database_name, context={}):
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
                                               db_name=duplicated_database_name,
                                               context=context)

    def db_drop(self, super_admin_pwd, database_name, context={}):
        """
        Create a new database
        :param super_admin_pwd: OpenERP admin password.
        :type super_admin_pwd: str
        :param database_name: Name of the database to drop
        :type database_name: str
        :return:
        :rtype:
        """
        return self.call_with_fields_arguments('database', 'drop',
                                               drop_pwd=super_admin_pwd,
                                               drop_db=database_name,
                                               context=context)

    def db_change_password(self, old_pwd, new_pwd, context={}):
        """
        Change OpenERP admin password
        :param old_pwd: Current OpenERP admin password.
        :type old_pwd: str
        :param new_pwd: New OpenERP admin password to let
        :type new_pwd: str
        :return:
        :rtype:
        """
        return self.call_with_fields_arguments('database', 'change_password',
                                               old_pwd=old_pwd,
                                               new_pwd=new_pwd,
                                               context=context)

    #
    # Session service
    #
    def session_get_info(self, context={}):
        """
        Retreive session information
        :return: a dict containing session information
        """
        return self.call_with_named_arguments('session', 'get_session_info', context=context)

    def session_authenticate(self, db, login, password, base_location=None, context={}):
        """
        Authenticate against a database.

        :param db:
        :param login:
        :param password:
        :param base_location:
        :return:
        """
        result = self.call_with_named_arguments('session',
                                                'authenticate',
                                                db=db,
                                                login=login,
                                                password=password,
                                                base_location=base_location,
                                                context=context)
        self.user_context = result.get('user_context', {})
        return result

    def session_sc_list(self, context={}):
        """
        Retreive session information
        :return: a dict containing session information
        """
        return self.call_with_named_arguments('session', 'sc_list', context=context)

    #
    # Dataset service
    #
    def dataset_search_read(self, model, fields=False, offset=0, limit=False, domain=[], sort=None, context={}):
        """
        Perform a serch and a read in the same roundtrip
        :param model: Model involved in search
        :param fields: Fields you want to fetch. All by default
        :param offset: Offset of the first record you want to fetch. 0 by default
        :param limit: Number of record you want to fetch. All by default
        :param domain: An OpenERP domain specifying search_criteria. All records by default (OpenERP expects an empty domain( [] ) in that case)
        :param sort: Columns to sort record by. osv.Model _order attribute by default
        :return:
        """
        return self.call_with_named_arguments('dataset', 'search_read',
                                              model=model,
                                              fields=fields,
                                              offset=offset,
                                              limit=limit,
                                              domain=domain,
                                              sort=sort,
                                              context=context)

    def dataset_load(self, model, id, fields=False, context={}):
        """
        Load all fields of one object identified by a model and an id
        :param model: Model to load
        :param id: identifier of the object to load (only one)
        :param fields: Exists but unused in the controller definition
        :return: a dict with one key named "value" containing a dict of all object fields
        """
        return self.call_with_named_arguments('dataset', 'load',
                                              model=model,
                                              id=id,
                                              fields=fields,
                                              context=context)

    def dataset_call_kw(self, model, method, *args, **kwargs):
        """
        Packs args and kwargs so that they are compatible with dataset/call_kw json request
        then invoke dataset/call_kw

        We pack arguments so that they conform to this structure:
        {
            "id": "r78",
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "method": "create",
                "model": "res.users",
                "args": [
                    {
                        "action_id": false,
                        "active": true,
                        "company_id": 1,
                        "company_ids": [
                            [
                                6,
                                false,
                                [
                                    1
                                ]
                            ]
                        ],
                        ...
                    }
                ],
                "kwargs": {
                    "context": {
                        "lang": "Fr_fr",
                        "tz": false,
                        "uid": 1
                    }
                },
                "context": {
                    "lang": "Fr_fr",
                    "tz": false,
                    "uid": 1
                },
                "session_id": "d3b252a5526646b0b3073d4114d86bda"
            }
        }

        This method is used by OpenERPModelProxy
        """

        url = self._url_for_method('dataset', 'call_kw')

        # we build params
        params = {
            'method': method,
            'model': model,
            'args': args,
            'kwargs': kwargs,
            # if there is a context in kw_args, we duplicate it at "params" level
            'context': kwargs.get('context', {})
        }

        response = self.oe_jsonrpc(url, "call", params)
        return response

    def dataset_exec_workflow(self, model, id, signal):
        """Trigger signal on object id of model

        :return: workflow execution result
        """
        return self.call_with_named_arguments('dataset', 'exec_workflow',
                                              model=model,
                                              id=id,
                                              signal=signal)

    # Note: We don't implement exec_button() as it modifies returned action values in a way which is not consistent
    #       with server side behavior