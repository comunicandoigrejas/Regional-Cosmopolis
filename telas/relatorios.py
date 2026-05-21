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
        st.title(f"📊 Painel Financeiro Direto — {meses_nome[mes_atual_num]}/{ano_atual_num}")
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
        
        # Tratamento inicial dos dados vindos da planilha
        df[nome_col_data] = pd.to_datetime(df[nome_col_data], errors='coerce', dayfirst=True, utc=True).dt.tz_localize(None)
        df[nome_col_valor] = pd.to_numeric(df[nome_col_valor], errors='coerce').fillna(0)
        
        # Filtrar o mês atual para exibição e edição
        df_mes_atual = df[(df[nome_col_data].dt.month == mes_atual_num) & (df[nome_col_data].dt.year == ano_atual_num)].copy()
        
        if df_mes_atual.empty:
            st.info("Nenhum registro encontrado para este mês atual na planilha, irmão Willian.")
        else:
            # Cards de resumo lá em cima
            entradas = df_mes_atual[df_mes_atual[nome_col_tipo] == 'Entrada'][nome_col_valor].sum()
            saidas = df_mes_atual[df_mes_atual[nome_col_tipo] == 'Saída'][nome_col_valor].sum()
            saldo = entradas - saidas
            
            c1, c2, c3 = st.columns(3)
            c1.success(f"Entradas do Mês: R$ {entradas:.2f}")
            c2.error(f"Saídas do Mês: R$ {saidas:.2f}")
            c3.info(f"Saldo do Mês: R$ {saldo:.2f}")
            
            st.write("")
            st.markdown("💡 **Instruções abençoadas:** Clique duas vezes em qualquer célula da tabela abaixo para alterar os valores diretamente. Para deletar, use o painel logo abaixo da tabela.")

            # FORMATAR DATA PARA FORMATO BRASILEIRO NA PLANILHA INTERATIVA
            df_editor = df_mes_atual.copy()
            df_editor[nome_col_data] = df_editor[nome_col_data].dt.strftime('%d/%m/%Y')
            
            # -----------------------------------------------------------------
            # 💻 A MÁGICA ACONTECE AQUI: TABELA DIRETAMENTE EDITÁVEL!
            # -----------------------------------------------------------------
            lista_cidades = buscar_cidades()
            
            dados_editados = st.data_editor(
                df_editor[[nome_col_id, nome_col_data, nome_col_cidade, nome_col_tipo, nome_col_desc, nome_col_valor]],
                use_container_width=True,
                hide_index=True,
                disabled=[nome_col_id], # Bloqueia o ID para ninguém alterar sem querer
                column_config={
                    nome_col_id: st.column_config.TextColumn("ID", width="small"),
                    nome_col_data: st.column_config.TextColumn("Data (DD/MM/AAAA)"),
                    nome_col_cidade: st.column_config.SelectboxColumn("Igreja / Cidade", options=lista_cidades),
                    nome_col_tipo: st.column_config.SelectboxColumn("Tipo", options=["Entrada", "Saída"]),
                    nome_col_desc: st.column_config.TextColumn("Descrição / Histórico"),
                    nome_col_valor: st.column_config.NumberColumn("Valor (R$)", format="%.2f"),
                },
                key="tabela_financeira_direta"
            )
            
            # Captura se o usuário alterou alguma linha da tabela acima
            mudancas = st.session_state["tabela_financeira_direta"].get("edited_rows", {})
            
            if mudancas:
                st.warning("⚠️ Você fez alterações diretamente nos campos da tabela acima!")
                if st.button("💾 Gravar Alterações Diretas na Planilha", use_container_width=True, type="primary"):
                    sucesso_geral = True
                    
                    # Processa cada linha alterada na tabela dinâmica
                    for indice_linha_str, novos_campos in mudancas.items():
                        indice_linha = int(indice_linha_str)
                        linha_original = df_mes_atual.iloc[indice_linha]
                        id_alvo = str(linha_original[nome_col_id])
                        
                        # Monta os dados mesclando o original com o que foi digitado de novo
                        data_final = novos_campos.get(nome_col_data, linha_original[nome_col_data].strftime("%d/%m/%Y"))
                        cidade_final = novos_campos.get(nome_col_cidade, str(linha_original[nome_col_cidade]))
                        tipo_final = novos_campos.get(nome_col_tipo, str(linha_original[nome_col_tipo]))
                        desc_final = novos_campos.get(nome_col_desc, str(linha_original[nome_col_desc]))
                        valor_final = str(novos_campos.get(nome_col_valor, float(linha_original[nome_col_valor])))
                        
                        dados_update = {
                            "action": "editarLancamento",
                            "id_lancamento": id_alvo,
                            "data_lancamento": data_final,
                            "cidade": cidade_final,
                            "tipo": tipo_final,
                            "descricao": desc_final,
                            "valor": valor_final,
                            "usuario": st.session_state['usuario_atual']
                        }
                        
                        try:
                            res = requests.post(APPS_SCRIPT_URL, json=dados_update)
                            if res.status_code != 200:
                                sucesso_geral = False
                        except:
                            sucesso_geral = False
                    
                    if sucesso_geral:
                        st.success("Glória a Deus! Todas as linhas alteradas foram atualizadas na planilha!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Ocorreu uma falha ao tentar atualizar algumas linhas. Verifique a conexão.")

            st.write("")
            st.markdown("---")
            
            # Botões de utilidade adicionais (Exportar PDF e Exclusão Segura)
            col_b1, col_b2 = st.columns([1, 1])
            
            with col_b1:
                # GERADOR DO PDF MENSAL
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
                for index, row in df_editor.iterrows():
                    texto_desc = str(row[nome_col_desc])
                    largura_real_texto = pdf.get_string_width(texto_desc)
                    num_linhas = math.ceil(largura_real_texto / (larguras[3] - 3))
                    if num_linhas < 1: num_linhas = 1
                    
                    altura_da_linha_final = num_linhas * 6
                    y_topo = pdf.get_y()
                    
                    pdf.cell(larguras[0], altura_da_linha_final, str(row[nome_col_id]), border=1)
                    pdf.cell(larguras[1], altura_da_linha_final, str(row[nome_col_data]), border=1)
                    pdf.cell(larguras[2], altura_da_linha_final, str(row[nome_col_cidade])[:15], border=1)
                    x_pos_desc = pdf.get_x()
                    
                    pdf.multi_cell(larguras[3], 6, texto_desc, border=1)
                    pdf.set_xy(x_pos_desc + larguras[3], y_topo)
                    
                    pdf.cell(larguras[4], altura_da_linha_final, str(row[nome_col_tipo]), border=1)
                    pdf.cell(larguras[5], altura_da_linha_final, f"R$ {row[nome_col_valor]:.2f}", border=1)
                    pdf.set_xy(10, y_topo + altura_da_linha_final)
                
                pdf_bytes = bytes(pdf.output())
                st.download_button(
                    label="📥 Exportar Tabela Atual em PDF",
                    data=pdf_bytes,
                    file_name=f"Fechamento_{meses_nome[mes_atual_num]}_{ano_atual_num}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col_b2:
                # SISTEMA DE EXCLUSÃO SIMPLIFICADO POR ID
                with st.popover("❌ Deletar um Lançamento", use_container_width=True):
                    id_deletar = st.selectbox("Escolha o ID para remover definitivamente:", df_mes_atual[nome_col_id].tolist(), key="id_deletar_pop")
                    st.write("A operação é final e tirará a linha do Google Sheets.")
                    if st.button("Confirmar Remoção da Planilha", use_container_width=True, type="primary"):
                        dados_delete = {
                            "action": "deletarLancamento",
                            "id_lancamento": str(id_deletar)
                        }
                        try:
                            res_del = requests.post(APPS_SCRIPT_URL, json=dados_delete)
                            if res_del.status_code == 200:
                                st.success("Registro apagado com sucesso!")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("Erro interno ao deletar.")
                        except Exception as e:
                            st.error(f"Erro de conexão: {e}")
    else:
        st.info("Nenhum dado recebido do banco de dados da planilha.")
