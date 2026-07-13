# Credit Risk — Machine Learning

Aplicação de Ciência de Dados desenvolvida em Python para estimar a probabilidade de inadimplência de clientes de cartão de crédito.

O projeto contempla o pipeline completo de Machine Learning: obtenção e preparação dos dados, análise exploratória, comparação de algoritmos, seleção de threshold, avaliação em teste isolado, análise de importância das variáveis, estudo de equidade e disponibilização de uma interface interativa em Streamlit.

## Demonstração

A aplicação permite preencher informações relacionadas ao perfil financeiro do cliente, como:

- limite de crédito;
- idade;
- histórico de pagamentos;
- valores das faturas;
- valores pagos nos últimos seis meses.

Com base nessas informações, o sistema apresenta:

- probabilidade estimada de inadimplência;
- score interno ilustrativo;
- recomendação de aprovação, análise manual ou alto risco;
- indicadores financeiros complementares;
- alertas relacionados a atrasos, utilização do limite e pagamentos.

## Objetivo do projeto

O objetivo é demonstrar a construção de uma solução de Machine Learning orientada a um problema de negócio do setor financeiro.

Além da previsão, o projeto busca responder às seguintes perguntas:

- Qual modelo apresenta melhor capacidade de identificar inadimplentes?
- Qual threshold oferece equilíbrio adequado entre recall e precisão?
- Quais variáveis possuem maior influência nas previsões?
- Qual é o impacto da remoção de variáveis demográficas?
- O desempenho do modelo varia entre diferentes grupos?

## Dataset

Foi utilizado o dataset **Default of Credit Card Clients**, disponibilizado pela UCI Machine Learning Repository.

Fonte:

[UCI Machine Learning Repository — Default of Credit Card Clients](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients)

A base original possui:

- 30.000 registros;
- 23 variáveis explicativas;
- variável-alvo binária de inadimplência;
- dados históricos de clientes de cartão de crédito de Taiwan.

Durante a preparação:

- 35 registros duplicados foram removidos;
- 29.965 registros foram utilizados;
- não foram identificados valores ausentes;
- a taxa de inadimplência ficou em aproximadamente 22,13%.

## Metodologia

### 1. Preparação dos dados

A etapa de preparação inclui:

- download do dataset pela biblioteca `ucimlrepo`;
- tradução dos nomes das variáveis;
- ajuste de categorias não documentadas;
- conversão dos tipos de dados;
- validação da variável-alvo;
- identificação e remoção de registros duplicados.

### 2. Divisão da base

A base foi separada em três conjuntos:

- 60% para treinamento;
- 20% para validação;
- 20% para teste final.

A base de validação foi utilizada para escolher o algoritmo e definir o threshold.

A base de teste permaneceu isolada durante essas decisões e foi utilizada somente na avaliação final.

### 3. Modelos comparados

Foram comparados os seguintes algoritmos:

- Regressão Logística;
- Random Forest;
- HistGradientBoosting.

O principal critério de seleção foi o **PR AUC**, pois a classe inadimplente representa aproximadamente 22% dos registros.

### 4. Seleção do modelo

O Random Forest apresentou o melhor PR AUC na base de validação e foi selecionado como modelo principal.

Também foi criada uma versão reduzida do modelo, sem utilizar diretamente:

- sexo;
- escolaridade;
- estado civil.

A versão reduzida foi escolhida para a aplicação principal porque apresentou perda mínima de desempenho em relação ao modelo completo.

A idade continua sendo utilizada.

## Resultados do modelo reduzido

Resultados obtidos na base de teste isolada:

| Métrica | Resultado |
|---|---:|
| Acurácia | 68,46% |
| Precisão | 38,34% |
| Recall | 69,91% |
| F1-score | 49,52% |
| ROC AUC | 0,7718 |
| PR AUC | 0,5513 |
| Threshold | 36% |

O threshold de 36% foi selecionado buscando a maior precisão possível entre os limites que atingiram recall mínimo próximo de 70% na validação.

A redução do threshold aumenta a identificação de clientes inadimplentes, mas também aumenta a quantidade de clientes adimplentes classificados como alto risco.

## Comparação dos modelos completo e reduzido

| Métrica | Modelo completo | Modelo reduzido |
|---|---:|---:|
| Precisão | 38,75% | 38,34% |
| Recall | 70,66% | 69,91% |
| F1-score | 50,05% | 49,52% |
| ROC AUC | 0,7739 | 0,7718 |
| PR AUC | 0,5537 | 0,5513 |

A remoção das três variáveis demográficas provocou:

- redução de 0,0024 no PR AUC;
- redução de 0,0021 no ROC AUC;
- redução de 0,75 ponto percentual no recall;
- redução de 0,41 ponto percentual na precisão.

## Política de decisão

A aplicação utiliza três faixas operacionais:

| Probabilidade estimada | Recomendação |
|---|---|
| Abaixo de 26% | Aprovação sugerida |
| De 26% até menos de 36% | Análise manual |
| 36% ou mais | Alto risco |

A faixa de análise manual é uma regra operacional adicional. O modelo originalmente produz uma probabilidade de inadimplência, não uma decisão definitiva de crédito.

## Importância das variáveis

As variáveis com maior importância global no Random Forest foram:

