import streamlit as st
import requests

# Configuração da página principal (obrigatório ser o primeiro comando)
st.set_page_config(page_title="Finanças Regional Cosmópolis", page_icon="🕊️", layout="wide")

# Estilos Visuais (Cores: Azul, Roxo, Verde, Laranja, Amarelo)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #2b1b54; }
    [data-testid="stSidebar"] * { color: white !important; }
    div.stButton > button:first-child {
        background-color: #556b2f; color: white; border-radius: 8px; border: none;
    }
    div.stButton > button:first-child:hover { background-color: #ff8c00; color: white; }
    h1, h2, h3 { color: #000080; }
    /* Rodapé fixo na tela */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: transparent; color: #888888; text-align: center;
        padding: 10px; font-size: 12px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Puxando a URL da Planilha
try:
    APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]
except KeyError:
    st.error("Varão, o arquivo secrets.toml não foi encontrado ou a URL está faltando.")
    st.stop()

def verificar_login(usuario, senha):
    try:
        resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getUsuarios"})
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados["status"] == "sucesso":
                for linha in dados["dados"][1:]:
                    if len(linha) >= 4:
                        if str(usuario) == str(linha[2]) and str(senha) == str(linha[3]):
                            return True
    except Exception as e:
        st.error(f"Erro ao conectar no login: {e}")
    return False

# Gerenciamento de Sessão
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state:
    st.session_state['usuario_atual'] = ""

# Tela de Login
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🕊️ Financeiro Regional")
        st.write("A paz do Senhor! Faça seu login para liberar as páginas de lançamentos e relatórios.")
        
        usuario_input = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Sistema"):
            if verificar_login(usuario_input, senha):
                st.session_state['logado'] = True
                st.session_state['usuario_atual'] = usuario_input
                st.success("Login realizado! Use o menu lateral para navegar pelas páginas.")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos, varão. Tente novamente!")
else:
    st.title("🕊️ Bem-vindo ao Sistema Regional Cosmópolis")
    st.write(f"Irmão **{st.session_state['usuario_atual']}**, use o menu lateral à esquerda para acessar as janelas de Lançamentos ou Relatórios.")
    
    if st.sidebar.button("Sair do Sistema"):
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ""
        st.rerun()

# Rodapé da página
st.markdown('<div class="footer">Desenvolvido por Comunicando Igrejas</div>', unsafe_allow_html=True)
