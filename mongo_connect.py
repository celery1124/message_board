import pymongo
import constants

def connectMongo():
	url = "mongodb://" + constants.mongo_host + "/" + constants.mongo_db
	client = pymongo.MongoClient(url)
	db = client[constants.mongo_db]
	collection = db[constants.mongo_collection]
	return collection

