db.check.find(
    {
        datetime: 
        { "$gt" : 
//             new Date("2019-02-01")
            new Date("2019-07-01")            
        }        
    }
)