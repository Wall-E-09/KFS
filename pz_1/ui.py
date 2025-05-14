import tkinter as tk
from tkinter import messagebox
from logic import process_meter_data
from database import meters, history

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

        self.output = tk.Text(root, height=20, width=100)
        self.output.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def submit(self):
        meter_id = self.entry_id.get()
        try:
            day = int(self.entry_day.get())
            night = int(self.entry_night.get())
            bill = process_meter_data(meter_id, day, night)
            messagebox.showinfo("Успіх", f"Квитанція: {bill:.2f} грн")
        except ValueError:
            messagebox.showerror("Помилка", "Введіть числові значення")

    def show_history(self):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "=== ІСТОРІЯ ПОКАЗНИКІВ ===\n")
        for h in history.find():
            self.output.insert(tk.END, f"{h}\n")

    def show_meters(self):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "=== АКТУАЛЬНІ ЛІЧИЛЬНИКИ ===\n")
        for m in meters.find():
            self.output.insert(tk.END, f"{m}\n")
