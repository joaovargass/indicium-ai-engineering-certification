# Colunas Necessárias para Métricas e Gráficos

Este documento mapeia as colunas do dicionário de dados necessárias para calcular as métricas obrigatórias e gerar os gráficos solicitados no enunciado do desafio.

## Métricas Obrigatórias

### 1. Taxa de Aumento de Casos
**Descrição:** Mede o crescimento percentual de casos entre dois períodos.

**Colunas necessárias:**
- `DT_SIN_PRI` (Data de 1ºs sintomas) - Campo obrigatório
  - **Descrição:** Data de 1º sintomas do caso
  - **Uso:** Para agrupar casos por período e calcular a variação percentual

**Cálculo sugerido:**
- Comparar número de casos do período atual vs período anterior (ex: últimos 7 dias vs 7 dias anteriores)
- Fórmula: `((Casos Período Atual - Casos Período Anterior) / Casos Período Anterior) * 100`

---

### 2. Taxa de Mortalidade
**Descrição:** Percentual de casos que evoluíram para óbito.

**Colunas necessárias:**
- `EVOLUCAO` (Evolução do caso) - Campo Essencial
  - **Descrição:** Evolução do caso
  - **Valores:** 1-Cura, 2-Óbito, 3-Óbito por outras causas, 9-Ignorado
  - **Uso:** Identificar casos de óbito (valores 2 e 3)

**Cálculo sugerido:**
- Total de óbitos (EVOLUCAO = 2 ou 3) / Total de casos com evolução definida * 100
- Excluir casos com EVOLUCAO = 9 (Ignorado)

---

### 3. Taxa de Ocupação de UTI
**Descrição:** Percentual de leitos de UTI ocupados por pacientes com SRAG.

**Colunas necessárias:**
- `UTI` (Internado em UTI?) - Campo Essencial
  - **Descrição:** O paciente foi internado em UTI?
  - **Valores:** 1-Sim, 2-Não, 9-Ignorado
  - **Uso:** Identificar pacientes internados em UTI

- `DT_ENTUTI` (Data da entrada na UTI) - Campo Essencial
  - **Descrição:** Data de entrada do paciente na unidade de Terapia intensiva (UTI)
  - **Uso:** Calcular tempo de permanência e ocupação atual

- `DT_SAIDUTI` (Data da saída da UTI) - Campo Essencial
  - **Descrição:** Data em que o paciente saiu da Unidade de Terapia intensiva (UTI)
  - **Uso:** Calcular tempo de permanência e identificar leitos liberados
  - **Nota:** Se NULL, paciente ainda está na UTI

- `DT_INTERNA` (Data da internação por SRAG) - Campo Obrigatório
  - **Descrição:** Data em que o paciente foi hospitalizado
  - **Uso:** Contexto adicional para análise temporal

**Cálculo sugerido:**
- **Opção 1 (simplificada):** Total de pacientes em UTI (UTI = 1 e DT_SAIDUTI é NULL) / Total de leitos de UTI disponíveis * 100
- **Opção 2 (com tempo):** Considerar pacientes que entraram na UTI e ainda não saíram (DT_SAIDUTI é NULL ou > data atual)
- **Nota:** Pode ser necessário obter dados externos sobre total de leitos de UTI disponíveis na região

---

### 4. Taxa de Vacinação da População
**Descrição:** Percentual da população vacinada contra COVID-19 e/ou gripe.

**Colunas necessárias:**
- `VACINA_COV` (Recebeu vacina COVID-19?) - Campo Obrigatório
  - **Descrição:** Informar se o paciente recebeu vacina COVID-19
  - **Valores:** 1-Sim, 2-Não, 9-Ignorado
  - **Uso:** Identificar pacientes vacinados contra COVID-19

- `VACINA` (Recebeu vacina contra Gripe na última campanha?) - Campo Essencial
  - **Descrição:** Informar se o paciente foi vacinado contra gripe na última campanha
  - **Valores:** 1-Sim, 2-Não, 9-Ignorado
  - **Uso:** Identificar pacientes vacinados contra gripe

**Colunas opcionais (para análise mais detalhada):**
- `DOSE_1_COV` (Data 1ª dose da vacina COVID-19)
- `DOSE_2_COV` (Data 2ª dose da vacina COVID-19)
- `DOSE_REF` (Data da dose reforço da vacina COVID-19)
- `DT_UT_DOSE` (Data da vacinação contra gripe)

**Cálculo sugerido:**
- **Para COVID-19:** Total de pacientes com VACINA_COV = 1 / Total de pacientes * 100
- **Para Gripe:** Total de pacientes com VACINA = 1 / Total de pacientes * 100
- **Nota:** Esta métrica pode ser calculada sobre a população de casos notificados, ou pode requerer dados externos sobre população total (IBGE)

---

## Gráficos Obrigatórios

