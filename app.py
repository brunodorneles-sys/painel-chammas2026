import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta, time
import calendar

# Configuração da página
st.set_page_config(
    page_title="Chammas Engenharia - Gestão de Recursos SSMA",
    page_icon="🏗️",
    layout="wide"
)

# Estilização CSS Personalizada (Fundo Branco Limpo, Faixa Expandida e Cards Executivos)
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
    
    /* Banner do Cabeçalho Expandido (100% de largura) */
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

    /* Cards de Indicadores com Design Executivo e Bordas Institucionais */
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

    /* Tabela da Matriz Diária */
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

# GESTÃO DE PERSISTÊNCIA EM PLANILHA / MEMÓRIA LOCAL
SPREADSHEET_URL = st.secrets.get("SPREADSHEET_URL", None)

def carregar_tabela(nome_aba, colunas_default, dados_iniciais=None):
    if SPREADSHEET_URL:
        try:
            # Extrair chave da planilha
            sheet_id = SPREADSHEET_URL.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nome_aba}"
            df = pd.read_csv(csv_url)
            if not df.empty:
                return df
        except Exception:
            pass

    # Fallback em memória na sessão
    chave = f"tbl_{nome_aba}"
    if chave not in st.session_state:
        if dados_iniciais is not None:
            st.session_state[chave] = pd.DataFrame(dados_iniciais)
        else:
            st.session_state[chave] = pd.DataFrame(columns=colunas_default)
    return st.session_state[chave]

def salvar_tabela(nome_aba, df):
    chave = f"tbl_{nome_aba}"
    st.session_state[chave] = df.copy()

# Dados Iniciais Base
tsts_padrao = sorted([
    'Aline Alcantara Linhares', 'Cristiano Henrique Resende', 'Daniela Valesca Martins Silva',
    'Deise Cristina Santos Moreira', 'Gustavo Brito Lopes da Silva', 'Helber Alves Silva',
    'James Marques Lacerda', 'João Vitor de Souza', 'Natália Guimarães', 'Pedro Henrique Ferreira Santos',
    'Richardson Bernardo Fernandes', 'Sérgio Felix de Souza', 'Weryks Martins da Silva',
    'Aline Cristina Souza Ferreira', 'Jacqueline Cristina Pinto Barbosa', 'Marcirene Sales Ferreira',
    'Manoel Tagino dos Santos Junior', 'Charles Franklin de Faria', 'Jessica Arlene Beato',
    'Ricardo Duarte Batista', 'Fernanda de Oliveira Santos', 'Wania Marcia De Rezende',
    'Janaina Aparecida dos Santos', 'Vinicius Pinheiro de Oliveira'
])

veiculos_padrao = sorted([
    'SIB7B06','RUA5H43','SJI8H13','SYJ0J36','TCO9C94','TXY3F21','QMZ1D81','RTF6B55','RUW6A70','TCG3B90',
    'TDT9H59','TDU3E72','TDU3E73','TDU3E74','TDU3E75','TEE4C20','TEE4C33','UDG1J25','TEC6E42','TEE4B95',
    'TEE4C11','TEE4C28','TEE6B91','TXL6B90','TXY7G94','TZF9D38','TEI7D22','TEI7D35','TEI7D36','TES7B26',
    'SYR2J90','TDV9A59','TDW1J44','TEE4C05','TEI7D06','TEI7D18','TEI7D31','TEW0G98','TCK4J56','TDV9A61',
    'TEE4C15','SIX0C67','TDV9A53','TEE4C06','TXS0G24','TEE4C27','TXO0J84','RVT4E66','TDV9A52','TEI7D17',
    'RUT6I73','TDO8H14','TDV9A51','TEI7D34','TEO4G56','TEO4G58','TEO4G59','TXO5I56','SIR0G95','TEE6B90',
    'SYS3J92','TEI7D11','TEI7D20','TEI7D21','TEI7D26','TCE7H36','TCE8G30','TDV9A56','PZA0492','RNT6B86',
    'RUW6B08','RVU9F50','SIF7D10','SYV9F52','TCI8J28','TCT3J87','TDU8I87','TDU8I88','TDU8I89','TDU8I90',
    'TDV9A54','TDV9A57','TDV9A58','TDV9A60','TDW5A05','TEB4C38','TEI7D38','TYV5I62','TZW6H02','UVS4I29'
])

