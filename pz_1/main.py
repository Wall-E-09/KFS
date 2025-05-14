from database import process_meter_data
from datetime import datetime

# Приклад обробки лічильників
meter_id = "12345"
new_day = 1000
new_night = 800
date = datetime.now().isoformat()

result = process_meter_data(meter_id, new_day, new_night, date)
print(f"Processed meter {meter_id}: {result}")
