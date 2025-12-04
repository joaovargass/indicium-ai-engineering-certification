# Certificação Artificial Intelligence Engineer — Indicium

## A certificação

O objetivo desta certificação é avaliar suas competências em um projeto prático de **Artificial Intelligence Engineer**.

A obtenção desta certificação indica que você:

* Entende o processo de construção de uma solução baseada em **Inteligência Artificial Generativa** capaz de:

  * Consultar dados e notícias;
  * Gerar **relatórios automatizados**;
  * Criar **métricas relevantes** com explicações contextualizadas para interpretar o cenário atual que essas métricas buscam medir.

---

## Pré-requisitos

* Conhecimento em **Python** (listas, tuplas, dicionários, laços de repetição, API, etc.);
* Conhecimentos sobre **IA Generativa**:

  * LangChain
  * LangGraph
  * Agents
  * Bancos vetoriais
  * RAG e técnicas relacionadas
* Manipulação de **LLMs**

---

## Contexto

A **Indicium HealthCare Inc.** deseja criar uma solução baseada em dados para ajudar profissionais da saúde a entender, em tempo real, a severidade e o avanço de surtos de doenças.

Para isso, realizará uma **Prova de Conceito (PoC)** e você foi contratado como analista responsável pela solução.

A PoC consiste em construir uma solução capaz de:

1. Gerar um **relatório automatizado** por meio de um agente;
2. Esse agente deve:

   * Consultar o **banco de dados** para extrair métricas;
   * Consultar **notícias em tempo real** sobre **Síndrome Respiratória Aguda Grave (SRAG)**;
   * Embasar as métricas com comentários explicativos;
3. Para os dados, será utilizado o conjunto real de internações por SRAG disponível no **Open DATASUS**.

---

## Métricas obrigatórias no relatório

O relatório deve conter, no mínimo:

* **Taxa de aumento de casos**
* **Taxa de mortalidade**
* **Taxa de ocupação de UTI**
* **Taxa de vacinação da população**

Além disso, devem ser incluídos:

* **Gráfico 1**: Número diário de casos dos últimos **30 dias**
* **Gráfico 2**: Número mensal de casos dos últimos **12 meses**

---

## Descrição dos dados

* O dataset está disponível no **Open DATASUS** (com dicionário de dados e documentação).
* Arquivo CSV com aproximadamente:

  * **100 colunas**
  * **165.000 linhas**
* Contém problemas clássicos de dados reais:

  * Preenchimentos incorretos
  * Dados faltantes
* Você deve:

  * Selecionar colunas pertinentes;
  * Aplicar os tratamentos e limpeza de dados adequados.

---

## Entrega

Você deve entregar:

### 1. Repositório público no GitHub contendo:

* Todo o código da solução desenvolvida;
* Documentação completa no **README** e/ou relatórios presentes no repositório.

### 2. PDF obrigatório contendo:

* **Diagrama conceitual da arquitetura**, incluindo:

  * Agente principal (orquestrador)
  * Ferramentas (Tools)
  * Interações com:

    * LLM
    * Banco de dados
    * Fontes de notícias

---

## Avaliação

A nota será atribuída considerando:

* **Escolha da arquitetura**
* **Governança e transparência**

  * Mecanismos de auditoria
  * Registro das decisões dos agentes
* **Guardrails**
* **Tratamento de dados sensíveis**
* **Clean Code**

---

## Instruções finais

* Você terá **30 dias** após a inscrição para enviar o desafio.
* Após clicar em **"Enviar"**, só será possível fazer o envio **uma única vez**.
* Envie somente quando **tudo estiver concluído**.
