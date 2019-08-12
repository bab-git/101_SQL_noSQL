db.getCollection('check').find(
    {
//          $and: 
//          [   
//             {servertime: new ISODate("2019-06-01 01:04:55.000Z")},
            servertime: {
                            "$gte": new ISODate("2019-06-06 01:00:00.000Z"),
                            "$lte": new ISODate("2019-07-31 23:59:59.000Z")
                          },
//             {checkstatus: {$ne:"testok"}},
//             {description: {$search:"Anti"}},
            checkid:"16880243",
//             {description:{$not:/Anti/}},
            deviceid:745958,
//             {deviceid:{"$gte":1035046}},
//                dsc247: {$nin:[1,2]}
//          ],
//         $not:
//             description:{$nin:[/Anti/]}
//             description:{$not:/Anti/}
    },
    {
        deviceid:1,
        checkid:1,
        checkstatus:1,
        consecutiveFails:1,
        servertime:1        
    }    
)
// .count()
//     .limit(50)
    .sort({servertime: 1})
//     .sort({checkid: 1})