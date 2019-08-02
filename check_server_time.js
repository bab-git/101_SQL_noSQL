db.getCollection('check').find(
    {
         $and: 
         [   
//             {servertime: new ISODate("2019-06-01 01:04:55.000Z")},
            {datetime: {
                            "$gte": new ISODate("2019-07-31 01:00:00.000Z"),
                            "$lte": new ISODate("2019-07-31 23:59:59.000Z")
                          }},
//             {checkstatus: {$ne:"testok"}},
//             {description: {$search:"Anti"}},
//             {checkid:"29671730"},
//             {description:{$not:/Anti/}},
            {deviceid:1035046},
//             {deviceid:{"$gte":1035046}},
         ],
//         $not:
//             description:{$nin:[/Anti/]}
//             description:{$not:/Anti/}
    },
    {
//         deviceid:{$dsc247}
    }    
)
// .count()
    .limit(50)
//     .sort({datetime: 1})
//     .sort({checkid: 1})