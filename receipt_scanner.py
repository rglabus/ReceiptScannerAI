import streamlit as st
import google.generativeai as genai
import json
import sqlite3

# krok 1 konfiuracja klienta gemini 
# dlaczego uzywamy nowej biblioteki google genai? (jest to standard w 2026)
# api key pobieramy z funkcjonalnościa "secrets" aby nie poblikować go publicznie
# client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(...)


# krok 2 funkcja bazy danych - tworzymy lub łączymy się z bazą danych SQLite
st.title("Skaner paragonów z zakupów")
st.subheader("Wprowadź dane z paragonu, a ja pomogę Ci je zorganizować i przechowywać w bazie danych.")

def save_to_database(receipt_json):
    conn = sqlite3.connect('expanses.db')
    c = conn.cursor()
    # Tworzymy tabelę, jeśli nie istnieje
    c.execute('''CREATE TABLE IF NOT EXISTS receipts
                (store TEXT, total REAL, date TEXT)''')
# Wkładamy dane do tabeli
    c.execute("INSERT INTO receipts VALUES (?,?,?)",
              (receipt_json['store'], receipt_json['total'], receipt_json['date']))
    # Zatwierdzamy zmiany i zamykamy połączenie
    conn.commit()  
    conn.close()

# krok 3 User Interface - interfejs użytkownika
st.set_page_config(page_title="ScanerAI", page_icon="🧾")
st.title("Skaner paragonów z zakupów")
st.write("Zrób zdjęcie z paragonu, a AI zajmie sie resztą") 

# Komponent kamery - streamlit nie ma natywnie, ale można użyć zewnętrznej biblioteki lub komponentu
# Tutaj zakładamy, że mamy komponent do robienia zdjęć i zwracania ich jako plik lub URL
# image = st.camera_input("Zrób zdjęcie paragonu")

img_file = st.camera_input("Zrób zdjęcie paragonu")

if img_file:
    # wyświetlamy spinner, żeby UX był profesjonalny (uzytkonik widzi, ze coś się dzieje)
    with st.spinner("Gemini analizuje obraz..."):

        #pobieramy bajty orazu 
        #Dlaczego: Modele multimodalne Gemini przyjmują surowe bajty,nie musimy zapisywac pliku na dysku
        image_data = img_file.getvalue()

        # Definiujemy instrukcję dla modelu 
        # Dlaczego prompt musi być konkretny. W 2026 używamy wbudowanej usługi JSON.

        prompt = """
        Wyciągnij dane z tego paragonu. Zwróć dane wyłącznie w formacie JSON:
        {
            "store": "nazwa sklepu", 
            "date": "data w formacie YYYY-MM-DD",
            "totsl": suma jako liczba 
        }"""

        # Wywołanie modelu
        # Dlaczego: Gemini 3 Flasch jest ultra szybki i tani. Idealny do prostych zadań OCR.
        model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
            contents=[prompt, image_data]
        )
    # Parsujemy odpowiedź jako JSON
    try: 
        # 1.  wysyłanie zapytania do modelu i odbieranie odpowiedzi
        response = client.models.generate_content(
            model='gemini-3-flash', 
            contents=[prompt,image_data],
            config={'reponse_mime_type':'application/json'}
        )
        # 2. Wyciągamy tekst odpowiedzi ( poprawna metoda dla google-genai)
        res_json = json.loads(response.text)

        # 3. Wyświetlamy dane w UI 
        st.success("Dane odczytane poprawnie")
        st.json(res_json)

        # 4. Dodajemy przycisk do zapisu do bazy danych 
        if st.button(":Zapisz dane do bazy danych"):
                    save_to_database(res_json)
                    st.balloons() #Efekt wizualny po sukcesie
                    st.info("Dane zostały zapisane do pliku expanses.db")

    except Exception as e :
        st.error(f"Błąd podczas przetwarzania danych: {e}")        

