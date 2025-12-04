A seguir está o resumo dos tópicos mais importantes de cada arquivo, conforme solicitado, apresentado apenas em tópicos e com as respectivas citações.

## Apostila Modelos pre treinados.pdf

* **Módulo VI - Modelos de linguagem pré-treinados**
* Modelos pré-treinados
* Prompt engineering
* Retrieval-Augmented Generation (RAG)
* Agentes
* LLMOps
* Modelos de Linguagem Pré-treinados (LLMs)
* Técnicas avançadas de engenharia de prompts
* Implementar e gerenciar a recuperação de respostas assistida por geração (RAG)
* Técnicas de parsing, chunking, embeddings, e recuperação de documentos
* Desenvolver e integrar agentes de LLM
* Deployment e gerenciamento de LLMs no Databricks
* Conceitos de LLMs
* Importância dos LLMs
* Modelos de código aberto vs. proprietários
* AI engineering vs. traditional ML engineering
* Exemplos de grandes modelos de linguagem (GPT, Gemini, Claude)
* Evolução dos modelos de linguagem
* Conceitos básicos de LLMs
    * Prompts
    * Tokens
    * Mensagens
* Parâmetros dos LLMs
    * Temperatura
    * Top P (núcleo de amostragem)
* Tamanho dos LLMs
* Escalabilidade e Complexidade dos LLMs
* Treinamento de LLMs
    * Fornecimento de texto de entrada
    * Otimização de pesos do modelo
* Modelos de aprendizagem em LLMs
    * Aprendizagem zero-shot
    * Aprendizagem few-shot
    * Adaptação de domínio
* Técnicas de adaptação: prompt engineering vs. fine-tuning
* Aplicações no mundo real dos LLMs
    * Geração de conteúdo
    * Tradução de idiomas
    * Resumo de texto
    * Chatbots e Q&A
    * Moderação de conteúdo
    * Recuperação de informações
    * Ferramentas educacionais
    * Diagnóstico médico
* Introdução ao prompt engineering
* Aplicações de prompt engineering
* Técnicas de prompt engineering
    * Zero-shot learning
    * Few-shot learning
    * Chain-of-thought (CoT)
    * Prompt templates
    * Outros tipos de prompts (Extração, Classificação, Geração de código, Raciocínio, Conversação)
    * Boas práticas em engenharia de prompts
    * Encadeamento de prompts
        * Encadeamento sequencial
        * Encadeamento paralelo
        * Autoconsistência
        * Árvore de pensamentos
        * Loop
* Memória conversacional
    * Memória de buffer de conversação
    * Memória de janela de buffer de conversação
    * Memória de resumo de conversação
    * Memória de buffer de resumo de conversação
    * Memória de buffer de tokens de conversação
* Retrieval-Augmented Generation (RAG)
    * RAG vs Engenharia de prompt
    * Motivação para o uso de RAG
    * Processo RAG
    * Componentes de um sistema RAG
    * Casos de uso do RAG (Atendimento ao cliente, Melhoria de busca, Gestão de conhecimento corporativo)
    * Benefícios do RAG (Redução de alucinações, Precisão em aplicações críticas, Atualização constante, Personalização)
    * Técnicas de implementação do RAG (Busca de documentos, Criação de embeddings, Filtragem de conteúdo, Re-ranking, Incorporação contextual, Feedback e aprendizado contínuo)
* Embeddings
    * O que são embeddings?
    * Aplicações de embeddings (Busca semântica, Classificação de texto, Sistemas de recomendação, Tradução automática)
    * Considerações ao escolher o modelo de embedding
* Bancos de dados vetoriais (VectorDB)
    * O que são bancos de dados vetoriais?
    * Aplicações comuns (Busca semântica, Recomendação de conteúdo, Visão computacional)
    * Comparação com bancos de Dados tradicionais
    * Vantagens dos bancos de dados vetoriais
    * Técnicas de indexação em bancos de dados vetoriais (Árvores KD, LSH, HNSW)
    * Espaços vetoriais e representação de dados
    * Similaridade e distância (Distância euclidiana, Distância coseno, Distância de manhattan, Distância de hamming)
* Arquitetura e implementação de VectorDB (Estruturas de indexação, Principais sistemas e ferramentas)
* Desafios e tendências futuras (Escalabilidade e desempenho, Avanços tecnológicos)
* Parsing, retrieval e chunking
    * Introdução ao parsing
    * Introdução ao Retrieval (Recuperação de informação)
    * Tipos de retrieval (Information retrieval, Semantic retrieval)
    * Tipos de dados RAG (Dados estruturados, Dados não estruturados)
    * Estratégias de chunking (Tamanho fixo, Chunking semântico)
