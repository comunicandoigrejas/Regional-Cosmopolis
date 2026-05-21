import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import math

# 1. CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA LINHA!)
st.set_page_config(page_title="Finanças Regional Cosmópolis", page_icon="🕊️", layout="wide")

# 2. ESTILOS VISUAIS E OCULTAÇÃO DA BARRA SUPERIOR (GITHUB/SHARE)
st.markdown("""
    <style>
    /* Oculta o cabeçalho padrão do Streamlit (Botões GitHub, Share, Menu) */
    header {
        visibility: hidden !important;
    }
    footer {
        visibility: hidden !important;
    }
    #MainMenu {
        visibility: hidden !important;
    }
    
    /* Customização dos Botões de Menu Principal */
    .menu-box {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
    }
    
    /* Botões de Ação do Sistema (Verde Oliva) */
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
    }
    
    /* Títulos em Azul Marinho */
    h1, h2, h3 {
        color: #000080;
    }
    
    /* Rodapé fixo na tela */
    .footer-comunicando {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffff;
        color: #888888;
        text-align: center;
        padding: 10px;
        font-size: 13px;
        font-weight: bold;
        border-top: 1px solid #eaeaea;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# 3. PUXANDO A URL DA PLANILHA
try:
    APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]
except KeyError:
    st.error("Varão, o arquivo secrets.toml não foi encontrado ou a URL está faltando. Verifique as configurações!")
    st.stop()

# 4. FUNÇÕES DE COMUNICAÇÃO COM O GOOGLE SHEETS
def verificar_login(usuario, senha):
    try:
        resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getUsuarios"})
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados["status"] == "sucesso":
                usuarios_planilha = dados["dados"]
                for linha in usuarios_planilha[1:]:
                    if len(linha) >= 4:
                        if str(usuario) == str(linha[2]) and str(senha) == str(linha[3]):
                            return True
    except Exception as e:
        st.error(f"Erro ao conectar no login: {e}")
    return False

@st.cache_data(ttl=300)
def buscar_cidades():
    try:
        resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getCidades"})
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados["status"] == "sucesso":
                return [linha[0] for linha in dados["dados"][1:] if linha[0] != ""]
    except:
        pass
    return ["Cosmópolis", "Erro de Conexão"]

def buscar_lancamentos():
    try:
        resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getLancamentos"})
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados["status"] == "sucesso":
                return dados["dados"]
            else:
                st.error(f"Aviso do Google Sheets: {dados.get('mensagem', 'Sem mensagem de erro detalhada')}")
        else:
            st.error(f"Erro de resposta do servidor da planilha: Código {resposta.status_code}")
    except Exception as e:
        st.error(f"Falha crítica de conexão ao buscar os lançamentos: {e}")
    return []

# 5. GERADOR DE PDF COM TODAS AS COLUNAS CONTROLADAS E LOGO
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
        self.cell(0, 10, 'Desenvolvido por Comunicando Igrejas', align='C', ln=True)
        self.set_draw_color(0, 0, 0)
        self.line(60, self.get_y(), 150, self.get_y()) 
        self.cell(0, 5, 'Assinatura do Responsável', align='C')

# 6. GERENCIAMENTO DE ESTADO DA SESSÃO
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state:
    st.session_state['usuario_atual'] = ""
if 'tela_atual' not in st.session_state:
    st.session_state['tela_atual'] = "menu" # Controla qual janela está ativa por botões

# ==========================================
# TELA 1: LOGIN DO SISTEMA
# ==========================================
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.ln(5)
        st.title("🕊️ Financeiro Regional")
        st.write("A paz do Senhor! Faça seu login.")
        
        usuario_input = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Sistema", use_container_width=True):
            if verificar_login(usuario_input, senha):
                st.session_state['logado'] = True
                st.session_state['usuario_atual'] = usuario_input
                st.session_state['tela_atual'] = "menu"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos, varão. Tente novamente!")

# ==========================================
# TELA 2: SISTEMA LOGADO (SEM BARRA LATERAL)
# ==========================================
else:
    # --- JANELA: MENU PRINCIPAL DE BOTÕES ---
    if st.session_state['tela_atual'] == "menu":
        st.title("🕊️ Painel de Controle - Regional Cosmópolis")
        st.write(f"Bem-vindo, abençoado(a) **{st.session_state['usuario_atual']}**! Escolha a operação desejada:")
        st.ln(2)
        
        # Cria duas colunas largas para colocar os botões lado a lado no centro
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            st.markdown('<div class="menu-box"><h3>Registrar Movimentações</h3><p>Insira novas entradas e saídas de dízimos, ofertas ou despesas.</p></div>', unsafe_allow_html=True)
            if st.button("📝 Acessar Registrar Lançamentos", use_container_width=True):
                st.session_state['tela_atual'] = "lancamentos"
                st.rerun()
                
        with col_btn2:
            st.markdown('<div class="menu-box"><h3>Relatórios Financeiros</h3><p>Consulte registros, analise saldos e exporte o fechamento em PDF.</p></div>', unsafe_allow_html=True)
            if st.button("📊 Acessar Gerar Relatórios", use_container_width=True):
                st.session_state['tela_atual'] = "relatorios"
                st.rerun()
        
        st.ln(4)
        # Botão de Sair posicionado de forma limpa na base do menu
        if st.button("🚪 Encerrar Sessão / Sair", type="secondary"):
            st.session_state['logado'] = False
            st.session_state['usuario_atual'] = ""
            st.session_state['tela_atual'] = "menu"
            st.rerun()

    # --- JANELA: FORMULÁRIO DE LANÇAMENTOS ---
    elif st.session_state['tela_atual'] == "lancamentos":
        # Cabeçalho de Navegação Superior
        col_nav1, col_nav2 = st.columns([6, 2])
        with col_nav1:
            st.title("📝 Registrar Movimentação")
        with col_nav2:
            if st.button("⬅️ Voltar ao Menu Principal", use_container_width=True):
                st.session_state['tela_atual'] = "menu"
                st.rerun()
                
        cidades_lista = buscar_cidades()
        
        with st.form("form_lancamentos", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                data_lancamento = st.date_input("Data do Lançamento", format="DD/MM/YYYY")
                tipo = st.selectbox("Tipo", ["Entrada (Dízimos, Ofertas)", "Saída (Despesas, Pagamentos)"])
            with col2:
                cidade = st.selectbox("Igreja/Cidade", cidades_lista)
                valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            descricao = st.text_input("Descrição (Ex: Conta de Luz, Oferta Culto de Domingo)")
            botao_salvar = st.form_submit_button("Gravar na Planilha", use_container_width=True)
            
            if botao_salvar:
                if descricao == "" or valor == 0:
                    st.warning("Varão, a descrição e o valor não podem ficar vazios!")
                else:
                    dados_envio = {
                        "action": "registrarLancamento",
                        "data_lancamento": data_lancamento.strftime("%d/%m/%Y"),
                        "cidade": city := cidade,
                        "tipo": "Entrada" if "Entrada" in tipo else "Saída",
                        "descricao": descricao,
                        "valor": valor,
                        "usuario": st.session_state['usuario_atual']
                    }
                    try:
                        resposta_post = requests.post(APPS_SCRIPT_URL, json=dados_envio)
                        if resposta_post.status_code == 200:
                            st.success(f"Aleluia! Lançamento registrado com sucesso por {st.session_state['usuario_atual']}!")
                        else:
                            st.error(f"Erro ao gravar na planilha. Código: {resposta_post.status_code}")
                    except Exception as e:
                        st.error(f"Erro de conexão no envio: {e}")

    # --- JANELA: CONSULTA E EXPORTAÇÃO DE RELATÓRIOS ---
    elif st.session_state['tela_atual'] == "relatorios":
        # Cabeçalho de Navegação Superior
        col_nav1, col_nav2 = st.columns([6, 2])
        with col_nav1:
            st.title("📊 Relatórios e Exportação")
        with col_nav2:
            if st.button("⬅️ Voltar ao Menu Principal", use_container_width=True):
                st.session_state['tela_atual'] = "menu"
                st.rerun()
                
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data Inicial", format="DD/MM/YYYY")
        with col2:
            data_fim = st.date_input("Data Final", format="DD/MM/YYYY")
            
        if st.button("Buscar Dados da Planilha", use_container_width=True):
            with st.spinner("Buscando as bênçãos e despesas na planilha..."):
                dados = buscar_lancamentos()
                
                if len(dados) > 1:
                    colunas = dados[0]
                    valores = dados[1:]
                    df = pd.DataFrame(valores, columns=colunas)
                    
                    nome_col_data = colunas[1]
                    nome_col_valor = colunas[5]
                    nome_col_tipo = colunas[3]
                    
                    df[nome_col_data] = pd.to_datetime(df[nome_col_data], errors='coerce', dayfirst=True, utc=True).dt.tz_localize(None)
                    df[nome_col_valor] = pd.to_numeric(df[nome_col_valor], errors='coerce').fillna(0)
                    
                    data_inicio_pd = pd.to_datetime(data_inicio)
                    data_fim_pd = pd.to_datetime(data_fim)
                    mask = (df[nome_col_data] >= data_inicio_pd) & (df[nome_col_data] <= data_fim_pd)
                    
                    df_filtrado = df.loc[mask].copy()
                    
                    if df_filtrado.empty:
                        st.warning("Nenhum lançamento encontrado neste período selecionado, irmão Willian.")
                    else:
                        entradas = df_filtrado[df_filtrado[nome_col_tipo] == 'Entrada'][nome_col_valor].sum()
                        saidas = df_filtrado[df_filtrado[nome_col_tipo] == 'Saída'][nome_col_valor].sum()
                        saldo = entries_sub_expenses := entradas - saidas
                        
                        st.markdown("### Resumo do Período")
                        c1, c2, c3 = st.columns(3)
                        c1.success(f"Entradas: R$ {entradas:.2f}")
                        c2.error(f"Saídas: R$ {saidas:.2f}")
                        c3.info(f"Saldo: R$ {saldo:.2f}")
                        
                        df_exibicao = df_filtrado.copy()
                        df_exibicao[nome_col_data] = df_exibicao[nome_col_data].dt.strftime('%d/%m/%Y')
                        st.dataframe(df_exibicao[[colunas[1], colunas[2], colunas[3], colunas[4], colunas[5]]], use_container_width=True)
                        
                        # GERAÇÃO DO PDF PROFISSIONAL COM GRID COMPLETO
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
                        altura_base_texto = 6
                        
                        for index, row in df_exibicao.iterrows():
                            texto_desc = str(row[colunas[4]])
                            largura_real_texto = pdf.get_string_width(texto_desc)
                            num_linhas = math.ceil(largura_real_texto / (larguras[2] - 3))
                            if num_linhas < 1:
                                num_linhas = 1
                            
                            altura_da_linha_final = num_linhas * altura_base_texto
                            y_topo = pdf.get_y()
                            
                            pdf.cell(larguras[0], altura_da_linha_final, str(row[colunas[1]]), border=1)
                            pdf.cell(larguras[1], altura_da_linha_final, str(row[colunas[2]])[:15], border=1)
                            x_pos_desc = pdf.get_x()
                            
                            pdf.multi_cell(larguras[2], altura_base_texto, texto_desc, border=1)
                            pdf.set_xy(x_pos_desc + larguras[2], y_topo)
                            
                            pdf.cell(larguras[3], altura_da_linha_final, str(row[colunas[3]]), border=1)
                            pdf.cell(larguras[4], altura_da_linha_final, f"R$ {row[colunas[5]]:.2f}", border=1)
                            
                            pdf.set_xy(10, y_topo + altura_da_linha_final)
                        
                        pdf_bytes = bytes(pdf.output())
                        st.ln(2)
                        st.download_button(
                            label="📥 Exportar Relatório Completo em PDF",
                            data=pdf_bytes,
                            file_name=f"Relatorio_{data_inicio}_a_{data_fim}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.info("A planilha retornou vazia ou sem linhas válidas para o período.")

# 7. ASSINATURA VISUAL EXCLUSIVA NO RODAPÉ DE TODAS AS TELAS
st.markdown('<div class="footer-comunicando">Desenvolvido por Comunicando Igrejas</div>', unsafe_allow_html=True)
