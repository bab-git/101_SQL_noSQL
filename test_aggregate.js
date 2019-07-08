// DBQuery.shellBatchSize = 100;
db.check.aggregate([
//      { $match: {_id:ObjectId("5c1bbcfbfe78c90007af2693")} },            
//      { $match: {datetime: { "$gt" : new Date("2019-07-01")} }}
    { 
        $match:
        {
            $and:
            [
                {datetime: { "$gt" : new ISODate("2019-07-01 01:00:10.000Z")}},
//                 {datetime: { "$gt" : new Date("2019-07-01")}},
//                 {datetime: { "$lt" : new ISODate("2019-07-01 01:00:28.000Z")}},
//                 {datetime: new ISODate("2019-07-01 01:00:27.000Z")},
//                 {emailalerts: 1}
            ]
//                         
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
                localField: "workstation.siteid",
                foreignField: "_id",
                as: "Wsite"
            }      
    },
    {
        $unwind: {path: "$Wsite", preserveNullAndEmptyArrays: true}
    },  
    {
         $lookup: 
            {
                from: "site",
                localField: "server.siteid",
                foreignField: "_id",
                as: "Ssite"
            }      
    },
    {
        $unwind: {path: "$Ssite", preserveNullAndEmptyArrays: true}
    }, 
    {
         $lookup: 
            {
                from: "client",
                localField: "Ssite.clientid",
                foreignField: "_id",
                as: "Sclient"
            }      
    },
     {
        $unwind: {path: "$Sclient", preserveNullAndEmptyArrays: true}
    },
    {
         $lookup: 
            {
                from: "client",
                localField: "Wsite.clientid",
                foreignField: "_id",
                as: "Wclient"
            }      
    },
     {
        $unwind: {path: "$Wclient", preserveNullAndEmptyArrays: true}
    },
//     { "$redact": { 
//         "$cond": [
//             {    
//                  $or :
//                  [
//                     {"$eq": [ "$server.siteid", "site2._id" ] } ,
//                      {"$eq": [ "$workstation.siteid", "site._id"]}
//                  ]
//             },
//             "$$KEEP", 
//             "$$KEEP"
//         ]
//     }}, 

//     { $project: { 
//         "deviceid": 1, 
//         "_class": 1, 
//          "siteid": "$workstation2.siteid", 
// //         "percent2": "$workstation.name"
//     }}    
//     {
    { $match: 
        { $or:
            [
                {"Wclient.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"},
                {"Sclient.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}
            ]
        }
    },
    { $match: {checkstatus:"testerror"}},
    { $match: {"Sclient.name":"Hans Erlenbach Entwicklung GmbH"}}
])