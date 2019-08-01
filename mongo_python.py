# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 13:55:19 2019

@author: Babak Hosseini
"""

import pymongo
#from pymongo import Connection
from pymongo import MongoClient
import pprint

Mclient = MongoClient('mongodb://192.168.2.208:27018')

db = Mclient.sms
db.list_collection_names()

clients = db['client']
checks = db['check']
#%%=======================
pprint.pprint(clients.find_one(
        {
#                servertime: {"$gt": new ISODate("2019-07-26 01:00:55.000Z")}
            "name":"101 - Busold Consulting"
        }))
#%%=======================
result = checks.find_one(
        {
#                servertime: {"$gt": new ISODate("2019-07-26 01:00:55.000Z")}
            "deviceid":1156225
        })

pprint.pprint(result)
#%%============
results = checks.find(
        {
            "deviceid":1156225
        }
        ).limit(2)

for result in results:
    pprint.pprint(result)
#%%============
clients.count_documents({})
#%%============ ?? list of enabled devices

#%%============ find last entry
agg_result = 
????from bson.son import SON
>>> pipeline = [
...     {"$unwind": "$tags"},
...     {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
...     {"$sort": SON([("count", -1), ("_id", -1)])}
... ]
>>> import pprint
>>> pprint.pprint(list(db.things.aggregate(pipeline)))
[{u'_id': u'cat', u'count': 3},
 {u'_id': u'dog', u'count': 2},
 {u'_id': u'mouse', u'count': 1}]


#print(client.f)

#connection = Connection()
#connection = Connection()