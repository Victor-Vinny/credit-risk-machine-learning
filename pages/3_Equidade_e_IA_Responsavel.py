import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Equidade do modelo",
    page_icon="⚖️",
    layout="wide",
)


# ============================================================
# CAMINHOS
# ============================================================

CAMINHO_COMPARACAO = (
    Path("reports")
    / "sensitive_feature_model_comparison.csv"
)

CAMINHO_EQUIDADE = (
    Path("reports")
    / "sensitive_feature_fairness.csv"
)

CAMINHO_DIFERENCAS = (
    Path("reports")
    / "sensitive_feature_fairness_gaps.csv"
)

CAMINHO_RESUMO = (
    Path("reports")
    / "sensitive_feature_comparison_summary.json"
)


# ============================================================
# FUNÇÕES DE CARREGAMENTO
# ============================================================

@st.cache_data
def carregar_csv(caminho):
    """
    Carrega um arquivo CSV.
    """

    if not caminho.exists():
        return None

    return pd.read_csv(
        caminho
    )


@st.cache_data
def carregar_json(caminho):
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


def formatar_numero(valor):
    """
    Formata números inteiros utilizando
    separador brasileiro.
    """

    return f"{int(valor):,}".replace(
        ",",
        ".",
    )


def formatar_diferenca_percentual(valor):
    """
    Formata diferenças percentuais utilizando
    sinal positivo ou negativo.
    """

    return f"{valor:+.2%}"


def aplicar_nomes_amigaveis(tabela):
    """
    Substitui os nomes técnicos dos modelos
    por nomes menores para exibição.
    """

    tabela = tabela.copy()

    tabela["modelo_exibicao"] = (
        tabela["modelo"]
        .replace(
            {
                "Modelo completo": (
                    "Modelo completo"
                ),

                "Modelo sem variáveis demográficas": (
                    "Modelo reduzido"
                ),
            }
        )
    )

    return tabela


def formatar_tabela_equidade(tabela):
    """
    Formata a tabela detalhada da análise
    por grupos.
    """

    tabela_formatada = tabela.copy()

    colunas_percentuais = [
        "taxa_inadimplencia_real",
        "taxa_classificacao_alto_risco",
        "precisao",
        "recall",
        "taxa_falso_positivo",
        "taxa_falso_negativo",
    ]

    for coluna in colunas_percentuais:

        tabela_formatada[coluna] = (
            tabela_formatada[coluna]
            .map(
                lambda valor: f"{valor:.2%}"
            )
        )

    tabela_formatada = (
        tabela_formatada.rename(
            columns={
                "modelo_exibicao": "Modelo",
                "grupo": "Grupo",
                "registros": "Registros",

                "taxa_inadimplencia_real": (
                    "Taxa real de inadimplência"
                ),

                "taxa_classificacao_alto_risco": (
                    "Classificados como alto risco"
                ),

                "precisao": "Precisão",
                "recall": "Recall",

                "taxa_falso_positivo": (
                    "Taxa de falso positivo"
                ),

                "taxa_falso_negativo": (
                    "Taxa de falso negativo"
                ),

                "verdadeiros_negativos": (
                    "Verdadeiros negativos"
                ),

                "falsos_positivos": (
                    "Falsos positivos"
                ),

                "falsos_negativos": (
                    "Falsos negativos"
                ),

                "verdadeiros_positivos": (
                    "Verdadeiros positivos"
                ),
            }
        )
    )

    colunas_exibidas = [
        "Modelo",
        "Grupo",
        "Registros",
        "Taxa real de inadimplência",
        "Classificados como alto risco",
        "Precisão",
        "Recall",
        "Taxa de falso positivo",
        "Taxa de falso negativo",
        "Verdadeiros negativos",
        "Falsos positivos",
        "Falsos negativos",
        "Verdadeiros positivos",
    ]

    return tabela_formatada[
        colunas_exibidas
    ]


# ============================================================
# CARREGAMENTO
# ============================================================

comparacao = carregar_csv(
    CAMINHO_COMPARACAO
)

equidade = carregar_csv(
    CAMINHO_EQUIDADE
)

diferencas = carregar_csv(
    CAMINHO_DIFERENCAS
)

