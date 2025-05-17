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

if __name__ == "__main__":
    unittest.main()
