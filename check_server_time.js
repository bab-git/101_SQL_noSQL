db.getCollection('check').find(
    {
        $and: 
        [   
//             {servertime: new ISODate("2019-07-20 12:02:34.000Z")},
            {servertime: {"$gt": new ISODate("2019-07-20 03:00:00")}},
            {servertime: {"$lt": new ISODate("2019-07-20 16:00:00")}},
            {checkstatus: {$ne:"testok"}},
            {deviceid:1145595}
        ]
    }        
).limit(30)