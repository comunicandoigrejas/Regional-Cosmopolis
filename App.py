# Configuração da página com um visual abençoado
st.set_page_config(page_title="Finanças Regional Cosmópolis", page_icon="🕊️", layout="centered")

# Puxando a URL de forma segura dos secrets
APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]

def verificar_login(usuario, senha):
    # Vai lá no Google Sheets buscar os usuários
    resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getUsuarios"})
    
    if resposta.status_code == 200:
        dados = resposta.json()
        if dados["status"] == "sucesso":
            usuarios_planilha = dados["dados"]
            
            # Começa do item 1 para pular o cabeçalho da planilha
            for linha in usuarios_planilha[1:]:
                # linha[2] é o Login, linha[3] é a Senha (conforme nossa ordem das colunas)
                user_planilha = linha[2] 
                senha_planilha = linha[3] 
                
                if str(usuario) == str(user_planilha) and str(senha) == str(senha_planilha):
                    return True
    return False

# A "memória" do nosso app para saber quem está logado
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

# Se a pessoa ainda não logou, mostra a tela de entrada
if not st.session_state['logado']:
    st.title("🙏 Financeiro - Regional Cosmópolis")
    st.write("A paz do Senhor! Faça seu login para acessar o sistema.")
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if verificar_login(usuario, senha):
            st.session_state['logado'] = True
            st.success("Glória a Deus! Acesso liberado.")
            st.rerun() # Recarrega a página para entrar no sistema
        else:
            st.error("Irmão, usuário ou senha incorretos. Tente novamente!")
            
# Aqui é o que acontece DEPOIS que a pessoa loga com sucesso
else:
    st.title("Página Inicial - Bem-vindo(a)!")
    st.write("Em breve, aqui teremos a tela de lançamentos...")
    
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()