resumo = carregar_json(
    CAMINHO_RESUMO
)


# ============================================================
# VERIFICAÇÃO
# ============================================================

arquivos = {
    "comparação dos modelos": comparacao,
    "análise detalhada de equidade": equidade,
    "diferenças de equidade": diferencas,
    "resumo da comparação": resumo,
}


arquivos_ausentes = [
    nome
    for nome, conteudo in arquivos.items()
    if conteudo is None
]


if arquivos_ausentes:

    st.error(
        "Alguns arquivos da comparação não foram encontrados."
    )

    st.write(
        "Arquivos ausentes:",
        ", ".join(
            arquivos_ausentes
        ),
    )

    st.code(
        "python compare_sensitive_features.py"
    )

    st.stop()


# ============================================================
# PREPARAÇÃO DOS NOMES
# ============================================================

comparacao = aplicar_nomes_amigaveis(
    comparacao
)

equidade = aplicar_nomes_amigaveis(
    equidade
)

diferencas = aplicar_nomes_amigaveis(
    diferencas
)


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "⚖️ Equidade e IA responsável"
)

st.write(
    "Comparação entre o modelo completo e uma versão "
    "que não utiliza diretamente sexo, escolaridade "
    "e estado civil."
)


st.warning(
    "O modelo reduzido ainda utiliza idade. Além disso, "
    "remover atributos demográficos não elimina possíveis "
    "efeitos indiretos ou variáveis que funcionem como proxies."
)


# ============================================================
# VISÃO GERAL DA COMPARAÇÃO
# ============================================================

st.markdown(
    "## Visão geral"
)


modelo_completo = resumo[
    "modelo_completo"
]

modelo_reduzido = resumo[
    "modelo_reduzido"
]


(
    coluna_geral_1,
    coluna_geral_2,
    coluna_geral_3,
    coluna_geral_4,
) = st.columns(4)


with coluna_geral_1:

    st.metric(
        "Diferença de PR AUC",
        formatar_diferenca_percentual(
            resumo[
                "diferenca_pr_auc"
            ]
        ),
        help=(
            "Diferença do modelo reduzido em relação "
            "ao modelo completo."
        ),
    )


with coluna_geral_2:

    st.metric(
        "Diferença de ROC AUC",
        formatar_diferenca_percentual(
            resumo[
                "diferenca_roc_auc"
            ]
        ),
    )


with coluna_geral_3:

    st.metric(
        "Diferença de recall",
        formatar_diferenca_percentual(
            resumo[
                "diferenca_recall"
            ]
        ),
    )


with coluna_geral_4:

    st.metric(
        "Diferença de precisão",
        formatar_diferenca_percentual(
            resumo[
                "diferenca_precisao"
            ]
        ),
    )


st.info(
    "As diferenças são apresentadas como resultado do modelo "
    "reduzido menos o resultado do modelo completo."
)


# ============================================================
# ATRIBUTOS REMOVIDOS
# ============================================================

with st.expander(
    "Ver configuração dos modelos"
):

    st.markdown(
        "### Modelo completo"
    )

    st.write(
        "Utiliza todas as 23 variáveis disponíveis, "
        "incluindo sexo, escolaridade e estado civil."
    )

    st.write(
        "**Threshold:**",
        f"{modelo_completo['threshold']:.0%}",
    )


    st.markdown(
        "### Modelo reduzido"
    )

    st.write(
        "Não utiliza diretamente:"
    )

    for variavel in resumo[
        "variaveis_removidas"
    ]:

        st.markdown(
            f"- `{variavel}`"
        )

    st.write(
        "**Threshold:**",
        f"{modelo_reduzido['threshold']:.0%}",
    )

    st.write(
        "**Critério do threshold:**",
        modelo_reduzido[
            "criterio_threshold"
        ],
    )


# ============================================================
# COMPARAÇÃO DAS MÉTRICAS
# ============================================================

st.markdown(
    "## Desempenho dos modelos"
)


comparacao_formatada = comparacao.copy()


comparacao_formatada[
    "usa_variaveis_demograficas"
] = comparacao_formatada[
    "usa_variaveis_demograficas"
].map(
    {
        True: "Sim",
        False: "Não",
    }
)


