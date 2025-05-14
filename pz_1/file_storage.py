import json
import os
from datetime import datetime

HISTORY_DIR = "history"
RECEIPTS_DIR = "receipts"

os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(RECEIPTS_DIR, exist_ok=True)

def save_history_to_file(meter_id, data):
    """Зберігає історію у JSON-файл окремо від MongoDB"""
    filename = os.path.join(HISTORY_DIR, f"{meter_id}_history.json")
    try:
        with open(filename, "a") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Помилка збереження історії у файл: {e}")

def save_receipt_to_file(meter_id, data):
    """Генерує текстову квитанцію у файл"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(RECEIPTS_DIR, f"{meter_id}_{timestamp}.txt")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception as e:
        print(f"Помилка збереження квитанції: {e}")

def generate_receipt_text(meter_id, date, prev_day, prev_night, curr_day, curr_night, bill):
    """Генерує текст квитанції"""
    day_delta = curr_day - prev_day
    night_delta = curr_night - prev_night
    
    return f"""
    Квитанція №{date}
    Лічильник: {meter_id}
    Дата формування: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    ---
    Попередні показники:
      День: {prev_day} кВт
      Ніч: {prev_night} кВт
    ---
    Поточні показники:
      День: {curr_day} кВт (+{day_delta} кВт)
      Ніч: {curr_night} кВт (+{night_delta} кВт)
    ---
    Вартість:
      Денний тариф: {day_delta} * {TARIFF_DAY} = {day_delta * TARIFF_DAY:.2f} грн
      Нічний тариф: {night_delta} * {TARIFF_NIGHT} = {night_delta * TARIFF_NIGHT:.2f} грн
    ---
    ЗАГАЛЬНА СУМА ДО СПЛАТИ: {bill:.2f} грн
    """