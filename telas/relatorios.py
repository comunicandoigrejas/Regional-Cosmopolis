import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import math
from fpdf import FPDF
import os

class GeradorPDF(FPDF):
    def __init__(self, usuario_logado, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario_logado = str(usuario_logado).strip().lower()

    def header(self):
        caminho_logo = os.path.join("assets", "logo.png")
        if os.path.exists(caminho_logo):
            self.image(caminho_logo, x=10, y=8, w=30)
            self.set_x(45)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(43, 27, 84) 
        self.cell(0, 10, 'Relatório Financeiro', align='C', ln=True)
        self.ln(15)

    def footer(self):
        self.set_y(-25)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def renderizar_tela_relatorios(APPS_SCRIPT_URL, buscar_lancamentos, buscar_cidades):
    st.title("📊 Painel Financeiro Regional")
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        mes_escolhido = st.selectbox("Mês:", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"], index=datetime.now().month-1)
    with col_b:
        ano_escolhido = st.number_input("Ano:", min_value=2020, max_value=2100, value=datetime.now().year)
    
    mapa_meses = {"Janeiro":1, "Fevereiro":2, "Março":3, "Abril":4, "Maio":5, "Junho":6, "Julho":7, "Agosto":8, "Setembro":9, "Outubro":10, "Novembro":11, "Dezembro":12}
    mes_num = mapa_meses[mes_escolhido]

    dados = buscar_lancamentos()
    if len(dados) > 1:
        df = pd.DataFrame(dados[1:], columns=dados[0])
        # Ajuste: garantindo que as colunas existam e estejam no formato correto
        df[dados[0][1]] = pd.to_datetime(df[dados[0][1]], dayfirst=True)
        df[dados[0][5]] = pd.to_numeric(df[dados[0][5]])
        
        df_filtro = df[(df[dados[0][1]].dt.month == mes_num) & (df[dados[0][1]].dt.year == ano_escolhido)].copy()
        
        if df_filtro.empty:
            st.warning("Nenhum lançamento encontrado neste período.")
        else:
            st.data_editor(df_filtro, use_container_width=True, hide_index=True)

            # GERADOR DO PDF
            pdf = GeradorPDF(usuario_logado=st.session_state.get('usuario_atual', 'Regional'))
            pdf.add_page()
            pdf.set_font("helvetica", "", 12)
            pdf.cell(0, 10, f"Fechamento: {mes_escolhido}/{ano_escolhido}", ln=True)
            
           # A versão atual da biblioteca fpdf2 usa o método output() para retornar os bytes diretamente
            pdf_bytes = pdf.output()
            
            st.download_button(
                label="📥 Baixar PDF deste período",
                data=pdf_bytes,
                file_name=f"Relatorio_{mes_escolhido}_{ano_escolhido}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.error("Erro ao carregar dados da planilha.")
