db.server.aggregate([
    { $match: {_id:1178511} },
    {
        $lookup:
            {
                from: "site",
                localField: "siteid",
                foreignField: "_id",
                as: "site_doc"
            }    
    },
    {
        $unwind
    }
])