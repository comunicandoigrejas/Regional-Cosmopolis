import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import math
from fpdf import FPDF
import os

class GeradorPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'Relatório Financeiro', align='C', ln=True)
        self.ln(10)

def renderizar_tela_relatorios(APPS_SCRIPT_URL, buscar_lancamentos, buscar_cidades):
    st.title("📊 Painel Financeiro Regional")
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_escolhido = st.selectbox("Mês:", meses, index=datetime.now().month-1)
    with col_b:
        ano_escolhido = st.number_input("Ano:", min_value=2020, max_value=2100, value=datetime.now().year)
    
    mapa_meses = {m: i+1 for i, m in enumerate(meses)}
    
    dados = buscar_lancamentos()
    if len(dados) > 1:
        df = pd.DataFrame(dados[1:], columns=dados[0])
        df[dados[0][1]] = pd.to_datetime(df[dados[0][1]], dayfirst=True, errors='coerce')
        df_filtro = df[(df[dados[0][1]].dt.month == mapa_meses[mes_escolhido]) & (df[dados[0][1]].dt.year == ano_escolhido)].copy()
        
        if df_filtro.empty:
            st.warning("Nenhum lançamento encontrado neste período.")
            return

        st.dataframe(df_filtro, use_container_width=True)

        # GERAÇÃO SEGURA DO PDF
        pdf = GeradorPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 10, f"Fechamento: {mes_escolhido}/{ano_escolhido}", ln=True)
        
        # O método output() da fpdf2 retorna os bytes diretamente.
        # Não usamos 'dest' nem 'encode', apenas o output() puro.
        pdf_conteudo = pdf.output()
        
        # Forçamos a conversão para garantir que é um objeto de bytes do Python
        # Se for um objeto da classe fpdf.output.Output, pegamos seus bytes.
        try:
            if hasattr(pdf_conteudo, "getvalue"): # Caso seja um buffer
                pdf_bytes = pdf_conteudo.getvalue()
            elif isinstance(pdf_conteudo, bytes): # Caso já sejam bytes
                pdf_bytes = pdf_conteudo
            else: # Caso seja uma string ou outro tipo
                pdf_bytes = str(pdf_conteudo).encode('latin-1')
        except:
            pdf_bytes = b""

        st.download_button(
            label="📥 Baixar PDF deste período",
            data=pdf_bytes,
            file_name=f"Relatorio_{mes_escolhido}_{ano_escolhido}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.error("Erro ao carregar dados da planilha.")