for coluna in [
    "threshold",
    "acuracia",
    "precisao",
    "recall",
    "f1_score",
]:

    comparacao_formatada[coluna] = (
        comparacao_formatada[coluna]
        .map(
            lambda valor: f"{valor:.2%}"
        )
    )


for coluna in [
    "roc_auc",
    "pr_auc",
]:

    comparacao_formatada[coluna] = (
        comparacao_formatada[coluna]
        .map(
            lambda valor: f"{valor:.4f}"
        )
    )


comparacao_formatada = (
    comparacao_formatada.rename(
        columns={
            "modelo_exibicao": "Modelo",

            "usa_variaveis_demograficas": (
                "Usa atributos removidos"
            ),

            "threshold": "Threshold",
            "acuracia": "Acurácia",
            "precisao": "Precisão",
            "recall": "Recall",
            "f1_score": "F1-score",
            "roc_auc": "ROC AUC",
            "pr_auc": "PR AUC",

            "falsos_positivos": (
                "Falsos positivos"
            ),

            "falsos_negativos": (
                "Falsos negativos"
            ),
        }
    )
)


st.dataframe(
    comparacao_formatada[
        [
            "Modelo",
            "Usa atributos removidos",
            "Threshold",
            "Acurácia",
            "Precisão",
            "Recall",
            "F1-score",
            "ROC AUC",
            "PR AUC",
            "Falsos positivos",
            "Falsos negativos",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# GRÁFICO DE DESEMPENHO
# ============================================================

dados_grafico_desempenho = (
    comparacao[
        [
            "modelo_exibicao",
            "precisao",
            "recall",
            "f1_score",
            "roc_auc",
            "pr_auc",
        ]
    ]
    .melt(
        id_vars="modelo_exibicao",
        var_name="metrica",
        value_name="valor",
    )
)


dados_grafico_desempenho[
    "metrica"
] = dados_grafico_desempenho[
    "metrica"
].map(
    {
        "precisao": "Precisão",
        "recall": "Recall",
        "f1_score": "F1-score",
        "roc_auc": "ROC AUC",
        "pr_auc": "PR AUC",
    }
)


grafico_desempenho = (
    alt.Chart(
        dados_grafico_desempenho
    )
    .mark_bar()
    .encode(
        x=alt.X(
            "metrica:N",
            title="Métrica",
        ),

        y=alt.Y(
            "valor:Q",
            title="Resultado",
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
            "modelo_exibicao:N",
            title="Modelo",
        ),

        xOffset=alt.XOffset(
            "modelo_exibicao:N"
        ),

        tooltip=[
            alt.Tooltip(
                "modelo_exibicao:N",
                title="Modelo",
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
    .properties(
        height=420,
    )
)


st.altair_chart(
    grafico_desempenho,
    use_container_width=True,
)


st.success(
    "A remoção das três variáveis provocou uma redução "
    "muito pequena de desempenho. O PR AUC caiu somente "
    f"{abs(resumo['diferenca_pr_auc']):.4f}."
)


# ============================================================
# DIFERENÇAS DE EQUIDADE
# ============================================================

st.markdown(
    "## Diferenças entre grupos"
)


st.write(
    "A tabela mostra a distância entre o grupo com maior "
    "resultado e o grupo com menor resultado para cada atributo."
)


diferencas_formatadas = diferencas.copy()


for coluna in [
    "diferenca_classificacao_alto_risco",
    "diferenca_recall",
    "diferenca_falso_positivo",
    "diferenca_falso_negativo",
]:

    diferencas_formatadas[coluna] = (
        diferencas_formatadas[coluna]
        .map(
            lambda valor: f"{valor:.2%}"
        )
    )


diferencas_formatadas = (
    diferencas_formatadas.rename(
        columns={
            "modelo_exibicao": "Modelo",
            "atributo": "Atributo",

            "diferenca_classificacao_alto_risco": (
                "Diferença na classificação de alto risco"
            ),

            "diferenca_recall": (
                "Diferença de recall"
            ),

            "diferenca_falso_positivo": (
                "Diferença de falso positivo"
            ),

            "diferenca_falso_negativo": (
                "Diferença de falso negativo"
            ),
        }
    )
)


st.dataframe(
    diferencas_formatadas[
        [
            "Modelo",
            "Atributo",
            "Diferença na classificação de alto risco",
            "Diferença de recall",
            "Diferença de falso positivo",
            "Diferença de falso negativo",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# GRÁFICO INTERATIVO DAS DIFERENÇAS
# ============================================================

metrica_diferenca = st.selectbox(
    "Métrica de diferença exibida no gráfico",
    options=[
        "diferenca_classificacao_alto_risco",
        "diferenca_recall",
        "diferenca_falso_positivo",
        "diferenca_falso_negativo",
    ],
    format_func=lambda valor: {
        "diferenca_classificacao_alto_risco": (
            "Classificação de alto risco"
        ),

        "diferenca_recall": (
            "Recall"
        ),

        "diferenca_falso_positivo": (
            "Taxa de falso positivo"
        ),

        "diferenca_falso_negativo": (
            "Taxa de falso negativo"
        ),
    }[valor],
)


dados_grafico_diferencas = diferencas[
    [
        "modelo_exibicao",
        "atributo",
        metrica_diferenca,
    ]
].copy()


dados_grafico_diferencas = (
    dados_grafico_diferencas.rename(
        columns={
            metrica_diferenca: "valor"
        }
    )
)


grafico_diferencas = (
    alt.Chart(
        dados_grafico_diferencas
    )
    .mark_bar()
    .encode(
        x=alt.X(
            "atributo:N",
            title="Atributo analisado",
        ),

        y=alt.Y(
            "valor:Q",
            title="Diferença entre grupos",
            axis=alt.Axis(
                format=".0%"
            ),
        ),

        color=alt.Color(
            "modelo_exibicao:N",
            title="Modelo",
        ),

        xOffset=alt.XOffset(
            "modelo_exibicao:N"
        ),

        tooltip=[
            alt.Tooltip(
                "modelo_exibicao:N",
                title="Modelo",
            ),

            alt.Tooltip(
                "atributo:N",
                title="Atributo",
            ),

            alt.Tooltip(
                "valor:Q",
                title="Diferença",
                format=".2%",
            ),
        ],
    )
    .properties(
        height=420,
    )
)


st.altair_chart(
    grafico_diferencas,
    use_container_width=True,
)


# ============================================================
# RESULTADOS DETALHADOS POR GRUPO
# ============================================================

st.markdown(
    "## Resultados detalhados por grupo"
)


atributos_disponiveis = (
    equidade[
        "atributo"
    ]
    .drop_duplicates()
    .tolist()
)


atributo_selecionado = st.selectbox(
    "Selecione o atributo",
    options=atributos_disponiveis,
)


equidade_atributo = (
    equidade[
        equidade[
            "atributo"
        ]
        == atributo_selecionado
    ]
    .copy()
)


grupos_pequenos = (
    equidade_atributo[
        equidade_atributo[
            "registros"
        ]
        < 100
    ][
        [
            "modelo_exibicao",
            "grupo",
            "registros",
        ]
    ]
    .drop_duplicates(
        subset=[
            "grupo"
        ]
    )
)


if not grupos_pequenos.empty:

    nomes_grupos = (
        grupos_pequenos[
            "grupo"
        ]
        .astype(str)
        .tolist()
    )

    st.warning(
        "Grupos com menos de 100 registros: "
        + ", ".join(nomes_grupos)
        + ". Os resultados desses grupos são mais instáveis."
    )


tabela_equidade_formatada = (
    formatar_tabela_equidade(
        equidade_atributo
    )
)


st.dataframe(
    tabela_equidade_formatada,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# GRÁFICO DETALHADO
# ============================================================

dados_grafico_grupos = (
    equidade_atributo[
        [
            "modelo_exibicao",
            "grupo",
            "taxa_classificacao_alto_risco",
            "recall",
            "taxa_falso_positivo",
            "taxa_falso_negativo",
        ]
    ]
    .melt(
        id_vars=[
            "modelo_exibicao",
            "grupo",
        ],
        var_name="metrica",
        value_name="valor",
    )
)


dados_grafico_grupos[
    "metrica"
] = dados_grafico_grupos[
    "metrica"
].map(
    {
        "taxa_classificacao_alto_risco": (
            "Classificados como alto risco"
        ),

        "recall": "Recall",

        "taxa_falso_positivo": (
            "Taxa de falso positivo"
        ),

        "taxa_falso_negativo": (
            "Taxa de falso negativo"
        ),
    }
)


metrica_grupo = st.selectbox(
    "Métrica detalhada",
    options=[
        "Classificados como alto risco",
        "Recall",
        "Taxa de falso positivo",
        "Taxa de falso negativo",
    ],
)


dados_grafico_grupos = (
    dados_grafico_grupos[
        dados_grafico_grupos[
            "metrica"
        ]
        == metrica_grupo
    ]
)


grafico_grupos = (
    alt.Chart(
        dados_grafico_grupos
    )
    .mark_bar()
    .encode(
        x=alt.X(
            "grupo:N",
            title=atributo_selecionado,
        ),

        y=alt.Y(
            "valor:Q",
            title=metrica_grupo,
            axis=alt.Axis(
                format=".0%"
            ),
            scale=alt.Scale(
                domain=[
                    0,
                    1,
                ]
            ),
        ),

        color=alt.Color(
            "modelo_exibicao:N",
            title="Modelo",
        ),

        xOffset=alt.XOffset(
            "modelo_exibicao:N"
        ),

        tooltip=[
            alt.Tooltip(
                "modelo_exibicao:N",
                title="Modelo",
            ),

            alt.Tooltip(
                "grupo:N",
                title="Grupo",
            ),

            alt.Tooltip(
                "valor:Q",
                title=metrica_grupo,
                format=".2%",
            ),
        ],
    )
    .properties(
        height=420,
    )
)


st.altair_chart(
    grafico_grupos,
    use_container_width=True,
)


# ============================================================
# INTERPRETAÇÃO
# ============================================================

st.markdown(
    "## Interpretação"
)


st.markdown(
    """
    - O modelo reduzido apresentou desempenho quase igual
      ao modelo completo.

    - A diferença na classificação de alto risco por sexo
      caiu de 6,11% para 4,01%.

    - A diferença na taxa de falsos positivos por sexo
      caiu de 6,07% para 4,63%.

    - A diferença de recall por sexo aumentou de 0,02%
      para 4,24%.

    - Na escolaridade, a diferença de classificação de
      alto risco diminuiu, mas a diferença de recall
      permaneceu elevada.

    - Parte da diferença de escolaridade é influenciada
      pelo grupo “Outros”, que possui somente 90 registros.

    - O resultado não demonstra que um dos modelos seja
      universalmente mais justo.
    """
)


# ============================================================
# RECOMENDAÇÃO PARA O PROJETO
# ============================================================

st.markdown(
    "## Recomendação para o projeto"
)


st.success(
    "Utilizar o modelo reduzido como versão principal da "
    "aplicação é uma decisão defensável: ele não utiliza "
    "diretamente sexo, escolaridade e estado civil e perdeu "
    "muito pouco desempenho preditivo."
)


st.warning(
    "Essa escolha não garante equidade. O modelo reduzido "
    "continua utilizando idade e outras variáveis podem "
    "conter informações indiretas relacionadas aos grupos."
)


# ============================================================
# LIMITAÇÕES
# ============================================================

with st.expander(
    "Ver limitações da comparação"
):

    st.markdown(
        """
        1. O modelo reduzido ainda utiliza idade.

        2. A remoção de atributos não elimina proxies.

        3. Alguns grupos possuem poucos registros.

        4. A base representa clientes históricos de Taiwan.

        5. As métricas não comprovam causalidade.

        6. Diferentes definições de equidade podem produzir
        conclusões diferentes.

        7. Uma aplicação real exigiria revisão jurídica,
        regulatória, estatística e de negócio.
        """
    )


# ============================================================
# AVISO FINAL
# ============================================================

st.divider()


st.caption(
    "Análise educacional de IA responsável. "
    "Os resultados não devem ser utilizados isoladamente "
    "para validar uma política real de crédito."
)