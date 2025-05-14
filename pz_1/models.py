def create_meter_dict(meter_id, date, day, night):
    return {
        "meter_id": meter_id,
        "last_update": date,
        "day": day,
        "night": night
    }

def create_history_record(meter_id, date, prev_day, prev_night, curr_day, curr_night, bill):
    return {
        "meter_id": meter_id,
        "date": date,
        "prev_day": prev_day,
        "prev_night": prev_night,
        "curr_day": curr_day,
        "curr_night": curr_night,
        "bill": bill
    }
