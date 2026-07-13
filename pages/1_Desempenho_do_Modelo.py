import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Desempenho do modelo",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# CAMINHOS DOS ARQUIVOS
# ============================================================

CAMINHO_COMPARACAO = (
    Path("reports")
    / "real_model_comparison.csv"
)

CAMINHO_METADATA = (
    Path("reports")
    / "real_model_metadata.json"
)

CAMINHO_POLITICA = (
    Path("reports")
    / "real_threshold_policy.json"
)

CAMINHO_METRICAS_TESTE = (
    Path("reports")
    / "real_test_metrics.json"
)

CAMINHO_MATRIZ_TESTE = (
    Path("reports")
    / "real_test_confusion_matrix.csv"
)

CAMINHO_RELATORIO_TESTE = (
    Path("reports")
    / "real_test_classification_report.csv"
)

CAMINHO_THRESHOLDS = (
    Path("reports")
    / "real_threshold_analysis.csv"
)

CAMINHO_IMPORTANCIA = (
    Path("reports")
    / "real_feature_importance_grouped.csv"
)


# ============================================================
# FUNÇÕES DE CARREGAMENTO
# ============================================================

@st.cache_data
def carregar_csv(
    caminho,
    index_col=None,
):
    """
    Carrega um arquivo CSV.
    """

    if not caminho.exists():
        return None

    return pd.read_csv(
        caminho,
        index_col=index_col,
    )


@st.cache_data
def carregar_json(
    caminho,
):
    """
    Carrega um arquivo JSON.
    """

    if not caminho.exists():
        return None

    with open(
        caminho,
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(
            arquivo
        )


def formatar_numero(
    valor,
):
    """
    Formata números inteiros utilizando
    o separador brasileiro.
    """

    return f"{int(valor):,}".replace(
        ",",
        ".",
    )


# ============================================================
# CARREGAMENTO DOS RELATÓRIOS
# ============================================================

comparacao = carregar_csv(
    CAMINHO_COMPARACAO
)

metadata = carregar_json(
    CAMINHO_METADATA
)

politica = carregar_json(
    CAMINHO_POLITICA
)

metricas_teste = carregar_json(
    CAMINHO_METRICAS_TESTE
)

matriz_teste = carregar_csv(
    CAMINHO_MATRIZ_TESTE,
    index_col=0,
)

relatorio_teste = carregar_csv(
    CAMINHO_RELATORIO_TESTE
)

analise_thresholds = carregar_csv(
    CAMINHO_THRESHOLDS
)

importancia_variaveis = carregar_csv(
    CAMINHO_IMPORTANCIA
)


# ============================================================
# VERIFICAÇÃO DOS ARQUIVOS
# ============================================================

arquivos_obrigatorios = {
    "comparação dos modelos": comparacao,
    "metadados": metadata,
    "política de threshold": politica,
    "métricas de teste": metricas_teste,
    "matriz de confusão": matriz_teste,
    "relatório de classificação": relatorio_teste,
    "análise de thresholds": analise_thresholds,
    "importância das variáveis": importancia_variaveis,
}


arquivos_ausentes = [
    nome
    for nome, conteudo in arquivos_obrigatorios.items()
    if conteudo is None
]


if arquivos_ausentes:

    st.error(
        "Alguns relatórios da base real não foram encontrados."
    )

    st.write(
        "Arquivos ausentes:",
        ", ".join(
            arquivos_ausentes
        ),
    )

    st.write(
        "Execute novamente os comandos:"
    )

    st.code(
        "python train_real_models.py\n"
        "python real_feature_importance.py"
    )

    st.stop()


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "📊 Desempenho do modelo"
)

st.write(
    "Avaliação dos algoritmos treinados com o dataset real "
    "Default of Credit Card Clients, disponibilizado pela "
    "UCI Machine Learning Repository."
)


# ============================================================
# VISÃO GERAL
# ============================================================

st.markdown(
    "## Visão geral"
)


(
    coluna_resumo_1,
    coluna_resumo_2,
    coluna_resumo_3,
    coluna_resumo_4,
) = st.columns(4)


