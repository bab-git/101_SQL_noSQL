db.workstation.aggregate([
//     { $match: {_id:1096537}},    
    { $match: {_id:881738}},        
// db.server.aggregate([
//     { $match: {_id:881738} },            
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
//     { $match: {"client.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}},
//     { $match: {"site.enabled":true}}
])