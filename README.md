# Дашборд медицинских работников для ClickHouse

Программа для подключения к базе данных ClickHouse и визуализации данных о медицинских работниках.

## Структура таблицы

Ожидаемая структура таблицы в ClickHouse:

```sql
CREATE TABLE medical_workers (
    medicalWorkerId String,
    medicalOrganizationOid String,
    structuralDivisionOid String,
    snils String,
    firstName String,
    middleName String,
    lastName String,
    birthDate String,
    medicalOrganizationName String,
    structuralSubdivisionName String,
    federalDirectoryPositionName String,
    positionTypeName String,
    rate String,
    startWorkDate String
) ENGINE = MergeTree()
ORDER BY medicalWorkerId;
```

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте подключение к ClickHouse в файле `config.py`:
```python
CLICKHOUSE_CONFIG = {
    'host': 'localhost',      # Хост ClickHouse
    'port': 9000,             # Порт (обычно 9000 для native протокола)
    'database': 'default',    # Имя базы данных
    'user': 'default',        # Пользователь
    'password': '',           # Пароль
}

TABLE_NAME = 'medical_workers'  # Имя вашей таблицы
```

## Запуск

### Тестирование подключения
```bash
python database.py
```

### Запуск дашборда
```bash
streamlit run app.py
```

Дашборд откроется в браузере по адресу `http://localhost:8501`

## Возможности дашборда

- **Общая статистика**: количество работников, организаций и должностей
- **Визуализация**:
  - Топ-10 организаций по количеству работников
  - Топ-10 должностей
  - Распределение по ставкам (столбчатая диаграмма и круговая)
- **Таблица данных** с фильтрами:
  - Фильтр по организации
  - Фильтр по должности
  - Фильтр по ставке
- **Экспорт данных** в CSV формат
- **Просмотр структуры таблицы**

## Файлы проекта

- `config.py` - конфигурация подключения к ClickHouse
- `database.py` - модуль для работы с базой данных
- `app.py` - приложение дашборда на Streamlit
- `requirements.txt` - зависимости Python
- `README.md` - документация

## Примечания

- Для работы требуется установленный и настроенный ClickHouse
- Порт 9000 используется для native протокола (clickhouse-connect)
- Для HTTP протокола используйте порт 8123