const collection = db.getCollection('client');
const changeStream = collection.watch();