// DBQuery.shellBatchSize = 100;
db.check.explain().aggregate([
// db.check.aggregate([
//      { $match: {_id:ObjectId("5c1bbcfbfe78c90007af2693")} },            
//      { $match: {datetime: { "$gt" : new Date("2019-07-01")} }}
    { 
        $match:
        {
            $and:
            [
//                 {datetime: { "$gt" : new ISODate("2019-07-01 01:00:10.000Z")}},
//                 {datetime: { "$lt" : new ISODate("2019-07-01 01:00:17")}}
                {datetime: { "$gt" : new ISODate("2019-02-04 10:49:10")}},
                {datetime: { "$lt" : new ISODate("2019-02-04 19:49:31")}},
//                 {datetime: new ISODate("2019-07-01 01:00:17.000Z")},
//                 {emailalerts: 1}
//                 {checkid: {$in: ["23538852","22261308"]}}
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
//     {
//         $lookup:
//             {
//                 from: "server",
//                 localField: "deviceid",
//                 foreignField: "_id",
//                 as: "server"
//             }    
//     },
//     {
//         $unwind: {path: "$server", preserveNullAndEmptyArrays: true}
//     },  
//     
//     {
//          $lookup: 
//             {
//                 from: "site",
//                 localField: "workstation.siteid",
//                 foreignField: "_id",
//                 as: "Wsite"
//             }      
//     },
//     {
//         $unwind: {path: "$Wsite", preserveNullAndEmptyArrays: true}
//     },  
//     {
//          $lookup: 
//             {
//                 from: "site",
//                 localField: "server.siteid",
//                 foreignField: "_id",
//                 as: "Ssite"
//             }      
//     },
//     {
//         $unwind: {path: "$Ssite", preserveNullAndEmptyArrays: true}
//     }, 
//     {
//          $lookup: 
//             {
//                 from: "client",
//                 localField: "Ssite.clientid",
//                 foreignField: "_id",
//                 as: "Sclient"
//             }      
//     },
//      {
//         $unwind: {path: "$Sclient", preserveNullAndEmptyArrays: true}
//     },
//     {
//          $lookup: 
//             {
//                 from: "client",
//                 localField: "Wsite.clientid",
//                 foreignField: "_id",
//                 as: "Wclient"
//             }      
//     },
//      {
//         $unwind: {path: "$Wclient", preserveNullAndEmptyArrays: true}
//     },
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

    { $project: { 
        "deviceid": 1, 
//         "_class": 1, 
        "description":1,
         "siteid": "$workstation.siteid", 
         "workstation": 1,
         "wname": "$workstation.name"
//         "percent2": "$workstation.name"
    }},    
//     {
//     { $match: 
//         { $or:
//             [
//                 {"Wclient.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"},
//                 {"Sclient.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}
//             ]
//         }
//     },
//     { $match: {checkstatus:"testerror"}},
//     { $match: {"Sclient.name":"Hans Erlenbach Entwicklung GmbH"}}
//        { $match: {description : /Festplattenspei/}},
//        { $match: {wname : /STEPHAN/}},
//        {$limit: 10}
])