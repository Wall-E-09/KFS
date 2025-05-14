from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["energy_db"]

meters = db["meters"]
history = db["history"]
