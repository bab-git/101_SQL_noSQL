# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 13:55:19 2019

@author: Babak Hosseini
"""
import numpy as np
from datetime import datetime
import pandas as pd
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
#%%==================== List of active devices for the month
# getting list of device ids for WK ans servers
pipelin3 = [
           {
           "$lookup":
                     {
                       "from": "site",
                       "localField": "siteid",
                       "foreignField": "_id",
                       "as": "site"
                      }    
            },
            {
                "$unwind": {"path": "$site", "preserveNullAndEmptyArrays": True}
            },
            {
                 "$lookup": 
                    {
                        "from": "client",
                        "localField": "site.clientid",
                        "foreignField": "_id",
                        "as": "client"
                    }      
            },
            {
                "$unwind": {"path": "$client", "preserveNullAndEmptyArrays": True}
            },
            {"$match": {"site.enabled" : True}},
            {"$match": {"client.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}},
            {"$match": {"dscLocalDate": {"$gt":datetime(2019,7,1)}}},
#            {"$count": "device count"},
            {
                    "$project": {
                                    "device_name":"$name",
                                    "site_name":"$site.name",
                                    "client_name":"$client.name",
#                                    "name" : 1
                                }
            },            
         ] 
WK_list = list(db.workstation.aggregate(pipelin3))
SV_list = list(db.server.aggregate(pipelin3))
WK_db = pd.DataFrame(WK_list)
WK_db['Type'] = "workstation"
#WK_db = pd.DataFrame({values:WK_db.values, 'Type':'Workstation'}, index = index)
SV_db = pd.DataFrame(SV_list)
SV_db['Type'] = "server"
device_db = pd.concat([SV_db,WK_db], ignore_index = True)
print(device_list [0])
#%%==================== loop of getting faield checks - for the month
#for i in range(len(device_db)):
i = 2
#device_id = WK_list[i]['_id']
device_id = int(device_db['_id'][i])
results = checks.find(
            {
                "servertime": {
                                "$gte": datetime(2019,6,1,1,0,0),
                                "$lte": datetime(2019,7,31,23,59,59)
                                },    
                "deviceid":device_id,
#                "dsc247":2,
                "checkstatus": {"$ne":"testok"}                
#                "checkid": "16879864"
            }
            )
check_results = list(results)
len_fails = len(check_results)
print(len_fails)
if len(check_results) > 0:
    check_SQL=pd.DataFrame(check_results, columns = ['servertime','description',
                                                     'checkstatus','consecutiveFails','dsc247',
                                                     'extra','checkid','deviceid']).sort_values(by = 'servertime')#, ascending = False)
#%%                            
    check_SQL = check_SQL.reset_index(drop = True)
    temp_SQL = check_SQL[check_SQL.index == 0]
    ch_id_hist = np.array(check_SQL['checkid'][0])
    temp_SQL['last_fail'] = ''
    temp_SQL.last_fail[0] = check_SQL['servertime'][0]
    for i_f in range(1,len_fails):
        if check_SQL['checkid'][i_f] in ch_id_hist:
#            check_SQL['checkid'][i_f]
            a = temp_SQL[temp_SQL.checkid == check_SQL['checkid'][i_f]]['last_fail'][0]            
            b = check_SQL['servertime'][i_f]
            if (b - a).total_seconds() > 3*3600:   # a broken sequence of failures ==> new failure
                i_match = temp_SQL.checkid == check_SQL['checkid'][i_f]
                temp_SQL['last_fail'][i_match] = b
            else:
                print("what?")# continues failing sequanece    
                
        else:  # new failure
            temp_SQL = temp_SQL.append(check_SQL.iloc[i_f],ignore_index=True)
            temp_SQL.last_fail[len(temp_SQL)-1] = check_SQL['servertime'][[i_f]]
            ch_id_hist = np.append(ch_id_hist,check_SQL['checkid'][i_f])
                
                
            
        
        
    
#%%
    
pd.DataFrame({values:df_her1.values,
                           'Percentage':price_ratio},
                            index = shorten_names).sort_values(by = 'preis',ascending=False)      
 

#%%==================== Check the running operations
a=db.current_op()
print(len(a['inprog']))
if len(a['inprog']) > 1:
    print("Still running operations")
#agg_expl = db.command('aggregate','check',pipeline=pipeline, explain=True)

#            {"$group": {"_id":"$deviceid", "max_time":{"$max":"$servertime"}}}    


#print(client.f)

#connection = Connection()
#connection = Connection()