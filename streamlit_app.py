import streamlit as st
import pandas as pd
import os
import base64

# Logo einfügen
st.image("Logo_namowo_blau.svg", width=150)

# Initialisierung von Session States
if "step" not in st.session_state:
    st.session_state.step = 1
if "project_info" not in st.session_state:
    st.session_state.project_info = {}
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "measures_state" not in st.session_state:
    st.session_state.measures_state = {}
if "difficulty_state" not in st.session_state:
    st.session_state.difficulty_state = {}
if "final_submitted" not in st.session_state:
    st.session_state.final_submitted = False
if "analysis_category_index" not in st.session_state:
    st.session_state.analysis_category_index = 0
if "measures_category_index" not in st.session_state:
    st.session_state.measures_category_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}

# Datei einlesen
file_path = "Analysefaktoren.xlsx"
df = pd.read_excel(file_path)
if "Antwort" not in df.columns:
    df["Antwort"] = ""
if "Umsetzbar" not in df.columns:
    df["Umsetzbar"] = ""
if "Schwierigkeitsgrad" not in df.columns:
    df["Schwierigkeitsgrad"] = ""
categories = df["Kategorie"].drop_duplicates().tolist()

# Fortschrittsanzeige und Style
progress_map = {1: 0.0, 2: 0.25, 3: 0.5, 4: 0.75, 5: 1.0}
progress = progress_map[st.session_state.step]
st.markdown("""
    <style>
        div.stButton > button {
            color: #005C9E;
            border: 1px solid #005C9E;
        }
        div.stButton > button:hover {
            background-color: #005C9E;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.progress(progress, text=f"Fortschritt: {int(progress * 100)}% abgeschlossen")

# Abschnitt 1: Begrüßung
if st.session_state.step == 1:
    st.title("Willkommen zum Check deines Standortes")
    st.write("In diesem Tool wirst du Schritt für Schritt durch die Standortanalyse und Maßnahmenerhebung geführt. Dabei prüfen wir, welche Faktoren an deinem Einzelhandelsstandort relevant sind und leiten daraus sinnvolle Mobilitätsmaßnahmen ab. Am Ende erhältst du ein übersichtliches Ergebnis, das durch unser Team gesichtet und mit konkreten Empfehlungen ergänzt wird.")
    if st.button("Weiter", key="start_next"):
        st.session_state.step = 2
        st.rerun()

# Abschnitt 2: Projektdaten erfassen
if st.session_state.step == 2:
    st.title("Projektdaten erfassen")
    with st.form(key="project_form"):
        project_title = st.text_input("Projektname", value=st.session_state.project_info.get("Projektname", ""))
        address = st.text_input("Adresse des Standorts", value=st.session_state.project_info.get("Adresse", ""))
        name = st.text_input("Vor- und Nachname", value=st.session_state.project_info.get("Name", ""))
        email = st.text_input("E-Mail", value=st.session_state.project_info.get("E-Mail", ""))
        client_address = st.text_input("Adresse des Auftraggebers", value=st.session_state.project_info.get("Auftraggeberadresse", ""))

        musterdaten = st.form_submit_button("Musterdaten")
        submitted = st.form_submit_button("Weiter")

        if musterdaten:
            st.session_state.project_info = {
                "Projektname": "Pilotstandort REWE Nord",
                "Adresse": "Musterstraße 123, 12345 Musterstadt",
                "Name": "Max Mustermann",
                "E-Mail": "max.mustermann@example.com",
                "Auftraggeberadresse": "Beispielweg 5, 54321 Beispielstadt"
            }
            st.rerun()

        if submitted and all([project_title, address, name, email, client_address]):
            st.session_state.project_info = {
                "Projektname": project_title,
                "Adresse": address,
                "Name": name,
                "E-Mail": email,
                "Auftraggeberadresse": client_address
            }
            st.session_state.step = 3
            st.rerun()
        elif submitted:
            st.warning("Bitte alle Felder ausfüllen, um fortzufahren.")

    # Move "Zurück" button outside the form
    if st.button("Zurück", key="project_back"):
        st.session_state.step = 1
        st.rerun()

# Abschnitt 3: Analyse
analysis_file = f"{st.session_state.project_info.get('Projektname', 'projekt')}_Analyseergebnisse_temp.xlsx"
if st.session_state.step == 3:
    st.header("Analyse")

    # Fortschrittsanzeige für die Analyse
    progress = min((st.session_state.analysis_category_index + 1) / len(categories), 1.0)  # Clamp progress to 1.0
    st.progress(progress, text=f"Analysefortschritt: {int(progress * 100)}% abgeschlossen")

    if st.session_state.analysis_category_index < len(categories):
        current_category = categories[st.session_state.analysis_category_index]
        st.subheader(current_category)

        selected_df = df[df["Kategorie"] == current_category]

        for index, row in selected_df.iterrows():
            toggle_key = f"analyse_{index}"
            antwort = str(row["Antwort"]).strip().lower()
            default = st.session_state.answers.get(toggle_key, antwort == "ja")
            toggle = st.checkbox(f"**{row['Überschrift']}**\n{row['Frage']}", value=default, key=toggle_key)
            st.session_state.answers[toggle_key] = toggle
            df.at[index, "Antwort"] = "ja" if toggle else "nein"

        if st.button("Weiter zur nächsten Kategorie"):
            st.session_state.analysis_category_index += 1
            df.to_excel(analysis_file, index=False)
            st.rerun()
    else:
        # Transition to the measures section after the last category
        if "Maßnahme" not in df.columns:
            df["Maßnahme"] = ""  # Ensure the "Maßnahme" column exists
        df.to_excel(analysis_file, index=False)
        st.session_state.analysis_done = True
        st.session_state.step = 4  # Move to the measures section
        st.session_state.measures_category_index = 0
        st.rerun()

    # Move "Zurück" button outside the loop
    if st.button("Zurück", key="analysis_back"):
        if st.session_state.analysis_category_index > 0:
            st.session_state.analysis_category_index -= 1
        else:
            st.session_state.step = 2
        st.rerun()

# Abschnitt 4: Maßnahmen
final_export_file = f"{st.session_state.project_info.get('Projektname', 'projekt')}_Finale_Analysefaktoren_temp.xlsx"
if st.session_state.step == 4 and os.path.exists(analysis_file):
    st.header("Maßnahmen")
    df_analysis = pd.read_excel(analysis_file)

    # Debugging: Überprüfen, ob die Spalte "Maßnahme" korrekt gefüllt ist
    if "Maßnahme" not in df_analysis.columns:
        st.error("Die Spalte 'Maßnahme' fehlt in der Analyse-Datei.")
        st.stop()

    # Filterung: Nur Maßnahmen mit "Yes" anzeigen
    filtered_df = df_analysis[df_analysis["Maßnahme"].astype(str).str.lower() == "yes"]

    # Debugging: Überprüfen, ob der Filter Ergebnisse liefert
    if filtered_df.empty:
        st.info("Für die ausgewählten Analyseantworten wurden keine Maßnahmen vorgeschlagen.")
        st.write("Debugging-Info: Überprüfen Sie die Spalte 'Maßnahme' und die Filterbedingungen.")
        st.write(df_analysis[["Antwort", "Maßnahme"]])  # Zeige relevante Spalten zur Überprüfung
        st.session_state.step = 5
        st.rerun()

    measures_categories = filtered_df["Kategorie"].drop_duplicates().tolist()

    # Fortschrittsanzeige für Maßnahmen
    progress = min((st.session_state.measures_category_index + 1) / len(measures_categories), 1.0)  # Clamp progress to 1.0
    st.progress(progress, text=f"Maßnahmenfortschritt: {int(progress * 100)}% abgeschlossen")

    if st.session_state.measures_category_index < len(measures_categories):
        current_category = measures_categories[st.session_state.measures_category_index]
        st.subheader(current_category)
        selected_df = filtered_df[filtered_df["Kategorie"] == current_category]

        for index, row in selected_df.iterrows():
            toggle_key = f"massnahme_{index}"
            toggle = st.checkbox(f"**{row['Überschrift']}**\n{row['Frage']}", key=toggle_key)
            st.session_state.measures_state[toggle_key] = toggle

            difficulty_key = f"difficulty_{index}"
            if toggle:
                difficulty = st.select_slider("Schwierigkeitsgrad", options=["Leicht", "Mittel", "Schwer"], key=difficulty_key)
                st.session_state.difficulty_state[difficulty_key] = difficulty
            else:
                difficulty = ""

            df_analysis.at[row.name, "Umsetzbar"] = "ja" if toggle else "nein"
            df_analysis.at[row.name, "Schwierigkeitsgrad"] = difficulty

        if st.button("Weiter zur nächsten Kategorie Maßnahmen"):
            st.session_state.measures_category_index += 1
            df_analysis.to_excel(final_export_file, index=False)
            st.rerun()
    else:
        # Transition to the results section after the last category
        df_analysis.to_excel(final_export_file, index=False)
        st.session_state.step = 5  # Move to the results section
        st.rerun()

    # Move "Zurück" button outside the loop
    if st.button("Zurück", key="measures_back"):
        if st.session_state.measures_category_index > 0:
            st.session_state.measures_category_index -= 1
        else:
            st.session_state.step = 3
            st.session_state.analysis_category_index = len(categories) - 1
        st.rerun()

# Abschnitt 5: Ergebnis & Versand
if st.session_state.step == 5:
    if not st.session_state.final_submitted:
        st.header("Analyse abgeschlossen")
        st.write("Die Analyse- und Maßnahmenerhebung ist abgeschlossen. Deine Angaben werden nun von unserem Team bei namowo geprüft. In der Regel erhältst du innerhalb von 48 Stunden ein Konzept mit konkreten Umsetzungsempfehlungen.")

        def create_download_link(file_path, label):
            with open(file_path, "rb") as f:
                file_data = f.read()
            b64 = base64.b64encode(file_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{label}</a>'
            return href

        if st.button("Erhebung abschicken"):
            df_final = pd.read_excel(final_export_file)
            df_final.to_excel("Finale_Analyse.xlsx", index=False)
            st.session_state.final_submitted = True
            st.success("Vielen Dank!")
            download_link = create_download_link("Finale_Analyse.xlsx", "📅 Finale Ergebnisse herunterladen")
            st.markdown(download_link, unsafe_allow_html=True)

        # Move "Zurück" button outside the submission logic
        if st.button("Zurück", key="result_back"):
            st.session_state.step = 4
            st.session_state.measures_category_index = len(measures_categories) - 1
            st.rerun()
    else:
        st.title("Vielen Dank!")
