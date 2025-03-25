import streamlit as st
import pandas as pd
import os

# Logo einfügen
st.image("Logo_namowo_blau.svg", width=150)

# Titel der Anwendung
st.title("Analysefaktoren - Interaktive Auswertung")

# Eingabefeld für den Projektnamen
project_name = st.text_input("Projektname eingeben:", "")
if not project_name:
    st.warning("Bitte einen Projektnamen eingeben, um die Datei speichern zu können.")
    st.stop()

# Datei einlesen
file_path = "Analysefaktoren.xlsx"
df = pd.read_excel(file_path)

# Sicherstellen, dass die Spalten existieren
df["Antwort"] = df.get("Antwort", "")
df["Umsetzbar"] = df.get("Umsetzbar", "")
df["Schwierigkeitsgrad"] = df.get("Schwierigkeitsgrad", "")

# Zustand für abgeschlossene Analyse und Maßnahmen verwalten
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "measures_state" not in st.session_state:
    st.session_state.measures_state = {}
if "difficulty_state" not in st.session_state:
    st.session_state.difficulty_state = {}

# Analyse-Abschnitt
st.header("Analyse")
st.write("Wähle die Faktoren aus, die auf diesen Standort zutreffen.")
categories = df["Kategorie"].unique()
responses = {}

for category in categories:
    with st.expander(category):
        category_df = df[df["Kategorie"] == category]
        
        for index, row in category_df.iterrows():
            st.write(f"**{row['Überschrift']}**")
            st.write(row['Frage'])
            toggle = st.toggle("", key=f"analyse_{index}", value=(row["Antwort"] == "ja"))
            responses[row.name] = "ja" if toggle else "nein"

# Speichern der Antworten aus der Analyse
for idx, answer in responses.items():
    df.at[idx, "Antwort"] = answer

# Temporäre Zwischenspeicherung für Maßnahmen
analysis_file = f"{project_name}_Analyseergebnisse_temp.xlsx"
final_export_file = f"{project_name}_Finale_Analysefaktoren_temp.xlsx"
if st.button("Analyse abschließen"):
    df.to_excel(analysis_file, index=False)
    st.session_state.analysis_done = True
    st.success(f"Analyseergebnisse gespeichert")

# Maßnahmen-Abschnitt (nur sichtbar, wenn Analyse abgeschlossen ist)
if st.session_state.analysis_done and os.path.exists(analysis_file):
    st.header("Maßnahmen")
    st.write("Wähle hier die Maßnahmen aus, die an diesem Standort umsetzbar erscheinen und bewerte, wie hoch der Schwierigkeitsgrad für die Umsetzung ist.")
    df_analysis = pd.read_excel(analysis_file)
    filtered_df = df_analysis[df_analysis["Antwort"] == "nein"]
    
    for category in categories:
        category_df = filtered_df[filtered_df["Kategorie"] == category]
        if not category_df.empty:
            with st.expander(category):
                for index, row in category_df.iterrows():
                    st.write(f"**{row['Überschrift']}**")
                    st.write(row['Frage'])
                    toggle_key = f"massnahme_{index}"
                    toggle_value = st.session_state.measures_state.get(toggle_key, False)
                    toggle = st.toggle("", key=toggle_key, value=toggle_value)
                    st.session_state.measures_state[toggle_key] = toggle
                    
                    difficulty_key = f"difficulty_{index}"
                    if toggle:
                        difficulty_value = st.session_state.difficulty_state.get(difficulty_key, "Leicht")
                        difficulty = st.select_slider("Schwierigkeitsgrad", options=["Leicht", "Mittel", "Schwer"], key=difficulty_key, value=difficulty_value)
                        st.session_state.difficulty_state[difficulty_key] = difficulty
                    else:
                        difficulty = ""
                    
                    df_analysis.at[row.name, "Umsetzbar"] = "ja" if toggle else "nein"
                    df_analysis.at[row.name, "Schwierigkeitsgrad"] = difficulty
    
    # Speichern der Maßnahmen
    if st.button("Speichern & Exportieren"):
        df_analysis.to_excel(final_export_file, index=False)
        st.success("Finale Analyse gespeichert")
        with open(final_export_file, "rb") as file:
            st.download_button("📥 Datei herunterladen", file, file_name=f"{project_name}_Finale_Analysefaktoren.xlsx")

# Zurücksetzen der Antworten und Löschen temporärer Dateien
if st.button("Antworten zurücksetzen"):
    df["Antwort"] = ""
    df["Umsetzbar"] = ""
    df["Schwierigkeitsgrad"] = ""
    df.to_excel(file_path, index=False)
    if os.path.exists(analysis_file):
        os.remove(analysis_file)
    if os.path.exists(final_export_file):
        os.remove(final_export_file)
    st.session_state.analysis_done = False
    st.session_state.measures_state = {}
    st.session_state.difficulty_state = {}
    st.rerun()
