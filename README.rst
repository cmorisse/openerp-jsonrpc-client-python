=======================
OpenERP JSON-RPC Client
=======================

This module allows to remotely interact with an OpenERP Server 7.0 with Python
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
        These are the exact services called by the latest web client.
    - provides a way to conveniently call OpenERP Orm Objects methods (provided by the *dataset* service via the call_kw() method).

**Why a new module when they are several NET-RPC and XML-RPC client libraries ?**
    1) For tests, openerp_jsonrpc_client allows to use the exact same rpc as the *Web client*.
    2) json-rpc is becoming the standard way to call an OpenERP Server as the *Web client* is becoming the standard client.
    3) json-rpc allows to preserve context values accross calls as if they were made inside the server.
    4) openerp_jsonrpc_client allows to use positional and keywords arguments which simplifies some calls.

---------------
Getting Started
---------------

Install the module
==================
    * Use pip or easy_install with this url: http://bitbucket.org/cmorisse/openerp-jsonrpc-client
        ``pip install http://bitbucket.org/cmorisse/openerp-jsonrpc-client``



Let's say you an OpenERP Server 7.0 available at http://myserver.com:8069

--------
Overview
--------

OEJRPC allow to programmaticaly interect with OpenERP using the same proctocol as the web client.

Error handling
==============

As an RPC framework, you can face X differents error conditions:
- Failure of the RPC
- Failure of the remote call invoked

Example
server = OpenERPJSONRPCClient("http://nonexistenthost")
will raise requests.exceptions.ConnectionError

db_svc = server.get_service('databasard')
will raise a openerp_jsonrpc_client.OpenERPJSONRPCClientServiceNotFoundError

db_list = db_svc.get_listo()
willraise a openerp_jsonrpc_client.OpenERPJSONRPCClientMethodNotFoundError


Named parameters
================

OEJRPC supports named parameters (that XML-RPC don't support).

Let's consider 'dataset' service search_read() method which combines a search and a read in
one server roundtrip.

The method signature is:
    search_read(self, req, model, fields=False, offset=0, limit=False, domain=None, sort=None)

OEJRPC allow us to call it this way:
::
    >>> # First we connect the server and autenticate
    >>> server = OpenERPJSONRPCClient('http://localhost:8069')
    >>> session_info = session_svc.authenticate(db='oejrpc_dev', login='admin', password='admin')
    >>> # Now wa can access some data
    >>> ds_svc = server.get_service('dataset')
    >>> cyril_partners = ds_svc.search_read('res.partner', domain=[('name', 'ilike', 'cyril')])
    >>> cyril_partners


Typical calls sequence
======================

To invoke a method, you need one server object and various services objects.
Once you get them, you can call all the methods which do not require you to be authenticated
(mainly the function used by the "Manage Databases" menu.
::
    server = OpenERPJSONRPCClient('http://server:8069')
    database_svc = server.get_service('database')
    db_list = database_svc.get_list()

To go further and access objects, you need to authenticate using the 'session' service:
::
    >>> session_svc = server.get_service('session')
    >>> try:
    >>>    session_info = session_svc.authenticate(db='CMoag', login='admin', password='blabla')
    >>> except OpenERPJSONRPCClientException as exc:
    >>>    print exc.code, exc.message, exc.data['fault_code']
    >>> # NOTE: exc and exc.data content exploration is left to the user as a thriving exercise
    >>> session_info
    {u'username': u'admin', u'user_context': {u'lang': u'fr_FR', u'tz': False, u'uid': 1}, u'db': u'atr_dev', u'uid': 1, u'session_id': u'309e8bac985a44fe9059232fcab921f9'}

session_svc.authenticate() returns a session_info dict that you should store as it contains
the user context.

Not OEJRPC stores your session id so that you don't need to manage it in subsequent calls to
the server.

Accessing OpenERP objects (Dataset service)
---------------------------------------

The "dataset" service allows to access osv objects.
This service:
    - provides some helper functions to manipulate objects
    - allows to call osv objects methods

Dataset service helpers functions
`````````````````````````````````
These functions are defined in the Dataset class (``$OPENERP_ROOT/openerp/addons/web/controllers/main.py``).

Functions available via the JSON-RPC protocol are annotated with @openerpweb.jsonrequest

Let's take a look at these 2 functions:
    - search_read()
    - call_kw()

search_read()
'''''''''''''
search_read() is just a way to execute a search then a read in one server roundrip.
::
    >>> # First we connect the server and autenticate
    >>> server = OpenERPJSONRPCClient('http://localhost:8069')
    >>> session_info = session_svc.authenticate(db='CMoag', login='admin', password='blabla')
    >>> context = session_info['context']

    >>> dataset_svc = server.get_service('dataset')
    >>> context['tz'] = 'Europe/Paris'
    >>> result = dataset_svc.search_read(model='res.partner',
    >>>                                  fields=['state', 'name', 'date_deadline'],
    >>>                                  context=context)
    >>> result
    ....





==========
References
==========

-----
Tools
-----
HTTP Scoop : Nothing would have been possible without this tool.










=======
Titre 1
=======

coucou

-------
Titre 2
-------

coucou


Titre 3
=======

coucou

Titre 4
-------

coucou

Titre 5
```````

coucou

Titre 6
'''''''

coucou


Titre 7
.......

coucou

Titre 8
~~~~~~~

coucou

Titre 9
*******

coucou

Titre 10
++++++++

coucou

Titre 11
^^^^^^^^

coucou
