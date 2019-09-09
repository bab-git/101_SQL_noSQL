db.getCollection('check').find(
    {
//          $and: 
//          [   
//             {servertime: new ISODate("2019-06-01 01:04:55.000Z")},
            servertime: {
                            "$gte": new ISODate("2019-06-01 15:00:00.000Z"),
                            "$lte": new ISODate("2019-07-31 18:59:59.000Z"),
                            "$ne": false    
                          },
//             checkstatus: {$ne:"testok"},
//             checkstatus : "add",
//             description: /Terra Backup/,
//             description: /Anti-Virus-Aktualisierungsüberprüfung/,
//             description: /Anti-Virus-Aktualisierungsüberprüfung - G Data Enterprise Client Engine/,
//             description: /Leistungsüberwachung - Festplatte/,
//             extra: /Insgesamt:/
//             description : /Gerät: MAV Deinstallation/
//             description: {$not: /Engine A/}
//             Anti-Virus-Aktualisierungsüberprüfung - G Data Enterprise Client Engine A/B
//             extra :{$not:/Backupjob:/}
//             description: /Kinect/
//             Skriptüberprüfung - Terra Backup
//             checkid:"16879861",
//             {description:{$not:/Anti/}},
//             deviceid:1141533,
//             {deviceid:{"$gte":1035046}},
//                dsc247: {$nin:[1,2]}
//          ],
//         $not:
//             description:{$nin:[/Anti/]}
//             description:{$not:/Anti/}
    }
//     {
//         deviceid:1,
//         checkid:1,
//         checkstatus:1,
//         consecutiveFails:1,
//         servertime:1        
//     }    
)
.count()
//     .limit(50)
//     .sort({servertime: 1})
//     .sort({deviceid: 1})