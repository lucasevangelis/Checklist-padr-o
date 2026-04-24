import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuração da Página
st.set_page_config(page_title="Dashboard de Controle", page_icon="📊", layout="wide")

# --- AUTENTICAÇÃO ---
if "auth_dashboard" not in st.session_state:
    st.session_state.auth_dashboard = False

if not st.session_state.auth_dashboard:
    st.title("🔒 Acesso Restrito - Dashboard")
    senha_correta = os.getenv("SENHA_DASHBOARD", "Callink@01")
    senha = st.text_input("Digite a senha de acesso ao Dashboard:", type="password")
    if st.button("Entrar", type="primary"):
        if senha == senha_correta:
            st.session_state.auth_dashboard = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()
# ----------------------

# Estilização Customizada
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        border-left: 5px solid #00C4B4;
    }
    .metric-title {
        color: #A0A0A0;
        font-size: 1rem;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .metric-subtitle {
        color: #00C4B4;
        font-size: 0.9rem;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏢 Dashboard de Controle de Pisos")
st.markdown("Visualização e análise de dados sobre observações, posições e pisos.")

# Caminho do arquivo padrão
DEFAULT_FILE = "Checklist dos pisos(Planilha1).csv"

# Sidebar para Upload de Novos Arquivos e Filtros
st.sidebar.header("📁 Atualizar Dados")
uploaded_file = st.sidebar.file_uploader("Faça upload de um novo arquivo CSV para atualizar o dashboard", type=["csv"])

@st.cache_data(ttl=2)
def load_data(file):
    try:
        # Tenta carregar com utf-8-sig ou latin-1
        try:
            df = pd.read_csv(file, encoding='utf-8-sig')
        except:
            if hasattr(file, 'seek'): file.seek(0)
            df = pd.read_csv(file, encoding='latin-1')
        
        # Limpar colunas não nomeadas (vazias criadas por vírgulas no final das linhas)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Renomear colunas para garantir padronização, caso tenha problemas de encoding
        col_mapping = {}
        for col in df.columns:
            if 'Data' in col: col_mapping[col] = 'Data'
            elif 'Piso' in col: col_mapping[col] = 'Piso'
            elif 'Posi' in col: col_mapping[col] = 'Posicao'
            elif 'Módul' in col or 'Modul' in col: col_mapping[col] = 'Modulo'
            elif 'Observa' in col: col_mapping[col] = 'Observacao'
        
        df.rename(columns=col_mapping, inplace=True)
        
        # Converter coluna Data para datetime
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce', dayfirst=False)
            
        return df
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return pd.DataFrame()

# Carregar dados
data_source = uploaded_file if uploaded_file is not None else (DEFAULT_FILE if os.path.exists(DEFAULT_FILE) else None)

if data_source is None:
    st.info("Nenhum dado encontrado. Por favor, faça upload de um arquivo CSV.")
else:
    df = load_data(data_source)
    
    if df.empty:
        st.warning("O arquivo carregado está vazio ou não possui o formato esperado.")
    else:
        # Extrair mês/ano para filtros
        if 'Data' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Data']):
            meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
            
            df['Ano'] = df['Data'].dt.year
            df['Mes_Num'] = df['Data'].dt.month
            df['Mes'] = df['Mes_Num'].map(meses_pt)
            
            st.sidebar.header("🔍 Filtros de Período")
            
            anos_disponiveis = sorted([int(x) for x in df['Ano'].dropna().unique()], reverse=True)
            
            if anos_disponiveis:
                ano_selecionado = st.sidebar.selectbox("Ano:", ["Todos"] + anos_disponiveis)
                
                if ano_selecionado != "Todos":
                    df_filtered = df[df['Ano'] == ano_selecionado]
                else:
                    df_filtered = df
                
                meses_nums = sorted([int(x) for x in df_filtered['Mes_Num'].dropna().unique()])
                meses_nomes = [meses_pt[m] for m in meses_nums]
                
                mes_selecionado = st.sidebar.selectbox("Mês:", ["Todos"] + meses_nomes)
                
                if mes_selecionado != "Todos":
                    df_filtered = df_filtered[df_filtered['Mes'] == mes_selecionado]
            else:
                df_filtered = df
        else:
            df_filtered = df
            
        # Função para mostrar detalhes em um modal
        @st.dialog("Detalhes dos Registros", width="large")
        def show_details(titulo, filtro_col, filtro_val, df_detalhes):
            st.markdown(f"### Detalhes: {titulo} - **{filtro_val}**")
            df_filtrado = df_detalhes[df_detalhes[filtro_col] == filtro_val].copy()
            if 'Data' in df_filtrado.columns and pd.api.types.is_datetime64_any_dtype(df_filtrado['Data']):
                df_filtrado['Data'] = df_filtrado['Data'].dt.strftime('%d/%m/%Y')
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

        def format_number(val):
            try:
                fval = float(val)
                return str(int(fval)) if fval.is_integer() else str(val)
            except:
                return str(val)

        # Calcular Métricas
        st.markdown("### 🎯 Métricas Principais")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'Piso' in df_filtered.columns:
                piso_counts = df_filtered['Piso'].value_counts()
                if not piso_counts.empty:
                    piso_critico = piso_counts.idxmax()
                    piso_qtd = piso_counts.max()
                    piso_display = format_number(piso_critico)
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-title">Piso Mais Ofensivo</div>
                        <div class="metric-value">Piso {piso_display}</div>
                        <div class="metric-subtitle">{piso_qtd} ocorrências</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    if st.button("🔍 Ver Detalhes", key="btn_piso", use_container_width=True):
                        show_details('Piso Mais Ofensivo', 'Piso', piso_critico, df_filtered)
                else:
                    st.info("Sem dados de Piso")

        with col2:
            if 'Observacao' in df_filtered.columns:
                obs_counts = df_filtered['Observacao'].value_counts()
                if not obs_counts.empty:
                    obs_critica = obs_counts.idxmax()
                    obs_qtd = obs_counts.max()
                    # Truncar se for muito longa
                    obs_display = obs_critica if len(str(obs_critica)) < 40 else str(obs_critica)[:37] + "..."
                    st.markdown(f'''
                    <div class="metric-card" style="border-left-color: #FF4B4B;">
                        <div class="metric-title">Observação Mais Crítica</div>
                        <div class="metric-value" style="font-size: 1.2rem; margin: 10px 0;">{obs_display}</div>
                        <div class="metric-subtitle">{obs_qtd} repetições</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    if st.button("🔍 Ver Detalhes", key="btn_obs", use_container_width=True):
                        show_details('Observação Mais Crítica', 'Observacao', obs_critica, df_filtered)
                else:
                    st.info("Sem dados de Observação")

        with col3:
            if 'Posicao' in df_filtered.columns:
                pos_counts = df_filtered['Posicao'].value_counts()
                if not pos_counts.empty:
                    pos_critica = pos_counts.idxmax()
                    pos_qtd = pos_counts.max()
                    pos_display = format_number(pos_critica)
                    st.markdown(f'''
                    <div class="metric-card" style="border-left-color: #FFA500;">
                        <div class="metric-title">Posição Mais Crítica</div>
                        <div class="metric-value">{pos_display}</div>
                        <div class="metric-subtitle">{pos_qtd} ocorrências</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    if st.button("🔍 Ver Detalhes", key="btn_pos", use_container_width=True):
                        show_details('Posição Mais Crítica', 'Posicao', pos_critica, df_filtered)
                else:
                    st.info("Sem dados de Posição")

        with col4:
            if 'Modulo' in df_filtered.columns:
                mod_counts = df_filtered['Modulo'].value_counts()
                if not mod_counts.empty:
                    mod_critico = mod_counts.idxmax()
                    mod_qtd = mod_counts.max()
                    mod_display = format_number(mod_critico)
                    st.markdown(f'''
                    <div class="metric-card" style="border-left-color: #9C27B0;">
                        <div class="metric-title">Módulo Mais Crítico</div>
                        <div class="metric-value">{mod_display}</div>
                        <div class="metric-subtitle">{mod_qtd} ocorrências</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    if st.button("🔍 Ver Detalhes", key="btn_mod", use_container_width=True):
                        show_details('Módulo Mais Crítico', 'Modulo', mod_critico, df_filtered)
                else:
                    st.info("Sem dados de Módulo")

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráficos
        st.markdown("### 📊 Análise Gráfica")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            if 'Piso' in df_filtered.columns:
                piso_df = df_filtered['Piso'].value_counts().reset_index()
                piso_df.columns = ['Piso', 'Ocorrências']
                piso_df['Piso'] = piso_df['Piso'].apply(format_number)
                
                fig_piso = go.Figure(data=[
                    go.Bar(
                        x=piso_df['Piso'], 
                        y=piso_df['Ocorrências'],
                        marker=dict(
                            color=piso_df['Ocorrências'],
                            colorscale='Teal',
                            line=dict(color='rgba(0, 196, 180, 1.0)', width=2)
                        ),
                        text=piso_df['Ocorrências'],
                        textposition='auto',
                        hoverinfo='x+y'
                    )
                ])
                fig_piso.update_layout(
                    title='Ocorrências por Piso',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    margin=dict(t=40, l=0, r=0, b=0)
                )
                fig_piso.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
                st.plotly_chart(fig_piso, use_container_width=True)
                
        with col_chart2:
            if 'Observacao' in df_filtered.columns:
                obs_top_df = df_filtered['Observacao'].value_counts().head(5).reset_index()
                obs_top_df.columns = ['Observação', 'Qtd']
                
                pulls = [0.1 if i == 0 else 0 for i in range(len(obs_top_df))]
                
                fig_obs = go.Figure(data=[
                    go.Pie(
                        labels=obs_top_df['Observação'], 
                        values=obs_top_df['Qtd'], 
                        hole=0.5,
                        pull=pulls,
                        marker=dict(
                            colors=px.colors.qualitative.Bold,
                            line=dict(color='#1E1E1E', width=3)
                        ),
                        textinfo='percent',
                        textposition='inside',
                        hoverinfo='label+percent+value'
                    )
                ])
                fig_obs.update_layout(
                    title='Top 5 Observações Mais Comuns',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    margin=dict(t=60, l=0, r=0, b=20),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )
                st.plotly_chart(fig_obs, use_container_width=True)


        # Tabela de Dados
        st.markdown("### 📋 Tabela de Dados Detalhada")
        df_display = df_filtered.copy()
        if 'Data' in df_display.columns and pd.api.types.is_datetime64_any_dtype(df_display['Data']):
            df_display['Data'] = df_display['Data'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_display, use_container_width=True, hide_index=True)
