db.getCollection("check").aggregate(
    [
        {        
            $match:
            {
                $and:
                [
//                     {servertime: {"$gt": new ISODate("2019-07-31 00:00:00.000Z")}},
                    {servertime: 
                        {"$gt": new ISODate("2019-06-29 07:00:00"),
                         "$lt": new ISODate("2019-07-31 07:00:00")}},
//                     {deviceid:1035046}
                     {checkstatus: {$ne:"testok"}},
//                     {description : 'Skript�berpr�fung - Kinect Error'}
//                     {description: /Anti-Virus-Aktualisierungs�berpr�fung - G Data Enterprise Client Engine/}
//                     {description: /Festplattenspeicher�berpr�fung - Laufwerk/}
//                     {checkstatus: {$ne:"testok"}},
                    {description: �berpr�fung des Dateisystemspeicherplatzes - Backup}
//                     {description: /�berpr�fung des Dateisystemspeicherplatzes - /}
                ]
            }               
        },
        
        {
           $group:
            {
//               _id:{deviceid: "$deviceid",checkid: "$checkid"},
              _id:"$description",
//               _id:"$checkstatus",                  
//               "dcs247":"  
//               max_time:{$max:"$servertime"},
              count: {$sum:1},
            }            
        },    
            
                       
        {$limit:100},
//         {$sort:{max_time:-1}}
])