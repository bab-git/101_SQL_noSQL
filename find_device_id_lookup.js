db.workstation.aggregate([
//     { $match: {_id:625873}},    
    { $match: {_id:1258081}},
// db.server.aggregate([
//     { $match: {_id:1013764} },            
    {
        $lookup:
            {
                from: "site",
                localField: "siteid",
                foreignField: "_id",
                as: "site"
            }    
    },
    {
        $unwind: {path: "$site", preserveNullAndEmptyArrays: true}
    },
    {
         $lookup: 
            {
                from: "client",
                localField: "site.clientid",
                foreignField: "_id",
                as: "client"
            }      
    },
    {
        $unwind: {path: "$client", preserveNullAndEmptyArrays: true}
    },
    {
            "$project": {
                "_class":0, 
                "guid":0,
                "lastBootTime":0,
                "utcOffset":0,
                "agentVersion":0,                               
                }
    },
//     { $match: {"client.apiKey":{$not:/ae/}}},
    { $match: {"site.enabled" : true}},
    { $match: {"client.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}},
//     {$match: {dscLocalDate: {"$gt":ISODate("2019-08-01 01:00:10.000Z")}}},
//     { $not: {"checkstatus":"testok"}}
//     {$count: "device count"}
])