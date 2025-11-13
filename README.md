# Estimador de Emissões de CO₂ de Data Centers no Brasil

Integrantes: 
- Diego Paz Oliveira Morais 
- Sergio Augusto de Araújo 
- Ary Paulo Wiese Neto 
- Pedro Henrique Sousa dos Santos 

Monitor:
- Gabriel Brito de França

## Objetivo geral 
Desenvolver um estimador exploratório (aplicação simples) que calcule emissões operacionais de CO₂ associadas ao consumo elétrico de data centers e aplicar o estimador a cenários do Brasil (e, quando útil, comparativamente a países vizinhos), com análise de sensibilidade e recomendações de mitigação.

## Objetivos específicos
1. Revisar literatura recente sobre consumo energético dos data centers e crescimento previsto devido à IA. 
2. Construir um modelo/algoritmo simples: Emissões (kg CO₂) = Consumo (kWh) × Fator de Emissão (kg CO₂/kWh). 
3. Reunir fatores de emissão e dados de matriz elétrica para o Brasil (e fontes equivalentes para Argentina / Chile / Peru). 
4. Rodar cenários (presente, projeção IEA até 2030, matriz mais limpa / mais fóssil) e comparar resultados. 
5. Discutir limitações e propor medidas de mitigação/boas práticas para data centers no Brasil.

# Justificativa
- A eletrificação e o aumento do processamento (especialmente IA) projetam forte aumento do consumo de data centers globalmente — a IEA projeta que o consumo de eletricidade pode mais que dobrar até 2030 (≈945 TWh no cenário base). 
- O Brasil tem uma matriz elétrica comparativamente limpa (alta participação de renováveis), o que reduz a intensidade carbônica por kWh — ainda assim, períodos de seca ou ativação de térmicas fósseis podem aumentar a intensidade. 
- Há incertezas importantes (definição de fronteiras das emissões, eficiência dos data centers, contabilização de emissões incorporadas), e a literatura recente chama atenção para variações metodológicas significativas.

## Metodologia 
- Escopo: Emissões operacionais associadas ao consumo elétrico (Escopo 2). 
- Fórmula central: Emissões de CO₂(kg) = Consumo em kWh × Fator de Emissao em kg de CO2/kWh 
- Variáveis de entrada: Localização, Consumo estimado, Período de análise e Cenário da matriz elétrica.
- Base de dados: MCTI/SIRENE, EPE (BEN), IEA (Energy & AI).

