import streamlit as st
import google.generativeai as genai
import json
import sqlite3

st.set_page_config(page_title="ScanerAI", page_icon="🧾")

# Konfiguracja
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Zamiast 'models/gemini-1.5-flash', użyjmy 'gemini-1.5-flash' bez przedrostka
# lub spróbujmy najpopularniejszego modelu.
model_name = "gemini-1.5-flash" 

st.title("Skaner paragonów")

img_file = st.camera_input("Zrób zdjęcie paragonu")

if img_file:
    with st.spinner("Analizuję..."):
        image_data = img_file.getvalue()
        
        prompt = "Wyciągnij dane z tego paragonu w formacie JSON: {'store': '', 'date': '', 'total': 0.0}"
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
            
            st.write(response.text)
            st.success("Sukces!")
        except Exception as e:
            st.error(f"Błąd modelu: {e}")
            st.info("Jeśli błąd 404 nadal występuje, sprawdź czy klucz API w Streamlit Secrets jest poprawny i czy ma dostęp do Google AI Studio.")