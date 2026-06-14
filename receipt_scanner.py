import streamlit as st
import google.generativeai as genai
import json
import sqlite3

# 1. Konfiguracja strony
st.set_page_config(page_title="ScanerAI", page_icon="🧾")

# 2. Konfiguracja klienta i modelu
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Używamy najnowszego stabilnego modelu
model = genai.GenerativeModel('gemini-2.5-flash')

def save_to_database(receipt_json):
    conn = sqlite3.connect('expanses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS receipts (store TEXT, total REAL, date TEXT)''')
    c.execute("INSERT INTO receipts VALUES (?,?,?)",
              (receipt_json['store'], receipt_json['total'], receipt_json['date']))
    conn.commit()  
    conn.close()

st.title("Skaner paragonów z zakupów")
img_file = st.camera_input("Zrób zdjęcie paragonu")

if img_file:
    with st.spinner("Gemini analizuje obraz..."):
        image_data = img_file.getvalue()
        prompt = """Wyciągnij dane z tego paragonu. Zwróć dane WYŁĄCZNIE w formacie JSON:
        {"store": "nazwa sklepu", "date": "YYYY-MM-DD", "total": 0.00}"""

        try:
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
            
            # Usuwamy ewentualne znaczniki markdown, które AI czasem dodaje
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            res_json = json.loads(clean_text)

            st.success("Dane odczytane poprawnie")
            st.json(res_json)

            if st.button("Zapisz dane do bazy danych"):
                save_to_database(res_json)
                st.balloons()
                st.info("Dane zostały zapisane do pliku expanses.db")

        except Exception as e:
            st.error(f"Błąd podczas przetwarzania: {e}")