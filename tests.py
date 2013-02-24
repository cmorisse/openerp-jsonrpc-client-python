# coding=utf8
__author__ = 'cmorisse'
import requests
import cookielib
import json
from oe_json_rpc_client import *


OE_BASE_SERVER_URL = 'http://inouk.fr:8070'

# client instanciation, sets-up werkzeug session (sid cookie) and openerp session (session_id)
server = OpenERPJSONRPCClient(OE_BASE_SERVER_URL)

database_svc = server.get_service('database')
print "database list=%s" % database_svc.get_list()

session_svc = server.get_service('session')
print session_svc.authenticate(db='atr_test', login='admin', password='OpenAT&R=2013')
session_info = session_svc.get_session_info()
context = session_info['user_context']
print "session_info =", session_info
print "context =", context

# we test methods as they appeat web/controllers/main.py
dataset_svc = server.get_service('dataset')
context['tz'] = 'Europe/Paris'
result = dataset_svc.search_read(model='res.partner',
                                 fields=['id'],
                                 #fields=['title', 'name', 'city', 'country'],
                                 domain=[('name', 'ilike', 'cyril')], context=context)
                                 #offset=5, limit=10)
print result
id_cyril = result['records'][0]['id']
print id_cyril


partner_obj = server.get_model('res.partner')
id = partner_obj.create({'name': 'Christal'}, context=context)
print "new id = %s" % (id,)


# we create a user

#new_id = dataset_svc.call_kw(model='res.partner',
#                                 fields=['id'],
                                 #fields=['title', 'name', 'city', 'country'],
#                                 domain=[('name', 'ilike', 'cyril')], context=context)
#offset=5, limit=10)







# we update name of user cyril


# call of model standard model via call_kw ( create, read, search, ...)
#call_kw

# call of special method via call_kw
#call_kw

exit( )





# r5 : appel classqiue à read
request_num = 1
request_dict_data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "res.partner",
        "method": "read",
        "args": [
            [ 31, 30 ],
            [
                "color",
                "street",
                "city",
                "title",
                "country_id",
                "parent_id",
                "is_company",
                "email",
                "function",
                "fax",
                "zip",
                "street2",
                "phone",
                "name",
                "mobile",
                "has_image",
                "state_id",
                "__last_update"
            ]
        ],
        "kwargs": {
            "context": {
                "lang": "fr_FR",
                "tz": "Europe/Paris",
                "uid": 1
            }
        },
        'session_id': oe_session_id,
        "context": {
            "lang": "fr_FR",
            "tz": "Europe/Brussels",
            "uid": 1
        }
    },
    'id': "r%d" % request_num
}
url = OE_BASE_SERVER_URL + '/web/dataset/call_kw'
r5 = requests.post(url, json.dumps(request_dict_data), cookies=werkzeug_session_cookie)
print "r5: %s" % r5.status_code
print r5.json()


# r6 : create
request_num += 1
request_dict_data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "res.partner",
        "method": "create",
        "args": [
            {
                "name": "Cyril_%s" % request_num,
                "category_id": [
                    [ 6, False, [ ] ]
                ],
                "type": "default",
                "use_parent_address": True,
                "company_id": 1,
                "customer": True,
                "supplier": False,
                "lang": "fr_FR",
                "active": True,
                "opt_out": False,
                "credit_limit": 0,
            }
        ],
        "kwargs": {
            "context": {
                "lang": "fr_FR",
                "tz": "Europe/Brussels",
                "uid": 1,
                "search_default_customer": 1
            }
        },
        "context": {
            "lang": "fr_FR",
            "tz": "Europe/Brussels",
            "uid": 1
        },
        'session_id': oe_session_id,
    },
    'id': "r%d" % request_num
}
url = OE_BASE_SERVER_URL + '/web/dataset/call_kw'
r6 = requests.post( url, json.dumps( request_dict_data ), cookies=werkzeug_session_cookie )
print "r6: %s" % r5.status_code
print r6.json( )
