// DBQuery.shellBatchSize = 100;
// DBQuery.shellBatchSize = 500;
db.getCollection('check').aggregate([
//      { $match: {_id:ObjectId("5c1bbcfbfe78c90007af2693")} },            
//      { $match: {datetime: { "$gt" : new Date("2019-07-01")} }}
    { 
        $match:
        {
            $and:
            [
                {datetime: { "$gt" : new ISODate("2019-07-01 01:00:10.000Z")}},
//                 {datetime: { "$lt" : new ISODate("2019-07-01 01:00:17")}}
//                 {datetime: { "$gt" : new ISODate("2019-02-04 01:49:00")}},
//                 {datetime: { "$lt" : new ISODate("2019-02-04 14:50:00")}},
//                 {datetime: new ISODate("2019-07-01 01:00:17.000Z")},
//                 {emailalerts: 1}
//                 {checkid: {$in: ["23538852","22261308"]}}
            ]
//                         
        }
    },
    {
        $lookup:
            {
                from: "workstation",
                localField: "deviceid",
                foreignField: "_id",
                as: "workstation"
            }    
    },
    {
        $unwind: {path: "$workstation", preserveNullAndEmptyArrays: true}
    },    
    {
        $lookup:
            {
                from: "server",
                localField: "deviceid",
                foreignField: "_id",
                as: "server"
            }    
    },
    {
        $unwind: {path: "$server", preserveNullAndEmptyArrays: true}
    },  
    
    {
         $lookup: 
            {
                from: "site",
                let: {
                    ssiteid : "$server.siteid",
                    wsiteid : "$workstation.siteid"
                },
                pipeline: [
                    { $match:
                        { $expr: {//                          
                            
                            $or: [
                                {$eq : ["$_id","$$ssiteid"]},
                                {$eq : ["$_id","$$wsiteid"]}
                            ]
                            }                                                
                        }                                               
                    }],                
                as: "site"
            }      
    },
    {
        $unwind: {path: "$site", preserveNullAndEmptyArrays: true}
    },  

    {
         $lookup: 
            {
                from: "client",
                localField: "site.clientid",
                foreignField: "_id",
                as: "client"
            }      
    },
    {
        $unwind: {path: "$client", preserveNullAndEmptyArrays: true}
    },

//     { "$redact": { 
//         "$cond": [
//             {    
//                  $or :
//                  [
//                     {"$eq": [ "$server.siteid", "site2._id" ] } ,
//                      {"$eq": [ "$workstation.siteid", "site._id"]}
//                  ]
//             },
//             "$$KEEP", 
//             "$$KEEP"
//         ]
//     }}, 

    { $project: { 
        "_id": 1, 
//         "checkid": 1, 
//         "deviceid": 1,
        "description": 1, 
        "extra": 1,
        "datetime": 1,
        "cname" : "$client.name",    
        "apiKey" : "$client.apiKey",
        "workstation": 1 ,
        "server":1,
        "enabled": "$site.enabled"
//         "siteid": "$workstation.siteid",     
        }    
    },

    { $match: 
        { apiKey:"ae0a4c75230afae756fcfecd3d2838cf"}
    },
    { $match: 
        { enabled:true}
    },
    
//     { $match: {checkstatus:"testerror"}},
//        { $match: {description : /Festplattenspei/}},
//        { $match: {cname : /Redd/}},
//      { $match: {"client.name":"FH-057 PC-SPEZIALIST VERL"}}
//     {$sort: { checkstatus : -1 }}
     {$limit: 30}
])