// DBQuery.shellBatchSize = 100;
db.check.aggregate([
//      { $match: {_id:ObjectId("5c1bbcfbfe78c90007af2693")} },            
//      { $match: {datetime: { "$gt" : new Date("2019-07-01")} }}
    { 
        $match:
        {
            $and:
            [
//                 {datetime: { "$gt" : new ISODate("2019-07-01 01:00:10.000Z")}},
//                 {datetime: { "$gt" : new Date("2019-07-01")}},
//                 {datetime: { "$lt" : new ISODate("2019-07-01 01:00:28.000Z")}},
                {datetime: new ISODate("2019-07-01 01:00:27.000Z")},
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
                as: "workstation2"
            }    
    },
    {
        $unwind: {path: "$workstation2", preserveNullAndEmptyArrays: true}
    },    
    {
        $lookup:
            {
                from: "server",
                localField: "deviceid",
                foreignField: "_id",
                as: "server2"
            }    
    },
    {
        $unwind: {path: "$server2", preserveNullAndEmptyArrays: true}
    },  
    { "$redact": { 
        "$cond": [
            {    
                $or :
                [
                    { "$eq": [ "$emailalerts", "$workstation2.dscActive" ] }, 
                    { "$eq": [ "$dsc247", "$workstation2.dscActive" ] } 
                ]
            },
            "$$KEEP", 
            "$$PRUNE"
        ]
    }}, 
//     { $project: { 
//         "deviceid": 1, 
//         "_class": 1, 
// //         "percent1": "$checkid", 
// //         "percent2": "$workstation.name"
//     }}    
//     {
//         $lookup:
//             {
//                 from: "workstation",
//                 let: {
//                     field1: "$deviceid"
//                     field2: "$_class"                    
//                 },
//                 pipeline: [
//                     {
//                      $match: {
//                        $expr: {
//                          $and: [
//                             {
//                                $eq: [
//                                   "$deviceid",
//                                   "$$field1"
//                                ]
//                             },
//                             {
//                                $eq: [
//                                   "$_class",
//                                   "$$field2"
//                                ]
//                             }
//                          ]
//                       }
//                    }
//                         
//                         
//                     }                                                              
//                 ],
//                 
//                 as: "workstation"
//             }    
//     }
//     {
//         $unwind: {path: "$workstation2", preserveNullAndEmptyArrays: true}
//     },
//     { 
//      $project: 
//         { 
//             mid: { $cond: [ { $eq: [ '$_class', '$workstation2._class' ] }, 1, 0 ] } 
//         } 
//     },
//     {$match : { mid : 1}}
])