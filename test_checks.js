db.check.find(
    {
        datetime: 
        { "$gt" : 
            new Date("2019-02-01")
        }        
    }
).limit(3)