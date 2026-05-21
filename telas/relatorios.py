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
        self.set_y(-40)
        self.set_font('helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f"Cosmópolis {data_hoje}", align='C', ln=True)
        self.ln(5)
        
        if "pastora" in self.usuario_logado:
            nome_assinatura = "Pastora Fátima Leal"
        elif "pastor" in self.usuario_logado:
            nome_assinatura = "Pastor Marcelo Alves de Souza"
        else:
            nome_assinatura = "Responsável Regional"
            
        self.set_draw_color(0, 0, 0)
        self.line(60, self.get_y(), 150, self.get_y())
        
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, nome_assinatura, align='C', ln=True)
        
        self.set_y(-12)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')


def renderizar_tela_relatorios(APPS_SCRIPT_URL, buscar_lancamentos, buscar_cidades):
    col_nav1, col_nav2 = st.columns([6, 2])
    with col_nav1:
        meses_nome = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        mes_atual_num = datetime.now().month
        ano_atual_num = datetime.now().year
        st.title(f"📊 Lançamentos de {meses_nome[mes_atual_num]} de {ano_atual_num}")
    with col_nav2:
        if st.button("⬅️ Voltar ao Menu Principal", use_container_width=True):
            st.session_state['tela_atual'] = "menu"
            st.rerun()

    dados = buscar_lancamentos()
    
    if len(dados) > 1:
        colunas = dados[0]
        valores = dados[1:]
        df = pd.DataFrame(valores, columns=colunas)
        
        nome_col_id = colunas[0]
        nome_col_data = colunas[1]
        nome_col_cidade = colunas[2]
        nome_col_tipo = colunas[3]
        nome_col_desc = colunas[4]
        nome_col_valor = colunas[5]
        
        df[nome_col_data] = pd.to_datetime(df[nome_col_data], errors='coerce', dayfirst=True, utc=True).dt.tz_localize(None)
        df[nome_col_valor] = pd.to_numeric(df[nome_col_valor], errors='coerce').fillna(0)
        
        df_mes_atual = df[(df[nome_col_data].dt.month == mes_atual_num) & (df[nome_col_data].dt.year == ano_atual_num)].copy()
        
        if df_mes_atual.empty:
            st.info("Nenhum registro encontrado para este mês atual na planilha, irmão Willian.")
        else:
            entradas = df_mes_atual[df_mes_atual[nome_col_tipo] == 'Entrada'][nome_col_valor].sum()
            saidas = df_mes_atual[df_mes_atual[nome_col_tipo] == 'Saída'][nome_col_valor].sum()
            saldo = entradas - saidas
            
            c1, c2, c3 = st.columns(3)
            c1.success(f"Entradas do Mês: R$ {entradas:.2f}")
            c2.error(f"Saídas do Mês: R$ {saidas:.2f}")
            c3.info(f"Saldo do Mês: R$ {saldo:.2f}")
            
            df_exibicao = df_mes_atual.copy()
            df_exibicao[nome_col_data] = df_exibicao[nome_col_data].dt.strftime('%d/%m/%Y')
            
            st.dataframe(df_exibicao[[nome_col_id, colunas[1], colunas[2], colunas[3], colunas[4], colunas[5]]], use_container_width=True, hide_index=True)
            
            # PDF GENERATOR
           # Proteção para garantir que o sistema não caia se o estado da sessão demorar para carregar
            usuario_pdf = st.session_state.get('usuario_atual', 'Responsável Regional')
            pdf = GeradorPDF(usuario_logado=usuario_pdf)
            pdf.add_page()
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 10, f"Fechamento Mensal - Referência: {meses_nome[mes_atual_num]}/{ano_atual_num}", ln=True)
            pdf.ln(5)
            
            larguras = [20, 25, 32, 73, 22, 23] 
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(larguras[0], 10, "ID", border=1, fill=True)
            pdf.cell(larguras[1], 10, "Data", border=1, fill=True)
            pdf.cell(larguras[2], 10, "Cidade", border=1, fill=True)
            pdf.cell(larguras[3], 10, "Descrição", border=1, fill=True)
            pdf.cell(larguras[4], 10, "Tipo", border=1, fill=True)
            pdf.cell(larguras[5], 10, "Valor", border=1, fill=True, ln=True)
            
            pdf.set_font("helvetica", "", 9)
            for index, row in df_exibicao.iterrows():
                texto_desc = str(row[colunas[4]])
                largura_real_texto = pdf.get_string_width(texto_desc)
                num_linhas = math.ceil(largura_real_texto / (larguras[3] - 3))
                if num_linhas < 1: num_linhas = 1
                
                altura_da_linha_final = num_linhas * 6
                y_topo = pdf.get_y()
                
                pdf.cell(larguras[0], altura_da_linha_final, str(row[colunas[0]]), border=1)
                pdf.cell(larguras[1], altura_da_linha_final, str(row[colunas[1]]), border=1)
                pdf.cell(larguras[2], altura_da_linha_final, str(row[colunas[2]])[:15], border=1)
                x_pos_desc = pdf.get_x()
                
                pdf.multi_cell(larguras[3], 6, texto_desc, border=1)
                pdf.set_xy(x_pos_desc + larguras[3], y_topo)
                
                pdf.cell(larguras[4], altura_da_linha_final, str(row[colunas[3]]), border=1)
                pdf.cell(larguras[5], altura_da_linha_final, f"R$ {row[colunas[5]]:.2f}", border=1)
                pdf.set_xy(10, y_topo + altura_da_linha_final)
            
            pdf_bytes = bytes(pdf.output())
            st.download_button(
                label="📥 Exportar Fechamento do Mês Atual em PDF",
                data=pdf_bytes,
                file_name=f"Fechamento_{meses_nome[mes_atual_num]}_{ano_atual_num}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            st.markdown("---")
            st.subheader("🛠️ Painel de Ajustes e Correções")
            
            tab_editar, tab_deletar = st.tabs(["✏️ Corrigir Lançamento", "❌ Excluir Lançamento"])
            
            with tab_editar:
                id_lista = df_mes_atual[nome_col_id].tolist()
                id_selecionado = st.selectbox("Selecione o ID do Lançamento que deseja CORRIGIR:", id_lista, key="id_edit")
                
                if id_selecionado:
                    linha_original = df_mes_atual[df_mes_atual[nome_col_id] == id_selecionado].iloc[0]
                    
                    with st.form("form_correcao"):
                        col_ed1, col_ed2 = st.columns(2)
                        with col_ed1:
                            nova_data = st.date_input("Corrigir Data", value=pd.to_datetime(linha_original[nome_col_data]), format="DD/MM/YYYY")
                            novo_tipo = st.selectbox("Corrigir Tipo", ["Entrada", "Saída"], index=0 if linha_original[nome_col_tipo] == "Entrada" else 1)
                        with col_ed2:
                            lista_cidades_ed = buscar_cidades()
                            idx_cid = lista_cidades_ed.index(linha_original[nome_col_cidade]) if linha_original[nome_col_cidade] in lista_cidades_ed else 0
                            nova_cidade = st.selectbox("Corrigir Igreja/Cidade", lista_cidades_ed, index=idx_cid)
                            novo_valor = st.number_input("Corrigir Valor (R$)", min_value=0.0, value=float(linha_original[nome_col_valor]), format="%.2f")
                        
                        nova_desc = st.text_input("Corrigir Descrição", value=str(linha_original[nome_col_desc]))
                        botao_atualizar = st.form_submit_button("Salvar Correções no Sistema", use_container_width=True)
                        
                        if botao_atualizar:
                            dados_update = {
                                "action": "editarLancamento",
                                "id_lancamento": str(id_selecionado),
                                "data_lancamento": nova_data.strftime("%d/%m/%Y"),
                                "cidade": nova_cidade,
                                "tipo": novo_tipo,
                                "descricao": nova_desc,
                                "valor": novo_valor,
                                "usuario": st.session_state['usuario_atual']
                            }
                            try:
                                res_up = requests.post(APPS_SCRIPT_URL, json=dados_update)
                                if res_up.status_code == 200:
                                    st.success("Glória a Deus! Lançamento corrigido com sucesso! Atualizando...")
                                    st.rerun()
                                else:
                                    st.error("Erro técnico na alteração junto ao servidor.")
                            except Exception as e:
                                st.error(f"Falha de rede: {e}")
            
            with tab_deletar:
                id_deletar = st.selectbox("Selecione o ID do Lançamento que deseja EXCLUIR:", df_mes_atual[nome_col_id].tolist(), key="id_del")
                st.warning("⚠️ Atenção abençoado: esta operação é definitiva e apagará o registro selecionado!")
                
                if st.button("🔴 Confirmar Exclusão Definitiva", use_container_width=True):
                    dados_delete = {
                        "action": "deletarLancamento",
                        "id_lancamento": str(id_deletar)
                    }
                    try:
                        res_del = requests.post(APPS_SCRIPT_URL, json=dados_delete)
                        if res_del.status_code == 200:
                            st.success("Registro removido com sucesso! Sincronizando dados...")
                            st.rerun()
                        else:
                            st.error("Erro ao tentar remover o lançamento da planilha.")
                    except Exception as e:
                        st.error(f"Falha ao conectar no servidor de exclusão: {e}")
    else:
        st.info("Nenhum dado recebido do banco de dados da planilha.")
