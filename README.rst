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
    - is not available on pypi yet

Introduction
============
This module:
    - allows to remotely invoked **ALL** OpenERP services defined in openerp/addons/web/controllers/main.py.
        These are the exact services called by the latest web client.
    - provides a way to conveniently call OpenERP Orm Objects methods (provided by the `dataset` service via the call_kw() method).

Why a new module when they are several netrpc and xml-rpc client library ?
__________________________________________________________________________

    1) For tests, openerp_jsonrpc_client allows to use the exact same rpc as the `Web client`.
    2) openerp_jsonrpc_client allows to use positional and keywords arguments which simplifies some calls.
    3) json-rpc is becoming the standard way to call an OpenERP Server as the `Web client is becoming the standard client.

Getting Started
===============
Let's say you an OpenERP Server 7.0 available at http://myserver.com:8069

Install the module
------------------
    * For pip and easy_install use this url: http://bitbucket.org/cmorisse/openerp-jsonrpc-client
        pip install http://bitbucket.org/cmorisse/openerp-jsonrpc-client
    * For buildout, there is an example `buildout.cfg` in the project source tree.









