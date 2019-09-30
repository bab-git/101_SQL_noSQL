// DBQuery.shellBatchSize = 100;
// DBQuery.shellBatchSize = 500;
db.getCollection('check').aggregate([
//      { $match: {_id:ObjectId("5c1bbcfbfe78c90007af2693")} },            
//      { $match: {datetime: { "$gt" : new Date("2019-07-01")} }}
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
                "$unwind": {"path": "$site", "preserveNullAndEmptyArrays": true}
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
                "$unwind": {"path": "$client", "preserveNullAndEmptyArrays": true}
            },
            {"$match": {"site.enabled" : true}},
            {"$match": {"client.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}},
            {"$match": {"dscLocalDate": {"$gt": new ISODate("2019-07-01 01:00:10.000Z")}}},
// #            {"$count": "device count"},
            {
                    "$project": {
                                    "device_name":"$name",
                                    "site_name":"$site.name",
                                    "client_name":"$client.name",
                                    "dscLocalDate":"$dscLocalDate"
// #                                    "name" : 1
                                }
            },  
])