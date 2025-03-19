import streamlit as st
import pandas as pd
import io
from fpdf import FPDF

def main():
    # Logo oben rechts anzeigen
    logo_path = "Logo_namowo_blau.svg"
    st.sidebar.image(logo_path, use_container_width=True)
    
    st.markdown("<h1 style='color:#193B4D; font-weight:bold; font-family:sans-serif;'>Maßnahmendatenbank</h1>", unsafe_allow_html=True)
    
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
                body { font-family: 'Arial', sans-serif; color: #333333; line-height: 1.6; }
                h1 { color: #193B4D; font-size: 28px; font-weight: bold; }
                h2 { color: #E05A47; font-size: 24px; font-weight: bold; }
                p { font-size: 16px; }
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
    
    if st.button("PDF exportieren"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(200, 10, "Maßnahmen-Export", ln=True, align='C')
        pdf.ln(10)
        
        for kategorie in kategorien:
            pdf.set_font("Arial", style='B', size=14)
            pdf.cell(200, 10, kategorie, ln=True)
            pdf.ln(5)
            
            kategorietexte = texte[texte['kategorie'] == kategorie]
            for idx, text in kategorietexte.iterrows():
                if ausgewählte_texte.get(f"toggle_{idx}"):
                    pdf.set_font("Arial", style='B', size=12)
                    pdf.cell(200, 10, text['überschrift'], ln=True)
                    pdf.set_font("Arial", size=10)
                    pdf.multi_cell(0, 10, text['text'])
                    pdf.ln(5)
        
        pdf_output = io.BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin1')  # Konvertierung für Sonderzeichen
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)
        
        st.download_button(
            label="PDF-Datei herunterladen",
            data=pdf_output,
            file_name="export.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
