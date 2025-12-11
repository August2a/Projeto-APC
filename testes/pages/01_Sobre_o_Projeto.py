import streamlit as st

st.set_page_config(page_title="Sobre o Projeto", layout="wide")

st.title("Sobre o Projeto – Estimador de Emissões de CO₂ de Data Centers no Brasil")

st.markdown("""
## Visão Geral

Este projeto tem como objetivo desenvolver um **estimador exploratório** capaz de calcular e projetar as 
emissões operacionais de CO₂ associadas ao consumo de energia elétrica dos **data centers no Brasil**.

A proposta faz parte da disciplina **APC – Algoritmos e Programação de Computadores**, integrando conceitos 
de tratamento de dados, modelagem matemática, previsão temporal e visualização interativa.

---

## Objetivos Principais

1. **Carregar e tratar dados reais** de consumo energético do Brasil (2006–2024).  
2. Aplicar **fatores oficiais de emissão (tCO₂/MWh)** para converter consumo em emissões.  
3. Estimar a **participação dos data centers no consumo total**, utilizando curvas de crescimento suave.  
4. Calcular:
   - Consumo anual dos DCs (MWh)  
   - Emissões anuais dos DCs (tCO₂)  
5. Criar **cenários de projeção**:
   - Base  
   - Otimista  
   - Pessimista  
6. Utilizar **Facebook Prophet** para prever a evolução das emissões até um ano escolhido.  
7. Apresentar resultados em um **dashboard interativo** usando **Streamlit + Plotly**.

---

## Metodologia Resumida

### 1. Dados Utilizados

- **Fatores de emissão do MCTI** (Inventário Nacional de Emissões) → tCO₂ por MWh.  
- **Consumo mensal de energia** (EPE) → agregado para consumo anual.  
- Participação estimada dos data centers:
  - 2006 → 0,3%  
  - 2024 → 1,7%  
  - Ano futuro escolhido → valor definido pelo usuário  
  → interpolação suave entre esses marcos.

---

### 2. Processamento dos Dados

- Tratamento de CSV e Excel.
- Conversão de datas e padronização de tipos.
- Agregação de consumo mensal → anual.
- Cálculo de emissões totais.
- Segmentação das emissões atribuídas aos DCs.

---

### 3. Modelo de Previsão

Usamos o **Prophet** para modelar a série histórica de emissões totais, prevendo valores até o ano solicitado.
Essas projeções alimentam o cálculo dos cenários dos data centers.

---

### 4. Visualização Interativa

O app permite:

- Selecionar ano final da projeção  
- Ajustar a participação dos DCs  
- Ativar/desativar emissões e consumo  
- Comparar cenários  
- Analisar histórico e projeção com dois eixos (tCO₂ e MWh)

A visualização é feita com **Plotly**, garantindo:
- Interatividade  
- Hover detalhado  
- Zoom  
- Exportação  

---

## Equipe

- Diego Paz Oliveira Morais  
- Sergio Augusto de Araújo  
- Ary Paulo Wiese Neto  
- Pedro Henrique Sousa dos Santos  

Monitor:
- Gabriel Brito de França

---

## Conclusão

O estimador demonstra como o crescimento dos data centers pode pressionar o perfil de emissões do setor elétrico brasileiro, permitindo visualizar cenários futuros realistas, conservadores e agressivos.

O projeto integra habilidades essenciais:
- Ciência de dados  
- Modelagem temporal  
- Interpretação ambiental  
- Desenvolvimento web interativo  

Tornando-se uma ferramenta experimental útil tanto para estudo quanto para análises exploratórias reais.

""")
