import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da Página
st.set_page_config(
    page_title="Raio-X do Desmatamento no Brasil",
    page_icon="🌳",
    layout="wide"
)

# --- CABEÇALHO / STORYTELLING: INTRODUÇÃO ---
st.title("🌳 Storytelling: Análise do Desmatamento no Brasil")
st.markdown("""
Este painel interativo foi desenvolvido para explorar dados públicos sobre o desmatamento, 
permitindo entender **de onde vieram os dados**, **como foram tratados** e quais são os principais 
insights geográficos e temporais.
""")

# Carregamento dos dados
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("data/desmatamento_processado.csv")
    except:
        # Dados de exemplo caso o arquivo CSV ainda não esteja na pasta data/
        data = {
            'ano': [2021, 2021, 2022, 2022, 2023, 2023],
            'estado': ['Pará', 'Mato Grosso', 'Pará', 'Amazonas', 'Pará', 'Mato Grosso'],
            'bioma': ['Amazônia', 'Cerrado', 'Amazônia', 'Amazônia', 'Amazônia', 'Cerrado'],
            'area_km2': [5200, 3100, 4800, 2500, 4100, 2900]
        }
        df = pd.DataFrame(data)
    return df

df = carregar_dados()

# --- SEÇÃO 1: A JORNADA DOS DADOS (ORIGEM E LIMPEZA) ---
with st.expander("🔍 Entenda a Origem e a Limpeza dos Dados (Clique para expandir)", expanded=False):
    st.markdown("""
    * **Fonte dos Dados:** Dados abertos governamentais / institutos de monitoramento ambiental (ex: INPE/PRODES).
    * **Etapa de Coleta:** Obtenção de arquivos brutos contendo registros históricos por ano e unidade federativa.
    * **Limpeza e Tratamento aplicados:**
        1. *Remoção de valores nulos (dropna):* Linhas sem registro de área ou estado foram descartadas para evitar distorções.
        2. *Padronização:* Conversão de nomes de estados para formato padronizado e renomeação de colunas para facilitar a leitura.
        3. *Filtro inicial:* Seleção apenas dos registros com área maior que zero.
    """)
    st.write(f"📊 **Dimensões finais da base tratada:** {df.shape[0]} linhas e {df.shape[1]} colunas.")

st.markdown("---")

# --- ELEMENTOS INTERATIVOS (Filtros na Barra Lateral) ---
st.sidebar.header("🎛️ Filtros Dinâmicos")

estados_disponiveis = df['estado'].unique().tolist()
estado_escolhido = st.sidebar.selectbox("Selecione o Estado:", options=["Todos"] + estados_disponiveis)

if 'ano' in df.columns:
    anos = sorted(df['ano'].unique())
    ano_min, ano_max = int(min(anos)), int(max(anos))
    ano_selecionado = st.sidebar.slider("Filtrar por Ano:", min_value=ano_min, max_value=ano_max, value=(ano_min, ano_max))
else:
    ano_selecionado = (2020, 2023)

df_filtrado = df.copy()
if estado_escolhido != "Todos":
    df_filtrado = df_filtrado[df_filtrado['estado'] == estado_escolhido]

if 'ano' in df.columns:
    df_filtrado = df_filtrado[(df_filtrado['ano'] >= ano_selecionado[0]) & (df_filtrado['ano'] <= ano_selecionado[1])]

# --- KPIs (Métricas de Destaque) ---
st.subheader("📈 Indicadores Principais")
col1, col2, col3 = st.columns(3)

total_area = df_filtrado['area_km2'].sum() if 'area_km2' in df_filtrado.columns else 0
media_area = df_filtrado['area_km2'].mean() if 'area_km2' in df_filtrado.columns else 0
total_registros = len(df_filtrado)

col1.metric("Área Total Mapeada (km²)", f"{total_area:,.1f}")
col2.metric("Média por Registro (km²)", f"{media_area:,.1f}")
col3.metric("Total de Registros Filtrados", total_registros)

# --- VISUALIZAÇÕES E GRÁFICOS ---
st.markdown("### 📊 Análise Visual")

if not df_filtrado.empty and 'area_km2' in df_filtrado.columns:
    fig, ax = plt.subplots(figsize=(10, 4))
    df_agrupado = df_filtrado.groupby('estado')['area_km2'].sum().reset_index()
    ax.bar(df_agrupado['estado'], df_agrupado['area_km2'], color='#2ca02c')
    ax.set_title("Área Desmatada por Estado (km²)")
    ax.set_xlabel("Estado")
    ax.set_ylabel("km²")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")
