=======================
OpenERP JSON-RPC Client
=======================

OpenERP-JSON-RPC-Client ( or OEJRPC ) allows to remotely interact with an OpenERP Server 7.0 with Python
using the same JSON-RPC interface used by the standard OpenERP web client.

This module :
    - has only been tested on Python 2.7
    - depends on the **requests** library available at http://python-requests.org
    - is released under the FreeBSD Licence
    - is in alpha stage

------------
Introduction
------------

This module:
    - allows to remotely invoked **ALL** OpenERP services defined in openerp/addons/web/controllers/main.py.
        These are the exact same services called by the latest web client.
    - provides a way to conveniently call OpenERP Orm Objects methods (provided by the *dataset* service via the call_kw() method).

**Why a new module when they are several NET-RPC and XML-RPC client libraries ?**
    1) For tests, openerp_jsonrpc_client allows to use the exact same rpc as the *Web client*.
    2) OEJRPC allows to remotely use **ALL** OpenERP Services (eg. Database) ; not only the Dataset Service.
    3) JSON-RPC do not authenticate at each call.
    4) JSON-RPC is becoming the standard way to call an OpenERP Server since the *Web client* is now the standard client.
    5) JSON-RPC allows to preserve context values accross calls as if they were made inside the server.
    6) openerp_jsonrpc_client allows to use positional and keywords arguments which simplifies some calls.

---------------
Getting Started
---------------

Let's say you have an OpenERP Server 7.0 running at http://localhost:8069

Install the module
==================
    * Use pip or easy_install with this url: http://bitbucket.org/cmorisse/openerp-jsonrpc-client
        ``pip install http://bitbucket.org/cmorisse/openerp-jsonrpc-client``

Import the module
==================

To run all examples below, you must: ::

    >>> import openerp_jsonrpc_client

Typical calls sequence
======================

To invoke a method, you need one Server object and various Services objects.
Some Services requires you authenticate before you call them, some others don't.

Call example that do not require authentication
-----------------------------------------------

The database.get_list() method don"t require authentication. ::

    >>> server = OpenERPJSONRPCClient('http://server:8069')
    >>> database_svc = server.get_service('database')
    >>> db_list = database_svc.get_list()

Authentication
--------------

To go further and access objects, you need to authenticate using the 'session' service: ::

    >>> session_svc = server.get_service('session')
    >>> try:
    >>>    session_info = session_svc.authenticate(db='CMoag', login='admin', password='blabla')
    >>> except OpenERPJSONRPCClientException as exc:
    >>>    print exc.code, exc.message, exc.data['fault_code']
    >>> # NOTE: exc and exc.data content exploration is left to the user as a thriving exercise
    >>> session_info
    >>> {u'username': u'admin', u'user_context': {u'lang': u'fr_FR', u'tz': False, u'uid': 1}, u'db': u'atr_dev', u'uid': 1, u'session_id': u'309e8bac985a44fe9059232fcab921f9'}

session_svc.authenticate() returns a session_info dict that you should store as it contains the user context.

Note that OEJRPC stores your session id so that you don't need to manage it in subsequent calls to
the server.

Named parameters
================

As you may have notice it in the previous example, OEJRPC supports named parameters (that XML-RPC don't support).

Let's consider the 'dataset' service search_read() method which combines a search then a read in
one server roundtrip.

The method signature is: ::

    search_read(self, req, model, fields=False, offset=0, limit=False, domain=None, sort=None)

OEJRPC allow us to call it this way (much more natural than the XML-RPC way): ::

    >>> # First we connect the server and autenticate
    >>> server = OpenERPJSONRPCClient('http://localhost:8069')
    >>> session_info = session_svc.authenticate(db='oejrpc_dev', login='admin', password='admin')
    >>> # Now we can access some data
    >>> ds_svc = server.get_service('dataset')
    >>> partners = ds_svc.search_read('res.partner', domain=[('name', 'ilike', 'cyril')])
    >>> partners
    >>> ...

Error handling
==============

You can face 2 differents error conditions:

- Exceptions due to Failure of the RPC mechanism
- Errors returned by the server

Exceptions
----------

ORJRPC raise 3 different Exceptions as shown here: ::

    >>> server = OpenERPJSONRPCClient("http://nonexistenthost")  # will raise requests.exceptions.ConnectionError
    >>> db_svc = server.get_service('databasard')                # will raise openerp_jsonrpc_client.OpenERPJSONRPCClientServiceNotFoundError
    >>> db_list = db_svc.get_listo()                             # will raise openerp_jsonrpc_client.OpenERPJSONRPCClientMethodNotFoundError

Errors
------

If your call raise an Exception on the serveur, it will return an Error.

In that case, OEJRPC will raise an OpenERPJSONRPCClientException that contains the detail of the error object
and the whole JSON response returned by the server.

Look at the OpenERPJSONRPCClientException class definition for implementation detail.

------------------------------------------------
Using OEJRPC with the different OpenERP Services
------------------------------------------------


OEJRPC provides helpers methods for some common methods.

You can find them grouped by service at the end of openerp-json-rpc-client.py

You can find usage examples in the tests files ; there is on test file per service.

OpenERPJSONRPClient is reasonably documented so don't hesitate to use python help system.

Quicklook on the Dataset service helpers functions
==================================================

Note: Take a look at test_dataset_svc.py for examples of all available functions.

OEJRPC implements the following helpers:

    - server.dataset_search_read("<model_name>")
    - server.dataset_load("<model_name>", id)
    - server.dataset_exec_workflow("<model_name">, id, "<signal_name>")

You can access model using either a proxied form or a low level.

Using a proxy:
--------------

Model proxy allows to call all objects method straight on a model object.

Example: ::

    OE_BASE_SERVER_URL = "http://localhost:8069"
    server = OpenERPJSONRPCClient(OE_BASE_SERVER_URL)
    session_info = server.session_authenticate('db_test_session', 'admin', 'admin', OE_BASE_SERVER_URL)

    try:
        res_users_obj = server.get_model('res.users')
        user = res_users_obj.read([1], ['login', 'password'])

    except OpenERPJSONRPCClientException as exc:
        print "message: %s" % exc.message
        print "data: %s" % exc.data
        print "data.type: %s" % exc.data['type']
        print "data.fault_code: %s" % exc.data['fault_code']
        raise exc


==========
References
==========

-----
Tools
-----
HTTP Scoop : To inspect HTTP Traffic