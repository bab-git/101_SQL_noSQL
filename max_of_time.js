db.getCollection("check").aggregate(
    [
        {        
            $match:
            {
                $and:
                [
//                     {servertime: {"$gt": new ISODate("2019-07-31 00:00:00.000Z")}},
                    {servertime: 
                        {"$gt": new ISODate("2019-07-31 00:00:00.000Z"),
                         "$lt": new ISODate("2019-08-01 00:00:00.000Z")}},
                    {deviceid:1035046}
                ]
            }               
        },
        
        {
           $group:
            {
              _id:"$deviceid",
//               "dcs247":"  
              max_time:{$max:"$servertime"},
              count: {$sum:1},
            }            
        },    
            
                       
//     {$limit:1}
    ]
)