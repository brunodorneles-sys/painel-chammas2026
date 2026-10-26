import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta, time
import calendar
import json
import os
import requests
import base64

# Configuração da página
st.set_page_config(
    page_title="Chammas Engenharia - Gestão de Recursos SSMA",
    page_icon="🏗️",
    layout="wide"
)

# Estilização CSS Personalizada
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
        padding: 22px 30px;
        border-radius: 10px;
        margin-bottom: 25px;
        border-bottom: 5px solid #E65100;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        width: 100%;
    }

    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #5C061C;
        border-bottom: 3px solid #E65100;
        border-radius: 10px;
        padding: 18px 15px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(92, 6, 28, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(92, 6, 28, 0.12);
    }

    .metric-title {
        color: #5C061C;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #E65100;
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1;
    }

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

    .cell-allocated {
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
    }

    .cell-substitution {
        background-color: #FBC02D !important;
        color: #212121 !important;
        font-weight: bold;
    }

    .cell-vacation {
        background-color: #C62828 !important;
        color: white !important;
        font-weight: bold;
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

# Gestão e Sincronização de Dados com GitHub
def persistir_backup_github(conteudo_json):
    token = st.secrets.get("GITHUB_TOKEN", None)
    repo = "brunodorneles-sys/painel-chammas2026"
    path = "backup_dados.json"
    
    if not token:
        # Se não houver token configurado em st.secrets, salva apenas localmente
        with open("backup_dados.json", "w", encoding="utf-8") as f:
            f.write(conteudo_json)
        return False
        
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Obter SHA do ficheiro se existir
    res_get = requests.get(url, headers=headers)
    sha = res_get.json().get("sha") if res_get.status_code == 200 else None
    
    dados_commit = {
        "message": f"Backup automático SSMA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": base64.b64encode(conteudo_json.encode("utf-8")).decode("utf-8")
    }
    if sha:
        dados_commit["sha"] = sha
        
    requests.put(url, headers=headers, json=dados_commit)
    return True

def gerar_backup_json():
    conn = sqlite3.connect('chammas_gestao.db')
    backup = {
        "tsts": pd.read_sql_query("SELECT * FROM tsts", conn).to_dict(orient="records"),
        "veiculos": pd.read_sql_query("SELECT * FROM veiculos", conn).to_dict(orient="records"),
        "etilometros": pd.read_sql_query("SELECT * FROM etilometros", conn).to_dict(orient="records"),
        "projetos": pd.read_sql_query("SELECT * FROM projetos", conn).to_dict(orient="records"),
        "alocacoes": pd.read_sql_query("SELECT * FROM alocacoes", conn).to_dict(orient="records"),
        "ferias": pd.read_sql_query("SELECT * FROM ferias", conn).to_dict(orient="records")
    }
    conn.close()
    conteudo_json = json.dumps(backup, ensure_ascii=False, indent=2)
    persistir_backup_github(conteudo_json)
    return conteudo_json

def restaurar_backup_json(dados_json):
    conn = sqlite3.connect('chammas_gestao.db')
    c = conn.cursor()
    try:
        dados = json.loads(dados_json) if isinstance(dados_json, str) else dados_json
        for tabela in ["tsts", "veiculos", "etilometros", "projetos", "alocacoes", "ferias"]:
            if tabela in dados and len(dados[tabela]) > 0:
                df = pd.DataFrame(dados[tabela])
                df.to_sql(tabela, conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

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
        # Tenta restaurar do ficheiro de backup se existir no repositório
        if os.path.exists("backup_dados.json"):
            with open("backup_dados.json", "r", encoding="utf-8") as f:
                restaurar_backup_json(f.read())
        else:
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
    gerar_backup_json()

def processar_auto_alocacao_diaria():
    agora = datetime.now()
    hoje = agora.date()
    ontem = hoje - timedelta(days=1)
    
    if agora.time() >= time(6, 0):
        conn = sqlite3.connect('chammas_gestao.db')
        c = conn.cursor()
        c.execute("""
            SELECT projeto, tst, veiculo, etilometro, data_inicio, data_fim, is_substituicao, observacao 
            FROM alocacoes 
            WHERE data_inicio <= ? AND data_fim >= ?
        """, (str(ontem), str(ontem)))
        alocacoes_ontem = c.fetchall()
        
        alterou = False
        for aloc in alocacoes_ontem:
            proj, tst_nom, veic, etil, d_ini, d_fim, is_sub, obs = aloc
            if d_fim >= str(hoje):
                c.execute("SELECT COUNT(*) FROM alocacoes WHERE tst = ? AND data_inicio <= ? AND data_fim >= ?", (tst_nom, str(hoje), str(hoje)))
                ja_alocado_hoje = c.fetchone()[0] > 0
                if not ja_alocado_hoje:
                    c.execute("""
                        INSERT INTO alocacoes (projeto, tst, veiculo, etilometro, data_inicio, data_fim, is_substituicao, observacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (proj, tst_nom, veic, etil, str(hoje), d_fim, is_sub, f"Propagado automaticamente: {obs}"))
                    alterou = True
        conn.commit()
        conn.close()
        if alterou:
            gerar_backup_json()

processar_auto_alocacao_diaria()

def verificar_disponibilidade_tst(tst_nome, dt_inicio_str, dt_fim_str):
    conn = sqlite3.connect('chammas_gestao.db')
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM ferias 
        WHERE tst = ? AND (
            (data_inicio <= ? AND data_fim >= ?) OR
            (data_inicio <= ? AND data_fim >= ?) OR
            (? <= data_inicio AND ? >= data_fim)
        )
    """, (tst_nome, dt_inicio_str, dt_inicio_str, dt_fim_str, dt_fim_str, dt_inicio_str, dt_fim_str))
    em_ferias = c.fetchone()[0] > 0

    c.execute("""
        SELECT COUNT(*) FROM alocacoes 
        WHERE tst = ? AND (
            (data_inicio <= ? AND data_fim >= ?) OR
            (data_inicio <= ? AND data_fim >= ?) OR
            (? <= data_inicio AND ? >= data_fim)
        )
    """, (tst_nome, dt_inicio_str, dt_inicio_str, dt_fim_str, dt_fim_str, dt_inicio_str, dt_fim_str))
    em_alocacao = c.fetchone()[0] > 0

    conn.close()
    return not (em_ferias or em_alocacao)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 1.9rem; font-weight: 800; letter-spacing: 1.5px;">CHAMMAS ENGENHARIA</h1>
    <p style="margin:4px 0 0 0; font-size: 1.05rem; opacity: 0.9; font-weight: 600;">Gestão de Recursos SSMA</p>
</div>
""", unsafe_allow_html=True)

df_tsts = run_query("SELECT id, nome FROM tsts")['nome'].tolist()
df_veiculos = run_query("SELECT id, placa FROM veiculos")['placa'].tolist()
df_etilometros = run_query("SELECT id, codigo FROM etilometros")['codigo'].tolist()
df_projetos = run_query("SELECT id, nome FROM projetos")['nome'].tolist()

df_alocacoes = run_query("SELECT * FROM alocacoes")
df_ferias = run_query("SELECT * FROM ferias")

# Cards Indicadores
col1, col2, col3, col4, col5 = st.columns(5)
total_tsts = len(df_tsts)
tsts_alocados = df_alocacoes['tst'].nunique() if not df_alocacoes.empty else 0
tsts_ferias = df_ferias['tst'].nunique() if not df_ferias.empty else 0
tsts_livres = max(0, total_tsts - (tsts_alocados + tsts_ferias))
tsts_com_veiculo = df_alocacoes[df_alocacoes['veiculo'].notnull() & (df_alocacoes['veiculo'] != '') & (df_alocacoes['veiculo'] != 'Nenhum')]['tst'].nunique() if not df_alocacoes.empty else 0

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total TSTs</div><div class="metric-value">{total_tsts}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Alocados em Projetos</div><div class="metric-value">{tsts_alocados}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Em Férias</div><div class="metric-value">{tsts_ferias}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Sem Alocação</div><div class="metric-value">{tsts_livres}</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Com Veículo</div><div class="metric-value">{tsts_com_veiculo}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

menu = st.tabs(["📊 Visão Sistêmica", "➕ Nova Alocação", "🌴 Gestão de Férias", "⚙️ Cadastros Base", "💾 Cópia de Segurança & Restauro", "📥 Exportar para Power BI"])

# TAB 1: VISÃO SISTÊMICA
with menu[0]:
    st.subheader("Gestão diária de Recursos Humanos")
    st.caption("ℹ️ *A virada diária ocorre automaticamente às 06:00 a.m. (UTC-3), mantendo as alocações vigentes do dia anterior.*")
    
    col_d1, col_d2 = st.columns(2)
    dt_inicio_vis = col_d1.date_input("Visualizar Período de:", date.today().replace(day=1))
    dt_fim_vis = col_d2.date_input("Até:", date.today().replace(day=1) + timedelta(days=60))
    
    if dt_inicio_vis <= dt_fim_vis:
        datas_lista = pd.date_range(start=dt_inicio_vis, end=dt_fim_vis)
        
        meses_grupos = {}
        for d in datas_lista:
            chave_mes = d.strftime("%b/%Y").upper()
            meses_grupos[chave_mes] = meses_grupos.get(chave_mes, 0) + 1
            
        html_lines = []
        html_lines.append('<div class="gantt-matrix-container"><table class="gantt-table">')
        html_lines.append('<thead><tr><th rowspan="2">Nº</th><th rowspan="2">Colaborador (TST)</th><th rowspan="2">Projeto Atual</th>')
        for m_nome, count_dias in meses_grupos.items():
            html_lines.append(f'<th colspan="{count_dias}" class="header-month">{m_nome}</th>')
        html_lines.append('</tr><tr>')
        
        for d in datas_lista:
            html_lines.append(f'<th class="header-day">{d.day}</th>')
        html_lines.append('</tr></thead><tbody>')
        
        for idx, tst_nome in enumerate(df_tsts, start=1):
            aloc_tst = df_alocacoes[df_alocacoes['tst'] == tst_nome] if not df_alocacoes.empty else pd.DataFrame()
            unidade_nome = aloc_tst['projeto'].iloc[-1] if not aloc_tst.empty else "-"
            
            html_lines.append(f'<tr><td>{idx}</td><td class="col-info">{tst_nome}</td><td class="col-info">{unidade_nome}</td>')
            
            for d in datas_lista:
                data_curr_str = d.strftime('%Y-%m-%d')
                cell_class = ""
                cell_text = ""
                
                if not df_ferias.empty:
                    ferias_act = df_ferias[(df_ferias['tst'] == tst_nome) & (df_ferias['data_inicio'] <= data_curr_str) & (df_ferias['data_fim'] >= data_curr_str)]
                    if not ferias_act.empty:
                        cell_class = "cell-vacation"
                        cell_text = "F"
                
                if not cell_class and not df_alocacoes.empty:
                    aloc_act = df_alocacoes[(df_alocacoes['tst'] == tst_nome) & (df_alocacoes['data_inicio'] <= data_curr_str) & (df_alocacoes['data_fim'] >= data_curr_str)]
                    if not aloc_act.empty:
                        is_sub = aloc_act['is_substituicao'].iloc[0]
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
            <div><span style="background-color: #2E7D32; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">X</span> Alocação Titular (Verde)</div>
            <div><span style="background-color: #FBC02D; color: black; padding: 2px 8px; border-radius: 3px; font-weight: bold;">S</span> Substituto de Férias (Amarelo)</div>
            <div><span style="background-color: #C62828; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">F</span> Ausência por Férias (Vermelho)</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("A data final deve ser maior ou igual à data inicial.")

    st.markdown("---")
    st.markdown("### ✏️ Gerenciar e Excluir Alocações Existentes")
    if not df_alocacoes.empty:
        for index, row in df_alocacoes.iterrows():
            col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns([3, 3, 3, 3, 1])
            col_a1.write(f"**Projeto:** {row['projeto']}")
            col_a2.write(f"**TST:** {row['tst']}")
            col_a3.write(f"**Veículo:** {row['veiculo']} | **Etilômetro:** {row['etilometro']}")
            col_a4.write(f"**Período:** {row['data_inicio']} até {row['data_fim']}")
            if col_a5.button("🗑️", key=f"del_aloc_{row['id']}"):
                execute_db("DELETE FROM alocacoes WHERE id = ?", (row['id'],))
                st.success("Alocação excluída!")
                st.rerun()
    else:
        st.info("Nenhuma alocação cadastrada.")

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
            st.success("Alocação registrada e cópia de segurança atualizada!")
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
            if tst_ferias == tst_sub:
                st.error("❌ O TST em férias não pode ser o seu próprio substituto!")
            elif tst_sub != "Nenhum" and not verificar_disponibilidade_tst(tst_sub, str(f_inicio), str(f_fim)):
                st.error(f"❌ **TST Não Disponível!** O substituto **{tst_sub}** possui outros compromissos no período de **{f_inicio.strftime('%d/%m/%Y')}** a **{f_fim.strftime('%d/%m/%Y')}**.")
            else:
                execute_db(
                    "INSERT INTO ferias (tst, substituto, data_inicio, data_fim) VALUES (?,?,?,?)",
                    (tst_ferias, tst_sub, str(f_inicio), str(f_fim))
                )
                
                if tst_sub != "Nenhum":
                    aloc_titular = df_alocacoes[df_alocacoes['tst'] == tst_ferias] if not df_alocacoes.empty else pd.DataFrame()
                    projeto_cobertura = aloc_titular['projeto'].iloc[-1] if not aloc_titular.empty else "Cobertura de Férias"
                    
                    execute_db(
                        "INSERT INTO alocacoes (projeto, tst, veiculo, etilometro, data_inicio, data_fim, is_substituicao, observacao) VALUES (?,?,?,?,?,?,?,?)",
                        (projeto_cobertura, tst_sub, "Nenhum", "Nenhum", str(f_inicio), str(f_fim), 1, f"Cobertura de férias de {tst_ferias}")
                    )
                    st.success(f"✅ Férias registradas! O TST **{tst_sub}** foi alocado em amarelo (S) para cobrir o projeto **{projeto_cobertura}**.")
                else:
                    st.success("✅ Férias registradas com sucesso!")
                st.rerun()

    st.markdown("---")
    st.markdown("### ✏️ Gerenciar e Excluir Registros de Férias")
    if not df_ferias.empty:
        for index, row in df_ferias.iterrows():
            col_f1, col_f2, col_f3, col_f4 = st.columns([4, 4, 3, 1])
            col_f1.write(f"**TST em Férias:** {row['tst']}")
            col_f2.write(f"**Substituto:** {row['substituto']}")
            col_f3.write(f"**Período:** {row['data_inicio']} até {row['data_fim']}")
            if col_f4.button("🗑️", key=f"del_ferias_{row['id']}"):
                execute_db("DELETE FROM ferias WHERE id = ?", (row['id'],))
                if row['substituto'] and row['substituto'] != "Nenhum":
                    execute_db("DELETE FROM alocacoes WHERE tst = ? AND is_substituicao = 1 AND data_inicio = ? AND data_fim = ?", (row['substituto'], row['data_inicio'], row['data_fim']))
                st.success("Registro de férias e substituição excluídos!")
                st.rerun()

# TAB 4: CADASTROS BASE DE RECURSOS
with menu[3]:
    st.subheader("⚙️ Cadastros de Recursos e Projetos")
    
    tab_cad1, tab_cad2, tab_cad3, tab_cad4 = st.tabs(["Projetos", "TSTs", "Veículos", "Etilômetros"])
    
    with tab_cad1:
        st.write("#### Cadastrar Novo Projeto")
        with st.form("form_add_projeto"):
            novo_proj = st.text_input("Nome do Projeto (Ex: Vale Norte - 6000)")
            if st.form_submit_button("Adicionar Projeto") and novo_proj:
                try:
                    execute_db("INSERT INTO projetos (nome) VALUES (?)", (novo_proj,))
                    st.success(f"Projeto '{novo_proj}' adicionado com sucesso!")
                    st.rerun()
                except:
                    st.error("Projeto já cadastrado ou erro na gravação.")
        st.write("##### Projetos Existentes:")
        df_p_full = run_query("SELECT id, nome FROM projetos")
        for idx, r in df_p_full.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['nome'])
            if c2.button("🗑️", key=f"del_p_{r['id']}"):
                execute_db("DELETE FROM projetos WHERE id = ?", (r['id'],))
                st.rerun()

    with tab_cad2:
        st.write("#### Cadastrar Novo TST")
        with st.form("form_add_tst"):
            novo_tst = st.text_input("Nome Completo do TST")
            if st.form_submit_button("Adicionar TST") and novo_tst:
                try:
                    execute_db("INSERT INTO tsts (nome) VALUES (?)", (novo_tst,))
                    st.success(f"TST '{novo_tst}' adicionado com sucesso!")
                    st.rerun()
                except:
                    st.error("TST já cadastrado ou erro na gravação.")
        st.write("##### TSTs Existentes:")
        df_t_full = run_query("SELECT id, nome FROM tsts")
        for idx, r in df_t_full.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['nome'])
            if c2.button("🗑️", key=f"del_t_{r['id']}"):
                execute_db("DELETE FROM tsts WHERE id = ?", (r['id'],))
                st.rerun()

    with tab_cad3:
        st.write("#### Cadastrar Novo Veículo")
        with st.form("form_add_veiculo"):
            nova_placa = st.text_input("Placa do Veículo")
            if st.form_submit_button("Adicionar Veículo") and nova_placa:
                try:
                    execute_db("INSERT INTO veiculos (placa) VALUES (?)", (nova_placa.upper(),))
                    st.success(f"Veículo '{nova_placa.upper()}' adicionado com sucesso!")
                    st.rerun()
                except:
                    st.error("Veículo já cadastrado ou erro na gravação.")
        st.write("##### Veículos Existentes:")
        df_v_full = run_query("SELECT id, placa FROM veiculos")
        for idx, r in df_v_full.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['placa'])
            if c2.button("🗑️", key=f"del_v_{r['id']}"):
                execute_db("DELETE FROM veiculos WHERE id = ?", (r['id'],))
                st.rerun()

    with tab_cad4:
        st.write("#### Cadastrar Novo Etilômetro")
        with st.form("form_add_etilometro"):
            novo_eti = st.text_input("Código/Número do Etilômetro")
            if st.form_submit_button("Adicionar Etilômetro") and novo_eti:
                try:
                    execute_db("INSERT INTO etilometros (codigo) VALUES (?)", (novo_eti,))
                    st.success(f"Etilômetro '{novo_eti}' adicionado com sucesso!")
                    st.rerun()
                except:
                    st.error("Etilômetro já cadastrado ou erro na gravação.")
        st.write("##### Etilômetros Existentes:")
        df_e_full = run_query("SELECT id, codigo FROM etilometros")
        for idx, r in df_e_full.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['codigo'])
            if c2.button("🗑️", key=f"del_e_{r['id']}"):
                execute_db("DELETE FROM etilometros WHERE id = ?", (r['id'],))
                st.rerun()

# TAB 5: BACKUP E RESTAURO
with menu[4]:
    st.subheader("💾 Cópia de Segurança e Persistência de Dados")
    st.write("Todas as alterações realizadas no painel são salvas automaticamente em backup JSON.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("#### Descarregar Cópia de Segurança")
        st.write("Faça o descarregamento do ficheiro JSON atual com todos os registos (alocações, férias e cadastros).")
        conteudo_bkp = gerar_backup_json()
        st.download_button(
            label="📥 Descarregar backup_dados.json",
            data=conteudo_bkp,
            file_name=f"chammas_backup_{date.today()}.json",
            mime="application/json"
        )
        
    with col_b2:
        st.markdown("#### Restaurar Base de Dados")
        st.write("Caso a aplicação reinicie ou pretenda restaurar dados anteriores, carregue o ficheiro de backup:")
        arquivo_upload = st.file_uploader("Selecione o ficheiro de cópia de segurança (.json)", type=["json"])
        if arquivo_upload is not None:
            if st.button("Restaurar Dados Agora"):
                sucesso = restaurar_backup_json(arquivo_upload.read().decode('utf-8'))
                if sucesso:
                    st.success("✅ Base de dados restaurada com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao restaurar os dados do ficheiro.")

# TAB 6: POWER BI
with menu[5]:
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
