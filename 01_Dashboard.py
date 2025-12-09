#############################################################
# Estimador de Emissões de CO₂ de Data Centers no Brasil.
#############################################################

import numpy as np
import pandas as pd
import streamlit as st
from prophet import Prophet
import plotly.graph_objects as go

# Config padrão do app: página larga pra aproveitar o espaço dos gráficos
st.set_page_config(
    page_title="Estimador CO₂ – Data Centers",
    layout="wide"
)

st.title("Estimador de Emissões de CO₂ de Data Centers no Brasil")


#############################################################
# 1) CARREGAR ARQUIVOS
# Aqui só deixamos em funções com cache pra não ficar relendo
# arquivo toda hora que o usuário mexe nos sliders.
#############################################################

@st.cache_data
def carregar_fatores(path="input/fatores_emissao.csv"):
    # Fatores de emissão anuais (tCO₂/MWh)
    df = pd.read_csv(path)
    df["ano"] = df["ano"].astype(int)
    return df

@st.cache_data
def carregar_consumo(path="input/Dados_abertos_Consumo_Mensal.xlsx"):
    # Consumo mensal → agregamos por ano para simplificar o modelo
    df = pd.read_excel(path, dtype={"Data": str})
    df["Consumo"] = df["Consumo"].astype(float)
    df["ano"] = df["Data"].str[:4].astype(int)

    # Mantemos só o recorte da série que faz sentido com os fatores
    df = df[df["ano"].between(2006, 2024)]

    # Soma do consumo de todos os meses do ano
    df_anual = df.groupby("ano")["Consumo"].sum().reset_index()
    df_anual = df_anual.rename(columns={"Consumo": "consumo_total_MWh"})
    return df_anual

fatores = carregar_fatores()
consumo_anual = carregar_consumo()


#############################################################
# 2) CÁLCULO DAS EMISSÕES HISTÓRICAS
# Aqui ainda não falamos de data centers, é o sistema elétrico
# inteiro (malha nacional).
#############################################################

@st.cache_data
def calcular_emissoes(consumo, fatores):
    # Junta consumo anual com o fator de emissão daquele ano
    df = consumo.merge(fatores, on="ano", how="inner")
    # Emissão total do sistema elétrico
    df["emissao_total_tCO2"] = df["consumo_total_MWh"] * df["fator_emissao_tCO2_MWh"]
    return df

df_final = calcular_emissoes(consumo_anual, fatores)

ano_inicio = df_final["ano"].min()
ultimo_ano_hist = df_final["ano"].max()


#############################################################
# 3) PREPARAÇÃO DO PROPHET
# O Prophet exige uma coluna ds (datas) e y (série alvo).
# A ideia é prever a emissão total do sistema, depois recortar
# só a parte dos DCs.
#############################################################

@st.cache_data
def preparar_prophet(df):
    p = df.rename(columns={"ano": "ds", "emissao_total_tCO2": "y"})
    # Jogamos tudo para 31/12 de cada ano, só pra ter uma data válida
    p["ds"] = pd.to_datetime(p["ds"].astype(str) + "-12-31")
    return p

df_prophet = preparar_prophet(df_final)

@st.cache_resource
def treinar(df):
    # Modelo bem simples: só tendência, sem sazonalidade diária/semanal
    # porque estamos trabalhando com dados anuais.
    model = Prophet(
        growth="linear",
        daily_seasonality=False,
        weekly_seasonality=False,
        yearly_seasonality=False
    )
    model.fit(df)
    return model

model = treinar(df_prophet)


#############################################################
# 4) CONTROLES DO USUÁRIO – NA PÁGINA
#############################################################

st.markdown("### Configurações do Gráfico")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    # Até que ano queremos olhar o futuro?
    ano_fim = st.number_input(
        "Ano final da projeção:",
        min_value=ultimo_ano_hist,
        max_value=2050,
        value=2030,
        step=1
    )

