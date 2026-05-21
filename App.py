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

# 5. GERADOR DE PDF ABENÇOADO COM SUPORTE A LOGO NA PASTA ASSETS
class GeradorPDF(FPDF):
    def header(self):
        # CAMINHO CORRIGIDO: Puxa o logo de dentro da pasta assets do GitHub
        caminho_logo = os.path.join("assets", "logo.png")
        if os.path.exists(caminho_logo):
            self.image(caminho_logo, x=10, y=8, w=30)
            self.set_x(45) # Desloca o texto para o lado do logo do GitHub
        
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(43, 27, 84) 
        self.cell(0, 10, 'Relatório Financeiro - Regional Cosmópolis', align='C', ln=True)
        self.ln(15)

    def footer(self):
        self.set_y(-40)
        self.set_draw_color(0, 0, 0)
        self.line(60, self.get_y(), 150, self.get_y()) 
        self.ln(2)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 10, 'Assinatura do Responsável', align='C')
        self.ln(10)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
        self.cell(0, 10, f'Documento exportado em: {data_atual}', align='C')

# 6. GERENCIAMENTO DE SESSÃO
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state:
    st.session_state['usuario_atual'] = ""

# ==========================================
# TELA 1: LOGIN DO SISTEMA
# ==========================================
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🕊️ Financeiro Regional")
        st.write("A paz do Senhor! Faça seu login.")
        
        usuario_input = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Sistema"):
            if verificar_login(usuario_input, senha):
                st.session_state['logado'] = True
                st.session_state['usuario_atual'] = usuario_input  # Guarda dinamicamente o usuário logado
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos, varão. Tente novamente!")

