import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from prophet import Prophet

# --- Configuração da Página ---
st.set_page_config(page_title="Análise de Energia", layout="wide")

st.title("⚡ Dashboard de de Energia Global")

# --- 1. Carregamento de Dados com Cache ---
# O @st.cache_data faz com que o arquivo não seja recarregado a cada clique, melhorando a performance
@st.cache_data
def load_data():
    # Tenta carregar do caminho local especificado
    try:
        df = pd.read_csv('./input/World Energy Consumption.csv')
        return df
    except FileNotFoundError:
        st.error("Arquivo './input/World Energy Consumption.csv' não encontrado.")
        return None

df = load_data()

if df is None:
    st.error("Erro: Arquivo './input/World Energy Consumption.csv' não encontrado.")
    st.stop()

# --- ANÁLISE GLOBAL ---
st.header("1. Consumo Global")

global_energy = df.groupby('year')['primary_energy_consumption'].sum().reset_index()

# Criar a figura explicitamente para o Streamlit
fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.lineplot(data=global_energy, x='year', y='primary_energy_consumption', ax=ax1)
ax1.set_title('Consumo global de energia primária ao longo do tempo')
ax1.set_xlabel('Ano')
ax1.set_ylabel('Consumo de energia (TWh)')
ax1.grid(True)

# Exibir no Streamlit
st.pyplot(fig1)

st.markdown("---")

# --- ANÁLISE POR PAÍS COM PROPHET ---
st.header("2. Previsão por País (Prophet)")

# Interatividade: Escolha o país
lista_paises = df['country'].unique()
# Tenta definir o padrão como Brazil, se existir
index_padrao = list(lista_paises).index('Brazil') if 'Brazil' in lista_paises else 0
pais = st.selectbox("Selecione o país para análise:", lista_paises, index=index_padrao)

# Filtra o país
dados_pais = df[df['country'] == pais]

# Verifica se há dados suficientes
if dados_pais['primary_energy_consumption'].sum() == 0:
    st.warning(f"O país {pais} não possui dados de consumo válidos.")
else:
    # Lógica original de tratamento de dados
    primeiro_ano_valido = dados_pais.loc[
        dados_pais['primary_energy_consumption'] > 0, 'year'
    ].min()

    st.write(f"**Primeiro ano com consumo > 0:** {primeiro_ano_valido}")

    dados_validos = dados_pais[
        dados_pais['year'] >= primeiro_ano_valido
    ][['year', 'primary_energy_consumption']].dropna()

    # Preparação para o Prophet
    dados_validos = dados_validos.rename(columns={'year': 'ds', 'primary_energy_consumption': 'y'})
    dados_validos['ds'] = pd.to_datetime(dados_validos['ds'], format='%Y')

    # Treinamento do Modelo (com spinner de carregamento)
    with st.spinner('Treinando o modelo Prophet...'):
        modelo = Prophet()
        modelo.fit(dados_validos)

        # Gera datas futuras (20 anos)
        # Nota: freq='YE' é para pandas novos. Se der erro, use freq='Y'
        datas_futuras = modelo.make_future_dataframe(periods=20, freq='YE') 
        previsoes = modelo.predict(datas_futuras)

    # Plot 1: Componentes do Prophet
    st.subheader("Tendência Gerada pelo Prophet")
    fig2 = modelo.plot(previsoes)
    st.pyplot(fig2)

    # Plot 2: Comparação Real vs Futuro (Seu gráfico customizado)
    st.subheader("Visualização: Histórico vs Previsão")
    
    ultimo_ano = dados_validos['ds'].max().year
    
    # Criando gráfico customizado
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    
    # Dados reais
    ax3.plot(dados_validos['ds'], dados_validos['y'], label='Dados reais', linewidth=2)
    
    # Dados previstos (filtrando apenas o futuro para destacar)
    dados_futuros = previsoes[previsoes['ds'].dt.year > ultimo_ano]
    ax3.plot(dados_futuros['ds'], dados_futuros['yhat'], label='Previsão', linestyle='--', color='red')
    
    ax3.set_title(f'Previsão do consumo de energia primária - {pais}')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    st.pyplot(fig3)
    
    # Tabela com os dados previstos
    with st.expander("Ver tabela de dados previstos"):
        st.dataframe(dados_futuros[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head(10))
