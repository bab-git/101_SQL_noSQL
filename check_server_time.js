db.getCollection('check').find(
    {
        $and: 
        [   
//             {servertime: new ISODate("2019-07-20 12:02:34.000Z")},
            {servertime: {"$gt": new ISODate("2019-07-20 00:00:00")}},
            {servertime: {"$lt": new ISODate("2019-07-20 23:00:00")}},
            {checkstatus: {$ne:"testok"}},
//             {checkid:"20126304"},
            {deviceid:563882}
        ]
    }        
).limit(100)