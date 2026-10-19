import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Chammas Engenharia - Gestão de Alocação e SSMA",
    page_icon="🏗️",
    layout="wide"
)

# Estilização CSS personalizada (Cores Vinho e Laranja da Chammas)
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
    if c.fetchone()[0] == 0:
        etilometros_iniciais = ['18302', '18303', '18304', '18305', '18306', '18307', '19407', '19408']
        c.executemany("INSERT INTO etilometros (codigo) VALUES (?)", [(e,) for e in etilometros_iniciais])

    c.execute("SELECT COUNT(*) FROM projetos")
    if c.fetchone()[0] == 0:
        projetos_iniciais = [
            'Gerdau - 5955', 'Vale Brucutu - 5930', 'Gerdau - 5919', 'Vale Norte - 5426', 
            'St. George - 6874', 'Jaguar - 6132', 'Vale - 6300', 'Vale Itabira - 5907', 
            'Kinross - 5852', 'Vale Água Limpa - 5930', 'CBMM - 6150', 'Gerdau - 6677'
        ]
        c.executemany("INSERT INTO projetos (nome) VALUES (?)", [(p,) for p in projetos_iniciais])

    conn.commit()
    conn.close()

init_db()

def run_query(query):
    conn = sqlite3.connect('chammas_gestao.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def execute_db(query, params=()):
    conn = sqlite3.connect('chammas_gestao.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;">CHAMMAS ENGENHARIA</h1>
    <p style="margin:0; opacity: 0.9;">Informação Geotécnica & Segurança Operacional | Painel Sistêmico de Alocação</p>
</div>
""", unsafe_allow_html=True)

df_tsts = run_query("SELECT nome FROM tsts")['nome'].tolist()
df_veiculos = run_query("SELECT placa FROM veiculos")['placa'].tolist()
df_etilometros = run_query("SELECT codigo FROM etilometros")['codigo'].tolist()
df_projetos = run_query("SELECT nome FROM projetos")['nome'].tolist()

df_alocacoes = run_query("SELECT * FROM alocacoes")
df_ferias = run_query("SELECT * FROM ferias")

# Indicadores em Cards
col1, col2, col3, col4, col5 = st.columns(5)

total_tsts = len(df_tsts)
tsts_alocados = df_alocacoes['tst'].nunique() if not df_alocacoes.empty else 0
tsts_ferias = df_ferias['tst'].nunique() if not df_ferias.empty else 0
tsts_livres = max(0, total_tsts - (tsts_alocados + tsts_ferias))
tsts_com_veiculo = df_alocacoes[df_alocacoes['veiculo'].notnull() & (df_alocacoes['veiculo'] != '') & (df_alocacoes['veiculo'] != 'Nenhum')]['tst'].nunique() if not df_alocacoes.empty else 0

with col1:
    st.metric("Total TSTs", total_tsts)
with col2:
    st.metric("Alocados em Projetos", tsts_alocados)
with col3:
    st.metric("Em Férias", tsts_ferias)
with col4:
    st.metric("Sem Alocação", tsts_livres)
with col5:
    st.metric("Com Veículo", tsts_com_veiculo)

st.markdown("---")

menu = st.tabs(["📊 Visão Sistêmica (Gantt)", "➕ Nova Alocação", "🌴 Gestão de Férias", "📥 Exportar para Power BI"])

# TAB 1: VISÃO GANTT VISUAL
with menu[0]:
    st.subheader("Gráfico de Gantt: Alocação por Projeto")
    if not df_alocacoes.empty:
        df_alocacoes['data_inicio'] = pd.to_datetime(df_alocacoes['data_inicio'])
        df_alocacoes['data_fim'] = pd.to_datetime(df_alocacoes['data_fim'])
        df_alocacoes['Tipo'] = df_alocacoes['is_substituicao'].apply(lambda x: 'Substituição de Férias' if x == 1 else 'Titular')
        
        fig_gantt = px.timeline(
            df_alocacoes,
            x_start="data_inicio",
            x_end="data_fim",
            y="projeto",
            color="Tipo",
            hover_data=["tst", "veiculo", "etilometro", "observacao"],
            color_discrete_map={'Titular': '#5C061C', 'Substituição de Férias': '#E65100'},
            title="Linha do Tempo de Projetos e Alocações"
        )
        fig_gantt.update_yaxes(autorange="reversed")
        
        # Ajuste do eixo X para cabeçalho no topo e formato dd/mm/yyyy diário
        fig_gantt.update_xaxes(
            side="top",
            dtick="D1",
            tickformat="%d/%m/%Y",
            tickangle=-45
        )
        
        fig_gantt.update_layout(height=450, margin=dict(l=0, r=0, t=60, b=10))
        st.plotly_chart(fig_gantt, use_container_width=True)

        st.markdown("### Tabela Detalhada de Alocações")
        st.dataframe(
            df_alocacoes[['projeto', 'tst', 'veiculo', 'etilometro', 'data_inicio', 'data_fim', 'Tipo', 'observacao']],
            use_container_width=True
        )
    else:
        st.info("Nenhuma alocação registrada até o momento. Cadastre novas alocações na aba 'Nova Alocação'.")

    st.markdown("---")
    st.subheader("Cronograma de Férias da Equipe")
    if not df_ferias.empty:
        df_ferias['data_inicio'] = pd.to_datetime(df_ferias['data_inicio'])
        df_ferias['data_fim'] = pd.to_datetime(df_ferias['data_fim'])

        fig_ferias = px.timeline(
            df_ferias,
            x_start="data_inicio",
            x_end="data_fim",
            y="tst",
            hover_data=["substituto"],
            color_discrete_sequence=['#E65100'],
            title="Escala de Férias dos TSTs"
        )
        fig_ferias.update_yaxes(autorange="reversed")
        
        # Ajuste do eixo X no topo e formato dd
