import streamlit as st
import pandas as pd

# --- CONTEÚDO PRINCIPAL DO APP ---

st.title("📚 Referências do Projeto usados durante a pesquisa")


# --- DEFINIÇÃO DA FUNÇÃO DA TABELA ---

def criar_tabela_referencias():
    """Cria e exibe a tabela de mapeamento de referências no Streamlit."""
    
    # Dados do mapeamento
    data = {
        'Tópico/Arquivo': [
            'World Energy Consuption',
            'Energy_consumption',
            'Capacidade_geração',
            'Fatores_emissao',
            'Fatores de emissão simples ajustado - Cálculos de 2024 - FE_simplesajustado_2024',
            'Inventário_2025_janset',
            'Tabelas de emissões do MCTI inventario_2025_janset',
            'Consumo_anual_MWh',
            'Dados_abertos_consumo_mensal',
            'Emissões_anuais_2006_2024'
        ],
        'Referência': [
            'https://iea.blob.core.windows.net/assets/601eaec9-ba91-4623-819b-4ded331ec9e8/EnergyandAI.pdf',
            'https://datacenters.lbl.gov/sites/default/files/Masanet_et_al_Science_2020.full_.pdf',
            'https://www.datacentermap.com/brazil/',
            'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao',
            'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao',
            'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/central-de-conteudo/noti/mcti-publica-fatores-de-emissao-de-co2-da-geracao-de-energia-eletrica-no-brasil-para-2025',
            'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/cgcl/paginas/NT_FE_jun25.pdf',
            'Datacenter Map',
            'Dados mensais de consumo energético da EPE', 
            'SIRENE/MCTI'      
        ]
    }

    df = pd.DataFrame(data)

    st.header("Mapeamento de Arquivos/Tópicos para Referências")
    # Usa st.dataframe para exibir a tabela formatada
    st.dataframe(df, use_container_width=True) 

# --- CHAMADA DA FUNÇÃO ---

# Esta linha é crucial. Ela executa o código dentro da função.
criar_tabela_referencias()