with col2:
    # Quanto dos dados centros vão representar no consumo nesse ano final?
    # Usamos esse valor como alvo da curva suave.
    participacao_final = st.number_input(
        f"Participação dos DCs em {ano_fim} (% do consumo):",
        min_value=0.0,
        max_value=100.0,
        value=3.6,
        step=0.1
    ) / 100  # já convertemos pra fração

with col3:
    # Liga/desliga o que aparece no gráfico, pra não ficar poluído
    st.write("Ativar no gráfico:")
    show_emissao = st.checkbox("Emissões (tCO₂)", True)
    show_consumo = st.checkbox("Consumo (MWh)", True)


#############################################################
# 5) PREVISÃO USANDO PROPHET
#############################################################

periods = ano_fim - ultimo_ano_hist
future = model.make_future_dataframe(periods=periods, freq="YE")
forecast = model.predict(future)

previsao = forecast[["ds", "yhat"]].copy()
previsao["ano"] = previsao["ds"].dt.year

# Mantemos de 2006 até o ano final escolhido
previsao = previsao[previsao["ano"].between(ano_inicio, ano_fim)]

# Trazemos junto a série histórica de consumo e emissões reais
previsao = previsao.merge(
    df_final[["ano", "consumo_total_MWh", "emissao_total_tCO2"]],
    on="ano", how="left"
)

# Onde não tem dado real, usamos o valor previsto pelo Prophet
previsao["emissao_total_tCO2"] = previsao["emissao_total_tCO2"].fillna(previsao["yhat"])

# Consumo elétrico: para frente, mantemos a última observação
# (poderíamos prever também, mas aqui priorizamos simplicidade).
previsao["consumo_total_MWh"] = previsao["consumo_total_MWh"].ffill()

anos = previsao["ano"].values.astype(float)


#############################################################
# 6) CURVA SUAVE
# Curva de participação dos DCs ao longo do tempo:
# - começa baixa, em 2006 bate 0,3% (valor estimado),
# - em 2024 bate 1,7% (dado Brasscom),
# - e vai até o valor que o usuário escolheu no ano final.
#############################################################

def curva_suave(anos, alvo):
    return np.interp(
        anos,
        [ano_inicio, 2024, ano_fim],
        [0.003, 0.017, alvo]  # 0,3% em 2006 → 1,7% em 2024 → alvo no futuro
    )


#############################################################
# 7) GERAR TRÊS CENÁRIOS
# Base: valor informado
# Otimista: menor participação (DCs mais eficientes / menos crescimento)
# Pessimista: maior participação (explosão de DCs)
#############################################################

cenarios = {
    "Base": participacao_final,
    "Otimista": participacao_final * 0.7,
    "Pessimista": min(1.0, participacao_final * 1.3)  # nunca passa de 100%
}

cenarios_detalhados = []

for nome, alvo in cenarios.items():

    # Começamos de uma cópia da previsão "macro" (malha inteira)
    df_c = previsao.copy()
    df_c["cenario"] = nome

    # Para cada cenário, geramos uma curva própria de participação
    df_c["participacao_DC"] = curva_suave(anos, alvo)

    # Consumo dos DCs = consumo total * participação da curva
    df_c["consumo_DC_MWh"] = df_c["consumo_total_MWh"] * df_c["participacao_DC"]

    # Precisamos novamente do fator de emissão para calcular só os DCs
    df_c = df_c.merge(fatores, on="ano", how="left")
    df_c["fator_emissao_tCO2_MWh"] = df_c["fator_emissao_tCO2_MWh"].ffill()

    # Emissão dos DCs = consumo dos DCs * fator de emissão
    df_c["emissao_DC_tCO2"] = (
        df_c["consumo_DC_MWh"] * df_c["fator_emissao_tCO2_MWh"]
    )

    cenarios_detalhados.append(df_c)

