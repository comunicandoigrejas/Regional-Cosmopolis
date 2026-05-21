import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
from fpdf import FPDF

class GeradorPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'Relatório Financeiro', align='C', ln=True)
        self.ln(10)

def processar_mudanca_direta(APPS_SCRIPT_URL, df_mes_selecionado, colunas):
    mudancas = st.session_state["tabela_financeira_direta"].get("edited_rows", {})
    if mudancas:
        for indice_linha_str, novos_campos in mudancas.items():
            indice_linha = int(indice_linha_str)
            linha_original = df_mes_selecionado.iloc[indice_linha]
            
            data_str = novos_campos.get(colunas[1], linha_original[colunas[1]].strftime("%d/%m/%Y"))
            
            dados_update = {
                "action": "editarLancamento",
                "id_lancamento": str(linha_original[colunas[0]]),
                "data_lancamento": data_str,
                "cidade": novos_campos.get(colunas[2], str(linha_original[colunas[2]])),
                "tipo": novos_campos.get(colunas[3], str(linha_original[colunas[3]])),
                "descricao": novos_campos.get(colunas[4], str(linha_original[colunas[4]])),
                "valor": str(novos_campos.get(colunas[5], float(linha_original[colunas[5]]))),
                "usuario": st.session_state.get('usuario_atual', 'Sistema')
            }
            requests.post(APPS_SCRIPT_URL, json=dados_update)
        st.cache_data.clear()

def renderizar_tela_relatorios(APPS_SCRIPT_URL, buscar_lancamentos, buscar_cidades):
    if st.button("⬅️ Voltar ao Menu Principal"):
        st.session_state['tela_atual'] = "menu"
        st.rerun()

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
        colunas = dados[0]
        df = pd.DataFrame(dados[1:], columns=colunas)
        
        df[colunas[1]] = pd.to_datetime(df[colunas[1]], dayfirst=True, errors='coerce').dt.date
        df[colunas[5]] = pd.to_numeric(df[colunas[5]], errors='coerce').fillna(0)
        
        df_filtro = df[(pd.to_datetime(df[colunas[1]]).dt.month == mapa_meses[mes_escolhido]) & 
                       (pd.to_datetime(df[colunas[1]]).dt.year == ano_escolhido)].copy()
        
        if df_filtro.empty:
            st.warning("Nenhum lançamento encontrado neste período.")
            return

        df_exibicao = df_filtro.copy()
        df_exibicao[colunas[1]] = df_exibicao[colunas[1]].apply(lambda x: x.strftime('%d/%m/%Y'))

        st.data_editor(
            df_exibicao, 
            key="tabela_financeira_direta", 
            on_change=processar_mudanca_direta, 
            args=(APPS_SCRIPT_URL, df_filtro, colunas),
            use_container_width=True,
            hide_index=True
        )

        # GERAÇÃO DO PDF USANDO ARQUIVO TEMPORÁRIO (A PROVA DE ERROS)
        pdf = GeradorPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 10, f"Fechamento: {mes_escolhido}/{ano_escolhido}", ln=True)
        
        nome_arquivo = "temp_relatorio.pdf"
        pdf.output(nome_arquivo)
        
        with open(nome_arquivo, "rb") as f:
            st.download_button(
                label="📥 Baixar PDF deste período",
                data=f,
                file_name=f"Relatorio_{mes_escolhido}_{ano_escolhido}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        # Remove o arquivo temporário após criar o botão
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)
            
    else:
        st.error("Erro ao carregar dados da planilha.")