1. status de pagamento de setembro;
2. status de pagamento de agosto;
3. valor pago em setembro;
4. status de pagamento de julho;
5. limite de crédito;
6. valor da fatura de setembro.

A importância utilizada é baseada na redução de impureza das árvores.

Ela indica quanto cada variável foi utilizada pelo modelo, mas não informa isoladamente se determinado valor aumenta ou reduz o risco e não representa causalidade.

## Equidade e IA responsável

O projeto inclui uma análise do comportamento do modelo entre grupos de:

- sexo;
- escolaridade;
- estado civil;
- faixa de idade.

Também foi comparado o modelo completo com uma versão sem sexo, escolaridade e estado civil.

A remoção desses atributos reduziu algumas diferenças entre grupos, mas aumentou outras. Por isso, não é possível afirmar que a versão reduzida seja automaticamente justa.

Outras variáveis podem funcionar como proxies, e grupos com poucas observações apresentam métricas mais instáveis.

Uma aplicação real exigiria:

- avaliação jurídica e regulatória;
- validação estatística adicional;
- monitoramento contínuo;
- revisão periódica do modelo;
- análise de impacto sobre grupos;
- participação de especialistas de negócio.

## Páginas da aplicação

### Início

Formulário para análise individual de risco.

Apresenta:

- probabilidade de inadimplência;
- score interno ilustrativo;
- decisão recomendada;
- histórico de atrasos;
- utilização do limite;
- proporção entre pagamentos e faturas;
- alertas complementares.

### Desempenho do Modelo

Apresenta:

- comparação dos algoritmos;
- resultados na validação;
- métricas no teste isolado;
- matriz de confusão;
- desempenho por classe;
- análise de threshold;
- importância das variáveis;
- metodologia utilizada.

### Análise dos Dados

Apresenta:

- visão geral da base;
- distribuição da inadimplência;
- análise por idade, sexo, escolaridade e estado civil;
- distribuição do limite de crédito;
- histórico de pagamentos;
- evolução das faturas e pagamentos;
- correlações;
- estatísticas descritivas.

### Equidade e IA Responsável

Apresenta:

- modelo completo versus modelo reduzido;
- diferenças de desempenho;
- métricas entre grupos;
- taxas de falsos positivos e falsos negativos;
- alertas para grupos com amostras pequenas;
- limitações da análise.

## Tecnologias utilizadas

- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit
- Altair
- Joblib
- UCI ML Repository
- Git e GitHub

## Estrutura do projeto

```text
CREDIT RISK
├── data
│   ├── processed
│   │   └── credit_default_real.csv
│   └── raw
│       ├── credit_default_uci_raw.csv
│       └── uci_variables.csv
│
├── models
│   ├── credit_risk_real_model.joblib
│   └── credit_risk_reduced_model.joblib
│
├── pages
│   ├── 1_Desempenho_do_Modelo.py
│   ├── 2_Analise_dos_Dados.py
│   └── 3_Equidade_e_IA_Responsavel.py
│
├── reports
│   ├── real_feature_importance_grouped.csv
│   ├── real_model_comparison.csv
│   ├── real_model_metadata.json
│   ├── real_test_metrics.json
│   ├── real_threshold_analysis.csv
│   ├── reduced_model_threshold_policy.json
│   ├── sensitive_feature_fairness.csv
│   ├── sensitive_feature_fairness_gaps.csv
│   └── sensitive_feature_model_comparison.csv
│
├── Inicio.py
├── prepare_real_data.py
├── train_real_models.py
├── real_feature_importance.py
├── compare_sensitive_features.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Como executar

### 1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
cd NOME_DO_REPOSITORIO
```

### 2. Criar o ambiente virtual

No Windows:

```powershell
python -m venv .venv
```

### 3. Ativar o ambiente virtual

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 5. Executar a aplicação

```powershell
streamlit run Inicio.py
```

## Como reconstruir o projeto

Os artefatos necessários para executar a aplicação já estão incluídos no projeto.

Para reconstruir todo o pipeline, execute na seguinte ordem:

```powershell
python prepare_real_data.py
```

```powershell
python train_real_models.py
```

```powershell
python real_feature_importance.py
```

```powershell
python compare_sensitive_features.py
```

Depois:

```powershell
streamlit run Inicio.py
```

## Limitações

- O dataset contém dados históricos de Taiwan.
- Os resultados não devem ser generalizados automaticamente para outros países.
- O modelo não considera variáveis macroeconômicas.
- A base não representa necessariamente o mercado atual.
- O score interno não corresponde a um score oficial de mercado.
- A aplicação não calcula juros, limite recomendado ou valor de parcela.
- O modelo reduzido ainda utiliza idade.
- A remoção de variáveis demográficas não elimina possíveis proxies.
- O projeto não substitui análise humana, política de crédito ou validação regulatória.

## Próximas melhorias

- explicabilidade individual com SHAP;
- importância por permutação;
- busca de hiperparâmetros;
- validação cruzada;
- calibração das probabilidades;
- API com FastAPI;
- testes automatizados;
- monitoramento de drift;
- versionamento de experimentos com MLflow;
- pipeline de CI/CD;
- persistência do histórico das análises.

## Aviso

Este projeto possui finalidade educacional e de portfólio.

As previsões e recomendações apresentadas não devem ser utilizadas isoladamente para conceder, negar ou alterar condições reais de crédito.