# ==========================================
# TELA 2: DENTRO DO SISTEMA (PÁGINAS SEPARADAS)
# ==========================================
else:
    st.sidebar.title("🕊️ Menu Principal")
    st.sidebar.write(f"Usuário ativo: **{st.session_state['usuario_atual']}**")
    
    # Menu para alternar janelas mantendo a leveza do sistema
    menu = st.sidebar.radio("Navegação", ["📝 Registrar Lançamentos", "📊 Gerar Relatórios"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair do Sistema"):
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ""
        st.rerun()

    # --- JANELA 1: APENAS LANÇAMENTOS ---
    if menu == "📝 Registrar Lançamentos":
        st.title("📝 Registrar Movimentação")
        
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
                        "usuario": st.session_state['usuario_atual'] # Salva o usuário dinâmico (ex: teste)
                    }
                    try:
                        resposta_post = requests.post(APPS_SCRIPT_URL, json=dados_envio)
                        if resposta_post.status_code == 200:
                            st.success(f"Aleluia! Lançamento registrado com sucesso pelo usuário {st.session_state['usuario_atual']}!")
                        else:
                            st.error(f"Erro ao gravar na planilha. Código: {resposta_post.status_code}")
                    except Exception as e:
                        st.error(f"Erro de conexão no envio: {e}")

    # --- JANELA 2: APENAS RELATÓRIOS ---
    elif menu == "📊 Gerar Relatórios":
        st.title("📊 Relatórios e Exportação")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data Inicial", format="DD/MM/YYYY")
        with col2:
            data_fim = st.date_input("Data Final", format="DD/MM/YYYY")
            
        if st.button("Buscar Lançamentos"):
            with st.spinner("Buscando as bênçãos e despesas na planilha..."):
                dados = buscar_lancamentos()
                
                if len(dados) > 1:
                    colunas = dados[0]
                    valores = dados[1:]
                    df = pd.DataFrame(valores, columns=colunas)
                    
                    nome_col_data = colunas[1]
                    nome_col_valor = colunas[5]
                    nome_col_tipo = colunas[3]
                    
                    # Correção e purificação de fusos horários das datas
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
                        saldo = entradas - saidas
                        
                        st.markdown("### Resumo do Período")
                        c1, c2, c3 = st.columns(3)
                        c1.success(f"Entradas: R$ {entradas:.2f}")
                        c2.error(f"Saídas: R$ {saidas:.2f}")
                        c3.info(f"Saldo: R$ {saldo:.2f}")
                        
                        df_exibicao = df_filtrado.copy()
                        df_exibicao[nome_col_data] = df_exibicao[nome_col_data].dt.strftime('%d/%m/%Y')
                        st.dataframe(df_exibicao[[colunas[1], colunas[2], colunas[3], colunas[4], colunas[5]]], use_container_width=True)
                        
                        # GERAÇÃO DO PDF PROFISSIONAL COM QUEBRA DE LINHA COMPLETA
                        pdf = GeradorPDF()
                        pdf.add_page()
                        
                        pdf.set_font("helvetica", "B", 12)
                        pdf.cell(0, 10, f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", ln=True)
                        pdf.cell(0, 10, f"Entradas: R$ {entradas:.2f} | Saídas: R$ {saidas:.2f} | Saldo: R$ {saldo:.2f}", ln=True)
                        pdf.ln(5)
                        
                        # Definição das larguras exatas das colunas (Total = 190mm para caber no A4)
                        larguras = [23, 32, 85, 25, 25] 
                        
                        # Cabeçalho da Tabela
                        pdf.set_fill_color(200, 220, 255)
                        pdf.set_font("helvetica", "B", 10)
                        pdf.cell(larguras[0], 10, "Data", border=1, fill=True)
                        pdf.cell(larguras[1], 10, "Cidade", border=1, fill=True)
                        pdf.cell(larguras[2], 10, "Descrição", border=1, fill=True)
                        pdf.cell(larguras[3], 10, "Tipo", border=1, fill=True)
                        pdf.cell(larguras[4], 10, "Valor", border=1, fill=True, ln=True)
                        
                        # Linhas dinâmicas
                        pdf.set_font("helvetica", "", 9)
                        altura_base_texto = 6  # Tamanho ideal para cada linha de texto dentro da célula
                        
                        for index, row in df_exibicao.iterrows():
                            texto_desc = str(row[colunas[4]])
                            
                            # Calcula dinamicamente quantas linhas a descrição precisa baseada no tamanho do texto
                            largura_real_texto = pdf.get_string_width(texto_desc)
                            num_linhas = math.ceil(largura_real_texto / (larguras[2] - 3)) # 3mm de margem
                            if num_linhas < 1:
                                num_linhas = 1
                            
                            # Multiplica a quantidade de linhas pelo tamanho do texto para definir a altura uniforme da linha inteira
                            altura_da_linha_final = num_linhas * altura_base_texto
                            
                            # Registra a posição do topo da linha
                            y_topo = pdf.get_y()
                            
                            # Coluna 1: Data (Usa a altura calculada)
                            pdf.cell(larguras[0], altura_da_linha_final, str(row[colunas[1]]), border=1)
                            
                            # Coluna 2: Cidade (Usa a altura calculada)
                            pdf.cell(larguras[1], altura_da_linha_final, str(row[colunas[2]])[:15], border=1)
                            
                            # Salva o X exato onde a descrição deve iniciar
                            x_pos_desc = pdf.get_x()
                            
                            # Coluna 3: Descrição (Aqui usamos multi_cell para fazer as quebras automáticas)
                            pdf.multi_cell(larguras[2], altura_base_texto, texto_desc, border=1)
                            
                            # Move o cursor para o lado direito da descrição no mesmo topo (Y) para fazer o restante
                            pdf.set_xy(x_pos_desc + larguras[2], y_topo)
                            
                            # Coluna 4: Tipo (Usa a altura calculada)
                            pdf.cell(larguras[3], altura_da_linha_final, str(row[colunas[3]]), border=1)
                            
                            # Coluna 5: Valor (Usa a altura calculada)
                            pdf.cell(larguras[4], altura_da_linha_final, f"R$ {row[colunas[5]]:.2f}", border=1)
                            
                            # Envia o cursor de volta para a margem esquerda e logo abaixo da linha recém-criada
                            pdf.set_xy(10, y_topo + altura_da_linha_final)
                        
                        pdf_bytes = bytes(pdf.output())
                        
                        st.download_button(
                            label="📥 Exportar Relatório em PDF",
                            data=pdf_bytes,
                            file_name=f"Relatorio_{data_inicio}_a_{data_fim}.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.info("A planilha retornou vazia ou sem linhas válidas.")
