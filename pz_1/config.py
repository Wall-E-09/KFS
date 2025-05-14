# Базові тарифи (до 2000 кВт*год)
BASE_TARIFF_DAY = 2.64  # грн/кВт*год
BASE_TARIFF_NIGHT = 1.32  # половина денного (1.32 грн/кВт*год)

# Підвищений тариф (після 2000 кВт*год)
HIGH_TARIFF_DAY = 4.32  # грн/кВт*год
HIGH_TARIFF_NIGHT = 2.16  # половина денного (2.16 грн/кВт*год)

# Ліміт для базового тарифу (кВт*год)
TARIFF_LIMIT = 2000

# Коригування при зворотному ході лічильника
FAKE_ADDITION_DAY = 100
FAKE_ADDITION_NIGHT = 80

# Для зворотної сумісності (якщо десь використовувались старі назви)
TARIFF_DAY = BASE_TARIFF_DAY
TARIFF_NIGHT = BASE_TARIFF_NIGHT
TARIFFS = {
    "day": BASE_TARIFF_DAY,
    "night": BASE_TARIFF_NIGHT
}
ADJUSTMENT = {
    "day": FAKE_ADDITION_DAY,
    "night": FAKE_ADDITION_NIGHT
}