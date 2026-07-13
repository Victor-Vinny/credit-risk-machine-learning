from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Análise dos dados",
    page_icon="🔎",
    layout="wide",
)


# ============================================================
# CAMINHO DA BASE
# ============================================================

CAMINHO_BASE = (
    Path("data")
    / "processed"
    / "credit_default_real.csv"
)


# ============================================================
# FUNÇÕES
# ============================================================

@st.cache_data
def carregar_dados():
    """
    Carrega a base real processada.
    """

    if not CAMINHO_BASE.exists():
        return None

    return pd.read_csv(
        CAMINHO_BASE
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


def formatar_percentual(valor):
    """
    Formata valores decimais como percentual.
    """

    return f"{valor:.2%}"


# ============================================================
# CARREGAMENTO DA BASE
# ============================================================

dados = carregar_dados()


if dados is None:

    st.error(
        "A base real processada não foi encontrada. "
        "Execute: python prepare_real_data.py"
    )

    st.stop()


# ============================================================
# PREPARAÇÃO PARA ANÁLISE
# ============================================================

dados_analise = (
    dados.drop_duplicates()
    .reset_index(drop=True)
)


quantidade_original = len(
    dados
)

quantidade_duplicados = int(
    dados.duplicated().sum()
)

quantidade_registros = len(
    dados_analise
)

quantidade_colunas = len(
    dados_analise.columns
)

quantidade_variaveis_explicativas = (
    quantidade_colunas - 1
)

quantidade_ausentes = int(
    dados_analise
    .isna()
    .sum()
    .sum()
)

quantidade_inadimplentes = int(
    dados_analise[
        "inadimplente"
    ].sum()
)

quantidade_adimplentes = int(
    (
        dados_analise[
            "inadimplente"
        ]
        == 0
    ).sum()
)

taxa_inadimplencia = float(
    dados_analise[
        "inadimplente"
    ].mean()
)


# ============================================================
# MAPEAMENTOS
# ============================================================

mapa_sexo = {
    1: "Masculino",
    2: "Feminino",
}


mapa_escolaridade = {
    1: "Pós-graduação",
    2: "Universidade",
    3: "Ensino médio",
    4: "Outros",
}


mapa_estado_civil = {
    1: "Casado",
    2: "Solteiro",
    3: "Outros",
}


mapa_status_pagamento = {
    -2: "Código -2",
    -1: "Pagamento em dia",
    0: "Código 0",
    1: "1 mês de atraso",
    2: "2 meses de atraso",
    3: "3 meses de atraso",
    4: "4 meses de atraso",
    5: "5 meses de atraso",
    6: "6 meses de atraso",
    7: "7 meses de atraso",
    8: "8 meses de atraso",
    9: "9 meses ou mais",
}


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "🔎 Análise dos dados"
)

st.write(
    "Análise exploratória do dataset real "
    "Default of Credit Card Clients, disponibilizado "
    "pela UCI Machine Learning Repository."
)


# ============================================================
# VISÃO GERAL
# ============================================================

st.markdown(
    "## Visão geral da base"
)


(
    coluna_geral_1,
    coluna_geral_2,
    coluna_geral_3,
    coluna_geral_4,
    coluna_geral_5,
) = st.columns(5)


with coluna_geral_1:

    st.metric(
        "Registros utilizados",
        formatar_numero(
            quantidade_registros
        ),
    )


with coluna_geral_2:

    st.metric(
        "Variáveis explicativas",
        quantidade_variaveis_explicativas,
    )


with coluna_geral_3:

    st.metric(
        "Inadimplentes",
        formatar_numero(
            quantidade_inadimplentes
        ),
    )


with coluna_geral_4:

    st.metric(
        "Taxa de inadimplência",
        formatar_percentual(
            taxa_inadimplencia
        ),
    )


with coluna_geral_5:

    st.metric(
        "Valores ausentes",
        quantidade_ausentes,
    )


