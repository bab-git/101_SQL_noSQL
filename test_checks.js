// DBQuery.shellBatchSize = 500;
 DBQuery.shellBatchSize = 50;
db.check.find(
//     {     
//         $match:
        {
//             $and:
//             [
//                 {datetime: { "$gt" : new ISODate("2019-02-04 01:00:10.000Z")}},
//                 {servertime: { "$eq" : ISODate("2019-07-09 13:09:17")}}
//                datetime: { "$gt" : ISODate("2019-07-04 10:48:00")}
               deviceid: {"$gt":267576}
//                servertime: new ISODate("2018-12-21 23:17:30.000Z")
//                datetime: new ISODate("2018-07-11 10:32:54.000Z")
//                 {datetime: { "$lt" : new ISODate("2019-07-09 03:00:00")}}
//                    {datetime: { "$gt" : new Date("2018-12-03")}},
//                 {datetime: { "$lt" : Date("2019-02-05")}},
//                 datetime: new ISODate("2020-01-01")
//                 {emailalerts: 1}
//                 {checkid: {$in: ["23538852","22261308"]}}
//                {description : /Festplattenspei/},
//                {checkstatus : "testerror"}
//             ]                         
        }        
//         ,{
//             datetime :1,
//             servertime :1
//         }
//     }
    ).limit(50)
     .sort({
            "deviceid" : 1,
            "description" : 1
            }
           )