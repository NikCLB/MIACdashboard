"""
Конфигурация подключения к ClickHouse
Заполните параметры подключения своими данными
"""

CLICKHOUSE_CONFIG = {
    'host': 'localhost',      # Хост ClickHouse
    'port': 9000,             # Порт (обычно 9000 для native протокола)
    'database': 'default',    # Имя базы данных
    'user': 'default',        # Пользователь
    'password': '',           # Пароль
}

# Имя таблицы с данными медицинских работников
TABLE_NAME = 'medical_workers'