with st.expander(
    "Ver informações de qualidade da base"
):

    (
        coluna_qualidade_1,
        coluna_qualidade_2,
        coluna_qualidade_3,
    ) = st.columns(3)


    with coluna_qualidade_1:

        st.metric(
            "Registros originais",
            formatar_numero(
                quantidade_original
            ),
        )


    with coluna_qualidade_2:

        st.metric(
            "Duplicados identificados",
            formatar_numero(
                quantidade_duplicados
            ),
        )


    with coluna_qualidade_3:

        st.metric(
            "Registros após remoção",
            formatar_numero(
                quantidade_registros
            ),
        )


    st.write(
        "Os registros duplicados são removidos antes "
        "do treinamento para reduzir o risco de o mesmo "
        "perfil aparecer simultaneamente em treino e teste."
    )


# ============================================================
# DISTRIBUIÇÃO DA VARIÁVEL-ALVO
# ============================================================

st.markdown(
    "## Distribuição da inadimplência"
)


distribuicao_alvo = pd.DataFrame(
    {
        "Situação": [
            "Adimplente",
            "Inadimplente",
        ],

        "Quantidade": [
            quantidade_adimplentes,
            quantidade_inadimplentes,
        ],
    }
)


st.bar_chart(
    distribuicao_alvo,
    x="Situação",
    y="Quantidade",
)


(
    coluna_alvo_1,
    coluna_alvo_2,
) = st.columns(2)


with coluna_alvo_1:

    st.metric(
        "Clientes adimplentes",
        formatar_numero(
            quantidade_adimplentes
        ),
        f"{1 - taxa_inadimplencia:.2%}",
    )


with coluna_alvo_2:

    st.metric(
        "Clientes inadimplentes",
        formatar_numero(
            quantidade_inadimplentes
        ),
        f"{taxa_inadimplencia:.2%}",
    )


st.info(
    "A classe inadimplente representa aproximadamente "
    "22% dos registros. Por isso, a avaliação do modelo "
    "não deve utilizar somente a acurácia."
)


# ============================================================
# DISTRIBUIÇÃO POR SEXO
# ============================================================

st.markdown(
    "## Distribuição por sexo"
)


distribuicao_sexo = (
    dados_analise[
        "sexo"
    ]
    .map(
        mapa_sexo
    )
    .value_counts()
    .rename_axis(
        "Sexo"
    )
    .reset_index(
        name="Quantidade"
    )
)


st.bar_chart(
    distribuicao_sexo,
    x="Sexo",
    y="Quantidade",
)


taxa_sexo = (
    dados_analise
    .assign(
        Sexo=dados_analise[
            "sexo"
        ].map(
            mapa_sexo
        )
    )
    .groupby(
        "Sexo",
        observed=True,
    )["inadimplente"]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
)


taxa_sexo[
    "Taxa de inadimplência"
] = taxa_sexo[
    "Taxa"
].map(
    lambda valor: f"{valor:.2%}"
)


