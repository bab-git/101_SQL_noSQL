db.getCollection('check').find(
    {
         $and: 
         [   
//             {servertime: new ISODate("2019-06-01 01:04:55.000Z")},
            {servertime: {"$gt": new ISODate("2019-07-26 01:00:55.000Z")}},
            {servertime: {"$lt": new ISODate("2019-07-27 04:14:55.000Z")}},
//             {checkstatus: {$ne:"testok"}}
//             {description: {$search:"Anti"}},
//             {checkid:"30073493"},
//             {description:{$not:/Anti/}},
            {deviceid:1156225},
         ],
//         $not:
//             description:{$nin:[/Anti/]}
//             description:{$not:/Anti/}
    },
    {}    
).limit(50)
//     .sort({datetime: 1})
    .sort({checkid: 1})    