with coluna_resumo_1:

    st.metric(
        "Modelo selecionado",
        metadata[
            "modelo_selecionado"
        ],
    )


with coluna_resumo_2:

    st.metric(
        "Registros utilizados",
        formatar_numero(
            metadata[
                "registros_utilizados"
            ]
        ),
    )


with coluna_resumo_3:

    st.metric(
        "Taxa de inadimplência",
        (
            f"{metadata['taxa_inadimplencia_total']:.2%}"
        ),
    )


with coluna_resumo_4:

    st.metric(
        "Threshold selecionado",
        (
            f"{metadata['threshold_recomendado']:.0%}"
        ),
    )


with st.expander(
    "Ver divisão dos dados"
):

    (
        coluna_divisao_1,
        coluna_divisao_2,
        coluna_divisao_3,
        coluna_divisao_4,
    ) = st.columns(4)


    with coluna_divisao_1:

        st.metric(
            "Registros originais",
            formatar_numero(
                metadata[
                    "registros_originais"
                ]
            ),
        )


    with coluna_divisao_2:

        st.metric(
            "Duplicados removidos",
            formatar_numero(
                metadata[
                    "duplicados_removidos"
                ]
            ),
        )


    with coluna_divisao_3:

        st.metric(
            "Treinamento",
            formatar_numero(
                metadata[
                    "registros_treino"
                ]
            ),
        )


    with coluna_divisao_4:

        st.metric(
            "Validação / teste",
            (
                f"{formatar_numero(metadata['registros_validacao'])}"
                " / "
                f"{formatar_numero(metadata['registros_teste'])}"
            ),
        )


    st.write(
        "O modelo foi selecionado na base de validação. "
        "A avaliação final foi realizada em uma base de teste "
        "isolada durante a escolha do algoritmo e do threshold."
    )


# ============================================================
# COMPARAÇÃO DOS MODELOS
# ============================================================

st.markdown(
    "## Comparação dos modelos na validação"
)


comparacao_formatada = comparacao.copy()


colunas_percentuais = [
    "acuracia",
    "precisao",
    "recall",
    "f1_score",
]


for coluna in colunas_percentuais:

    comparacao_formatada[
        coluna
    ] = comparacao_formatada[
        coluna
    ].map(
        lambda valor: f"{valor:.2%}"
    )


comparacao_formatada[
    "roc_auc"
] = comparacao_formatada[
    "roc_auc"
].map(
    lambda valor: f"{valor:.4f}"
)


comparacao_formatada[
    "pr_auc"
] = comparacao_formatada[
    "pr_auc"
].map(
    lambda valor: f"{valor:.4f}"
)


comparacao_formatada = (
    comparacao_formatada.rename(
        columns={
            "modelo": "Modelo",
            "acuracia": "Acurácia",
            "precisao": "Precisão",
            "recall": "Recall",
            "f1_score": "F1-score",
            "roc_auc": "ROC AUC",
            "pr_auc": "PR AUC",
        }
    )
)


