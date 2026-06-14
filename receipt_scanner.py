import streamlit as st
import google.generativeai as genai
import json
import sqlite3

# Konfiguracja strony musi być na samym początku
st.set_page_config(page_title="ScanerAI", page_icon="🧾")

# Konfiguracja klienta
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def save_to_database(receipt_json):
    conn = sqlite3.connect('expanses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS receipts
                (store TEXT, total REAL, date TEXT)''')
    c.execute("INSERT INTO receipts VALUES (?,?,?)",
              (receipt_json['store'], receipt_json['total'], receipt_json['date']))
    conn.commit()  
    conn.close()

st.title("Skaner paragonów z zakupów")
st.write("Zrób zdjęcie paragonu, a AI zajmie się resztą") 

img_file = st.camera_input("Zrób zdjęcie paragonu")

if img_file:
    with st.spinner("Gemini analizuje obraz..."):
        image_data = img_file.getvalue()

        prompt = """
        Wyciągnij dane z tego paragonu. Zwróć dane wyłącznie w formacie JSON:
        {
            "store": "nazwa sklepu", 
            "date": "YYYY-MM-DD",
            "total": 0.00
        }"""

        try:
            # Wywołanie modelu
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
            
            # Parsowanie JSON z odpowiedzi
            res_json = json.loads(response.text)

            st.success("Dane odczytane poprawnie")
            st.json(res_json)

            if st.button("Zapisz dane do bazy danych"):
                save_to_database(res_json)
                st.balloons()
                st.info("Dane zostały zapisane do pliku expanses.db")

        except Exception as e:
            st.error(f"Błąd podczas przetwarzania: {e}")