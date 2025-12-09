import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from prophet import Prophet

# ==============================
# CONFIGURAÇÃO BÁSICA DO APP
# ==============================
st.set_page_config(
    page_title="Estimador de Emissões de CO₂ de Data Centers",
    layout="wide"
)

st.title("🌍 Estimador de Emissões de CO₂ de Data Centers no Brasil")
st.markdown(
    """
    Projeto APC – Estimando emissões de CO₂ associadas ao consumo elétrico de *data centers* no Brasil.

    Use os controles ao lado para:
    - escolher até que ano projetar as emissões;
    - definir o cenário de participação dos data centers (por % ou por número/consumo médio);
    - personalizar o gráfico final.
    """
)

# ==============================
# 1) CARREGAR DADOS
# ==============================

@st.cache_data
def load_df_final():
    """
    Lê os CSVs de fatores de emissão e consumo anual
    e monta o df_final com emissões totais.
    """
    fatores = pd.read_csv("input/fatores_emissao.csv")
    consumo = pd.read_csv("input/consumo_anual_MWh.csv")

    fatores["ano"] = fatores["ano"].astype(int)
    consumo["ano"] = consumo["ano"].astype(int)

    df_final = consumo.merge(fatores, on="ano", how="inner")
    df_final["emissao_tCO2"] = (
        df_final["consumo_anual_MWh"] * df_final["fator_emissao_tCO2_MWh"]
    )

    return df_final

df_final = load_df_final()

# Garantir ordenação
df_final = df_final.sort_values("ano").reset_index(drop=True)

# ==============================
# 2) PREPARAR SÉRIE PARA PROPHET
# ==============================

@st.cache_data
def prepare_prophet_series(df_final: pd.DataFrame):
    df = df_final.copy()
    df_prophet = df.rename(columns={
        "ano": "ds",
        "emissao_tCO2": "y"
    })
    df_prophet["ds"] = pd.to_datetime(df_prophet["ds"].astype(str) + "-12-31")
    ano_inicio = df_prophet["ds"].dt.year.min()
    ultimo_ano_hist = df_prophet["ds"].dt.year.max()
    return df_prophet, ano_inicio, ultimo_ano_hist

df_prophet, ano_inicio, ultimo_ano_hist = prepare_prophet_series(df_final)

@st.cache_resource
def get_prophet_model(df_prophet: pd.DataFrame):
    model = Prophet()
    model.fit(df_prophet)
    return model

model = get_prophet_model(df_prophet)

# ==============================
# 3) SIDEBAR – PARÂMETROS
# ==============================

st.sidebar.header("⚙️ Parâmetros da previsão")

ano_fim = st.sidebar.slider(
    "Ano final da projeção",
    min_value=int(ultimo_ano_hist),
    max_value=2050,
    value=min(2030, int(ultimo_ano_hist) + 10),
    step=1,
)

modo_dc = st.sidebar.radio(
    "Cenário dos data centers",
    options=[
        "Por percentual da emissão total",
        "Por número de DCs e consumo médio"
    ],
    index=0
)

# parâmetros fixos conhecidos
ano_ref_2024 = 2024
participacao_inicio = 0.003   # 0,3% em 2006 (hipótese)
participacao_2024   = 0.017   # 1,7% em 2024 (Brasscom)

if modo_dc == "Por percentual da emissão total":
    participacao_final_percent = st.sidebar.number_input(
        f"Participação dos DCs em {ano_fim} (%):",
        min_value=0.0,
        max_value=100.0,
        value=3.6,
        step=0.1,
        help="Valor alvo de participação dos data centers no ano final da projeção."
    )
    participacao_final = participacao_final_percent / 100.0
else:
    st.sidebar.markdown("### Número de data centers")
    n_dc_inicio = st.sidebar.number_input(
        f"Nº de DCs em {ano_inicio}:",
        min_value=0,
        value=50,
        step=1
    )
    n_dc_fim = st.sidebar.number_input(
        f"Nº de DCs em {ano_fim}:",
        min_value=0,
        value=200,
        step=1
    )

    st.sidebar.markdown("### Consumo médio anual por DC")
    cons_dc_inicio = st.sidebar.number_input(
        f"Consumo médio em {ano_inicio} (MWh/ano por DC):",
        min_value=0.0,
        value=5000.0,
        step=100.0
    )
    cons_dc_fim = st.sidebar.number_input(
        f"Consumo médio em {ano_fim} (MWh/ano por DC):",
        min_value=0.0,
        value=12000.0,
        step=100.0
    )

