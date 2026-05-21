import streamlit as st
import requests

st.set_page_config(page_title="Registrar Lançamentos", page_icon="📝", layout="wide")

# Estilos Visuais e Rodapé
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #2b1b54; }
    div.stButton > button:first-child { background-color: #556b2f; color: white; border-radius: 8px; }
    div.stButton > button:first-child:hover { background-color: #ff8c00; }
    h1 { color: #000080; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; color: #888888; font-size: 12px; font-weight: bold; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# Segurança: Verifica se está logado
if 'logado' not in st.session_state or not st.session_state['logado']:
    st.warning("Varão, você precisa fazer o login na página principal (App.py) primeiro!")
    st.stop()

APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]

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
    return ["Cosmópolis"]

st.title("📝 Registrar Movimentação")
st.sidebar.write(f"Usuário: **{st.session_state['usuario_atual']}**")

cidades_lista = buscar_cidades()

with st.form("form_lancamentos", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        data_lancamento = st.date_input("Data do Lançamento", format="DD/MM/YYYY")
        tipo = st.selectbox("Tipo", ["Entrada (Dízimos, Ofertas)", "Saída (Despesas, Pagamentos)"])
    with col2:
        cidade = st.selectbox("Igreja/Cidade", cidades_lista)
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    
    descricao = st.text_input("Descrição")
    botao_salvar = st.form_submit_button("Gravar no Sistema")
    
    if botao_salvar:
        if descricao == "" or valor == 0:
            st.warning("A descrição e o valor não podem ficar vazios!")
        else:
            dados_envio = {
                "action": "registrarLancamento",
                "data_lancamento": data_lancamento.strftime("%d/%m/%Y"),
                "cidade": cidade,
                "tipo": "Entrada" if "Entrada" in tipo else "Saída",
                "descricao": descricao,
                "valor": valor,
                "usuario": st.session_state['usuario_atual']
            }
            try:
                resposta_post = requests.post(APPS_SCRIPT_URL, json=dados_envio)
                if resposta_post.status_code == 200:
                    st.success(f"Aleluia! Lançamento registrado com sucesso por {st.session_state['usuario_atual']}!")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

st.markdown('<div class="footer">Desenvolvido por Comunicando Igrejas</div>', unsafe_allow_html=True)