etilometros_padrao = sorted(['18302', '18303', '18304', '18305', '18306', '18307', '19407', '19408'])
projetos_padrao = sorted([
    'Gerdau - 5955', 'Vale Brucutu - 5930', 'Gerdau - 5919', 'Vale Norte - 5426', 
    'St. George - 6874', 'Jaguar - 6132', 'Vale - 6300', 'Vale Itabira - 5907', 
    'Kinross - 5852', 'Vale Água Limpa - 5930', 'CBMM - 6150', 'Gerdau - 6677'
])

# Carregamento persistente
df_tsts_tbl = carregar_tabela("tsts", ["nome"], [{"nome": n} for n in tsts_padrao])
df_veiculos_tbl = carregar_tabela("veiculos", ["placa"], [{"placa": p} for p in veiculos_padrao])
df_etilometros_tbl = carregar_tabela("etilometros", ["codigo"], [{"codigo": c} for c in etilometros_padrao])
df_projetos_tbl = carregar_tabela("projetos", ["nome"], [{"nome": p} for p in projetos_padrao])

df_alocacoes = carregar_tabela("alocacoes", ["id", "projeto", "tst", "veiculo", "etilometro", "data_inicio", "data_fim", "is_substituicao", "observacao"])
df_ferias = carregar_tabela("ferias", ["id", "tst", "substituto", "data_inicio", "data_fim"])

df_tsts = sorted(df_tsts_tbl['nome'].dropna().unique().tolist())
df_veiculos = sorted(df_veiculos_tbl['placa'].dropna().unique().tolist())
df_etilometros = sorted(df_etilometros_tbl['codigo'].dropna().unique().tolist())
df_projetos = sorted(df_projetos_tbl['nome'].dropna().unique().tolist())

def verificar_disponibilidade_tst(tst_nome, dt_inicio_str, dt_fim_str):
    if not df_ferias.empty:
        ferias_c = df_ferias[(df_ferias['tst'] == tst_nome) & (
            ((df_ferias['data_inicio'] <= dt_inicio_str) & (df_ferias['data_fim'] >= dt_inicio_str)) |
            ((df_ferias['data_inicio'] <= dt_fim_str) & (df_ferias['data_fim'] >= dt_fim_str)) |
            ((dt_inicio_str <= df_ferias['data_inicio']) & (dt_fim_str >= df_ferias['data_fim']))
        )]
        if not ferias_c.empty:
            return False

    if not df_alocacoes.empty:
        aloc_c = df_alocacoes[(df_alocacoes['tst'] == tst_nome) & (
            ((df_alocacoes['data_inicio'] <= dt_inicio_str) & (df_alocacoes['data_fim'] >= dt_inicio_str)) |
            ((df_alocacoes['data_inicio'] <= dt_fim_str) & (df_alocacoes['data_fim'] >= dt_fim_str)) |
            ((dt_inicio_str <= df_alocacoes['data_inicio']) & (dt_fim_str >= df_alocacoes['data_fim']))
        )]
        if not aloc_c.empty:
            return False

    return True

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 1.9rem; font-weight: 800; letter-spacing: 1.5px;">CHAMMAS ENGENHARIA</h1>
    <p style="margin:4px 0 0 0; font-size: 1.05rem; opacity: 0.9; font-weight: 600;">Gestão de Recursos SSMA</p>
