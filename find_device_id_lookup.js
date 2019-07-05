db.workstation.aggregate([
    { $match: {_id:1096537}},    
//     { $match: {_id:1154763}},        
// db.server.aggregate([
//     { $match: {_id:1178511} },            
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
            "$project": {
                "_class":0,
                "guid":0,
                "lastBootTime":0,
                "utcOffset":0,
                "agentVersion":0,                               
                }
    }
])