"""
Дашборд для визуализации данных о медицинских работниках из ClickHouse
Запуск: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import (
    test_connection,
    get_table_structure,
    get_medical_workers_data,
    get_statistics
)


# Настройка страницы
st.set_page_config(
    page_title="Дашборд медицинских работников",
    page_icon="🏥",
    layout="wide"
)

# Заголовок
st.title("🏥 Дашборд медицинских работников")
st.markdown("---")


# Проверка подключения
@st.cache_resource
def check_db_connection():
    """Проверяет подключение к БД с кэшированием"""
    return test_connection()


if not check_db_connection():
    st.error("❌ Не удалось подключиться к ClickHouse. Проверьте настройки в config.py")
    st.stop()

st.success("✅ Подключение к ClickHouse успешно!")


# Боковая панель
st.sidebar.header("Настройки")

# Выбор количества записей
limit = st.sidebar.slider(
    "Количество записей для отображения",
    min_value=100,
    max_value=10000,
    value=1000,
    step=100
)

# Кнопка обновления
if st.sidebar.button("🔄 Обновить данные"):
    st.cache_data.clear()
    st.rerun()


# Получение статистики
@st.cache_data
def load_statistics():
    """Загружает статистику с кэшированием"""
    return get_statistics()


stats = load_statistics()


# Основные метрики
st.header("📊 Общая статистика")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Всего медицинских работников",
        value=f"{stats['total_workers']:,}",
        delta=None
    )

with col2:
    st.metric(
        label="Количество организаций",
        value=len(stats['organizations']),
        delta=None
    )

with col3:
    st.metric(
        label="Уникальных должностей",
        value=len(stats['positions']),
        delta=None
    )

st.markdown("---")


# Графики
st.header("📈 Визуализация данных")

# График 1: Топ организаций
if stats['organizations']:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Топ-10 организаций по количеству работников")
        org_df = pd.DataFrame(stats['organizations'])
        fig_org = px.bar(
            org_df,
            x='count',
            y='organization',
            orientation='h',
            labels={'count': 'Количество работников', 'organization': 'Организация'},
            color='count',
            color_continuous_scale='Blues'
        )
        fig_org.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_org, use_container_width=True)
    
    # График 2: Топ должностей
    with col2:
        st.subheader("Топ-10 должностей")
        if stats['positions']:
            pos_df = pd.DataFrame(stats['positions'])
            fig_pos = px.bar(
                pos_df,
                x='count',
                y='position',
                orientation='h',
                labels={'count': 'Количество работников', 'position': 'Должность'},
                color='count',
                color_continuous_scale='Greens'
            )
            fig_pos.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_pos, use_container_width=True)


# График 3: Распределение по ставкам
if stats['rates']:
    st.subheader("Распределение по ставкам")
    rate_df = pd.DataFrame(stats['rates'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_rate_bar = px.bar(
            rate_df,
            x='rate',
            y='count',
            labels={'rate': 'Ставка', 'count': 'Количество работников'},
            color='count',
            color_continuous_scale='Oranges'
        )
        fig_rate_bar.update_layout(height=400)
        st.plotly_chart(fig_rate_bar, use_container_width=True)
    
    with col2:
        fig_rate_pie = px.pie(
            rate_df,
            values='count',
            names='rate',
            title='Доля ставок'
        )
        fig_rate_pie.update_layout(height=400)
        st.plotly_chart(fig_rate_pie, use_container_width=True)


# Таблица с данными
st.markdown("---")
st.header("📋 Данные о медицинских работниках")

@st.cache_data
def load_data(limit):
    """Загружает данные с кэшированием"""
    return get_medical_workers_data(limit=limit)


data = load_data(limit)

if data:
    df = pd.DataFrame(data)
    
    # Фильтры
    st.subheader("Фильтры")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        if 'medicalOrganizationName' in df.columns:
            org_filter = st.multiselect(
                "Организация",
                options=df['medicalOrganizationName'].unique(),
                default=[]
            )
    
    with filter_col2:
        if 'federalDirectoryPositionName' in df.columns:
            position_filter = st.multiselect(
                "Должность",
                options=df['federalDirectoryPositionName'].unique(),
                default=[]
            )
    
    with filter_col3:
        if 'rate' in df.columns:
            rate_filter = st.multiselect(
                "Ставка",
                options=df['rate'].unique(),
                default=[]
            )
    
    # Применение фильтров
    filtered_df = df.copy()
    
    if 'medicalOrganizationName' in df.columns and org_filter:
        filtered_df = filtered_df[filtered_df['medicalOrganizationName'].isin(org_filter)]
    
    if 'federalDirectoryPositionName' in df.columns and position_filter:
        filtered_df = filtered_df[filtered_df['federalDirectoryPositionName'].isin(position_filter)]
    
    if 'rate' in df.columns and rate_filter:
        filtered_df = filtered_df[filtered_df['rate'].isin(rate_filter)]
    
    st.write(f"Показано {len(filtered_df)} из {len(df)} записей")
    
    # Отображение таблицы
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )
    
    # Кнопка скачивания
    csv = filtered_df.to_csv(index=False, sep=';')
    st.download_button(
        label="📥 Скачать данные в CSV",
        data=csv,
        file_name='medical_workers.csv',
        mime='text/csv'
    )
else:
    st.warning("Нет данных для отображения")


# Информация о структуре таблицы
with st.expander("📖 Структура таблицы"):
    structure = get_table_structure()
    if structure:
        struct_df = pd.DataFrame(structure)
        st.dataframe(struct_df, use_container_width=True)


# Нижняя информация
st.markdown("---")
st.caption("Дашборд создан для работы с данными ClickHouse о медицинских работниках")
