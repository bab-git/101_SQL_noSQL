db.check.aggregate([
//      { $match: {_id:ObjectId("5c1bbcfbfe78c90007af2693")} },            
    { $match:
        {
            datetime: 
            { "$gt" : 
                new Date("2019-07-01")            
            }        
        }
    },
    {
        $lookup:
            {
                from: "workstation",
                localField: "deviceid",
                foreignField: "_id",
                as: "workstation"
            }    
    },
    {
        $unwind: {path: "$workstation", preserveNullAndEmptyArrays: true}
    },
    {
        $lookup:
            {
                from: "server",
                localField: "deviceid",
                foreignField: "_id",
                as: "server"
            }    
    },   
    
    {
        $unwind: {path: "$server", preserveNullAndEmptyArrays: true}
    },
    {
        $lookup:
            {
                from: "site",
                localField: "server.siteid",
                foreignField: "_id",
                as: "site"
            }    
    },    
    {
        $lookup:
            {
                from: "site",
                localField: "workstation.siteid",
                foreignField: "_id",
                as: "site"
            }    
    },           
//     {
//         $unwind: {path: "$site", preserveNullAndEmptyArrays: true}
//     },
//     {
//          $lookup: 
//             {
//                 from: "client",
//                 localField: "site.clientid",
//                 foreignField: "_id",
//                 as: "client"
//             }      
//     },
//     {
//         $unwind: {path: "$client", preserveNullAndEmptyArrays: true}
//     },
//     {
//             "$project": {
//                 "_class":0,
//                 "guid":0,
//                 "lastBootTime":0,
//                 "utcOffset":0,
//                 "agentVersion":0,                               
//                 }
//     },
//     { $match: {"client.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}},
//     { $match: {"site.enabled":true}}
])