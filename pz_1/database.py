from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["energy_db"]

meters = db["meters"]
history = db["history"]
bills = db["bills"]

if meters.count_documents({}) == 0:
    meters.insert_one({
        "meter_id": "default",
        "current_day": 0,
        "current_night": 0,
        "last_update": "2023-01-01T00:00:00"
    })