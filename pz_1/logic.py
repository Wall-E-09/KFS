from datetime import datetime
from config import TARIFFS, ADJUSTMENT
from pz_1.database import meters, bills, history

def process_meter_data(meter_id, new_day, new_night, date=None):
    date = date or datetime.now().isoformat()
    meter = meters.find_one({"meter_id": meter_id})

    if meter:
        prev_day = meter["current_day"]
        prev_night = meter["current_night"]

        if new_day < prev_day:
            new_day += ADJUSTMENT["day"]
        if new_night < prev_night:
            new_night += ADJUSTMENT["night"]

        used_day = new_day - prev_day
        used_night = new_night - prev_night

        history.insert_one({
            "meter_id": meter_id,
            "prev_day": prev_day,
            "prev_night": prev_night,
            "new_day": new_day,
            "new_night": new_night,
            "date": date,
            "used_day": used_day,
            "used_night": used_night
        })

        meters.update_one(
            {"meter_id": meter_id},
            {"$set": {"current_day": new_day, "current_night": new_night, "last_update": date}}
        )
    else:
        used_day = 0
        used_night = 0
        meters.insert_one({
            "meter_id": meter_id,
            "current_day": new_day,
            "current_night": new_night,
            "last_update": date
        })

    amount = used_day * TARIFFS["day"] + used_night * TARIFFS["night"]

    bills.insert_one({
        "meter_id": meter_id,
        "amount": amount,
        "used_day": used_day,
        "used_night": used_night,
        "date": date
    })

    return {
        "meter_id": meter_id,
        "used_day": used_day,
        "used_night": used_night,
        "amount": amount
    }

def seed_data():
    meters.delete_many({})
    bills.delete_many({})
    history.delete_many({})

    process_meter_data("12345", 1000, 800, "2025-05-01T12:00:00")
    process_meter_data("67890", 500, 400, "2025-05-01T12:00:00")
    process_meter_data("99999", 300, 200, "2025-05-01T12:00:00")
