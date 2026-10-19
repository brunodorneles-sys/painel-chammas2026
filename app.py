import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
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
        margin-bottom: 20px;
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
        padding: 6px 4px;
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
        min-width: 28px;
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

menu = st.tabs(["📊 Visão Sistêmica (Matriz)", "➕ Nova Alocação", "🌴 Gestão de Férias", "📥 Exportar para Power BI"])

# TAB 1: MATRIZ DIÁRIA ESTILO PLANILHA
with menu[0]:
    st.subheader("Matriz Diária de Alocação (Escala de Campo)")
    
    col_m, col_a = st.columns(2)
    meses_nomes = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    mes_sel_nome = col_m.selectbox("Selecione o Mês para Visualização", meses_nomes, index=datetime.now().month - 1)
    ano_sel = col_a.number_input("Ano", min_value=2024, max_value=2030, value=datetime.now().year)
    
    mes_num = meses_nomes.index(mes_sel_nome) + 1
    num_dias = calendar.monthrange(ano_sel, mes_num)[1]
    
    # Construção da Tabela HTML
    html_lines = []
    html_lines.append('<div class="gantt-matrix-container"><table class="gantt-table">')
    
    # Cabeçalho: Mês e Dias
    html_lines.append(f'<thead><tr><th rowspan="2">Nº</th><th rowspan="2">Colaborador (TST)</th><th rowspan="2">Unidade / Projeto</th><th colspan="{num_dias}" class="header-month">{mes_sel_nome} {ano_sel}</th></tr><tr>')
    for dia in range(1, num_dias + 1):
        html_lines.append(f'<th class="header-day">{dia}</th>')
    html_lines.append('</tr></thead><tbody>')
    
    # Linhas dos TSTs
    for idx, tst_nome in enumerate(df_tsts, start=1):
        aloc_tst = df_alocacoes[df_alocacoes['tst'] == tst_nome] if not df_alocacoes.empty else pd.DataFrame()
        unidade_nome = aloc_tst['projeto'].iloc[-1] if not aloc_tst.empty else "-"
        
        html_lines.append(f'<tr><td>{idx}</td><td class="col-info">{tst_nome}</td><td class="col-info">{unidade_nome}</td>')
        
        for dia in range(1, num_dias + 1):
            data_atual_str = f"{ano_sel:04d}-{mes_num:02d}-{dia:02d}"
            
            cell_class = ""
            cell_text = ""
            
            # Férias
            if not df_ferias.empty:
                ferias_ativa = df_ferias[(df_ferias['tst'] == tst_nome) & (df_ferias['data_inicio'] <= data_atual_str) & (df_ferias['data_fim'] >= data_atual_str)]
                if not ferias_ativa.empty:
                    cell_class = "cell-vacation"
                    cell_text = "F"
            
            # Alocações
            if not cell_class and not df_alocacoes.empty:
                aloc_ativa = df_alocacoes[(df_alocacoes['tst'] == tst_nome) & (df_alocacoes['data_inicio'] <= data_atual_str) & (df_alocacoes['data_fim'] >= data_atual_str)]
                if not aloc_ativa.empty:
                    is_sub = aloc_ativa['is_substituicao'].iloc[0]
                    if is_sub == 1:
                        cell_class = "cell-substitution"
                        cell_text = "S"
                    else:
                        cell_class = "cell-allocated"
                        cell_text = "X"
            
            html_lines.append(f'<td class="{cell_class}">{cell_text}</td>')
            
        html_lines.append('</tr>')
        
    html_lines.append('</tbody></table></div>')
    
    st.markdown("".join(html_lines), unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-top: 10px; margin-bottom: 25px; display: flex; gap: 20px; font-size: 13px;">
        <div><span style="background-color: #5C061C; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">X</span> Titular Alocado</div>
        <div><span style="background-color: #E65100; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">S</span> Substituição de Férias</div>
        <div><span style="background-color: #d9534f; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">F</span> Em Férias</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Registros de Alocações Cadastrados")
    if not df_alocacoes.empty:
        st.dataframe(df_alocacoes[['projeto', 'tst', 'veiculo', 'etilometro', 'data_inicio', 'data_fim', 'is_substituicao', 'observacao']], use_container_width=True)
    else:
        st.info("Nenhuma alocação registrada no banco de dados.")

# TAB 2: NOVA ALOCAÇÃO
with menu[1]:
    st.subheader("Registrar Alocação Diária / Projeto")
    with st.form("form_alocacao"):
        projeto_sel = st.selectbox("Projeto (Cliente - Código)", df_projetos)
        tst_sel = st.selectbox("Técnico de Segurança (TST)", df_tsts)
        veiculo_sel = st.selectbox("Veículo Alocado", ["Nenhum"] + df_veiculos)
        etilometro_sel = st.selectbox("Etilômetro", ["Nenhum"] + df_etilometros)
        
        c_dt1, c_dt2 = st.columns(2)
        dt_inicio = c_dt1.date_input("Data Inicial", date.today())
        dt_fim = c_dt2.date_input("Data Final", date.today())
        
        is_sub = st.checkbox("Esta alocação é uma substituição de férias?")
        obs = st.text_input("Observações")
        
        btn_alocar = st.form_submit_button("Salvar Alocação")
        
        if btn_alocar:
            execute_db(
                "INSERT INTO alocacoes (projeto, tst, veiculo, etilometro, data_inicio, data_fim, is_substituicao, observacao) VALUES (?,?,?,?,?,?,?,?)",
                (projeto_sel, tst_sel, veiculo_sel, etilometro_sel, str(dt_inicio), str(dt_fim), 1 if is_sub else 0, obs)
            )
            st.success("Alocação registrada com sucesso!")
            st.rerun()

# TAB 3: GESTÃO DE FÉRIAS
with menu[2]:
    st.subheader("Lançar Férias de TST")
    with st.form("form_ferias"):
        tst_ferias = st.selectbox("TST em Férias", df_tsts)
        tst_sub = st.selectbox("TST Substituto Designado", ["Nenhum"] + df_tsts)
        
        c_f1, c_f2 = st.columns(2)
        f_inicio = c_f1.date_input("Início das Férias", date.today())
        f_fim = c_f2.date_input("Fim das Férias", date.today())
        
        btn_ferias = st.form_submit_button("Registrar Férias")
        if btn_ferias:
            execute_db(
                "INSERT INTO ferias (tst, substituto, data_inicio, data_fim) VALUES (?,?,?,?)",
                (tst_ferias, tst_sub, str(f_inicio), str(f_fim))
            )
            st.success("Férias registradas com sucesso!")
            st.rerun()

# TAB 4: POWER BI
with menu[3]:
    st.subheader("Exportação de Dados para Power BI")
    st.write("Baixe o arquivo CSV da tabela fato para conectar no seu relatório do Power BI.")
    
    if not df_alocacoes.empty:
        csv = df_alocacoes.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar fato_alocacoes.csv",
            data=csv,
            file_name="fato_alocacoes_chammas.csv",
            mime="text/csv"
        )
    else:
        st.warning("Sem dados de alocação para exportar.")
