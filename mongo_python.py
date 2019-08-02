# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 13:55:19 2019

@author: Babak Hosseini
"""
from datetime import datetime
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
pipeline = [ 
            {"$match":{
                        "$and":[
                                  {"servertime":
                                      {"$gte": datetime(2019,7,31),"$lt": datetime(2019,8,1)}},
                                  {"deviceid":1035046}
                                ]
                     }},            

            {"$group":
                {
                  "_id":"$deviceid",    
                  "max_time":{"$max":"$servertime"},
#                  "count": {"$sum":1},
                }}
            #{"$limit":1},                                                                     
           ]

#{"deviceid":1035046}
#{"$gte": 'new ISODate("2019-07-31 00:00:08.000Z")'}},
agg_result = list(db.check.aggregate(pipeline))[0]
pprint.pprint(agg_result)
T_end = agg_result['max_time']
#%%==================== another sample
pipeline2 = [ 
            {"$match":{
                        "$and":[
                                  {"servertime":
                                      {"$gte": datetime(2019,7,31),"$lt": T_end}},
                                  {"deviceid":1035046}
                                ]
                     }},            

            {"$group":
                {
                  "_id":"$deviceid",    
                  "max_time":{"$max":"$servertime"},
#                  "count": {"$sum":1},
                }}
            #{"$limit":1},                                                                     
           ]
agg_result = list(db.check.aggregate(pipeline2))[0]
T_end_1 = agg_result['max_time']
Ts=T_end.hour-T_end_1.hour   # sampling time
#%%==================== another sample
a=db.current_op()
print(len(a['inprog']))
#agg_expl = db.command('aggregate','check',pipeline=pipeline, explain=True)

#            {"$group": {"_id":"$deviceid", "max_time":{"$max":"$servertime"}}}    


#print(client.f)

#connection = Connection()
#connection = Connection()