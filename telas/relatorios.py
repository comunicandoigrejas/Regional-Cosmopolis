import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import math
from fpdf import FPDF
import os

# [Mantenha a classe GeradorPDF como está no seu código anterior]
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
        self.cell(0, 10, 'Relatório Financeiro - Regional Cosmópolis', align='C', ln=True)
        self.ln(15)

    def footer(self):
        self.set_y(-40)
        self.set_font('helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f"Cosmópolis {data_hoje}", align='C', ln=True)
        self.ln(5)
        if "pastora" in self.usuario_logado: nome_assinatura = "Pastora Fátima Leal"
        elif "pastor" in self.usuario_logado: nome_assinatura = "Pastor Marcelo Alves de Souza"
        else: nome_assinatura = "Responsável Regional"
        self.set_draw_color(0, 0, 0)
        self.line(60, self.get_y(), 150, self.get_y())
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, nome_assinatura, align='C', ln=True)

def processar_mudanca_direta(APPS_SCRIPT_URL, df_mes_selecionado, colunas):
    mudancas = st.session_state["tabela_financeira_direta"].get("edited_rows", {})
    if mudancas:
        for indice_linha_str, novos_campos in mudancas.items():
            indice_linha = int(indice_linha_str)
            linha_original = df_mes_selecionado.iloc[indice_linha]
            # ... (Lógica de update idêntica à anterior)
            dados_update = {
                "action": "editarLancamento",
                "id_lancamento": str(linha_original[colunas[0]]),
                "data_lancamento": novos_campos.get(colunas[1], linha_original[colunas[1]].strftime("%d/%m/%Y")),
                "cidade": novos_campos.get(colunas[2], str(linha_original[colunas[2]])),
                "tipo": novos_campos.get(colunas[3], str(linha_original[colunas[3]])),
                "descricao": novos_campos.get(colunas[4], str(linha_original[colunas[4]])),
                "valor": str(novos_campos.get(colunas[5], float(linha_original[colunas[5]]))),
                "usuario": st.session_state.get('usuario_atual', 'Sistema')
            }
            requests.post(APPS_SCRIPT_URL, json=dados_update)
        st.cache_data.clear()

def renderizar_tela_relatorios(APPS_SCRIPT_URL, buscar_lancamentos, buscar_cidades):
    st.title("📊 Painel Financeiro Regional")
    
    # SELETOR DE MÊS E ANO
    col_a, col_b = st.columns([1, 1])
    with col_a:
        mes_escolhido = st.selectbox("Escolha o Mês:", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"], index=datetime.now().month-1)
    with col_b:
        ano_escolhido = st.number_input("Escolha o Ano:", min_value=2020, max_value=2100, value=datetime.now().year)
    
    mapa_meses = {"Janeiro":1, "Fevereiro":2, "Março":3, "Abril":4, "Maio":5, "Junho":6, "Julho":7, "Agosto":8, "Setembro":9, "Outubro":10, "Novembro":11, "Dezembro":12}
    mes_num = mapa_meses[mes_escolhido]

    dados = buscar_lancamentos()
    if len(dados) > 1:
        df = pd.DataFrame(dados[1:], columns=dados[0])
        df[dados[0][1]] = pd.to_datetime(df[dados[0][1]], dayfirst=True)
        df[dados[0][5]] = pd.to_numeric(df[dados[0][5]])
        
        df_filtro = df[(df[dados[0][1]].dt.month == mes_num) & (df[dados[0][1]].dt.year == ano_escolhido)].copy()
        
        if df_filtro.empty:
            st.warning(f"Nenhum lançamento encontrado em {mes_escolhido}/{ano_escolhido}.")
        else:
            # [Aqui segue a exibição da tabela com data_editor usando df_filtro]
            # Lembre-se de passar df_filtro para a função processar_mudanca_direta
            st.data_editor(df_filtro, key="tabela_financeira_direta", on_change=processar_mudanca_direta, args=(APPS_SCRIPT_URL, df_filtro, dados[0]))
            
            # Botão de PDF usando o mes_escolhido e ano_escolhido
            st.download_button("📥 Baixar PDF deste período", data=..., file_name=f"Relatorio_{mes_escolhido}_{ano_escolhido}.pdf")
