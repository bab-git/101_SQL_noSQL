db.getCollection('check').find(
    {
         $and: 
         [   
//             {servertime: new ISODate("2019-07-20 12:02:34.000Z")},
            {servertime: {"$gt": new ISODate("2019-07-01 00:00:00")}},
            {servertime: {"$lt": new ISODate("2019-07-20 23:00:00")}},
            {checkstatus: {$ne:"testok"}},
//             {description: {$search:"Anti"}},
//             {checkid:"30073493"},
            {description:{$not:/Anti/}},
            {deviceid:1156225},
         ],
//         $not:
//             description:{$nin:[/Anti/]}
//             description:{$not:/Anti/}
    },
    {}    
).limit(50).sort({datetime: 1})