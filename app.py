import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import calendar

# Configuração da página
st.set_page_config(
    page_title="Chammas Engenharia - Gestão de Alocação e SSMA",
    page_icon="🏗️",
    layout="wide"
)

# Estilização CSS personalizada (Cores Vinho e Laranja da Chammas + Tabela estilo Planilha)
st.markdown("""
<style>
    :root {
        --chammas-burgundy: #5C061C;
        --chammas-orange: #E65100;
        --chammas-bg: #F9F6F0;
    }
    
    .stApp {
        background-color: var(--chammas-bg);
    }
    
    .main-header {
        background-color: #5C061C;
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 25px;
        border-bottom: 4px solid #E65100;
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
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .gantt-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 12px;
        font-family: Arial, sans-serif;
    }

    .gantt-table th, .gantt-table td {
        border: 1px solid #ccc;
        text-align: center;
        padding: 4px 2px;
        white-space: nowrap;
    }

    .gantt-table th.header-month {
        background-color: #f2d7d5;
        color: #5C061C;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
    }

    .gantt-table th.header-day {
        background-color: #f8f9fa;
        color: #333;
        font-weight: bold;
        min-width: 25px;
    }

    .gantt-table td.col-info {
        text-align: left;
        padding-left: 8px;
        padding-right: 8px;
        font-weight: bold;
        background-color: #fafafa;
    }

    .cell-allocated {
        background-color: #5C061C !important;
        color: white !important;
        font-weight: bold;
    }

    .cell-substitution {
        background-color: #E65100 !important;
        color: white !important;
        font-weight: bold;
    }

    .cell-vacation {
        background-color: #d9534f !important;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Conexão e Inicialização do Banco de Dados SQLite
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
        veiculos_iniciais = [
            'SIB7B06','RUA5H43','SJI8H13','SYJ0J36','TCO9C94','TXY3F21','QMZ1D81','RTF6B55','RUW6A70','TCG3B90',
            'TDT9H59','TDU3E72','TDU3E73','TDU3E74','TDU3E75','TEE4C20','TEE4C33','UDG1J25','TEC6E42','TEE4B95',
            'TEE4C11','TEE4C28','TEE6B91','TXL6B90','TXY7G94','TZF9D38','TEI7D22','TEI7D35','TEI7D36','TES7B26',
            'SYR2J90','TDV9A59','TDW1J44','TEE4C05','TEI7D06','TEI7D18','TEI7D31','TEW0G98','TCK4J56','TDV9A61',
            'TEE4C15','SIX0C67','TDV9A53','TEE4C06','TXS0G24','TEE4C27','TXO0J84','RVT4E66','TDV9A52','TEI7D17',
            'RUT6I73','TDO8H14','TDV9A51','TEI7D34','TEO4G56','TEO4G58','TEO4G59','TXO5I56','SIR0G95','TEE6B90',
            'SYS3J92','TEI7D11','TEI7D20','TEI7D21','TEI7D26','TCE7H36','TCE8G30','TDV9A56','PZA0492','RNT6B86',
            'RUW6B08','RVU9F50','SIF7D10','SYV9F52','TCI8J28','TCT3J87','TDU8I87','TDU8I88','TDU8I89','TDU8I90',
            'TDV9A54','TDV9A57','TDV9A58','TDV9A60','TDW5A05','TEB4C38','TEI7D38','TYV5I62','TZW6H02','UVS4I29'
        ]
        c.executemany("INSERT INTO veiculos (placa) VALUES (?)", [(v,) for v in veiculos_iniciais])

    c.execute("SELECT COUNT(*) FROM etilometros")
