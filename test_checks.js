// DBQuery.shellBatchSize = 500;
db.getCollection('check').find(
//     {     
//         $match:
        {
//             $and:
//             [
//                 {datetime: { "$gt" : new ISODate("2019-02-04 01:00:10.000Z")}},
//                 {datetime: { "$lt" : new ISODate("2019-07-01 01:00:17")}}
               datetime: { 
                            "$gte" : new ISODate("2019-07-31 00:00:00"),
                            "$lt" : new ISODate("2019-07-31 23:59:59")
                           },
//                {datetime: { "$lt" : new ISODate("2019-02-04 18:50:00")}},
//                    {datetime: { "$gt" : new Date("2018-12-03")}},
//                 {datetime: { "$lt" : Date("2019-02-05")}},
//                 {datetime: new ISODate("2019-07-01 01:00:17.000Z")},
                dsc247: 1,
//                 {checkid: {$in: ["23538852","22261308"]}}
//                {description : /Festplattenspei/},
//                {checkstatus : "testerror"}
//                deviceid: 568912,
//                {checkid: "28226123"}
               checkstatus: {$ne:"testok"}
//             ]                         
        }     
//     }
//         { $not:
//             [
//                 {$match:{"$checkstatus":"testok"}}
//             ]        
//         }
//         {
//             datetime:1
//         }
    )
        .limit(50)
//         .count()