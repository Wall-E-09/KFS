import json
import os
from datetime import datetime
from config import TARIFF_DAY, TARIFF_NIGHT

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_history_to_file(meter_id, history_data):
    """Експортує історію з MongoDB у файл"""
    filename = os.path.join(EXPORT_DIR, f"{meter_id}_history_{datetime.now().strftime('%Y%m%d')}.json")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False, default=str)
        return filename
    except Exception as e:
        print(f"Помилка експорту: {e}")
        return None

def generate_receipt(meter_id, record):
    """Генерує текстову квитанцію на основі запису з MongoDB"""
    receipt_text = f"""
    КВИТАНЦІЯ
    Номер лічильника: {meter_id}
    Дата: {record['date']}
    ----------------------------------
    Попередні показники:
      День: {record['prev_day']} кВт
      Ніч: {record['prev_night']} кВт
    Поточні показники:
      День: {record['curr_day']} кВт (+{record['curr_day'] - record['prev_day']} кВт)
      Ніч: {record['curr_night']} кВт (+{record['curr_night'] - record['prev_night']} кВт)
    ----------------------------------
    Розрахунок:
      Денний тариф: {record['curr_day'] - record['prev_day']} * {TARIFF_DAY} = {(record['curr_day'] - record['prev_day']) * TARIFF_DAY:.2f} грн
      Нічний тариф: {record['curr_night'] - record['prev_night']} * {TARIFF_NIGHT} = {(record['curr_night'] - record['prev_night']) * TARIFF_NIGHT:.2f} грн
    ----------------------------------
    ДО СПЛАТИ: {record['bill']:.2f} грн
    """
    
    # Зберігаємо квитанцію у файл
    filename = os.path.join(EXPORT_DIR, f"receipt_{meter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(receipt_text.strip())
        return filename
    except Exception as e:
        print(f"Помилка збереження квитанції: {e}")
        return None