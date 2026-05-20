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
            
# ... (código do login fica igualzinho na parte de cima) ...

    # Aqui é o que acontece DEPOIS que a pessoa loga com sucesso
    else:
        # Criando um menu lateral para organização
        st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3004/3004613.png", width=100) # Ícone genérico, depois colocamos o logo da igreja
        st.sidebar.title("Menu Principal")
        menu = st.sidebar.radio("Navegação", ["Lançamentos", "Relatórios"])
        
        st.sidebar.markdown("---")
        if st.sidebar.button("Sair do Sistema"):
            st.session_state['logado'] = False
            st.rerun()

        # ==========================================
        # TELA DE LANÇAMENTOS
        # ==========================================
        if menu == "Lançamentos":
            st.title("📝 Registrar Lançamentos")
            st.write("Preencha os dados abaixo para registrar uma nova movimentação.")
            
            # Função para buscar as cidades da aba "Configuracoes"
            @st.cache_data(ttl=300) # Guarda na memória por 5 minutos para o app não ficar lento
            def buscar_cidades():
                try:
                    resposta = requests.get(APPS_SCRIPT_URL, params={"action": "getCidades"})
                    if resposta.status_code == 200:
                        dados = resposta.json()
                        if dados["status"] == "sucesso":
                            # Pula a primeira linha (cabeçalho) e pega os nomes
                            return [linha[0] for linha in dados["dados"][1:] if linha[0] != ""]
                except:
                    pass
                return ["Cosmópolis", "Erro ao carregar cidades"] # Prevenção de erro
                
            cidades_lista = buscar_cidades()
            
            # Criando o formulário
            with st.form("form_lancamentos", clear_on_submit=True):
                data_lancamento = st.date_input("Data do Lançamento")
                cidade = st.selectbox("Selecione a Igreja/Cidade", cidades_lista)
                
                # Usando um selectbox para Entrada/Saída
                tipo = st.selectbox("Tipo de Movimentação", ["Entrada (Dízimos, Ofertas)", "Saída (Despesas, Pagamentos)"])
                descricao = st.text_input("Descrição do Lançamento")
                valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
                
                botao_salvar = st.form_submit_button("Gravar no Sistema")
                
                if botao_salvar:
                    if descricao == "" or valor == 0:
                        # Usando a cor laranja/amarela (warning) para avisos
                        st.warning("Varão, a descrição e o valor não podem ficar vazios!")
                    else:
                        # Prepara a sacola de dados para mandar pro Google Sheets
                        dados_envio = {
                            "action": "registrarLancamento",
                            "data_lancamento": data_lancamento.strftime("%d/%m/%Y"),
                            "cidade": cidade,
                            "tipo": "Entrada" if "Entrada" in tipo else "Saída",
                            "descricao": descricao,
                            "valor": valor,
                            "usuario": "Pastora" # Aqui podemos puxar o nome de quem logou no futuro
                        }
                        
                        try:
                            resposta_post = requests.post(APPS_SCRIPT_URL, json=dados_envio)
                            if resposta_post.status_code == 200:
                                # Usando o verde oliva (success) para confirmação de vitória
                                st.success("Aleluia! Lançamento registrado na planilha com sucesso, benção!")
                            else:
                                st.error("Irmão, houve um erro ao comunicar com a planilha.")
                        except Exception as e:
                            st.error(f"Erro de conexão: {e}")

        # ==========================================
        # TELA DE RELATÓRIOS (Próximo Passo)
        # ==========================================
        elif menu == "Relatórios":
            st.title("📊 Relatórios e Consultas")
            st.info("A tela de relatórios e a geração do PDF com o logo da igreja e a assinatura da pastora será construída aqui.")
