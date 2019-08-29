db.getCollection("check").aggregate(
    [
        {        
            $match:
            {
                $and:
                [
//                     {servertime: {"$gt": new ISODate("2019-07-31 00:00:00.000Z")}},
                    {servertime: 
                        {"$gt": new ISODate("2019-07-01 07:00:00"),
                         "$lt": new ISODate("2019-07-02 07:00:00")}},
//                     {deviceid:1035046}
//                     {description : 'Skriptüberprüfung - Kinect Error'}
                ]
            }               
        },
        
        {
           $group:
            {
//               _id:{deviceid: "$deviceid",checkid: "$checkid"},
              _id:"$description",
//               "dcs247":"  
//               max_time:{$max:"$servertime"},
              count: {$sum:1},
            }            
        },    
            
                       
        {$limit:100}
        {$sort:{max_time:-1}}
])