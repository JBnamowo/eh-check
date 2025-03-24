import streamlit as st
import pandas as pd
import os

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

# Zustand für die abgeschlossene Analyse verwalten
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# Analyse-Abschnitt
st.header("Analyse")
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

# Button für Analyse abschließen
analysis_file = f"{project_name}_Analyseergebnisse.xlsx"
if st.button("Analyse abschließen"):
    df.to_excel(analysis_file, index=False)
    st.session_state.analysis_done = True
    st.success(f"Analyseergebnisse gespeichert als {analysis_file}")

# Maßnahmen-Abschnitt (nur sichtbar, wenn Analyse abgeschlossen ist)
if st.session_state.analysis_done and os.path.exists(analysis_file):
    st.header("Maßnahmen")
    df_analysis = pd.read_excel(analysis_file)
    filtered_df = df_analysis[df_analysis["Antwort"] == "nein"]
    measures = {}
    difficulties = {}
    
    for category in categories:
        category_df = filtered_df[filtered_df["Kategorie"] == category]
        if not category_df.empty:
            with st.expander(category):
                for index, row in category_df.iterrows():
                    st.write(f"**{row['Überschrift']}**")
                    st.write(row['Frage'])
                    toggle = st.toggle("", key=f"massnahme_{index}", value=False)
                    measures[row.name] = "ja" if toggle else "nein"
                    difficulty = st.select_slider("Schwierigkeitsgrad", options=["Leicht", "Mittel", "Schwer"], key=f"difficulty_{index}")
                    difficulties[row.name] = difficulty
    
    # Speichern der Maßnahmen
    if st.button("Speichern & Exportieren"):
        for idx, answer in measures.items():
            df_analysis.at[idx, "Umsetzbar"] = answer
        for idx, difficulty in difficulties.items():
            df_analysis.at[idx, "Schwierigkeitsgrad"] = difficulty
        export_filename = f"{project_name}_Finale_Analysefaktoren.xlsx"
        df_analysis.to_excel(export_filename, index=False)
        st.success(f"Datei gespeichert als {export_filename}")
        with open(export_filename, "rb") as file:
            st.download_button("📥 Datei herunterladen", file, file_name=export_filename)

# Zurücksetzen der Antworten
if st.button("Antworten zurücksetzen"):
    df["Antwort"] = ""
    df["Umsetzbar"] = ""
    df["Schwierigkeitsgrad"] = ""
    df.to_excel(file_path, index=False)
    if os.path.exists(analysis_file):
        os.remove(analysis_file)
    st.session_state.analysis_done = False
    st.rerun()
