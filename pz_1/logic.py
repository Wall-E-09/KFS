from datetime import datetime
from config import (BASE_TARIFF_DAY, BASE_TARIFF_NIGHT,
                   HIGH_TARIFF_DAY, HIGH_TARIFF_NIGHT,
                   TARIFF_LIMIT, FAKE_ADDITION_DAY, FAKE_ADDITION_NIGHT)
from database import meters, bills, history

def calculate_bill(used_day, used_night, prev_total):
    total_used = used_day + used_night + prev_total
    
    if total_used <= TARIFF_LIMIT:
        day_cost = used_day * BASE_TARIFF_DAY
        night_cost = used_night * BASE_TARIFF_NIGHT
    elif prev_total >= TARIFF_LIMIT:
        day_cost = used_day * HIGH_TARIFF_DAY
        night_cost = used_night * HIGH_TARIFF_NIGHT
    else:
        base_part = TARIFF_LIMIT - prev_total
        if used_day + used_night <= base_part:
            day_cost = used_day * BASE_TARIFF_DAY
            night_cost = used_night * BASE_TARIFF_NIGHT
        else:
            base_ratio = base_part / (used_day + used_night)
            day_base = used_day * base_ratio
            night_base = used_night * base_ratio
            
            day_high = used_day - day_base
            night_high = used_night - night_base
            
            day_cost = day_base * BASE_TARIFF_DAY + day_high * HIGH_TARIFF_DAY
            night_cost = night_base * BASE_TARIFF_NIGHT + night_high * HIGH_TARIFF_NIGHT
    
    return day_cost + night_cost

def process_meter_data(meter_id, new_day, new_night, date=None):
    date = date or datetime.now().isoformat()
    meter = meters.find_one({"meter_id": meter_id})
    
    if meter:
        prev_day = meter.get("current_day", 0)
        prev_night = meter.get("current_night", 0)
        prev_total = meter.get("total_consumption", 0)
        
        if new_day < prev_day:
            new_day += FAKE_ADDITION_DAY
        if new_night < prev_night:
            new_night += FAKE_ADDITION_NIGHT
            
        used_day = new_day - prev_day
        used_night = new_night - prev_night
        amount = calculate_bill(used_day, used_night, prev_total)
        new_total = prev_total + used_day + used_night
        
        history.insert_one({
            "meter_id": meter_id,
            "prev_day": prev_day,
            "prev_night": prev_night,
            "new_day": new_day,
            "new_night": new_night,
            "date": date,
            "used_day": used_day,
            "used_night": used_night,
            "amount": amount,
            "total_consumption": new_total
        })
        
        meters.update_one(
            {"meter_id": meter_id},
            {"$set": {
                "current_day": new_day,
                "current_night": new_night,
                "last_update": date,
                "total_consumption": new_total
            }}
        )
    else:
        used_day = 0
        used_night = 0
        amount = 0
        prev_total = 0  # Додано ініціалізацію для нового лічильника
        meters.insert_one({
            "meter_id": meter_id,
            "current_day": new_day,
            "current_night": new_night,
            "last_update": date,
            "total_consumption": 0
        })
    
    # Виправлено умову для tariff_type
    current_total = prev_total + used_day + used_night
    bills.insert_one({
        "meter_id": meter_id,
        "amount": amount,
        "used_day": used_day,
        "used_night": used_night,
        "date": date,
        "tariff_type": "BASE" if current_total <= TARIFF_LIMIT else "HIGH"
    })
    
    return {
        "meter_id": meter_id,
        "used_day": used_day,
        "used_night": used_night,
        "amount": amount
    }