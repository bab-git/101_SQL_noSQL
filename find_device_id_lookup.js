db.server.aggregate([
    { $match: {_id:1178511} },
    {
        $lookup:
            {
                from: "site",
                localField: "siteid",
                foreignField: "_id",
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
])