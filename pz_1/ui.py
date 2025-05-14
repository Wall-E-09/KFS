import tkinter as tk
from tkinter import messagebox, filedialog
from logic import process_meter_data
from database import meters, history, bills
import os
import json
from datetime import datetime
from config import (BASE_TARIFF_DAY, BASE_TARIFF_NIGHT,
                   HIGH_TARIFF_DAY, HIGH_TARIFF_NIGHT,
                   TARIFF_LIMIT)

class EnergyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Двофазний лічильник - День/Ніч")

        tk.Label(root, text="Номер лічильника:").grid(row=0, column=0, sticky="w")
        tk.Label(root, text="Денний тариф (кВт):").grid(row=1, column=0, sticky="w")
        tk.Label(root, text="Нічний тариф (кВт):").grid(row=2, column=0, sticky="w")

        self.entry_id = tk.Entry(root)
        self.entry_day = tk.Entry(root)
        self.entry_night = tk.Entry(root)

        self.entry_id.grid(row=0, column=1, padx=10, pady=5)
        self.entry_day.grid(row=1, column=1, padx=10, pady=5)
        self.entry_night.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(root, text="Відправити дані", command=self.submit).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(root, text="Показати історію", command=self.show_history).grid(row=4, column=0, columnspan=2)
        tk.Button(root, text="Показати лічильники", command=self.show_meters).grid(row=5, column=0, columnspan=2)
        tk.Button(root, text="Показати рахунки", command=self.show_bills).grid(row=6, column=0, columnspan=2)
        tk.Button(root, text="Експортувати історію", command=self.export_history).grid(row=7, column=0, pady=5)
        tk.Button(root, text="Відкрити папку з квитанціями", command=self.open_receipts_folder).grid(row=7, column=1, pady=5)
        tk.Button(root, text="Згенерувати квитанцію", command=self.generate_receipt).grid(row=8, column=0, columnspan=2, pady=5)

        self.output = tk.Text(root, height=20, width=100)
        self.output.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    def submit(self):
        meter_id = self.entry_id.get()
        try:
            day = int(self.entry_day.get())
            night = int(self.entry_night.get())
            result = process_meter_data(meter_id, day, night)
            messagebox.showinfo("Успіх", f"Рахунок: {result['amount']:.2f} грн\nВикористано: День - {result['used_day']} кВт, Ніч - {result['used_night']} кВт")
        except ValueError:
            messagebox.showerror("Помилка", "Введіть числові значення")

    def show_history(self):
        self.output.delete("1.0", tk.END)
        meter_id = self.entry_id.get()
        if not meter_id:
            messagebox.showerror("Помилка", "Введіть номер лічильника")
            return
            
        self.output.insert(tk.END, f"=== ІСТОРІЯ ПОКАЗНИКІВ ДЛЯ ЛІЧИЛЬНИКА {meter_id} ===\n")
        for h in history.find({"meter_id": meter_id}):
            self.output.insert(tk.END, f"{h}\n")

    def show_meters(self):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "=== ВСІ ЛІЧИЛЬНИКИ В СИСТЕМІ ===\n")
        for m in meters.find():
            self.output.insert(tk.END, f"{m}\n")

    def show_bills(self):
        self.output.delete("1.0", tk.END)
        meter_id = self.entry_id.get()
        if not meter_id:
            messagebox.showerror("Помилка", "Введіть номер лічильника")
            return
            
        self.output.insert(tk.END, f"=== РАХУНКИ ДЛЯ ЛІЧИЛЬНИКА {meter_id} ===\n")
        for b in bills.find({"meter_id": meter_id}):
            self.output.insert(tk.END, f"{b}\n")
    
    def export_history(self):
        meter_id = self.entry_id.get()
        if not meter_id:
            messagebox.showerror("Помилка", "Введіть номер лічильника")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{meter_id}_history_export.json"
        )
        
        if file_path:
            try:
                history_data = list(history.find({"meter_id": meter_id}))
                with open(file_path, "w", encoding='utf-8') as f:
                    json.dump(history_data, f, indent=2, default=str, ensure_ascii=False)
                messagebox.showinfo("Успіх", f"Історію експортовано до {file_path}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося експортувати: {e}")

    def open_receipts_folder(self):
        receipts_path = os.path.abspath("receipts")
        if not os.path.exists(receipts_path):
            os.makedirs(receipts_path, exist_ok=True)
        os.startfile(receipts_path)

    def generate_receipt(self):
        meter_id = self.entry_id.get()
        if not meter_id:
            messagebox.showerror("Помилка", "Введіть номер лічильника")
            return
        
        last_bill = bills.find_one({"meter_id": meter_id}, sort=[("date", -1)])
        if not last_bill:
            messagebox.showinfo("Інформація", "Немає даних для генерації квитанції")
            return
            
        last_history = history.find_one({"meter_id": meter_id}, sort=[("date", -1)])
        meter_data = meters.find_one({"meter_id": meter_id})
        
        if not last_history or not meter_data:
            messagebox.showerror("Помилка", "Дані лічильника не знайдені")
            return
        
        from config import (BASE_TARIFF_DAY, BASE_TARIFF_NIGHT,
                        HIGH_TARIFF_DAY, HIGH_TARIFF_NIGHT,
                        TARIFF_LIMIT)
        
        prev_total = meter_data.get("total_consumption", 0) - last_history['used_day'] - last_history['used_night']
        current_total = meter_data.get("total_consumption", 0)
        tariff_type = "Базовий" if current_total <= TARIFF_LIMIT else "Підвищений"
        
        if current_total <= TARIFF_LIMIT:
            day_cost = last_history['used_day'] * BASE_TARIFF_DAY
            night_cost = last_history['used_night'] * BASE_TARIFF_NIGHT
        elif prev_total >= TARIFF_LIMIT:
            day_cost = last_history['used_day'] * HIGH_TARIFF_DAY
            night_cost = last_history['used_night'] * HIGH_TARIFF_NIGHT
        else:
            remaining = TARIFF_LIMIT - prev_total
            if (last_history['used_day'] + last_history['used_night']) <= remaining:
                day_cost = last_history['used_day'] * BASE_TARIFF_DAY
                night_cost = last_history['used_night'] * BASE_TARIFF_NIGHT
            else:
                base_part_day = min(last_history['used_day'], remaining * (last_history['used_day'] / (last_history['used_day'] + last_history['used_night'])))
                base_part_night = remaining - base_part_day
                
                day_cost = base_part_day * BASE_TARIFF_DAY + (last_history['used_day'] - base_part_day) * HIGH_TARIFF_DAY
                night_cost = base_part_night * BASE_TARIFF_NIGHT + (last_history['used_night'] - base_part_night) * HIGH_TARIFF_NIGHT
        
        receipt_text = f"""
        {'='*50}
        КВИТАНЦІЯ №{last_bill['date']}
        Лічильник: {meter_id}
        Дата формування: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        {'-'*50}
        Тарифні ставки:
        - Базовий тариф (до {TARIFF_LIMIT} кВт*год):
        День: {BASE_TARIFF_DAY} грн/кВт*год | Ніч: {BASE_TARIFF_NIGHT} грн/кВт*год
        - Підвищений тариф:
        День: {HIGH_TARIFF_DAY} грн/кВт*год | Ніч: {HIGH_TARIFF_NIGHT} грн/кВт*год
        {'-'*50}
        Загальна витрата: {current_total} кВт*год ({tariff_type} тариф)
        {'-'*50}
        ПОКАЗНИКИ:
        Попередні:
        День: {last_history['prev_day']} кВт | Ніч: {last_history['prev_night']} кВт
        Поточні:
        День: {last_history['new_day']} кВт | Ніч: {last_history['new_night']} кВт
        Спожито:
        День: {last_history['used_day']} кВт | Ніч: {last_history['used_night']} кВт
        {'-'*50}
        РОЗРАХУНОК:
        Денна витрата: {last_history['used_day']} кВт * {BASE_TARIFF_DAY if current_total <= TARIFF_LIMIT else HIGH_TARIFF_DAY} грн = {day_cost:.2f} грн
        Нічна витрата: {last_history['used_night']} кВт * {BASE_TARIFF_NIGHT if current_total <= TARIFF_LIMIT else HIGH_TARIFF_NIGHT} грн = {night_cost:.2f} грн
        {'-'*50}
        СУМА ДО СПЛАТИ: {last_bill['amount']:.2f} грн
        {'='*50}
        """
        
        receipts_path = os.path.abspath("receipts")
        os.makedirs(receipts_path, exist_ok=True)
        filename = os.path.join(receipts_path, f"receipt_{meter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(receipt_text.strip())
            messagebox.showinfo("Успіх", f"Квитанцію збережено у файлі:\n{filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти квитанцію: {e}")