# Junta tudo em um único DataFrame para facilitar o plot
df_plot = pd.concat(cenarios_detalhados, ignore_index=True)

# Série histórica "consolidada" dos DCs (pegamos o primeiro cenário só pra ter base),
# porque até 2024 todos usam a mesma base de fatores e consumo.
df_hist = df_plot[df_plot["ano"] <= ultimo_ano_hist].groupby("ano").first().reset_index()


#############################################################
# 8) GRÁFICO FINAL – HISTÓRICO + CENÁRIOS, DOIS EIXOS Y
#############################################################

st.markdown("### Gráfico – Histórico e Cenários")

fig = go.Figure()

# ======================================================================
# 1) HISTÓRICO – aparece ou não conforme o usuário marcou as opções
# ======================================================================

# Emissões históricas dos DCs
if show_emissao:
    fig.add_trace(go.Scatter(
        x=df_hist["ano"],
        y=df_hist["emissao_DC_tCO2"],
        mode="lines+markers",
        name="Histórico – Emissões",
        line=dict(color="#FFA500", width=4),
        marker=dict(color="#FFA500"),
        yaxis="y"  # eixo de emissões
    ))

# Consumo histórico dos DCs
if show_consumo:
    fig.add_trace(go.Scatter(
        x=df_hist["ano"],
        y=df_hist["consumo_DC_MWh"],
        mode="lines+markers",
        name="Histórico – Consumo",
        line=dict(color="#00CED1", width=4, dash="dot"),
        marker=dict(color="#00CED1"),
        yaxis="y2"  # eixo de consumo
    ))


# ======================================================================
# 2) CENÁRIOS – mesmos eixos, mas com cores diferentes por cenário
# ======================================================================

cores = {"Base": "#1f77b4", "Otimista": "#2ca02c", "Pessimista": "#d62728"}

for cenario in ["Base", "Otimista", "Pessimista"]:

    df_c = df_plot[df_plot["cenario"] == cenario].copy()

    # Conectamos o cenário com o último ponto histórico
    df_last = df_hist.tail(1).copy()
    df_last["cenario"] = cenario
    df_c = pd.concat([df_last, df_c[df_c["ano"] > ultimo_ano_hist]])

    if show_emissao:
        fig.add_trace(go.Scatter(
            x=df_c["ano"],
            y=df_c["emissao_DC_tCO2"],
            mode="lines+markers",
            name=f"Emissões – {cenario}",
            line=dict(color=cores[cenario], width=3),
            yaxis="y"
        ))

    if show_consumo:
        fig.add_trace(go.Scatter(
            x=df_c["ano"],
            y=df_c["consumo_DC_MWh"],
            mode="lines+markers",
            name=f"Consumo – {cenario}",
            line=dict(color=cores[cenario], width=2, dash="dot"),
            yaxis="y2"
        ))


# ======================================================================
# 3) LAYOUT FINAL – arruma eixos, legenda, título e deixa legível
# ======================================================================

fig.update_layout(
    template="plotly_white",
    hovermode="x unified",

    xaxis=dict(
        title="Ano",
        tickmode="linear",
        dtick=1
    ),

    yaxis=dict(
        title="Emissões (tCO₂)",
        showgrid=True,
        zeroline=True
    ),

    yaxis2=dict(
        title="Consumo (MWh)",
        overlaying="y",
        side="right",
        showgrid=False
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.06,
        xanchor="center",
        x=0.5
    ),

    font=dict(size=14),
    title="Histórico vs Cenários – Emissões e Consumo dos Data Centers"
)

st.plotly_chart(fig, width='stretch')


#############################################################
# 9) TABELA FINAL
# Por fim, mostramos a base consolidada pra quem quiser inspecionar
# números exatos ou exportar depois.
#############################################################

st.markdown("### Tabela de Resultados")

st.dataframe(df_plot[[
    "ano", "cenario", "consumo_DC_MWh", "emissao_DC_tCO2"
]])