</div>
""", unsafe_allow_html=True)

# Indicadores em Cards
col1, col2, col3, col4, col5 = st.columns(5)
total_tsts = len(df_tsts)
tsts_alocados = df_alocacoes['tst'].nunique() if not df_alocacoes.empty else 0
tsts_ferias = df_ferias['tst'].nunique() if not df_ferias.empty else 0
tsts_livres = max(0, total_tsts - (tsts_alocados + tsts_ferias))
tsts_com_veiculo = df_alocacoes[df_alocacoes['veiculo'].notnull() & (df_alocacoes['veiculo'] != '') & (df_alocacoes['veiculo'] != 'Nenhum')]['tst'].nunique() if not df_alocacoes.empty else 0

with col1: st.markdown(f'<div class="metric-card"><div class="metric-title">Total TSTs</div><div class="metric-value">{total_tsts}</div></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-card"><div class="metric-title">Alocados em Projetos</div><div class="metric-value">{tsts_alocados}</div></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-card"><div class="metric-title">Em Férias</div><div class="metric-value">{tsts_ferias}</div></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-card"><div class="metric-title">Sem Alocação</div><div class="metric-value">{tsts_livres}</div></div>', unsafe_allow_html=True)
with col5: st.markdown(f'<div class="metric-card"><div class="metric-title">Com Veículo</div><div class="metric-value">{tsts_com_veiculo}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

menu = st.tabs(["📊 Visão Sistêmica", "➕ Nova Alocação", "🌴 Gestão de Férias", "⚙️ Cadastros Base", "📥 Exportar para Power BI"])

# TAB 1: VISÃO SISTÊMICA (SEMPRE EM ORDEM ALFABÉTICA)
with menu[0]:
    st.subheader("Gestão diária de Recursos Humanos")
    
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
                        cell_class = "cell-substitution" if is_sub == 1 else "cell-allocated"
                        cell_text = "S" if is_sub == 1 else "X"
                            
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
        for idx_row, row in df_alocacoes.iterrows():
            col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns([3, 3, 3, 3, 1])
            col_a1.write(f"**Projeto:** {row['projeto']}")
            col_a2.write(f"**TST:** {row['tst']}")
            col_a3.write(f"**Veículo:** {row['veiculo']} | **Etilômetro:** {row['etilometro']}")
            col_a4.write(f"**Período:** {row['data_inicio']} até {row['data_fim']}")
            if col_a5.button("🗑️", key=f"del_aloc_{idx_row}"):
                df_alocacoes = df_alocacoes.drop(idx_row).reset_index(drop=True)
                salvar_tabela("alocacoes", df_alocacoes)
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
            nova_aloc = pd.DataFrame([{
                "id": int(datetime.now().timestamp()),
                "projeto": projeto_sel,
                "tst": tst_sel,
                "veiculo": veiculo_sel,
                "etilometro": etilometro_sel,
                "data_inicio": str(dt_inicio),
                "data_fim": str(dt_fim),
                "is_substituicao": 1 if is_sub else 0,
                "observacao": obs
            }])
            df_alocacoes = pd.concat([df_alocacoes, nova_aloc], ignore_index=True)
            salvar_tabela("alocacoes", df_alocacoes)
            st.success("Alocação gravada permanentemente!")
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
                nova_f = pd.DataFrame([{
                    "id": int(datetime.now().timestamp()),
                    "tst": tst_ferias,
                    "substituto": tst_sub,
                    "data_inicio": str(f_inicio),
                    "data_fim": str(f_fim)
                }])
                df_ferias = pd.concat([df_ferias, nova_f], ignore_index=True)
                salvar_tabela("ferias", df_ferias)
                
                if tst_sub != "Nenhum":
                    aloc_titular = df_alocacoes[df_alocacoes['tst'] == tst_ferias] if not df_alocacoes.empty else pd.DataFrame()
                    projeto_cobertura = aloc_titular['projeto'].iloc[-1] if not aloc_titular.empty else "Cobertura de Férias"
                    
                    nova_sub_aloc = pd.DataFrame([{
                        "id": int(datetime.now().timestamp()) + 1,
                        "projeto": projeto_cobertura,
                        "tst": tst_sub,
                        "veiculo": "Nenhum",
                        "etilometro": "Nenhum",
                        "data_inicio": str(f_inicio),
                        "data_fim": str(f_fim),
                        "is_substituicao": 1,
                        "observacao": f"Cobertura de férias de {tst_ferias}"
                    }])
                    df_alocacoes = pd.concat([df_alocacoes, nova_sub_aloc], ignore_index=True)
                    salvar_tabela("alocacoes", df_alocacoes)
                    st.success(f"✅ Férias registradas! O TST **{tst_sub}** foi alocado em amarelo (S) no projeto **{projeto_cobertura}**.")
                else:
                    st.success("✅ Férias registradas com sucesso!")
                st.rerun()

    st.markdown("---")
    st.markdown("### ✏️ Gerenciar e Excluir Registros de Férias")
    if not df_ferias.empty:
        for idx_f, row in df_ferias.iterrows():
            col_f1, col_f2, col_f3, col_f4 = st.columns([4, 4, 3, 1])
            col_f1.write(f"**TST em Férias:** {row['tst']}")
            col_f2.write(f"**Substituto:** {row['substituto']}")
            col_f3.write(f"**Período:** {row['data_inicio']} até {row['data_fim']}")
            if col_f4.button("🗑️", key=f"del_ferias_{idx_f}"):
                sub_nome = row['substituto']
                d_ini = row['data_inicio']
                d_fim = row['data_fim']
                
                df_ferias = df_ferias.drop(idx_f).reset_index(drop=True)
                salvar_tabela("ferias", df_ferias)
                
                if sub_nome != "Nenhum" and not df_alocacoes.empty:
                    df_alocacoes = df_alocacoes[~(
                        (df_alocacoes['tst'] == sub_nome) & 
                        (df_alocacoes['is_substituicao'] == 1) & 
                        (df_alocacoes['data_inicio'] == d_ini) & 
                        (df_alocacoes['data_fim'] == d_fim)
                    )].reset_index(drop=True)
                    salvar_tabela("alocacoes", df_alocacoes)
                    
                st.success("Férias e substituição removidas!")
                st.rerun()

# TAB 4: CADASTROS BASE DE RECURSOS
with menu[3]:
    st.subheader("⚙️ Cadastros de Recursos e Projetos")
    tab_cad1, tab_cad2, tab_cad3, tab_cad4 = st.tabs(["Projetos", "TSTs", "Veículos", "Etilômetros"])
    
    with tab_cad1:
        st.write("#### Cadastrar Novo Projeto")
        with st.form("form_add_p"):
            novo_proj = st.text_input("Nome do Projeto")
            if st.form_submit_button("Adicionar Projeto") and novo_proj:
                if novo_proj not in df_projetos:
                    df_projetos_tbl = pd.concat([df_projetos_tbl, pd.DataFrame([{"nome": novo_proj}])], ignore_index=True)
                    salvar_tabela("projetos", df_projetos_tbl)
                    st.success("Projeto cadastrado!")
                    st.rerun()
        for idx_p, r in df_projetos_tbl.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['nome'])
            if c2.button("🗑️", key=f"del_p_{idx_p}"):
                df_projetos_tbl = df_projetos_tbl.drop(idx_p).reset_index(drop=True)
                salvar_tabela("projetos", df_projetos_tbl)
                st.rerun()

    with tab_cad2:
        st.write("#### Cadastrar Novo TST")
        with st.form("form_add_t"):
            novo_tst = st.text_input("Nome Completo do TST")
            if st.form_submit_button("Adicionar TST") and novo_tst:
                if novo_tst not in df_tsts:
                    df_tsts_tbl = pd.concat([df_tsts_tbl, pd.DataFrame([{"nome": novo_tst}])], ignore_index=True)
                    salvar_tabela("tsts", df_tsts_tbl)
                    st.success("TST cadastrado!")
                    st.rerun()
        for idx_t, r in df_tsts_tbl.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['nome'])
            if c2.button("🗑️", key=f"del_t_{idx_t}"):
                df_tsts_tbl = df_tsts_tbl.drop(idx_t).reset_index(drop=True)
                salvar_tabela("tsts", df_tsts_tbl)
                st.rerun()

    with tab_cad3:
        st.write("#### Cadastrar Novo Veículo")
        with st.form("form_add_v"):
            nova_placa = st.text_input("Placa do Veículo")
            if st.form_submit_button("Adicionar Veículo") and nova_placa:
                if nova_placa.upper() not in df_veiculos:
                    df_veiculos_tbl = pd.concat([df_veiculos_tbl, pd.DataFrame([{"placa": nova_placa.upper()}])], ignore_index=True)
                    salvar_tabela("veiculos", df_veiculos_tbl)
                    st.success("Veículo cadastrado!")
                    st.rerun()
        for idx_v, r in df_veiculos_tbl.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['placa'])
            if c2.button("🗑️", key=f"del_v_{idx_v}"):
                df_veiculos_tbl = df_veiculos_tbl.drop(idx_v).reset_index(drop=True)
                salvar_tabela("veiculos", df_veiculos_tbl)
                st.rerun()

    with tab_cad4:
        st.write("#### Cadastrar Novo Etilômetro")
        with st.form("form_add_e"):
            novo_eti = st.text_input("Código do Etilômetro")
            if st.form_submit_button("Adicionar Etilômetro") and novo_eti:
                if novo_eti not in df_etilometros:
                    df_etilometros_tbl = pd.concat([df_etilometros_tbl, pd.DataFrame([{"codigo": novo_eti}])], ignore_index=True)
                    salvar_tabela("etilometros", df_etilometros_tbl)
                    st.success("Etilômetro cadastrado!")
                    st.rerun()
        for idx_e, r in df_etilometros_tbl.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['codigo'])
            if c2.button("🗑️", key=f"del_e_{idx_e}"):
                df_etilometros_tbl = df_etilometros_tbl.drop(idx_e).reset_index(drop=True)
                salvar_tabela("etilometros", df_etilometros_tbl)
                st.rerun()

# TAB 5: POWER BI
with menu[4]:
    st.subheader("Exportação de Dados para Power BI")
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