st.dataframe(
    taxa_sexo[
        [
            "Sexo",
            "Registros",
            "Inadimplentes",
            "Taxa de inadimplência",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# ESCOLARIDADE
# ============================================================

st.markdown(
    "## Escolaridade"
)


analise_escolaridade = (
    dados_analise
    .assign(
        Escolaridade=dados_analise[
            "escolaridade"
        ].map(
            mapa_escolaridade
        )
    )
    .groupby(
        "Escolaridade",
        observed=True,
    )["inadimplente"]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
    .sort_values(
        by="Registros",
        ascending=False,
    )
)


grafico_escolaridade = (
    analise_escolaridade[
        [
            "Escolaridade",
            "Registros",
        ]
    ]
)


st.bar_chart(
    grafico_escolaridade,
    x="Escolaridade",
    y="Registros",
)


analise_escolaridade[
    "Taxa de inadimplência"
] = analise_escolaridade[
    "Taxa"
].map(
    lambda valor: f"{valor:.2%}"
)


st.dataframe(
    analise_escolaridade[
        [
            "Escolaridade",
            "Registros",
            "Inadimplentes",
            "Taxa de inadimplência",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# ESTADO CIVIL
# ============================================================

st.markdown(
    "## Estado civil"
)


analise_estado_civil = (
    dados_analise
    .assign(
        Estado_civil=dados_analise[
            "estado_civil"
        ].map(
            mapa_estado_civil
        )
    )
    .groupby(
        "Estado_civil",
        observed=True,
    )["inadimplente"]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
)


analise_estado_civil[
    "Taxa de inadimplência"
] = analise_estado_civil[
    "Taxa"
].map(
    lambda valor: f"{valor:.2%}"
)


st.dataframe(
    analise_estado_civil[
        [
            "Estado_civil",
            "Registros",
            "Inadimplentes",
            "Taxa de inadimplência",
        ]
    ].rename(
        columns={
            "Estado_civil": "Estado civil",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# DISTRIBUIÇÃO DA IDADE
# ============================================================

st.markdown(
    "## Distribuição da idade"
)


faixas_idade = pd.cut(
    dados_analise[
        "idade"
    ],
    bins=[
        17,
        25,
        30,
        35,
        40,
        45,
        50,
        60,
        100,
    ],
    labels=[
        "18 a 25",
        "26 a 30",
        "31 a 35",
        "36 a 40",
        "41 a 45",
        "46 a 50",
        "51 a 60",
        "Acima de 60",
    ],
)


analise_idade = (
    dados_analise
    .assign(
        Faixa_idade=faixas_idade
    )
    .groupby(
        "Faixa_idade",
        observed=True,
    )["inadimplente"]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
)


st.bar_chart(
    analise_idade,
    x="Faixa_idade",
    y="Registros",
)


analise_idade[
    "Taxa de inadimplência"
] = analise_idade[
    "Taxa"
].map(
    lambda valor: f"{valor:.2%}"
)


st.dataframe(
    analise_idade[
        [
            "Faixa_idade",
            "Registros",
            "Inadimplentes",
            "Taxa de inadimplência",
        ]
    ].rename(
        columns={
            "Faixa_idade": "Faixa de idade",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# LIMITE DE CRÉDITO
# ============================================================

st.markdown(
    "## Distribuição do limite de crédito"
)


faixas_limite = pd.cut(
    dados_analise[
        "limite_credito"
    ],
    bins=[
        0,
        50_000,
        100_000,
        200_000,
        300_000,
        500_000,
        1_000_000,
        float("inf"),
    ],
    labels=[
        "Até 50 mil",
        "50 a 100 mil",
        "100 a 200 mil",
        "200 a 300 mil",
        "300 a 500 mil",
        "500 mil a 1 milhão",
        "Acima de 1 milhão",
    ],
    include_lowest=True,
)


analise_limite = (
    dados_analise
    .assign(
        Faixa_limite=faixas_limite
    )
    .groupby(
        "Faixa_limite",
        observed=True,
    )["inadimplente"]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
)


st.bar_chart(
    analise_limite,
    x="Faixa_limite",
    y="Registros",
)


analise_limite[
    "Taxa de inadimplência"
] = analise_limite[
    "Taxa"
].map(
    lambda valor: f"{valor:.2%}"
)


st.dataframe(
    analise_limite[
        [
            "Faixa_limite",
            "Registros",
            "Inadimplentes",
            "Taxa de inadimplência",
        ]
    ].rename(
        columns={
            "Faixa_limite": "Faixa de limite",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# STATUS DE PAGAMENTO MAIS RECENTE
# ============================================================

st.markdown(
    "## Status de pagamento mais recente"
)


analise_status_setembro = (
    dados_analise
    .assign(
        Status=dados_analise[
            "status_pagamento_set"
        ].map(
            mapa_status_pagamento
        )
    )
    .groupby(
        "Status",
        observed=True,
    )["inadimplente"]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
    .sort_values(
        by="Taxa",
        ascending=False,
    )
)


analise_status_setembro[
    "Taxa de inadimplência"
] = analise_status_setembro[
    "Taxa"
].map(
    lambda valor: f"{valor:.2%}"
)


st.dataframe(
    analise_status_setembro[
        [
            "Status",
            "Registros",
            "Inadimplentes",
            "Taxa de inadimplência",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


grafico_taxa_status = (
    analise_status_setembro[
        [
            "Status",
            "Taxa",
        ]
    ]
    .rename(
        columns={
            "Taxa": "Taxa de inadimplência",
        }
    )
)


st.bar_chart(
    grafico_taxa_status,
    x="Status",
    y="Taxa de inadimplência",
)


st.caption(
    "O status de pagamento mais recente é uma das "
    "informações mais relevantes para identificar risco."
)


# ============================================================
# EVOLUÇÃO DAS FATURAS E PAGAMENTOS
# ============================================================

st.markdown(
    "## Valores médios por mês"
)


meses_exibicao = [
    "Setembro",
    "Agosto",
    "Julho",
    "Junho",
    "Maio",
    "Abril",
]


colunas_fatura = [
    "valor_fatura_set",
    "valor_fatura_ago",
    "valor_fatura_jul",
    "valor_fatura_jun",
    "valor_fatura_mai",
    "valor_fatura_abr",
]


colunas_pagamento = [
    "valor_pagamento_set",
    "valor_pagamento_ago",
    "valor_pagamento_jul",
    "valor_pagamento_jun",
    "valor_pagamento_mai",
    "valor_pagamento_abr",
]


medias_mensais = pd.DataFrame(
    {
        "Mês": meses_exibicao,

        "Fatura média": [
            dados_analise[
                coluna
            ].mean()
            for coluna in colunas_fatura
        ],

        "Pagamento médio": [
            dados_analise[
                coluna
            ].mean()
            for coluna in colunas_pagamento
        ],
    }
)


st.line_chart(
    medias_mensais,
    x="Mês",
    y=[
        "Fatura média",
        "Pagamento médio",
    ],
)


medias_mensais_formatadas = (
    medias_mensais.copy()
)


medias_mensais_formatadas[
    "Fatura média"
] = medias_mensais_formatadas[
    "Fatura média"
].map(
    lambda valor: (
        f"{valor:,.2f}"
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )
)


medias_mensais_formatadas[
    "Pagamento médio"
] = medias_mensais_formatadas[
    "Pagamento médio"
].map(
    lambda valor: (
        f"{valor:,.2f}"
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )
)


st.dataframe(
    medias_mensais_formatadas,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# CORRELAÇÃO COM A INADIMPLÊNCIA
# ============================================================

st.markdown(
    "## Correlação com a inadimplência"
)


correlacoes = (
    dados_analise
    .corr(
        numeric_only=True
    )["inadimplente"]
    .drop(
        "inadimplente"
    )
    .sort_values(
        ascending=False
    )
    .reset_index()
)


correlacoes.columns = [
    "Variável",
    "Correlação",
]


st.bar_chart(
    correlacoes,
    x="Variável",
    y="Correlação",
)


st.caption(
    "Correlação mede associação linear. Um valor baixo "
    "não significa necessariamente que a variável não seja "
    "útil para modelos não lineares, como Random Forest."
)


# ============================================================
# ESTATÍSTICAS DESCRITIVAS
# ============================================================

st.markdown(
    "## Estatísticas descritivas"
)


estatisticas = (
    dados_analise
    .describe()
    .transpose()
    .reset_index()
    .rename(
        columns={
            "index": "Variável",
            "count": "Quantidade",
            "mean": "Média",
            "std": "Desvio padrão",
            "min": "Mínimo",
            "25%": "25%",
            "50%": "Mediana",
            "75%": "75%",
            "max": "Máximo",
        }
    )
)


st.dataframe(
    estatisticas,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# VISUALIZAÇÃO DOS REGISTROS
# ============================================================

st.markdown(
    "## Visualização dos registros"
)


quantidade_exibida = st.slider(
    "Quantidade de registros exibidos",
    min_value=5,
    max_value=100,
    value=20,
    step=5,
)


dados_exibicao = (
    dados_analise
    .head(
        quantidade_exibida
    )
    .copy()
)


dados_exibicao[
    "sexo"
] = dados_exibicao[
    "sexo"
].map(
    mapa_sexo
)


dados_exibicao[
    "escolaridade"
] = dados_exibicao[
    "escolaridade"
].map(
    mapa_escolaridade
)


dados_exibicao[
    "estado_civil"
] = dados_exibicao[
    "estado_civil"
].map(
    mapa_estado_civil
)


dados_exibicao[
    "inadimplente"
] = dados_exibicao[
    "inadimplente"
].map(
    {
        0: "Não",
        1: "Sim",
    }
)


st.dataframe(
    dados_exibicao,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# AVISO FINAL
# ============================================================

st.divider()


st.info(
    "A base contém dados históricos de clientes de cartão "
    "de crédito de Taiwan. Os padrões observados descrevem "
    "esse conjunto específico e não devem ser generalizados "
    "automaticamente para outras populações ou mercados."
)