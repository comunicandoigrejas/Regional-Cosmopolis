import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import math

# 1. CONFIGURAÇÃO DA PÁGINA (Ícone da guia e Título)
st.set_page_config(page_title="Finanças Regional Cosmópolis", page_icon="🏛️", layout="wide")

# 2. ESTILOS VISUAIS CUSTOMIZADOS (Cores solicitadas e fontes escuras)
st.markdown("""
    <style>
    /* Oculta a barra superior padrão do Streamlit */
    header {
        visibility: hidden !important;
    }
    footer {
        visibility: hidden !important;
    }
    #MainMenu {
        visibility: hidden !important;
    }
    
    /* Títulos Principais das Páginas */
    h1, h2, h3 {
        color: #000080; /* Azul Marinho */
        font-weight: bold;
    }

    /* Estilização dos Botões de Menu (Cards Grandes) */
    div.stButton > button {
        border-radius: 12px !important;
        padding: 30px 20px !important;
        background-color: #f0f2f6 !important; /* Fundo cinza claro */
        border: 2px solid #2b1b54 !important; /* Borda fina */
        transition: all 0.3s ease;
        height: auto !important;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* Efeito ao passar o mouse por cima do Card (Laranja) */
    div.stButton > button:hover {
        background-color: #ff8c00 !important; 
        border-color: #ff8c00 !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.15);
    }
    
    /* Ajuste do Texto do Card (Fonte Escura) */
    div.stButton > button p {
        color: #1e1e1e !important; /* Cor cinza bem escura/preta */
        font-size: 16px !important;
        text-align: center;
    }
    
    /* Título dentro do Card (Azul Marinho) */
    div.stButton > button p strong {
        color: #000080 !important; 
        font-size: 22px !important;
        display: block;
        margin-bottom: 8px;
    }
    
    /* Inverte as cores do texto para Branco quando o mouse passa por cima do Card (Hover) */
    div.stButton > button:hover p, div.stButton > button:hover p strong {
        color: #ffffff !important;
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

# ... (restante das funções e lógica de login permanecem iguais)

# ==========================================
# TELA 1: LOGIN DO SISTEMA
# ==========================================
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        # Ícone de banco adicionado aqui no título
        st.title("🏛️ Financeiro Regional")
        st.write("Bem-vindo(a)! Faça seu login.")
        
        # ... (campos de login)

# ==========================================
# TELA 2: SISTEMA LOGADO
# ==========================================
else:
    # --- JANELA: MENU PRINCIPAL DE BOTÕES ---
    if st.session_state['tela_atual'] == "menu":
        # Ícone de banco adicionado aqui no título principal
        st.title("🏛️ Painel de Controle - Regional Cosmópolis")
        st.write(f"Bem-vindo, abençoado(a) **{st.session_state['usuario_atual']}**! Escolha a operação desejada:")
        st.write("")
        
        col_card1, col_card2, col_card3 = st.columns(3)
        
        with col_card1:
            # Texto do botão atualizado com ícone bancário
            texto_card1 = "🏛️ **Registrar Movimentações**\n\nInsira novas entradas e saídas de dízimos, ofertas ou despesas."
            if st.button(texto_card1, use_container_width=True, key="card_lancamentos"):
                st.session_state['tela_atual'] = "lancamentos"
                st.rerun()
                
        # ... (restante do código do menu)
