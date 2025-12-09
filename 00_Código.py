import streamlit as st

st.title("Como Rodar o Projeto")

st.write("""
         
Este projeto calcula e projeta as emissões operacionais de CO₂ associadas ao consumo elétrico de Data Centers no Brasil, utilizando dados reais e modelos de previsão.

Desenvolvido como parte da disciplina APC – Algoritmos e Programação de Computadores.
         
https://github.com/August2a/Projeto-APC

---

## 1. Pré-requisitos

Instale:

Python 3.10+  
Pip atualizado  
Dependências:

```bash
pip install streamlit prophet pandas plotly numpy openpyxl
```

Ou no Windows via Conda:

```bash
conda install -c conda-forge prophet
```

---

## 2. Estrutura de Pastas

```
projeto/
 ├── app.py
 ├── input/
 │   ├── fatores_emissao.csv
 │   └── Dados_abertos_Consumo_Mensal.xlsx
 ├── pages/
 │   ├── 00_Código.py
 │   ├── 01_Dashboard.py
 │   └── 02_Referências
 └── README.md
```

Regras importantes:

- A pasta deve se chamar pages
- Apenas app.py deve conter st.set_page_config()
- Páginas dentro de pages não devem chamar set_page_config()
- Execute sempre via:

```bash
streamlit run app.py
```

---

## 3. Como Rodar

Execute no terminal:

```bash
streamlit run app.py
```

Não execute diretamente páginas internas como:

```bash
streamlit run pages/01_Sobre_o_Projeto.py
```

Isso desativa o modo multipágina.

---

## 4. Criando Novas Páginas

Para adicionar uma nova página ao menu lateral:

1. Crie um arquivo dentro de pages/
2. Exemplo:

```
pages/02_Modelagem.py
```

3. Conteúdo mínimo:

```python
import streamlit as st
st.title("Modelagem de Dados")
st.write("Conteúdo da página…")
```

O Streamlit adiciona automaticamente ao menu lateral.

---

## 5. Dados Utilizados

### fatores_emissao.csv
- Fatores anuais de emissão (tCO₂/MWh)
- Fonte: MCTI – Inventário Nacional

### Dados_abertos_Consumo_Mensal.xlsx
- Dados mensais de consumo energético da EPE
- O sistema converte para consumo anual agregado

---

## 6. Funcionamento do Sistema

O aplicativo realiza:

- Tratamento e padronização dos dados
- Conversão do consumo total para emissões totais
- Curva suave da participação estimada dos Data Centers
  - 2006: 0,3%
  - 2024: 1,7%
  - Ano final: definido pelo usuário
- Geração de três cenários:
  - Base
  - Otimista
  - Pessimista
- Previsão com o modelo Prophet
- Construção de gráfico interativo com Plotly
  - Eixo esquerdo: Emissões (tCO₂)
  - Eixo direito: Consumo (MWh)
  - Histórico contínuo
  - Cenários sobrepostos
  - Interatividade (hover, zoom, exportação)

Além disso, a interface permite configurar:
- Ano final da projeção
- Participação futura dos Data Centers
- Ativar ou desativar curvas de consumo e emissões

---

## 7. Visualização

O dashboard apresenta:

- Histórico real (2006–2024)
- Projeções baseadas no Prophet
- Curva suavizada da participação dos Data Centers
- Comparação entre cenários
- Dois eixos Y independentes (tCO₂ e MWh)
- Gráficos interativos com Plotly

---

## 8. Considerações Finais

Este projeto combina ciência de dados, modelagem preditiva, análise ambiental e desenvolvimento web, oferecendo uma ferramenta prática para explorar o impacto dos Data Centers no consumo energético brasileiro.
""")
