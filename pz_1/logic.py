from config import *
from database import meters, history
from models import create_meter_dict, create_history_record
from datetime import datetime

def calculate_bill(day_delta, night_delta):
    return day_delta * TARIFF_DAY + night_delta * TARIFF_NIGHT

def process_meter_data(meter_id, curr_day, curr_night):
    existing = meters.find_one({"meter_id": meter_id})
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if existing:
        prev_day = existing["day"]
        prev_night = existing["night"]

        if curr_day < prev_day:
            curr_day = prev_day + FAKE_ADDITION_DAY
        if curr_night < prev_night:
            curr_night = prev_night + FAKE_ADDITION_NIGHT

        day_delta = curr_day - prev_day
        night_delta = curr_night - prev_night
        bill = calculate_bill(day_delta, night_delta)

        # Історія
        history.insert_one(create_history_record(
            meter_id, now, prev_day, prev_night, curr_day, curr_night, bill
        ))

        # Оновлення
        meters.update_one(
            {"meter_id": meter_id},
            {"$set": {
                "day": curr_day,
                "night": curr_night,
                "last_update": now
            }}
        )
    else:
        # Новий лічильник
        meters.insert_one(create_meter_dict(meter_id, now, curr_day, curr_night))
        bill = 0  # нічого не рахуємо

    return bill
