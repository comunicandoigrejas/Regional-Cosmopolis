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
        self.cell(0, 10, 'Relatório Financeiro - Regional Cosmópolis', align='C', ln=True)
        self.ln(15)

    def footer(self):
        self.set_y(-25)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def processar_mudanca_direta(APPS_SCRIPT_URL, df_mes_selecionado, colunas):
    mudancas = st.session_state["tabela_financeira_direta"].get("edited_rows", {})
    if mudancas:
        for indice_linha_str, novos_campos in mudancas.items():
            indice_linha = int(indice_linha_str)
            linha_original = df_mes_selecionado.iloc[indice_linha]
            id_alvo = str(linha_original[colunas[0]])
            
            dados_update = {
                "action": "editarLancamento",
                "id_lancamento": id_alvo,
                "data_lancamento": novos_campos.get(colunas[1], linha_original[colunas[1]].strftime("%d/%m/%Y")),
                "cidade": novos_campos.get(colunas[2], str(linha_original[colunas[2]])),
                "tipo": novos_campos.get(colunas[3], str(linha_original[colunas[3]])),
                "descricao": novos_campos.get(colunas[4], str(linha_original[colunas[4]])),
                "valor": str(novos_campos.get(colunas[5], float(linha_original[colunas[5]]))),
                "usuario": st.session_state.get('usuario_atual', 'Sistema')
            }
            try:
                res = requests.post(APPS_SCRIPT_URL, json=dados_update)
                if res.status_code == 200:
                    st.toast(f"Linha {id_alvo} atualizada com sucesso!", icon="✅")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
        st.cache_data.clear()

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
        colunas = dados[0]
        df = pd.DataFrame(dados[1:], columns=colunas)
        df[colunas[1]] = pd.to_datetime(df[colunas[1]], dayfirst=True, errors='coerce')
        df[colunas[5]] = pd.to_numeric(df[colunas[5]], errors='coerce').fillna(0)
        
        df_filtro = df[(df[colunas[1]].dt.month == mes_num) & (df[colunas[1]].dt.year == ano_escolhido)].copy()
        
        if df_filtro.empty:
            st.warning("Nenhum lançamento encontrado neste período.")
        else:
            # Exibe a tabela editável
            df_exibicao = df_filtro.copy()
            df_exibicao[colunas[1]] = df_exibicao[colunas[1]].dt.strftime('%d/%m/%Y')
            
            st.data_editor(
                df_exibicao, 
                key="tabela_financeira_direta", 
                on_change=processar_mudanca_direta, 
                args=(APPS_SCRIPT_URL, df_filtro, colunas),
                use_container_width=True,
                hide_index=True
            )

            # GERAÇÃO DO PDF
            pdf = GeradorPDF(usuario_logado=st.session_state.get('usuario_atual', 'Regional'))
            pdf.add_page()
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, f"Fechamento: {mes_escolhido}/{ano_escolhido}", ln=True)
            
            # Converte PDF para bytes de forma segura para a biblioteca fpdf2
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