# ==============================
# 4) PREVER EMISSÕES TOTAIS
# ==============================

periods = ano_fim - ultimo_ano_hist

future = model.make_future_dataframe(
    periods=periods,
    freq="YE"
)
forecast = model.predict(future)

# Série única real + prevista (emissão total)
previsao = forecast[["ds", "yhat"]].copy()
previsao["ano"] = previsao["ds"].dt.year
previsao = previsao[previsao["ano"].between(ano_inicio, ano_fim)].copy()

hist = df_final[["ano", "emissao_tCO2"]].copy()
hist = hist[hist["ano"].between(ano_inicio, ultimo_ano_hist)].copy()

previsao = previsao.merge(hist, on="ano", how="left")
previsao["emissao_total_tCO2"] = previsao["emissao_tCO2"].fillna(previsao["yhat"])
previsao = previsao.sort_values("ano").reset_index(drop=True)

anos = previsao["ano"].values.astype(float)

# ==============================
# 5) CENÁRIOS PARA OS DATA CENTERS
# ==============================

if modo_dc == "Por percentual da emissão total":
    # ------- MODO 1: POR PERCENTUAL -------
    participacao = np.zeros_like(anos, dtype=float)

    # 2006 → 2024: 0,3% → 1,7%
    mask_ate_2024 = anos <= ano_ref_2024
    denom1 = ano_ref_2024 - ano_inicio

    participacao[mask_ate_2024] = participacao_inicio + (
        (participacao_2024 - participacao_inicio)
        * (anos[mask_ate_2024] - ano_inicio)
        / denom1
    )

    # 2024 → ano_fim: 1,7% → participacao_final
    mask_depois_2024 = anos > ano_ref_2024
    if ano_fim > ano_ref_2024 and mask_depois_2024.any():
        denom2 = ano_fim - ano_ref_2024
        participacao[mask_depois_2024] = participacao_2024 + (
            (participacao_final - participacao_2024)
            * (anos[mask_depois_2024] - ano_ref_2024)
            / denom2
        )

    previsao["participacao_DC"] = participacao
    previsao["emissao_DC_tCO2"] = (
        previsao["emissao_total_tCO2"] * previsao["participacao_DC"]
    )

else:
    # ------- MODO 2: POR CONSUMO -------
    st.markdown(
        """
        **Modo consumo:** emissões dos DCs são calculadas a partir do número de data centers
        e do consumo médio anual por DC, multiplicado pelo fator de emissão (tCO₂/MWh).
        """
    )

    previsao["n_datacenters"] = np.interp(
        anos,
        [ano_inicio, ano_fim],
        [n_dc_inicio, n_dc_fim]
    )

    previsao["consumo_medio_DC_MWh"] = np.interp(
        anos,
        [ano_inicio, ano_fim],
        [cons_dc_inicio, cons_dc_fim]
    )

    previsao["consumo_DC_MWh"] = (
        previsao["n_datacenters"] * previsao["consumo_medio_DC_MWh"]
    )

    fatores = df_final[["ano", "fator_emissao_tCO2_MWh"]].drop_duplicates()
    fatores = fatores[fatores["ano"].between(ano_inicio, ultimo_ano_hist)]
    previsao = previsao.merge(fatores, on="ano", how="left")

    previsao["fator_emissao_tCO2_MWh"] = (
        previsao["fator_emissao_tCO2_MWh"].ffill().bfill()
    )

    previsao["emissao_DC_tCO2"] = (
        previsao["consumo_DC_MWh"] * previsao["fator_emissao_tCO2_MWh"]
    )

    previsao["participacao_DC"] = (
        previsao["emissao_DC_tCO2"] / previsao["emissao_total_tCO2"]
    )

