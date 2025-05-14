import unittest
from logic import calculate_bill, process_meter_data
from database import meters, history
from bson import ObjectId
import os
from file_export import export_history_to_file, generate_receipt

class TestEnergySystem(unittest.TestCase):
    TEST_METER_ID = "test_meter_123"
    
    def setUp(self):
        # Очищаємо тестові дані
        meters.delete_one({"meter_id": self.TEST_METER_ID})
        history.delete_many({"meter_id": self.TEST_METER_ID})
        
        # Видаляємо тестові файли експорту
        if os.path.exists("exports"):
            for f in os.listdir("exports"):
                if f.startswith(self.TEST_METER_ID):
                    os.remove(os.path.join("exports", f))

    def test_calculate_bill(self):
        self.assertEqual(calculate_bill(10, 5), 10*2.5 + 5*1.2)
        self.assertEqual(calculate_bill(0, 0), 0)
        
    def test_process_meter_data(self):
        # Тестуємо основну функціональність
        bill = process_meter_data(self.TEST_METER_ID, 100, 50)
        self.assertEqual(bill, 0)
        
        bill = process_meter_data(self.TEST_METER_ID, 150, 80)
        self.assertAlmostEqual(bill, (150-100)*2.5 + (80-50)*1.2)
        
        # Перевіряємо, що квитанція створилась
        receipt_files = [f for f in os.listdir("exports") if f.startswith(f"receipt_{self.TEST_METER_ID}")]
        self.assertEqual(len(receipt_files), 1)
        
    def test_export_functions(self):
        # Підготуємо тестові дані
        process_meter_data(self.TEST_METER_ID, 100, 50)
        process_meter_data(self.TEST_METER_ID, 150, 80)
        
        # Тестуємо експорт історії
        history_data = list(history.find({"meter_id": self.TEST_METER_ID}))
        filename = export_history_to_file(self.TEST_METER_ID, history_data)
        self.assertTrue(os.path.exists(filename))
        
        # Тестуємо генерацію квитанції
        receipt_file = generate_receipt(self.TEST_METER_ID, history_data[-1])
        self.assertTrue(os.path.exists(receipt_file))

    def tearDown(self):
        self.setUp()

if __name__ == "__main__":
    unittest.main()