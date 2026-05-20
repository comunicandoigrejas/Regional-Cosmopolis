import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# 1. CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA LINHA!)
st.set_page_config(page_title="Finanças Regional Cosmópolis", page_icon="🕊️", layout="wide")

# 2. ESTILOS VISUAIS (Cores: Azul, Roxo, Verde, Laranja, Amarelo)
st.markdown("""
    <style>
    /* Cor de fundo do Menu Lateral (Roxo/Azul) */
    [data-testid="stSidebar"] {
        background-color: #2b1b54; 
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* Botões principais (Verde Oliva/Laranja) */
    div.stButton > button:first-child {
        background-color: #556b2f;
        color: white;
        border-radius: 8px;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #ff8c00; 
        color: white;
    }
    /* Títulos em Azul Marinho */
    h1, h2, h3 {
        color: #000080;
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
        st.error(f"Erro ao conectar: {e}")
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
    except:
        pass
    return []

# 5. GERADOR DE PDF ABENÇOADO
class GeradorPDF(FPDF):
    def header(self):
        # Para colocar o logo da igreja, basta colocar a imagem na mesma pasta e descomentar a linha abaixo:
        # self.image('logo_igreja.png', 10, 8, 30)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(43, 27, 84) # Cor roxa escuro
        self.cell(0, 10, 'Relatório Financeiro - Regional Cosmópolis', align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-40)
        # Linha para a assinatura da pastora
        self.set_draw_color(0, 0, 0)
        self.line(60, self.get_y(), 150, self.get_y()) 
        self.ln(2)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 10, 'Assinatura da Pastora', align='C')
        self.ln(10)
        # Data de exportação
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
        self.cell(0, 10, f'Documento exportado em: {data_atual}', align='C')

# 6. GERENCIAMENTO DE SESSÃO
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

# ==========================================
# TELA 1: LOGIN DO SISTEMA
# ==========================================
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🕊️ Financeiro Regional")
        st.write("A paz do Senhor! Faça seu login.")
        
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Sistema"):
            if verificar_login(usuario, senha):
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos, varão. Tente novamente!")

# ==========================================
# TELA 2: DENTRO DO SISTEMA
# ==========================================
else:
    # Menu Lateral
    st.sidebar.title("🕊️ Menu Principal")
    st.sidebar.write("Bem-vinda, Pastora!")
    menu = st.sidebar.radio("Navegação", ["Lançamentos", "Relatórios"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair do Sistema"):
        st.session_state['logado'] = False
        st.rerun()

    # --- ABA DE LANÇAMENTOS ---
    if menu == "Lançamentos":
        st.title("📝 Registrar Movimentação")
        
        cidades_lista = buscar_cidades()
        
        with st.form("form_lancamentos", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                data_lancamento = st.date_input("Data do Lançamento")
                tipo = st.selectbox("Tipo", ["Entrada (Dízimos, Ofertas)", "Saída (Despesas, Pagamentos)"])
            with col2:
                cidade = st.selectbox("Igreja/Cidade", cidades_lista)
                valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            descricao = st.text_input("Descrição (Ex: Conta de Luz, Oferta Culto de Domingo)")
            
            botao_salvar = st.form_submit_button("Gravar no Sistema")
            
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
                        "usuario": "Pastora" 
                    }
                    try:
                        resposta_post = requests.post(APPS_SCRIPT_URL, json=dados_envio)
                        if resposta_post.status_code == 200:
                            st.success("Aleluia! Lançamento registrado com sucesso!")
                        else:
                            st.error("Erro ao gravar na planilha.")
                    except Exception as e:
                        st.error(f"Erro de conexão: {e}")

    # --- ABA DE RELATÓRIOS ---
    elif menu == "Relatórios":
        st.title("📊 Relatórios e Exportação")
        
        # Filtros de Data
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data Inicial")
        with col2:
            data_fim = st.date_input("Data Final")
            
        if st.button("Buscar Lançamentos"):
            with st.spinner("Buscando as bençãos e despesas na planilha..."):
                dados = buscar_lancamentos()
                
                if len(dados) > 1:
                    # Converte os dados do Google Sheets para uma tabela Pandas
                    colunas = dados[0]
                    valores = dados[1:]
                    df = pd.DataFrame(valores, columns=colunas)
                    
                    # Convertendo colunas para facilitar o filtro
                    # Assumindo que a coluna Data_Lancamento é a de índice 1 e Valor é índice 5
                    nome_col_data = colunas[1]
                    nome_col_valor = colunas[5]
                    nome_col_tipo = colunas[3]
                    
                    df[nome_col_data] = pd.to_datetime(df[nome_col_data], format='%d/%m/%Y', errors='coerce')
                    df[nome_col_valor] = pd.to_numeric(df[nome_col_valor], errors='coerce').fillna(0)
                    
                    # Filtrando pelas datas escolhidas
                    mask = (df[nome_col_data].dt.date >= data_inicio) & (df[nome_col_data].dt.date <= data_fim)
                    df_filtrado = df.loc[mask].copy()
                    
                    if df_filtrado.empty:
                        st.warning("Nenhum lançamento encontrado nesse período, irmão.")
                    else:
                        # Exibir totais
                        entradas = df_filtrado[df_filtrado[nome_col_tipo] == 'Entrada'][nome_col_valor].sum()
                        saidas = df_filtrado[df_filtrado[nome_col_tipo] == 'Saída'][nome_col_valor].sum()
                        saldo = entradas - saidas
                        
                        st.markdown("### Resumo do Período")
                        c1, c2, c3 = st.columns(3)
                        c1.success(f"Entradas: R$ {entradas:.2f}")
                        c2.error(f"Saídas: R$ {saidas:.2f}")
                        if saldo >= 0:
                            c3.info(f"Saldo: R$ {saldo:.2f}")
                        else:
                            c3.warning(f"Saldo: R$ {saldo:.2f}")
                        
                        # Mostrando a tabela na tela
                        df_exibicao = df_filtrado.copy()
                        df_exibicao[nome_col_data] = df_exibicao[nome_col_data].dt.strftime('%d/%m/%Y')
                        st.dataframe(df_exibicao[[colunas[1], colunas[2], colunas[3], colunas[4], colunas[5]]], use_container_width=True)
                        
                        # ==========================================
                        # GERAÇÃO DO PDF
                        # ==========================================
                        pdf = GeradorPDF()
                        pdf.add_page()
                        
                        # Resumo no PDF
                        pdf.set_font("helvetica", "B", 12)
                        pdf.cell(0, 10, f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", ln=True)
                        pdf.cell(0, 10, f"Entradas: R$ {entradas:.2f} | Saídas: R$ {saidas:.2f} | Saldo: R$ {saldo:.2f}", ln=True)
                        pdf.ln(5)
                        
                        # Cabeçalho da Tabela no PDF
                        pdf.set_fill_color(200, 220, 255)
                        pdf.set_font("helvetica", "B", 10)
                        pdf.cell(25, 10, "Data", border=1, fill=True)
                        pdf.cell(35, 10, "Cidade", border=1, fill=True)
                        pdf.cell(80, 10, "Descrição", border=1, fill=True)
                        pdf.cell(25, 10, "Tipo", border=1, fill=True)
                        pdf.cell(25, 10, "Valor", border=1, fill=True, ln=True)
                        
                        # Linhas da tabela no PDF
                        pdf.set_font("helvetica", "", 9)
                        for index, row in df_exibicao.iterrows():
                            pdf.cell(25, 8, str(row[colunas[1]]), border=1)
                            # Pega até 15 caracteres da cidade e 40 da descrição para não quebrar a tabela
                            pdf.cell(35, 8, str(row[colunas[2]])[:15], border=1) 
                            pdf.cell(80, 8, str(row[colunas[4]])[:40], border=1)
                            pdf.cell(25, 8, str(row[colunas[3]]), border=1)
                            pdf.cell(25, 8, f"R$ {row[colunas[5]]:.2f}", border=1, ln=True)
                        
                        # Gerar o arquivo para download
                        pdf_bytes = bytes(pdf.output())
                        
                        st.download_button(
                            label="📥 Exportar Relatório em PDF",
                            data=pdf_bytes,
                            file_name=f"Relatorio_{data_inicio}_a_{data_fim}.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.info("A planilha ainda não possui lançamentos registrados.")
