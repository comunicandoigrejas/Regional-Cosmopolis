import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os
import math

st.set_page_config(page_title="Gerar Relatórios", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #2b1b54; }
    div.stButton > button:first-child { background-color: #556b2f; color: white; border-radius: 8px; }
    div.stButton > button:first-child:hover { background-color: #ff8c00; }
    h1 { color: #000080; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; color: #888888; font-size: 12px; font-weight: bold; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'logado' not in st.session_state or not st.session_state['logado']:
    st.warning("Varão, você precisa fazer o login na página principal (App.py) primeiro!")
    st.stop()

APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]

class GeradorPDF(FPDF):
    def header(self):
        caminho_logo = os.path.join("assets", "logo.png")
        if os.path.exists(caminho_logo):
            self.image(caminho_logo, x=10, y=8, w=30)
            self.set_x(45)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(43, 27, 84) 
        self.cell(0, 10, 'Relatório Financeiro - Regional Cosmópolis', align='C', ln=True)
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        # Assinatura de Desenvolvimento solicitada no rodapé do PDF
        self.cell(0, 10, 'Desenvolvido por Comunicando Igrejas', align='C', ln=True)
        self.set_draw_color(0, 0, 0)
        self.line(60, self.get_y(), 150, self.get_y()) 
        self.cell(0, 5, 'Assinatura do Responsável', align='C')

def buscar_lancamentos():
    try:
        resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getLancamentos"})
        if resposta.status_code == 200:
            return resposta.json()["dados"]
    except:
        pass
    return []

st.title("📊 Relatórios e Exportação")
st.sidebar.write(f"Usuário: **{st.session_state['usuario_atual']}**")

col1, col2 = st.columns(2)
with col1:
    data_inicio = st.date_input("Data Inicial", format="DD/MM/YYYY")
with col2:
    data_fim = st.date_input("Data Final", format="DD/MM/YYYY")
    
if st.button("Buscar Lançamentos"):
    dados = buscar_lancamentos()
    if dados and len(dados) > 1:
        colunas = dados[0]
        df = pd.DataFrame(dados[1:], columns=colunas)
        
        df[colunas[1]] = pd.to_datetime(df[colunas[1]], errors='coerce', dayfirst=True, utc=True).dt.tz_localize(None)
        df[colunas[5]] = pd.to_numeric(df[colunas[5]], errors='coerce').fillna(0)
        
        mask = (df[colunas[1]] >= pd.to_datetime(data_inicio)) & (df[colunas[1]] <= pd.to_datetime(data_fim))
        df_filtrado = df.loc[mask].copy()
        
        if not df_filtrado.empty:
            entradas = df_filtrado[df_filtrado[colunas[3]] == 'Entrada'][colunas[5]].sum()
            saidas = df_filtrado[df_filtrado[colunas[3]] == 'Saída'][colunas[5]].sum()
            
            st.markdown("### Resumo do Período")
            c1, c2, c3 = st.columns(3)
            c1.success(f"Entradas: R$ {entradas:.2f}")
            c2.error(f"Saídas: R$ {saidas:.2f}")
            c3.info(f"Saldo: R$ {entradas - saidas:.2f}")
            
            df_exibicao = df_filtrado.copy()
            df_exibicao[colunas[1]] = df_exibicao[colunas[1]].dt.strftime('%d/%m/%Y')
            st.dataframe(df_exibicao[[colunas[1], colunas[2], colunas[3], colunas[4], colunas[5]]], use_container_width=True)
            
            # Gerando PDF
            pdf = GeradorPDF()
            pdf.add_page()
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 10, f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", ln=True)
            pdf.ln(5)
            
            larguras = [23, 32, 85, 25, 25]
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(larguras[0], 10, "Data", border=1, fill=True)
            pdf.cell(larguras[1], 10, "Cidade", border=1, fill=True)
            pdf.cell(larguras[2], 10, "Descrição", border=1, fill=True)
            pdf.cell(larguras[3], 10, "Tipo", border=1, fill=True)
            pdf.cell(larguras[4], 10, "Valor", border=1, fill=True, ln=True)
            
            pdf.set_font("helvetica", "", 9)
            altura_base = 6
            for index, row in df_exibicao.iterrows():
                texto_desc = str(row[colunas[4]])
                num_linhas = math.ceil(pdf.get_string_width(texto_desc) / (larguras[2] - 3))
                num_linhas = max(num_linhas, 1)
                altura_linha = num_linhas * altura_base
                
                y_topo = pdf.get_y()
                pdf.cell(larguras[0], altura_linha, str(row[colunas[1]]), border=1)
                pdf.cell(larguras[1], altura_linha, str(row[colunas[2]])[:15], border=1)
                x_pos_desc = pdf.get_x()
                pdf.multi_cell(larguras[2], altura_base, texto_desc, border=1)
                pdf.set_xy(x_pos_desc + larguras[2], y_topo)
                pdf.cell(larguras[3], altura_linha, str(row[colunas[3]]), border=1)
                pdf.cell(larguras[4], altura_linha, f"R$ {row[colunas[5]]:.2f}", border=1)
                pdf.set_xy(10, y_topo + altura_linha)
                
            st.download_button(label="📥 Exportar Relatório em PDF", data=bytes(pdf.output()), file_name="Relatorio.pdf", mime="application/pdf")
        else:
            st.warning("Nenhum lançamento no período.")

st.markdown('<div class="footer">Desenvolvido por Comunicando Igrejas</div>', unsafe_allow_html=True)
