db.workstation.aggregate([       
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
//     {
//         $unwind: {path: "$client", preserveNullAndEmptyArrays: true}
//     },
    { $match: {"site.enabled" : true}},
    { $match: {"client.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}},
    {$match: {dscLocalDate: {"$gt":ISODate("2019-07-01 01:00:10.000Z")}}},
    {
            "$project": {
//                 "_class":0, 
//                 "guid":0,
//                 "lastBootTime":0,
//                 "utcOffset":0,
//                 "agentVersion":0,                               
                 dev_name:"$name",
                 site_name:"$site.name",
//                  client:1,
//                  dscLocalDate:1
                }
    },
   
//     {$count: "device count"}
])