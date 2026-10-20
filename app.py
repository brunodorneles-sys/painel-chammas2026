import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import calendar
import os

# Caminho para o logotipo oficial enviado
LOGO_PATH = "CHMMS_icone-33.png" if os.path.exists("CHMMS_icone-33.png") else None

# Configuração da página (Favicon / Aba do navegador)
st.set_page_config(
    page_title="Chammas Engenharia - Gestão de Recursos SSMA",
    page_icon=LOGO_PATH if LOGO_PATH else "🏗️",
    layout="wide"
)

# Estilização CSS personalizada (Fundo Branco Limpo sem tom cinza)
st.markdown("""
<style>
    :root {
        --chammas-burgundy: #5C061C;
        --chammas-orange: #E65100;
        --chammas-bg: #FFFFFF;
    }
    
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #5C061C 0%, #3D0412 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        margin-bottom: 25px;
        border-bottom: 4px solid #E65100;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .stButton>button {
        background-color: #E65100;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
    }

    .stButton>button:hover {
        background-color: #BF360C;
        color: white;
    }

    /* Estilização da Tabela de Matriz Diária */
    .gantt-matrix-container {
        overflow-x: auto;
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    .gantt-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 11px;
        font-family: Arial, sans-serif;
    }

    .gantt-table th, .gantt-table td {
        border: 1px solid #DDD;
        text-align: center;
        padding: 5px 3px;
        white-space: nowrap;
    }

    .gantt-table th.header-month {
        background-color: #5C061C;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-transform: uppercase;
    }

    .gantt-table th.header-day {
        background-color: #FAFAFA;
        color: #333;
        font-weight: bold;
        min-width: 24px;
    }

    .gantt-table td.col-info {
        text-align: left;
        padding-left: 8px;
        padding-right: 8px;
        font-weight: bold;
        background-color: #FFFFFF;
    }

    /* Cores das Células */
    .cell-allocated {
        background-color: #2E7D32 !important; /* VERDE (Titular) */
        color: white !important;
        font-weight: bold;
    }

    .cell-substitution {
        background-color: #FBC02D !important; /* AMARELO (Substituto) */
        color: #212121 !important;
        font-weight: bold;
    }

    .cell-vacation {
        background-color: #C62828 !important; /* VERMELHO (Férias) */
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('chammas_gestao.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS tsts (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS veiculos (id INTEGER PRIMARY KEY AUTOINCREMENT, placa TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS etilometros (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS projetos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS alocacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projeto TEXT,
                    tst TEXT,
                    veiculo TEXT,
                    etilometro TEXT,
                    data_inicio DATE,
                    data_fim DATE,
                    is_substituicao INTEGER,
                    observacao TEXT
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS ferias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tst TEXT,
                    substituto TEXT,
                    data_inicio DATE,
                    data_fim DATE
                )''')
    
    c.execute("SELECT COUNT(*) FROM tsts")
    if c.fetchone()[0] == 0:
        tsts_iniciais = [
            'Aline Alcantara Linhares', 'Cristiano Henrique Resende', 'Daniela Valesca Martins Silva',
            'Deise Cristina Santos Moreira', 'Gustavo Brito Lopes da Silva', 'Helber Alves Silva',
            'James Marques Lacerda', 'João Vitor de Souza', 'Natália Guimarães', 'Pedro Henrique Ferreira Santos',
            'Richardson Bernardo Fernandes', 'Sérgio Felix de Souza', 'Weryks Martins da Silva',
            'Aline Cristina Souza Ferreira', 'Jacqueline Cristina Pinto Barbosa', 'Marcirene Sales Ferreira',
            'Manoel Tagino dos Santos Junior', 'Charles Franklin de Faria', 'Jessica Arlene Beato',
            'Ricardo Duarte Batista', 'Fernanda de Oliveira Santos', 'Wania Marcia De Rezende',
            'Janaina Aparecida dos Santos', 'Vinicius Pinheiro de Oliveira'
        ]
        c.executemany("INSERT INTO tsts (nome) VALUES (?)", [(t,) for t in tsts_iniciais])

    c.execute("SELECT COUNT(*) FROM veiculos")
    if c.fetchone()[0] == 0:
