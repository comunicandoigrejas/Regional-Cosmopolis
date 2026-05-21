import streamlit as st
import requests

def renderizar_tela_lancamentos(APPS_SCRIPT_URL, buscar_cidades):
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
                    else:
                        st.error(f"Erro ao gravar na planilha. Código: {resposta_post.status_code}")
                except Exception as e:
                    st.error(f"Erro de conexão no envio: {e}")
