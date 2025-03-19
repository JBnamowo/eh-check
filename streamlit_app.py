import streamlit as st
import pandas as pd
import io

def main():
    # Logo oben rechts anzeigen
    logo_path = "Logo_namowo_blau.svg"
    st.sidebar.image(logo_path, use_column_width=True)
    
    st.title("Maßnahmendatenbank")
    
    # Excel-Datei laden
    file_path = "Maßnahmen.xlsx"  # Datei liegt im Repository
    df = pd.read_excel(file_path)
    
    
    # Sicherstellen, dass die Spalte 'text' existiert und keine NaN-Werte enthält
    if 'text' not in df.columns or 'kategorie' not in df.columns:
        st.error("Benötigte Spalten fehlen!")
        return
    
    df['text'] = df['text'].fillna("Kein Text verfügbar")
    
    # Annahme: Die relevanten Spalten heißen 'kategorie', 'name' (Überschrift) und 'text' (Text)
    texte = df[['name', 'kategorie', 'text']].rename(columns={'name': 'überschrift'})
    
    ausgewählte_texte = {}
    
    # Gruppieren nach Kategorie
    kategorien = texte['kategorie'].unique()
    for kategorie in kategorien:
        with st.expander(kategorie):
            kategorietexte = texte[texte['kategorie'] == kategorie]
            for idx, text in kategorietexte.iterrows():
                key = f"toggle_{idx}"  # Eindeutiger Schlüssel für jedes Toggle-Element
                ausgewählte_texte[key] = st.toggle(text['überschrift'], key=key)
    
    

    if st.button("HTML exportieren"):
        html_content = """
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                h1 { color: #E05A47; }
                h2 { color: #193B4D; }
            </style>
        </head>
        <body>
        <img src='Logo_namowo_blau.svg' style='position: absolute; top: 10px; right: 10px; height: 50px;'>
        """
        
        for kategorie in kategorien:
            html_content += f"<section><h1>{kategorie}</h1>"
            kategorietexte = texte[texte['kategorie'] == kategorie]
            for idx, text in kategorietexte.iterrows():
                if ausgewählte_texte.get(f"toggle_{idx}"):
                    html_content += f"<h2>{text['überschrift']}</h2><p>{text['text']}</p>"
            html_content += "</section>"
        
        html_content += "</body></html>"
        
        output = io.BytesIO()
        output.write(html_content.encode("utf-8"))
        output.seek(0)
        
        st.download_button(
            label="HTML-Datei herunterladen",
            data=output,
            file_name="export.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