### Gráfico 1: Número Diário de Casos dos Últimos 30 Dias
**Descrição:** Gráfico de linha ou barras mostrando a evolução diária de casos.

**Colunas necessárias:**
- `DT_SIN_PRI` (Data de 1ºs sintomas) - Campo obrigatório
  - **Descrição:** Data de 1º sintomas do caso
  - **Uso:** Agrupar casos por dia e filtrar últimos 30 dias

**Alternativa (se DT_SIN_PRI não estiver disponível):**
- `DT_NOTIFIC` (Data do preenchimento da ficha de notificação) - Campo Obrigatório
  - **Descrição:** Data de preenchimento da ficha de notificação
  - **Uso:** Usar como proxy se DT_SIN_PRI tiver muitos valores faltantes

**Processamento:**
1. Filtrar registros onde DT_SIN_PRI está nos últimos 30 dias
2. Agrupar por data (DT_SIN_PRI)
3. Contar número de casos por dia
4. Ordenar por data crescente

---

### Gráfico 2: Número Mensal de Casos dos Últimos 12 Meses
**Descrição:** Gráfico de linha ou barras mostrando a evolução mensal de casos.

**Colunas necessárias:**
- `DT_SIN_PRI` (Data de 1ºs sintomas) - Campo obrigatório
  - **Descrição:** Data de 1º sintomas do caso
  - **Uso:** Agrupar casos por mês e filtrar últimos 12 meses

**Alternativa (se DT_SIN_PRI não estiver disponível):**
- `DT_NOTIFIC` (Data do preenchimento da ficha de notificação) - Campo Obrigatório
  - **Descrição:** Data de preenchimento da ficha de notificação
  - **Uso:** Usar como proxy se DT_SIN_PRI tiver muitos valores faltantes

**Processamento:**
1. Filtrar registros onde DT_SIN_PRI está nos últimos 12 meses
2. Extrair ano-mês de DT_SIN_PRI (formato: YYYY-MM)
3. Agrupar por ano-mês
4. Contar número de casos por mês
5. Ordenar por ano-mês crescente

---

## Resumo das Colunas por Prioridade

### Colunas Essenciais (Obrigatórias)
1. `DT_SIN_PRI` - Data de 1ºs sintomas (para gráficos e taxa de aumento)
2. `EVOLUCAO` - Evolução do caso (para taxa de mortalidade)
3. `UTI` - Internado em UTI? (para taxa de ocupação UTI)
4. `DT_ENTUTI` - Data da entrada na UTI (para taxa de ocupação UTI)
5. `DT_SAIDUTI` - Data da saída da UTI (para taxa de ocupação UTI)
6. `VACINA_COV` - Recebeu vacina COVID-19? (para taxa de vacinação)
7. `VACINA` - Recebeu vacina contra Gripe? (para taxa de vacinação)

### Colunas Alternativas/Complementares
- `DT_NOTIFIC` - Data do preenchimento da ficha (alternativa para DT_SIN_PRI)
- `DT_INTERNA` - Data da internação (contexto adicional para UTI)
- `DOSE_1_COV`, `DOSE_2_COV`, `DOSE_REF` - Datas de vacinação COVID-19 (análise detalhada)
- `DT_UT_DOSE` - Data da vacinação contra gripe (análise detalhada)

### Colunas de Identificação (Úteis para agregações)
- `SG_UF_NOT` - UF de notificação (para análises regionais)
- `ID_MUNICIP` ou `CO_MUN_NOT` - Município de notificação (para análises locais)
- `NU_NOTIFIC` - Número do registro (para contagem única de casos)

---

## Observações Importantes

1. **Dados Faltantes:** O enunciado menciona que os dados contêm problemas clássicos de dados reais (preenchimentos incorretos e dados faltantes). É necessário implementar tratamento adequado:
   - Validar datas (DT_SIN_PRI <= DT_NOTIFIC <= data atual)
   - Tratar valores 9 (Ignorado) nos campos categóricos
   - Decidir se excluir ou imputar valores faltantes

2. **Taxa de Ocupação de UTI:** Esta métrica pode requerer dados externos sobre o total de leitos de UTI disponíveis na região analisada. Se não disponível, pode-se calcular como "número de pacientes em UTI" sem o percentual.

3. **Taxa de Vacinação:** Pode ser calculada sobre a população de casos notificados (mais simples) ou sobre a população total (requer dados externos do IBGE).

4. **Performance:** Para datasets grandes (~165.000 linhas), considerar:
   - Uso de índices nas colunas de data
   - Agregações eficientes (GROUP BY otimizado)
   - Cache de resultados para métricas que não mudam frequentemente

5. **Validação de Dados:**
   - Verificar se DT_SIN_PRI está dentro de um range razoável (ex: 2019-2025)
   - Validar que DT_ENTUTI <= DT_SAIDUTI (quando ambos preenchidos)
   - Verificar consistência: se UTI = 1, então DT_ENTUTI deve estar preenchida

