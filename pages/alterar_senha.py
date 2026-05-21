import streamlit as st
import requests

def renderizar_tela_senha(APPS_SCRIPT_URL):
    col_nav1, col_nav2 = st.columns([6, 2])
    with col_nav1:
        st.title("🔑 Alterar Credenciais")
    with col_nav2:
        if st.button("⬅️ Voltar ao Menu Principal", use_container_width=True):
            st.session_state['tela_atual'] = "menu"
            st.rerun()
            
    with st.form("form_mudar_senha", clear_on_submit=True):
        st.write(f"Preencha os campos abaixo para atualizar a segurança do usuário: **{st.session_state['usuario_atual']}**")
        
        senha_atual_input = st.text_input("Digite sua Senha Atual", type="password")
        nova_senha = st.text_input("Digite a Nova Senha", type="password")
        confirmar_senha = st.text_input("Confirme a Nova Senha", type="password")
        
        botao_senha = st.form_submit_button("Atualizar Senha", use_container_width=True)
        
        if botao_senha:
            if senha_atual_input != st.session_state['senha_atual']:
                st.error("A senha atual digitada está incorreta, abençoado!")
            elif nova_senha == "" or confirmar_senha == "":
                st.warning("A nova senha não pode ficar em branco!")
            elif nova_senha != confirmar_senha:
                st.warning("A nova senha e a confirmação não coincidem, varão!")
            else:
                dados_senha = {
                    "action": "alterarSenha",
                    "usuario": st.session_state['usuario_atual'],
                    "nova_senha": nova_senha
                }
                try:
                    with st.spinner("Atualizando credenciais na planilha..."):
                        resposta_senha = requests.post(APPS_SCRIPT_URL, json=dados_senha)
                        if resposta_senha.status_code == 200:
                            dados_retorno = resposta_senha.json()
                            if dados_retorno.get("status") == "sucesso":
                                st.success("Glória a Deus! Sua senha foi alterada com sucesso!")
                                st.session_state['senha_atual'] = nova_senha 
                            else:
                                st.error(f"Erro informado pela planilha: {dados_retorno.get('mensagem')}")
                        else:
                            st.error("Erro técnico ao processar requisição com a planilha.")
                except Exception as e:
                    st.error(f"Falha na comunicação de dados: {e}")