st.dataframe(
    comparacao_formatada[
        [
            "Modelo",
            "Acurácia",
            "Precisão",
            "Recall",
            "F1-score",
            "ROC AUC",
            "PR AUC",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# GRÁFICO NÃO EMPILHADO DOS MODELOS
# ============================================================

comparacao_grafico = (
    comparacao[
        [
            "modelo",
            "roc_auc",
            "pr_auc",
        ]
    ]
    .melt(
        id_vars="modelo",
        var_name="metrica",
        value_name="valor",
    )
)


comparacao_grafico[
    "metrica"
] = comparacao_grafico[
    "metrica"
].map(
    {
        "roc_auc": "ROC AUC",
        "pr_auc": "PR AUC",
    }
)


ordem_modelos = comparacao[
    "modelo"
].tolist()


grafico_modelos = (
    alt.Chart(
        comparacao_grafico
    )
    .mark_bar()
    .encode(
        y=alt.Y(
            "modelo:N",
            title="Modelo",
            sort=ordem_modelos,
        ),

        x=alt.X(
            "valor:Q",
            title="Valor da métrica",
            scale=alt.Scale(
                domain=[
                    0,
                    1,
                ]
            ),
        ),

        color=alt.Color(
            "metrica:N",
            title="Métrica",
        ),

        yOffset=alt.YOffset(
            "metrica:N"
        ),

        tooltip=[
            alt.Tooltip(
                "modelo:N",
                title="Modelo",
            ),

            alt.Tooltip(
                "metrica:N",
                title="Métrica",
            ),

            alt.Tooltip(
                "valor:Q",
                title="Resultado",
                format=".4f",
            ),
        ],
    )
    .properties(
        height=260,
    )
)


st.altair_chart(
    grafico_modelos,
    use_container_width=True,
)


st.info(
    "O Random Forest foi selecionado pelo maior PR AUC "
    "na base de validação. Essa métrica recebe atenção "
    "especial porque a classe inadimplente é minoritária."
)


# ============================================================
# IMPORTÂNCIA DAS VARIÁVEIS
# ============================================================

st.markdown(
    "## Importância das variáveis"
)


st.write(
    "O gráfico mostra quais variáveis foram mais utilizadas "
    "pelo Random Forest durante a construção das árvores."
)


quantidade_importancias = st.slider(
    "Quantidade de variáveis exibidas",
    min_value=5,
    max_value=len(
        importancia_variaveis
    ),
    value=min(
        15,
        len(
            importancia_variaveis
        ),
    ),
    step=1,
)


top_importancias = (
    importancia_variaveis
    .head(
        quantidade_importancias
    )
    .copy()
)


grafico_importancia = (
    alt.Chart(
        top_importancias
    )
    .mark_bar()
    .encode(
        y=alt.Y(
            "nome_amigavel:N",
            title=None,
            sort=alt.SortField(
                field="percentual_importancia",
                order="descending",
            ),
        ),

        x=alt.X(
            "percentual_importancia:Q",
            title="Importância relativa",
            axis=alt.Axis(
                format=".0%"
            ),
        ),

        tooltip=[
            alt.Tooltip(
                "posicao:Q",
                title="Posição",
                format=".0f",
            ),

            alt.Tooltip(
                "nome_amigavel:N",
                title="Variável",
            ),

            alt.Tooltip(
                "percentual_importancia:Q",
                title="Importância",
                format=".2%",
            ),
        ],
    )
    .properties(
        height=max(
            350,
            quantidade_importancias * 30,
        ),
    )
)


st.altair_chart(
    grafico_importancia,
    use_container_width=True,
)


importancia_formatada = (
    top_importancias[
        [
            "posicao",
            "nome_amigavel",
            "percentual_importancia",
        ]
    ]
    .copy()
)


importancia_formatada[
    "percentual_importancia"
] = importancia_formatada[
    "percentual_importancia"
].map(
    lambda valor: f"{valor:.2%}"
)


importancia_formatada = (
    importancia_formatada.rename(
        columns={
            "posicao": "Posição",
            "nome_amigavel": "Variável",
            "percentual_importancia": "Importância relativa",
        }
    )
)


st.dataframe(
    importancia_formatada,
    use_container_width=True,
    hide_index=True,
)


st.warning(
    "A importância apresentada é global e baseada na "
    "redução de impureza das árvores. Ela não informa "
    "se um determinado valor aumenta ou reduz o risco "
    "e não deve ser interpretada como causalidade."
)


# ============================================================
# RESULTADOS FINAIS NO TESTE
# ============================================================

st.markdown(
    "## Avaliação final no teste isolado"
)


(
    coluna_teste_1,
    coluna_teste_2,
    coluna_teste_3,
    coluna_teste_4,
    coluna_teste_5,
    coluna_teste_6,
) = st.columns(6)


with coluna_teste_1:

    st.metric(
        "Acurácia",
        f"{metricas_teste['acuracia']:.2%}",
    )


with coluna_teste_2:

    st.metric(
        "Precisão",
        f"{metricas_teste['precisao']:.2%}",
    )


with coluna_teste_3:

    st.metric(
        "Recall",
        f"{metricas_teste['recall']:.2%}",
    )


with coluna_teste_4:

    st.metric(
        "F1-score",
        f"{metricas_teste['f1_score']:.2%}",
    )


with coluna_teste_5:

    st.metric(
        "ROC AUC",
        f"{metricas_teste['roc_auc']:.4f}",
    )


with coluna_teste_6:

    st.metric(
        "PR AUC",
        f"{metricas_teste['pr_auc']:.4f}",
    )


taxa_base = metadata[
    "taxa_inadimplencia_teste"
]


ganho_pr_auc = (
    metricas_teste[
        "pr_auc"
    ]
    / taxa_base
)


st.write(
    f"A taxa de inadimplência no teste é de "
    f"**{taxa_base:.2%}**. O modelo atingiu PR AUC de "
    f"**{metricas_teste['pr_auc']:.4f}**, aproximadamente "
    f"**{ganho_pr_auc:.2f} vezes** a taxa-base."
)


# ============================================================
# MATRIZ DE CONFUSÃO
# ============================================================

st.markdown(
    "## Matriz de confusão"
)


(
    coluna_matriz_1,
    coluna_matriz_2,
    coluna_matriz_3,
    coluna_matriz_4,
) = st.columns(4)


with coluna_matriz_1:

    st.metric(
        "Verdadeiros negativos",
        formatar_numero(
            metricas_teste[
                "verdadeiros_negativos"
            ]
        ),
        help=(
            "Clientes adimplentes classificados "
            "corretamente como adimplentes."
        ),
    )


with coluna_matriz_2:

    st.metric(
        "Falsos positivos",
        formatar_numero(
            metricas_teste[
                "falsos_positivos"
            ]
        ),
        help=(
            "Clientes adimplentes classificados "
            "incorretamente como alto risco."
        ),
    )


with coluna_matriz_3:

    st.metric(
        "Falsos negativos",
        formatar_numero(
            metricas_teste[
                "falsos_negativos"
            ]
        ),
        help=(
            "Clientes inadimplentes não identificados "
            "pelo modelo."
        ),
    )


with coluna_matriz_4:

    st.metric(
        "Verdadeiros positivos",
        formatar_numero(
            metricas_teste[
                "verdadeiros_positivos"
            ]
        ),
        help=(
            "Clientes inadimplentes identificados "
            "corretamente pelo modelo."
        ),
    )


st.dataframe(
    matriz_teste,
    use_container_width=True,
)


st.warning(
    f"Os {formatar_numero(metricas_teste['falsos_negativos'])} "
    "falsos negativos representam clientes inadimplentes "
    "que não foram identificados pelo modelo."
)


# ============================================================
# DESEMPENHO POR CLASSE
# ============================================================

st.markdown(
    "## Desempenho por classe"
)


classes_desejadas = [
    "Adimplente",
    "Inadimplente",
]


relatorio_classes = (
    relatorio_teste[
        relatorio_teste[
            "classe"
        ].isin(
            classes_desejadas
        )
    ]
    .copy()
)


relatorio_classes[
    "precision"
] = relatorio_classes[
    "precision"
].map(
    lambda valor: f"{valor:.2%}"
)


relatorio_classes[
    "recall"
] = relatorio_classes[
    "recall"
].map(
    lambda valor: f"{valor:.2%}"
)


relatorio_classes[
    "f1-score"
] = relatorio_classes[
    "f1-score"
].map(
    lambda valor: f"{valor:.2%}"
)


relatorio_classes[
    "support"
] = relatorio_classes[
    "support"
].astype(
    int
)


relatorio_classes = (
    relatorio_classes.rename(
        columns={
            "classe": "Classe",
            "precision": "Precisão",
            "recall": "Recall",
            "f1-score": "F1-score",
            "support": "Quantidade",
        }
    )
)


st.dataframe(
    relatorio_classes,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# ANÁLISE DO THRESHOLD
# ============================================================

st.markdown(
    "## Análise do threshold"
)


threshold_recomendado = float(
    politica[
        "threshold_recomendado"
    ]
)


metricas_validacao = politica[
    "metricas_validacao"
]


(
    coluna_threshold_1,
    coluna_threshold_2,
    coluna_threshold_3,
    coluna_threshold_4,
) = st.columns(4)


with coluna_threshold_1:

    st.metric(
        "Threshold recomendado",
        f"{threshold_recomendado:.0%}",
    )


with coluna_threshold_2:

    st.metric(
        "Recall na validação",
        (
            f"{metricas_validacao['recall']:.2%}"
        ),
    )


with coluna_threshold_3:

    st.metric(
        "Precisão na validação",
        (
            f"{metricas_validacao['precisao']:.2%}"
        ),
    )


with coluna_threshold_4:

    st.metric(
        "F1-score na validação",
        (
            f"{metricas_validacao['f1_score']:.2%}"
        ),
    )


st.write(
    "**Critério utilizado:**",
    politica[
        "criterio"
    ],
)


thresholds_grafico = (
    analise_thresholds[
        [
            "limite",
            "precisao",
            "recall",
            "f1_score",
        ]
    ]
    .melt(
        id_vars="limite",
        var_name="metrica",
        value_name="valor",
    )
)


thresholds_grafico[
    "metrica"
] = thresholds_grafico[
    "metrica"
].map(
    {
        "precisao": "Precisão",
        "recall": "Recall",
        "f1_score": "F1-score",
    }
)


grafico_linhas_threshold = (
    alt.Chart(
        thresholds_grafico
    )
    .mark_line(
        point=True
    )
    .encode(
        x=alt.X(
            "limite:Q",
            title="Threshold",
            axis=alt.Axis(
                format=".0%"
            ),
        ),

        y=alt.Y(
            "valor:Q",
            title="Resultado da métrica",
            scale=alt.Scale(
                domain=[
                    0,
                    1,
                ]
            ),
            axis=alt.Axis(
                format=".0%"
            ),
        ),

        color=alt.Color(
            "metrica:N",
            title="Métrica",
        ),

        tooltip=[
            alt.Tooltip(
                "limite:Q",
                title="Threshold",
                format=".0%",
            ),

            alt.Tooltip(
                "metrica:N",
                title="Métrica",
            ),

            alt.Tooltip(
                "valor:Q",
                title="Resultado",
                format=".2%",
            ),
        ],
    )
)


dados_linha_threshold = pd.DataFrame(
    {
        "limite": [
            threshold_recomendado
        ]
    }
)


linha_threshold = (
    alt.Chart(
        dados_linha_threshold
    )
    .mark_rule(
        strokeDash=[
            6,
            4,
        ]
    )
    .encode(
        x=alt.X(
            "limite:Q"
        ),

        tooltip=[
            alt.Tooltip(
                "limite:Q",
                title="Threshold escolhido",
                format=".0%",
            )
        ],
    )
)


st.altair_chart(
    (
        grafico_linhas_threshold
        + linha_threshold
    ),
    use_container_width=True,
)


st.caption(
    "Diminuir o threshold tende a identificar mais "
    "inadimplentes, mas também aumenta a quantidade "
    "de clientes adimplentes sinalizados como risco."
)


# ============================================================
# METODOLOGIA
# ============================================================

st.markdown(
    "## Metodologia"
)


with st.expander(
    "Ver detalhes metodológicos"
):

    st.markdown(
        """
        1. Os registros duplicados foram removidos antes
        da separação dos dados.

        2. A base foi dividida em treinamento, validação
        e teste.

        3. Regressão Logística, Random Forest e
        HistGradientBoosting foram comparados na validação.

        4. O modelo foi selecionado pelo maior PR AUC.

        5. O threshold foi definido utilizando somente
        a base de validação.

        6. O modelo selecionado foi treinado novamente
        utilizando treino e validação.

        7. A avaliação final foi executada na base de
        teste isolada.

        8. A importância global das variáveis foi extraída
        do Random Forest treinado.
        """
    )


# ============================================================
# AVISO FINAL
# ============================================================

st.divider()


st.info(
    "Os resultados foram obtidos com dados históricos "
    "de clientes de cartão de crédito de Taiwan. "
    "O projeto demonstra um pipeline educacional de "
    "Ciência de Dados e não representa uma política "
    "real de concessão de crédito."
)