# separar real x previsto para DCs
df_real_dc = previsao[previsao["ano"] <= ultimo_ano_hist].copy()
df_prev_dc = previsao[previsao["ano"] > ultimo_ano_hist].copy()

# ==============================
# 6) OPÇÕES DO GRÁFICO FINAL
# ==============================

st.subheader("📊 Gráfico personalizado")

col_opts1, col_opts2 = st.columns(2)

with col_opts1:
    show_total = st.checkbox(
        "Mostrar emissões totais de CO₂",
        value=True
    )
    show_dc = st.checkbox(
        "Mostrar emissões de CO₂ dos data centers",
        value=True
    )

with col_opts2:
    show_part = st.checkbox(
        "Mostrar participação dos DCs (%)",
        value=False
    )
    show_cons = st.checkbox(
        "Mostrar consumo total de energia (histórico, TWh)",
        value=False
    )

# ==============================
# 7) PLOT DO GRÁFICO
# ==============================

fig, ax1 = plt.subplots(figsize=(12, 6))

# Eixo principal: emissões (tCO2)
lines = []
labels = []

if show_total:
    l1, = ax1.plot(
        previsao["ano"],
        previsao["emissao_total_tCO2"],
        marker="o",
        linewidth=2,
        label="Emissões totais (tCO₂)"
    )
    lines.append(l1)
    labels.append(l1.get_label())

if show_dc:
    l2, = ax1.plot(
        previsao["ano"],
        previsao["emissao_DC_tCO2"],
        marker="o",
        linestyle="--",
        linewidth=2,
        label="Emissões dos data centers (tCO₂)"
    )
    lines.append(l2)
    labels.append(l2.get_label())

ax1.set_xlabel("Ano")
ax1.set_ylabel("Emissões (tCO₂)")
ax1.grid(True, linestyle="--", alpha=0.6)

# Eixo secundário (direita): participação (%) e/ou consumo (TWh)
if show_part or show_cons:
    ax2 = ax1.twinx()

    if show_part:
        l3, = ax2.plot(
            previsao["ano"],
            previsao["participacao_DC"] * 100.0,
            marker="s",
            linestyle=":",
            linewidth=2,
            label="Participação dos DCs (%)"
        )
        lines.append(l3)
        labels.append(l3.get_label())

    if show_cons:
        # consumo total só existe historicamente
        df_cons = df_final[["ano", "consumo_anual_MWh"]].copy()
        df_cons["consumo_TWh"] = df_cons["consumo_anual_MWh"] / 1e6  # MWh → TWh
        l4, = ax2.plot(
            df_cons["ano"],
            df_cons["consumo_TWh"],
            marker="^",
            linestyle="-.",
            linewidth=1.8,
            label="Consumo total (TWh, histórico)"
        )
        lines.append(l4)
        labels.append(l4.get_label())

    ax2.set_ylabel("Participação (%) / Consumo (TWh)")
else:
    ax2 = None

ax1.set_xticks(list(range(int(ano_inicio), int(ano_fim) + 1)))
plt.setp(ax1.get_xticklabels(), rotation=45)

if lines:
    ax1.legend(lines, labels, loc="upper left")

titulo_modo = "Percentual" if modo_dc.startswith("Por percentual") else "Consumo"
plt.title(f"Emissões de CO₂ e Cenário de Data Centers ({titulo_modo})")

plt.tight_layout()
st.pyplot(fig)

# ==============================
# 8) TABELA DE RESULTADOS
# ==============================

with st.expander("🔍 Ver tabela de resultados (previsão completa)"):
    st.dataframe(
        previsao[
            [
                "ano",
                "emissao_total_tCO2",
                "emissao_DC_tCO2",
                "participacao_DC"
            ] + (
                ["n_datacenters", "consumo_medio_DC_MWh", "consumo_DC_MWh"]
                if "n_datacenters" in previsao.columns
                else []
            )
        ]
    )

st.markdown(
    """
    💡 Dica: Para rodar este app localmente, salve este código como `app.py` e use:

    ```bash
    streamlit run app.py
    ```
    """
)
