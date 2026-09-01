"""
Модуль для подключения и работы с ClickHouse
"""

import clickhouse_connect
from config import CLICKHOUSE_CONFIG, TABLE_NAME


def get_client():
    """
    Создает и возвращает клиент для подключения к ClickHouse
    
    Returns:
        clickhouse_connect.driver.client.Client: Клиент ClickHouse
    """
    client = clickhouse_connect.get_client(
        host=CLICKHOUSE_CONFIG['host'],
        port=CLICKHOUSE_CONFIG['port'],
        database=CLICKHOUSE_CONFIG['database'],
        user=CLICKHOUSE_CONFIG['user'],
        password=CLICKHOUSE_CONFIG['password']
    )
    return client


def test_connection():
    """
    Проверяет подключение к ClickHouse
    
    Returns:
        bool: True если подключение успешно, иначе False
    """
    try:
        client = get_client()
        result = client.command('SELECT 1')
        print(f"Подключение успешно! Результат: {result}")
        return True
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return False


def get_table_structure():
    """
    Получает структуру таблицы
    
    Returns:
        list: Список колонок таблицы
    """
    try:
        client = get_client()
        query = f"DESCRIBE TABLE {TABLE_NAME}"
        result = client.query(query)
        columns = []
        for row in result.result_rows:
            columns.append({
                'name': row[0],
                'type': row[1]
            })
        return columns
    except Exception as e:
        print(f"Ошибка получения структуры таблицы: {e}")
        return []


def get_medical_workers_data(limit=1000):
    """
    Получает данные о медицинских работниках
    
    Args:
        limit (int): Ограничение количества записей
        
    Returns:
        list: Список записей из таблицы
    """
    try:
        client = get_client()
        query = f"""
            SELECT 
                medicalWorkerId,
                medicalOrganizationOid,
                structuralDivisionOid,
                snils,
                firstName,
                middleName,
                lastName,
                birthDate,
                medicalOrganizationName,
                structuralSubdivisionName,
                federalDirectoryPositionName,
                positionTypeName,
                rate,
                startWorkDate
            FROM {TABLE_NAME}
            LIMIT {limit}
        """
        result = client.query(query)
        columns = [col.name for col in result.column_names]
        data = []
        for row in result.result_rows:
            record = dict(zip(columns, row))
            data.append(record)
        return data
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return []


def get_statistics():
    """
    Получает статистику по медицинским работникам
    
    Returns:
        dict: Статистические данные
    """
    try:
        client = get_client()
        
        # Общее количество работников
        count_query = f"SELECT COUNT() as total FROM {TABLE_NAME}"
        total_result = client.query(count_query)
        total_count = total_result.result_rows[0][0] if total_result.result_rows else 0
        
        # Количество по организациям
        org_query = f"""
            SELECT 
                medicalOrganizationName,
                COUNT() as worker_count
            FROM {TABLE_NAME}
            WHERE medicalOrganizationName != ''
            GROUP BY medicalOrganizationName
            ORDER BY worker_count DESC
            LIMIT 10
        """
        org_result = client.query(org_query)
        org_stats = []
        for row in org_result.result_rows:
            org_stats.append({
                'organization': row[0],
                'count': row[1]
            })
        
        # Количество по должностям
        position_query = f"""
            SELECT 
                federalDirectoryPositionName,
                COUNT() as worker_count
            FROM {TABLE_NAME}
            WHERE federalDirectoryPositionName != ''
            GROUP BY federalDirectoryPositionName
            ORDER BY worker_count DESC
            LIMIT 10
        """
        position_result = client.query(position_query)
        position_stats = []
        for row in position_result.result_rows:
            position_stats.append({
                'position': row[0],
                'count': row[1]
            })
        
        # Распределение по ставкам (rate)
        rate_query = f"""
            SELECT 
                rate,
                COUNT() as worker_count
            FROM {TABLE_NAME}
            WHERE rate != ''
            GROUP BY rate
            ORDER BY rate
        """
        rate_result = client.query(rate_query)
        rate_stats = []
        for row in rate_result.result_rows:
            rate_stats.append({
                'rate': str(row[0]),
                'count': row[1]
            })
        
        return {
            'total_workers': total_count,
            'organizations': org_stats,
            'positions': position_stats,
            'rates': rate_stats
        }
    except Exception as e:
        print(f"Ошибка получения статистики: {e}")
        return {
            'total_workers': 0,
            'organizations': [],
            'positions': [],
            'rates': []
        }


if __name__ == '__main__':
    print("Тестирование подключения к ClickHouse...")
    if test_connection():
        print("\nСтруктура таблицы:")
        structure = get_table_structure()
        for col in structure:
            print(f"  {col['name']}: {col['type']}")
        
        print("\nСтатистика:")
        stats = get_statistics()
        print(f"  Всего работников: {stats['total_workers']}")
        print(f"  Организаций: {len(stats['organizations'])}")
        print(f"  Должностей: {len(stats['positions'])}")
