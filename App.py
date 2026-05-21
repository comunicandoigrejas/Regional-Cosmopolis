import streamlit as st
import requests

# IMPORTAÇÃO APONTANDO PARA A PASTA PAGES COM OS ARQUIVOS TOTALMENTE MINÚSCULOS
from pages.lancamentos import renderizar_tela_lancamentos
from pages.relatorios import renderizar_tela_relatorios
from pages.alterar_senha import renderizar_tela_senha

# 1. CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA LINHA!)
st.set_page_config(page_title="Finanças Regional Cosmópolis", page_icon="🏛️", layout="wide")

# 2. ESTILOS VISUAIS CUSTOMIZADOS PROTEGIDOS CONTRA DARK MODE
st.markdown("""
    <style>
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    
    h1, h2, h3 {
        color: #000080 !important;
        font-weight: bold !important;
    }

    div.stButton > button {
        border-radius: 12px !important;
        padding: 30px 20px !important;
        background-color: #f0f2f6 !important;
        border: 2px solid #2b1b54 !important;
        transition: all 0.3s ease !important;
        height: auto !important;
        min-height: 160px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    div.stButton > button:hover {
        background-color: #ff8c00 !important; 
        border-color: #ff8c00 !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    div.stButton > button p {
        color: #000000 !important; 
        font-size: 16px !important;
        text-align: center !important;
        white-space: pre-line !important;
    }
    
    div.stButton > button p strong {
        color: #000080 !important;
        font-size: 21px !important;
        display: block !important;
        margin-bottom: 6px !important;
    }
    
    div.stButton > button:hover p, div.stButton > button:hover p strong {
        color: #ffffff !important;
    }

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

# 3. CREDENCIAIS SECRETS
try:
    APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]
except KeyError:
    st.error("Varão, URL do Apps Script não configurada nas secrets.")
    st.stop()

# 4. FUNÇÕES GLOBAIS DE CONEXÃO COM A PLANILHA
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

@st.cache_data(ttl=60)
def buscar_cidades():
    try:
        resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getCidades"})
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados["status"] == "sucesso":
                lista = [str(linha[0]).strip() for linha in dados["dados"][1:] if len(linha) > 0 and str(linha[0]).strip() != ""]
                if lista: return lista
    except Exception as e:
        pass
    return ["Limeira", "Cosmópolis", "Capivari", "Conchal", "Leme", "Campinas", "Valinhos"]

def buscar_lancamentos():
    try:
        resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getLancamentos"})
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados["status"] == "sucesso": return dados["dados"]
    except Exception as e:
        st.error(f"Falha de conexão ao buscar os lançamentos: {e}")
    return []

# 5. GERENCIAMENTO DE ESTADO DA SESSÃO
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state: st.session_state['usuario_atual'] = ""
if 'senha_atual' not in st.session_state: st.session_state['senha_atual'] = ""
if 'tela_atual' not in st.session_state: st.session_state['tela_atual'] = "menu"

# TELA DE LOGIN
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.title("🏛️ Financeiro Regional")
        st.write("A paz do Senhor! Faça seu login.")
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Sistema", use_container_width=True):
            if verificar_login(usuario_input, senha_input):
                st.session_state['logado'] = True
                st.session_state['usuario_atual'] = usuario_input
                st.session_state['senha_atual'] = senha_input
                st.session_state['tela_atual'] = "menu"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos, varão. Tente novamente!")

# SISTEMA LOGADO - GERENCIADOR DE ROTAS
else:
    if st.session_state['tela_atual'] == "menu":
        st.title("🏛️ Painel de Controle")
        st.write(f"Bem-vindo, abençoado(a) **{st.session_state['usuario_atual']}**!")
        st.write("")
        
        col_card1, col_card2, col_card3 = st.columns(3)
        with col_card1:
            if st.button("**🏛️ Registrar Movimentações**\nInsira novas entradas e saídas de dízimos, ofertas ou despesas.", use_container_width=True):
                st.session_state['tela_atual'] = "lancamentos"
                st.rerun()
        with col_card2:
            if st.button("**📊 Consultar e Modificar**\nVeja os lançamentos do mês atual, corrija erros, exclua ou emita o PDF.", use_container_width=True):
                st.session_state['tela_atual'] = "relatorios"
                st.rerun()
        with col_card3:
            if st.button("**🔑 Alterar Minha Senha**\nMude sua senha padrão de acesso para garantir mais segurança.", use_container_width=True):
                st.session_state['tela_atual'] = "alterar_senha"
                st.rerun()
        
        st.write("")
        if st.button("🚪 Encerrar Sessão / Sair", type="secondary"):
            st.session_state['logado'] = False
            st.session_state['usuario_atual'] = ""
            st.session_state['senha_atual'] = ""
            st.session_state['tela_atual'] = "menu"
            st.rerun()

    # DIRECIONAMENTO PARA AS JANELAS SEPARADAS DENTRO DE MODULOS
    elif st.session_state['tela_atual'] == "lancamentos":
        renderizar_tela_lancamentos(APPS_SCRIPT_URL, buscar_cidades)
        
    elif st.session_state['tela_atual'] == "relatorios":
        renderizar_tela_relatorios(APPS_SCRIPT_URL, buscar_lancamentos, buscar_cidades)
        
    elif st.session_state['tela_atual'] == "alterar_senha":
        renderizar_tela_senha(APPS_SCRIPT_URL)

# RODAPÉ DE ASSINATURA DO APP
st.markdown('<div class="footer-comunicando">Desenvolvido por Comunicando Igrejas</div>', unsafe_allow_html=True)