* Agentes de LLM
    * Capacidades e aplicações dos agentes de LLM
    * Orientação de agentes de LLM
    * Intuição por trás dos agentes de LLM
    * Como os agentes funcionam?
    * Tipos de agentes (Zero-shot ReAct, Conversational ReAct, ReAct DocStore, Self-Ask with Search)
* Function Calling
    * Como function calling funciona
    * Ferramentas e modelos suportados
    * Benefícios do function calling
* ReAct agents com LangGraph
* Ferramentas personalizadas (Custom tools)
* LLMOps
    * Objetivos do LLMOps
    * Definição de requisitos e casos de uso
    * Adequação do caso de uso RAG
    * Experiência do usuário (Requisitos P0, P1, P2)
    * Fontes de dados (Requisitos P0, P1)
    * Desempenho e restrições (Requisitos P1)
    * Avaliação Contínua (Requisitos P0, P1)
    * Segurança (Requisitos P0, P1)
    * Integração e manutenção (Requisitos P1)
* Desenvolvimento orientado por avaliação
    * Construção da prova de conceito (PoC)
    * Análise exploratória de dados (EDA)
    * Desenvolvimento de uma pipeline de dados RAG
    * Desenvolvimento do agente RAG
* Avaliação da PoC
    * Criação de um Conjunto de Avaliação
    * Avaliação da Qualidade (Precisão, Relevância, Groundedness)
    * Estabelecimento de Linha de Base
* Diagnóstico e correção de problemas
    * Identificação das causas raízes (Problemas de recuperação e de geração)
    * Análise de recuperação
    * Análise de geração
    * Iteração e avaliação de correções
* Implantação e monitoramento em produção
    * Implantação (Integração, Versionamento e escalabilidade, Segurança)
    * Monitoramento contínuo (Métricas, Alertas, Análise contínua, Verificações de saúde)

## Apostila mlops.pdf

* Definição e escopo de um projeto de ciência de dados tradicional
* Versionamento e ambientes dev/prod para projetos de ciência de dados
* Desenvolvimento e avaliação de modelos de machine learning com MLflow tracking
* Disponibilização de modelos com MLflow models (batch x real time)
* Criação de execuções automatizadas com Databricks Asset Bundles
* MLOps (machine learning operations)
* Glossário (CI/CD, Artefatos, Feature)
* Machine Learning e AI (Projetos de ML vs. Generative AI)
* Separação de ambientes (dev/prod) e versionamento de código
* Ferramentas Databricks para separação de ambientes
    * Repos (Databricks Repos)
    * Widgets
* Desenvolvimento e avaliação de modelos de machine learning com MLflow tracking
* MLFlow (Plataforma, Componentes: Tracking, Projects, Models, Registry)
* MLFlow Tracking
* MLFlow Models
* MLFlow Serving
* Disponibilização de modelos com MLflow models
    * Inferência em Batch (em lote)
    * Inferência Sob demanda (em tempo real)
* Databricks Asset Bundles (DAB)
* Fluxo de trabalho de MLOps

## Apostila nlp.pdf

* Tópicos em processamento de linguagem natural (NLP)
* Limpeza de dados textuais
* Análise de dados textuais
* Tokenização e vetorização
* Análise de sentimentos
* Modelagem de tópicos
* Introdução ao processamento de linguagem natural (NLP)
* Definição de NLP
* Importância do NLP para IA e LLMs
* Aplicações de NLP (Tradução, Análise de sentimentos, Extração de informação, Chatbots, LLMs)
* Conceitos Básicos de NLP (Corpus, Documentos, Vocabulário)
* Codificação (ASCII, Unicode)
* Tipos de dados textuais (Estruturados e Não estruturados)
* Tokenização: destrinchando o texto
    * Tokenização de palavras
    * Tokenização de caracteres
    * Tokenização de subpalavras
* Vetorização de texto
* Ferramentas e bibliotecas de NLP (NLTK, spaCy)
* Limpeza e Padronização de Dados Textuais
    * Lematização e stemming
    * Disponibilidade em bibliotecas Python para limpeza de texto (NLTK, spaCy, Pandas)
    * Customização da limpeza de texto
* Explorando o Potencial Analítico do Texto
    * Dados textuais desestruturados
    * WordClouds como ferramenta analítica
    * N-gramas
    * Stopwords
    * Processamento de metadados textuais
* História e evolução da vetorização
    * Bag of words (BoW)
    * Term frequency-inverse document frequency (TF-IDF)
    * Outras técnicas de vetorização (Word2Vec, GloVe, BERT, GPT)
    * Word Embeddings
    * Modelos baseados em transformers
