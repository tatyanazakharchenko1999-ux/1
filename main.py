import streamlit as st
import pandas as pd
from io import BytesIO

# Налаштування сторінки
st.set_page_config(page_title="Агро-Портал", layout="wide")

# Список питань (винесено окремо для синхронізації)
QUESTIONS_LIST = [
    "1. Якою є середньорічна температура?", 
    "2. Річна кількість опадів?", 
    "3. Період вегетації?",
    "4. Середня віддаленість полів від господарства, км?", 
    "5. Середній розмір угідь, га?",
    "6. Перелік механізованих робіт (машини та пристрої)", 
    "7. Площа будівель (сховища тощо)",
    "8. Попередники культури?", 
    "9. Витрати насіння (назви, норми)",
    "10. Яке насіння використовується?", 
    "11. Вихід побічної продукції",
    "12. Чи прибираються рештки з поля?", 
    "13. Засоби захисту рослин (ЗЗР)",
    "14. Обсяг робіт, виконаних машинами", 
    "15. Послуги сторонніх організацій"
]

# --- ІНІЦІАЛІЗАЦІЯ ПАМ'ЯТІ ---
if 'survey_answers' not in st.session_state:
    st.session_state.survey_answers = {f"q{i}": "" for i in range(1, 16)}
    st.session_state.survey_answers["q12"] = "Так"

if 'land_df' not in st.session_state:
    st.session_state.land_df = pd.DataFrame([
        {"Види угідь": "Рілля", "У власності (га)": 0.0, "Оренда (га)": 0.0, "Оренда (грн/рік)": 0.0, "Здано (га)": 0.0, "Здано (грн/рік)": 0.0},
        {"Види угідь": "Сінокоси", "У власності (га)": 0.0, "Оренда (га)": 0.0, "Оренда (грн/рік)": 0.0, "Здано (га)": 0.0, "Здано (грн/рік)": 0.0},
        {"Види угідь": "Пасовища", "У власності (га)": 0.0, "Оренда (га)": 0.0, "Оренда (грн/рік)": 0.0, "Здано (га)": 0.0, "Здано (грн/рік)": 0.0},
    ])

if 'crop_df' not in st.session_state:
    st.session_state.crop_df = pd.DataFrame([{
        "Назва культури / землекорист.": "", "Площа га": 0.0, "Основна прод. ц/га": 0.0, 
        "Ціна грн/ц": 0.0, "Побічна продукція (опис/ціна)": "", "Частка серт. насіння %": 0.0, 
        "Інтенсивність ЗЗР": "сер", "Послуги підрядників (опис/ціна)": ""
    }])

if 'prod_system' not in st.session_state:
    st.session_state.prod_system = "звичайна"

# --- НАВІГАЦІЯ ---
page = st.sidebar.radio("Розділи:", ["📋 Опитувальник", "📊 Структура земель", "🌾 Посівні площі"])

# --- 1. ОПИТУВАЛЬНИК ---
if page == "📋 Опитувальник":
    st.title("📋 Опитувальний лист для агронома")
    
    for i, q_text in enumerate(QUESTIONS_LIST, 1):
        key = f"q{i}"
        if i == 12:
            st.session_state.survey_answers[key] = st.selectbox(q_text, ["Так", "Ні", "Частково"], 
                index=["Так", "Ні", "Частково"].index(st.session_state.survey_answers[key]))
        elif i in [6, 9, 11, 13, 14, 15]:
            st.session_state.survey_answers[key] = st.text_area(q_text, value=st.session_state.survey_answers[key])
        else:
            st.session_state.survey_answers[key] = st.text_input(q_text, value=st.session_state.survey_answers[key])

# --- 2. СТРУКТУРА ЗЕМЕЛЬ ---
elif page == "📊 Структура земель":
    st.title("📊 Склад та структура земель")
    st.session_state.prod_system = st.radio("Система виробництва:", ["звичайна", "органічна"], 
        index=0 if st.session_state.prod_system == "звичайна" else 1, horizontal=True)

    st.session_state.land_df = st.data_editor(st.session_state.land_df, num_rows="dynamic", use_container_width=True)

    st.divider()
    st.subheader("Корекція витрат часу (Дані з Опитувальника):")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.survey_answers["q4"] = st.text_input("Середня відстань (км):", value=st.session_state.survey_answers["q4"])
    with col2:
        st.session_state.survey_answers["q5"] = st.text_input("Середній розмір поля:", value=st.session_state.survey_answers["q5"])

# --- 3. ПОСІВНІ ПЛОЩІ ---
elif page == "🌾 Посівні площі":
    st.title("🌾 Структура посівних площ (стор. 13)")
    st.session_state.crop_df = st.data_editor(st.session_state.crop_df, num_rows="dynamic", use_container_width=True)

# --- ЕКСПОРТ (ВИПРАВЛЕНИЙ) ---
st.sidebar.divider()
if st.sidebar.button("💾 Сформувати Excel з повними питаннями"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # Створюємо таблицю, де Питання — це повний текст, а не q1, q2...
        df_survey_full = pd.DataFrame({
            "Назва питання": QUESTIONS_LIST,
            "Відповідь користувача": [st.session_state.survey_answers[f"q{i}"] for i in range(1, 16)]
        })
        
        df_survey_full.to_excel(writer, sheet_name='Анкета', index=False)
        st.session_state.land_df.to_excel(writer, sheet_name='Землі', index=False)
        st.session_state.crop_df.to_excel(writer, sheet_name='Посіви', index=False)
    
    st.sidebar.download_button("📥 Завантажити повний звіт", output.getvalue(), "Agro_Full_Report.xlsx")