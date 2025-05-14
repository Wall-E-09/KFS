from config import BASE_TARIFF_DAY, BASE_TARIFF_NIGHT, HIGH_TARIFF_DAY, HIGH_TARIFF_NIGHT, TARIFF_LIMIT
import unittest
from logic import calculate_bill, process_meter_data
from unittest.mock import patch, MagicMock
from datetime import datetime
from database import meters, history, bills

class TestEnergySystem(unittest.TestCase):
    def test_calculate_bill_base_tariff(self):
        result = calculate_bill(100, 50, 0)
        expected = 100 * BASE_TARIFF_DAY + 50 * BASE_TARIFF_NIGHT
        self.assertAlmostEqual(result, expected)

    def test_calculate_bill_high_tariff(self):
        result = calculate_bill(100, 50, TARIFF_LIMIT)
        expected = 100 * HIGH_TARIFF_DAY + 50 * HIGH_TARIFF_NIGHT
        self.assertAlmostEqual(result, expected)

    def test_calculate_bill_mixed_tariff(self):
        result = calculate_bill(300, 200, TARIFF_LIMIT - 250)
        self.assertGreater(result, 300 * BASE_TARIFF_DAY + 200 * BASE_TARIFF_NIGHT)
        self.assertLess(result, 300 * HIGH_TARIFF_DAY + 200 * HIGH_TARIFF_NIGHT)

    def test_process_meter_data_new_meter(self):
        result = process_meter_data("test_meter_1", 100, 50)
        self.assertEqual(result["amount"], 0)
        self.assertEqual(result["used_day"], 0)
        self.assertEqual(result["used_night"], 0)
        self.assertEqual(meters.count_documents({"meter_id": "test_meter_1"}), 1)
        self.assertEqual(bills.count_documents({"meter_id": "test_meter_1"}), 1)

    def test_process_meter_data_existing_meter(self):
        process_meter_data("test_meter_2", 100, 50)
        result = process_meter_data("test_meter_2", 150, 80)
        
        self.assertGreater(result["amount"], 0)
        self.assertEqual(result["used_day"], 50)
        self.assertEqual(result["used_night"], 30)
        self.assertEqual(history.count_documents({"meter_id": "test_meter_2"}), 2)
        self.assertEqual(bills.count_documents({"meter_id": "test_meter_2"}), 2)

    def test_process_meter_data_counter_rollback(self):

        process_meter_data("test_meter_3", 100, 50)
        result = process_meter_data("test_meter_3", 90, 40)
        
        meter = meters.find_one({"meter_id": "test_meter_3"})
        self.assertEqual(meter["current_day"], 190)
        self.assertEqual(meter["current_night"], 120)
        self.assertEqual(result["used_day"], 90)
        self.assertEqual(result["used_night"], 70)

if __name__ == "__main__":
    unittest.main()