* Dimensionalidade dos tokens
    * Desafios de dimensionalidade (Esparsidade, Complexidade computacional)
    * Soluções para dimensionalidade (Redução de dimensionalidade, Seleção de características, Regularização, Embedding de palavras)
* Análise de Sentimentos
    * Origem da análise de sentimento
    * Aplicações da análise de sentimento (Marketing, Atendimento ao Cliente, Análise de Concorrência, Monitoramento de Redes Sociais, Saúde Mental)
    * Abordagens comuns na análise de sentimento (Métodos Baseados em Dicionários, Modelos de Aprendizado de Máquina Supervisionado, Modelos de Deep Learning, Análise Semântica e Contextual)
    * Algoritmos e técnicas específicas (Naive Bayes, SVM, Random Forests, CNNs, RNNs/LSTMs, Transformers)
* Modelagem de Tópicos
    * Origens e Evolução da Modelagem de Tópicos (LSA, LDA)
    * Aplicações da modelagem de tópicos
    * Abordagens comuns na modelagem de tópicos (LDA, NMF, LSA, CTM, DTM, Neural Topic Models)
    * Algoritmos e técnicas para modelagem de tópicos (Gibbs Sampling, Variational Inference, EM, HDP, PyLDAvis, Gensim)
    * Desafios e considerações na modelagem de tópicos (Escolha do Número de Tópicos, Interpretação, Palavras Raras e Stopwords, Escalabilidade, Tópicos Dinâmicos)

## Apostila redes neurais.pdf

* Conceitos básicos de redes neurais
* Perceptron model
* MLP (Multi-Layer Perceptrons)
* Funções de ativação
* Back propagation (Retropropagação)
* Cost function (Função custo)
* Parameter initialization
* Introdução a recurrent neural networks (RNN)
* Vanilla RNN
* RNN batches
* Vanishing gradients problem
* LSTM (long short-term memory)
* GRU (Gated recurrent unit)
* Implementação de mecanismos de atenção
* Redes neurais artificiais (RNAs)
* Origens teóricas (Neurônio de McCulloch-Pitts)
* Características do Perceptron
* Limitações e desafios iniciais (Classificação linear, XOR problem)
* Funções de ativação das camadas ocultas
* Funções de ativação da camada de saída
* Função custo e gradient descent
* Dropout
* Avanços recentes (Deep learning, CNNs, RNNs, GANs)
* Exemplo de construção de uma rede neural artificial (ANN)
* Conceitos de RNNs (Recorrência, Desempacotamento/Unfold)
* Exploding gradient
* Arquitetura de uma LSTM (Porta de esquecimento, Porta de entrada, Porta de saída)
* Arquitetura de uma GRU (Porta de atualização, Porta de reinicialização)
* Transformers
    * Arquitetura do transformer
    * Componentes principais (Codificador, Decodificador, Atenção)
    * TransformerBlock
    * TokenAndPositionEmbedding
    * Utilizando modelos pré-treinados com Hugging Face transformers (BERT, GPT-2)

## Fundamentos de Databricks para IA.pdf

* Introdução à interface e features do Databricks para machine learning
* Fundamentos de computação distribuída, o Spark
* Integração com linguagens de programação populares (Python, Scala e SQL)
* Databricks Compute
    * All-Purpose Compute
    * Job Compute
    * Instance pools
    * Serverless SQL warehouses
    * Classic SQL warehouses
    * Serverless compute for notebooks
    * Serverless compute for workflows
    * Single-node vs Multi-node compute
* Databricks Runtime
    * Databricks Runtime ML
    * Versões LTS (Long Term Support)
* Databricks Git Folders (Git client visual e API)
* Feature Store (Repositório centralizado de variáveis)
    * Reutilização de features
    * Consistência
    * Colaboração
    * Versionamento
    * Integração com delta lake
* Versionamento de dados (timestamp as of, version as of)
* AutoML (Solução para construção de soluções de machine learning automatizada)
    * Modelos automáticos de classificação
    * Modelos automáticos de regressão
    * Modelos automáticos de séries temporais
    * Parâmetros em comum no AutoML
    * Integração do AutoML com Databricks Feature Store
* MLFlow gerenciado (Plataforma para gerenciamento do ciclo de vida de ML)
    * Tracking
    * Model Registry
    * MLFlow Deployments para LLMs
    * Evaluate
    * Prompt Engineering UI
    * Recipes
    * Projects
* MLFlow na prática (Registro de métricas, parâmetros e artefatos; Autolog)
* Modelos customizados com o MLFlow (Model flavor pyfunc)
* Conceitos básicos de computação distribuída
    * Apache Spark
    * Arquitetura Spark (Driver e Workers)
    * Apache Arrow
    * Avaliação preguiçosa (lazy evaluation)
    * Pandas on Spark
