import json
from pathlib import Path
from textwrap import dedent

import altair as alt
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Análise dos dados",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# FUNÇÕES VISUAIS
# ============================================================

def html(conteudo: str) -> None:
    """
    Renderiza componentes HTML e CSS.
    """

    st.html(
        dedent(conteudo).strip()
    )


html(
    """
    <style>
        :root {
            --ad-background: #080d15;
            --ad-surface: #111827;
            --ad-border: #273247;
            --ad-text: #f8fafc;
            --ad-muted: #94a3b8;
            --ad-blue: #2563eb;
            --ad-cyan: #38bdf8;
            --ad-green: #22c55e;
            --ad-yellow: #f59e0b;
            --ad-red: #ef4444;
            --ad-purple: #a855f7;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 84% 0%,
                    rgba(37, 99, 235, 0.12),
                    transparent 28rem
                ),
                var(--ad-background);
        }

        section[data-testid="stSidebar"] {
            background: #101621;
            border-right: 1px solid #293244;
        }

        .block-container {
            max-width: 1480px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        h1,
        h2,
        h3,
        h4 {
            letter-spacing: -0.025em;
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--ad-border);
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.62);
        }

        .ad-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            margin-bottom: 0.8rem;
            padding: 0.38rem 0.75rem;
            border: 1px solid rgba(56, 189, 248, 0.28);
            border-radius: 999px;
            background: rgba(14, 116, 144, 0.12);
            color: #7dd3fc;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }

        .ad-title {
            margin: 0;
            color: var(--ad-text);
            font-size: clamp(2.2rem, 4vw, 3.45rem);
            font-weight: 900;
            line-height: 1.05;
        }

        .ad-subtitle {
            max-width: 980px;
            margin: 0.75rem 0 1.2rem;
            color: #cbd5e1;
            font-size: 1.08rem;
            line-height: 1.65;
        }

        .ad-kicker {
            margin-top: 1.45rem;
            margin-bottom: 0.3rem;
            color: #60a5fa;
            font-size: 0.76rem;
            font-weight: 850;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .ad-section-title {
            margin: 0 0 0.35rem;
            color: var(--ad-text);
            font-size: 1.7rem;
            font-weight: 850;
        }

        .ad-description {
            margin: 0 0 1.1rem;
            color: var(--ad-muted);
            line-height: 1.55;
        }

        .ad-metric-card {
            height: 100%;
            min-height: 132px;
            padding: 1rem 1.05rem;
            border: 1px solid var(--ad-border);
            border-top: 3px solid var(--card-color);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.9);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
        }

        .ad-metric-label {
            margin-bottom: 0.45rem;
            color: var(--ad-muted);
            font-size: 0.78rem;
            font-weight: 750;
        }

        .ad-metric-value {
            color: var(--card-color);
            font-size: 1.75rem;
            font-weight: 900;
            line-height: 1.15;
        }

        .ad-metric-text {
            margin-top: 0.55rem;
            color: #cbd5e1;
            font-size: 0.77rem;
            line-height: 1.42;
        }

        .ad-insight {
            margin: 0.9rem 0;
            padding: 1rem 1.05rem;
            border: 1px solid rgba(56, 189, 248, 0.23);
            border-left: 5px solid #38bdf8;
            border-radius: 12px;
            background: rgba(14, 116, 144, 0.09);
            color: #dbeafe;
            line-height: 1.58;
        }

        .ad-insight-title {
            margin-bottom: 0.4rem;
            color: #7dd3fc;
            font-weight: 900;
        }

        .ad-warning {
            margin: 0.9rem 0;
            padding: 0.95rem 1rem;
            border: 1px solid rgba(245, 158, 11, 0.23);
            border-left: 4px solid #f59e0b;
            border-radius: 11px;
            background: rgba(120, 53, 15, 0.12);
            color: #fde68a;
            line-height: 1.55;
        }

        .ad-success {
            margin: 0.9rem 0;
            padding: 0.95rem 1rem;
            border: 1px solid rgba(34, 197, 94, 0.23);
            border-left: 4px solid #22c55e;
            border-radius: 11px;
            background: rgba(20, 83, 45, 0.13);
            color: #bbf7d0;
            line-height: 1.55;
        }

        .ad-comparison-card {
            height: 100%;
            min-height: 184px;
            padding: 1.05rem;
            border: 1px solid var(--ad-border);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.88);
        }

        .ad-comparison-title {
            min-height: 2.4rem;
            margin-bottom: 0.75rem;
            color: var(--ad-text);
            font-size: 0.9rem;
            font-weight: 850;
        }

        .ad-comparison-grid {
            display: grid;
            grid-template-columns: repeat(
                2,
                minmax(0, 1fr)
            );
            gap: 0.65rem;
        }

        .ad-comparison-item {
            padding: 0.7rem;
            border: 1px solid rgba(148, 163, 184, 0.13);
            border-radius: 10px;
            background: rgba(30, 41, 59, 0.48);
        }

        .ad-comparison-name {
            color: var(--ad-muted);
            font-size: 0.7rem;
        }

        .ad-comparison-value {
            margin-top: 0.25rem;
            font-size: 1.08rem;
            font-weight: 900;
        }

        .ad-comparison-item.good
        .ad-comparison-value {
            color: #4ade80;
        }

        .ad-comparison-item.risk
        .ad-comparison-value {
            color: #f87171;
        }

        .ad-comparison-help {
            margin-top: 0.7rem;
            color: #64748b;
            font-size: 0.72rem;
            line-height: 1.4;
        }

        .ad-quality-box {
            height: 100%;
            padding: 1rem;
            border: 1px solid var(--ad-border);
            border-radius: 13px;
            background: rgba(17, 24, 39, 0.84);
        }

        .ad-quality-value {
            color: #f8fafc;
            font-size: 1.45rem;
            font-weight: 900;
        }

        .ad-quality-label {
            margin-top: 0.28rem;
            color: var(--ad-muted);
            font-size: 0.75rem;
        }

        .ad-final {
            margin-top: 1rem;
            padding: 1.15rem;
            border: 1px solid rgba(37, 99, 235, 0.3);
            border-radius: 14px;
            background:
                linear-gradient(
                    120deg,
                    rgba(30, 64, 175, 0.17),
                    rgba(15, 23, 42, 0.92)
                );
        }

        .ad-final-title {
            margin-bottom: 0.5rem;
            color: #93c5fd;
            font-size: 1.03rem;
            font-weight: 900;
        }

        .ad-final-text {
            margin: 0;
            color: #dbeafe;
            line-height: 1.62;
        }

        @media (max-width: 900px) {
            .ad-metric-card,
            .ad-comparison-card {
                min-height: auto;
            }
        }
    </style>
    """
)


# ============================================================
# CAMINHOS
# ============================================================

CAMINHO_BASE = (
    Path("data")
    / "processed"
    / "credit_default_real.csv"
)

CAMINHO_METADATA = (
    Path("reports")
    / "real_model_metadata.json"
)


# ============================================================
# COLUNAS DA BASE
# ============================================================

COLUNAS_STATUS = [
    "status_pagamento_set",
    "status_pagamento_ago",
    "status_pagamento_jul",
    "status_pagamento_jun",
    "status_pagamento_mai",
    "status_pagamento_abr",
]


COLUNAS_FATURAS = [
    "valor_fatura_set",
    "valor_fatura_ago",
    "valor_fatura_jul",
    "valor_fatura_jun",
    "valor_fatura_mai",
    "valor_fatura_abr",
]


COLUNAS_PAGAMENTOS = [
    "valor_pagamento_set",
    "valor_pagamento_ago",
    "valor_pagamento_jul",
    "valor_pagamento_jun",
    "valor_pagamento_mai",
    "valor_pagamento_abr",
]


MESES_CRONOLOGICOS = [
    (
        "abr",
        "Abril",
        "valor_fatura_abr",
        "valor_pagamento_abr",
    ),
    (
        "mai",
        "Maio",
        "valor_fatura_mai",
        "valor_pagamento_mai",
    ),
    (
        "jun",
        "Junho",
        "valor_fatura_jun",
        "valor_pagamento_jun",
    ),
    (
        "jul",
        "Julho",
        "valor_fatura_jul",
        "valor_pagamento_jul",
    ),
    (
        "ago",
        "Agosto",
        "valor_fatura_ago",
        "valor_pagamento_ago",
    ),
    (
        "set",
        "Setembro",
        "valor_fatura_set",
        "valor_pagamento_set",
    ),
]


ORDEM_MESES = [
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
]


# ============================================================
# MAPEAMENTOS
# ============================================================

MAPA_SEXO = {
    1: "Masculino",
    2: "Feminino",
}


MAPA_ESCOLARIDADE = {
    1: "Pós-graduação",
    2: "Universidade",
    3: "Ensino médio",
    4: "Outros",
}


MAPA_ESTADO_CIVIL = {
    1: "Casado",
    2: "Solteiro",
    3: "Outros",
}


MAPA_STATUS_PAGAMENTO = {
    -2: "Sem atraso positivo — código -2",
    -1: "Pagamento em dia",
    0: "Sem atraso positivo — código 0",
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


NOMES_AMIGAVEIS = {
    "limite_credito": "Limite de crédito",
    "sexo": "Sexo",
    "escolaridade": "Escolaridade",
    "estado_civil": "Estado civil",
    "idade": "Idade",
    "status_pagamento_set": "Status de pagamento — setembro",
    "status_pagamento_ago": "Status de pagamento — agosto",
    "status_pagamento_jul": "Status de pagamento — julho",
    "status_pagamento_jun": "Status de pagamento — junho",
    "status_pagamento_mai": "Status de pagamento — maio",
    "status_pagamento_abr": "Status de pagamento — abril",
    "valor_fatura_set": "Fatura — setembro",
    "valor_fatura_ago": "Fatura — agosto",
    "valor_fatura_jul": "Fatura — julho",
    "valor_fatura_jun": "Fatura — junho",
    "valor_fatura_mai": "Fatura — maio",
    "valor_fatura_abr": "Fatura — abril",
    "valor_pagamento_set": "Pagamento — setembro",
    "valor_pagamento_ago": "Pagamento — agosto",
    "valor_pagamento_jul": "Pagamento — julho",
    "valor_pagamento_jun": "Pagamento — junho",
    "valor_pagamento_mai": "Pagamento — maio",
    "valor_pagamento_abr": "Pagamento — abril",
}


# ============================================================
# FUNÇÕES DE CARREGAMENTO
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


@st.cache_data
def carregar_json(
    caminho: Path,
):
    """
    Carrega um arquivo JSON.
    """

    if not caminho.exists():
        return None

    with caminho.open(
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(
            arquivo
        )


def formatar_numero(
    valor,
) -> str:
    """
    Formata números inteiros no padrão brasileiro.
    """

    return f"{int(valor):,}".replace(
        ",",
        ".",
    )


def formatar_percentual(
    valor,
    casas: int = 1,
) -> str:
    """
    Formata valores decimais como percentual.
    """

    return format(
        float(valor),
        f".{casas}%",
    )


def formatar_valor(
    valor,
) -> str:
    """
    Formata valores na moeda original da base.
    """

    numero = (
        f"{float(valor):,.0f}"
        .replace(
            ",",
            ".",
        )
    )

    return f"NT$ {numero}"


def renderizar_metrica(
    titulo: str,
    valor: str,
    texto: str,
    cor: str,
) -> None:
    """
    Renderiza um cartão de métrica.
    """

    html(
        f"""
        <div
            class="ad-metric-card"
            style="--card-color: {cor};"
        >
            <div class="ad-metric-label">
                {titulo}
            </div>

            <div class="ad-metric-value">
                {valor}
            </div>

            <div class="ad-metric-text">
                {texto}
            </div>
        </div>
        """
    )


def renderizar_comparacao(
    titulo: str,
    valor_adimplente: str,
    valor_inadimplente: str,
    ajuda: str,
) -> None:
    """
    Renderiza uma comparação entre as duas classes.
    """

    html(
        f"""
        <div class="ad-comparison-card">
            <div class="ad-comparison-title">
                {titulo}
            </div>

            <div class="ad-comparison-grid">
                <div class="ad-comparison-item good">
                    <div class="ad-comparison-name">
                        Adimplentes
                    </div>

                    <div class="ad-comparison-value">
                        {valor_adimplente}
                    </div>
                </div>

                <div class="ad-comparison-item risk">
                    <div class="ad-comparison-name">
                        Inadimplentes
                    </div>

                    <div class="ad-comparison-value">
                        {valor_inadimplente}
                    </div>
                </div>
            </div>

            <div class="ad-comparison-help">
                {ajuda}
            </div>
        </div>
        """
    )


def aplicar_tema(
    grafico,
):
    """
    Aplica o estilo visual padrão aos gráficos Altair.
    """

    return (
        grafico
        .configure(
            background="transparent",
        )
        .configure_view(
            strokeOpacity=0,
        )
        .configure_axis(
            gridColor="#263043",
            domainColor="#475569",
            labelColor="#cbd5e1",
            titleColor="#94a3b8",
        )
        .configure_legend(
            labelColor="#cbd5e1",
            titleColor="#94a3b8",
        )
        .configure_title(
            color="#f8fafc",
        )
    )


# ============================================================
# CARREGAMENTO
# ============================================================

dados = carregar_dados()

metadata = carregar_json(
    CAMINHO_METADATA
)


if dados is None:

    st.error(
        "A base real processada não foi encontrada. "
        "Execute: python prepare_real_data.py"
    )

    st.stop()


# ============================================================
# PREPARAÇÃO DA BASE
# ============================================================

dados_analise = (
    dados
    .drop_duplicates()
    .reset_index(
        drop=True
    )
)


dados_analise[
    "Situação"
] = dados_analise[
    "inadimplente"
].map(
    {
        0: "Adimplente",
        1: "Inadimplente",
    }
)


dados_analise[
    "Sexo"
] = (
    dados_analise[
        "sexo"
    ]
    .map(
        MAPA_SEXO
    )
    .fillna(
        "Não informado"
    )
)


dados_analise[
    "Escolaridade"
] = (
    dados_analise[
        "escolaridade"
    ]
    .map(
        MAPA_ESCOLARIDADE
    )
    .fillna(
        "Não informado"
    )
)


dados_analise[
    "Estado civil"
] = (
    dados_analise[
        "estado_civil"
    ]
    .map(
        MAPA_ESTADO_CIVIL
    )
    .fillna(
        "Não informado"
    )
)


dados_analise[
    "meses_com_atraso"
] = (
    dados_analise[
        COLUNAS_STATUS
    ]
    .gt(
        0
    )
    .sum(
        axis=1
    )
)


dados_analise[
    "teve_atraso"
] = (
    dados_analise[
        "meses_com_atraso"
    ]
    > 0
)


dados_analise[
    "maior_atraso"
] = (
    dados_analise[
        COLUNAS_STATUS
    ]
    .max(
        axis=1
    )
    .clip(
        lower=0
    )
)


faturas_positivas = (
    dados_analise[
        COLUNAS_FATURAS
    ]
    .clip(
        lower=0
    )
)


dados_analise[
    "total_faturas_6m"
] = (
    faturas_positivas
    .sum(
        axis=1
    )
)


dados_analise[
    "total_pagamentos_6m"
] = (
    dados_analise[
        COLUNAS_PAGAMENTOS
    ]
    .sum(
        axis=1
    )
)


denominador_faturas = (
    dados_analise[
        "total_faturas_6m"
    ]
    .replace(
        0,
        pd.NA,
    )
)


dados_analise[
    "cobertura_pagamentos"
] = (
    dados_analise[
        "total_pagamentos_6m"
    ]
    .div(
        denominador_faturas
    )
    .fillna(
        0
    )
)


denominador_limite = (
    dados_analise[
        "limite_credito"
    ]
    .replace(
        0,
        pd.NA,
    )
)


dados_analise[
    "utilizacao_setembro"
] = (
    dados_analise[
        "valor_fatura_set"
    ]
    .clip(
        lower=0
    )
    .div(
        denominador_limite
    )
    .fillna(
        0
    )
)


# ============================================================
# MÉTRICAS GERAIS
# ============================================================

quantidade_registros = len(
    dados_analise
)

quantidade_colunas = len(
    dados.columns
)

quantidade_variaveis = (
    quantidade_colunas - 1
)

quantidade_ausentes = int(
    dados_analise
    .isna()
    .sum()
    .sum()
)

quantidade_duplicados_processados = int(
    dados
    .duplicated()
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

idade_mediana = float(
    dados_analise[
        "idade"
    ].median()
)

limite_mediano = float(
    dados_analise[
        "limite_credito"
    ].median()
)


if metadata is not None:

    registros_originais = int(
        metadata.get(
            "registros_originais",
            quantidade_registros,
        )
    )

    duplicados_removidos = int(
        metadata.get(
            "duplicados_removidos",
            0,
        )
    )

else:

    registros_originais = quantidade_registros

    duplicados_removidos = 0


# ============================================================
# RESUMO COMPORTAMENTAL POR CLASSE
# ============================================================

resumo_comportamento = (
    dados_analise
    .groupby(
        "Situação",
        observed=True,
    )
    .agg(
        percentual_com_atraso=(
            "teve_atraso",
            "mean",
        ),

        mediana_meses_atraso=(
            "meses_com_atraso",
            "median",
        ),

        utilizacao_mediana=(
            "utilizacao_setembro",
            "median",
        ),

        cobertura_mediana=(
            "cobertura_pagamentos",
            "median",
        ),

        limite_mediano=(
            "limite_credito",
            "median",
        ),

        idade_mediana=(
            "idade",
            "median",
        ),
    )
)


resumo_adimplente = resumo_comportamento.loc[
    "Adimplente"
]

resumo_inadimplente = resumo_comportamento.loc[
    "Inadimplente"
]


# ============================================================
# CABEÇALHO
# ============================================================

html(
    """
    <div class="ad-badge">
        ● Análise exploratória do Behavioral Score
    </div>

    <h1 class="ad-title">
        🔎 Análise dos dados
    </h1>

    <p class="ad-subtitle">
        Entenda quem são os clientes da base e como atrasos,
        faturas, pagamentos e utilização do limite se
        relacionam com a inadimplência observada no mês
        seguinte.
    </p>
    """
)


st.info(
    "Esta base representa clientes que já possuíam cartão "
    "ou limite de crédito. Portanto, o projeto analisa o "
    "comportamento recente da carteira, e não uma primeira "
    "solicitação de crédito."
)


with st.expander(
    "Entenda esta página em 30 segundos"
):

    st.markdown(
        """
        1. A base contém o comportamento financeiro de
           clientes ao longo de seis meses.

        2. A variável-alvo informa se o cliente ficou
           inadimplente no mês seguinte.

        3. Os gráficos comparam clientes adimplentes e
           inadimplentes.

        4. As diferenças encontradas são associações
           observadas na base e não provam causalidade.
        """
    )


# ============================================================
# VISÃO GERAL
# ============================================================

html(
    """
    <div class="ad-kicker">
        Visão geral
    </div>

    <h2 class="ad-section-title">
        Qual é o tamanho e o perfil básico da base?
    </h2>

    <p class="ad-description">
        A análise utiliza a base processada após a remoção
        de registros duplicados.
    </p>
    """
)


(
    coluna_geral_1,
    coluna_geral_2,
    coluna_geral_3,
    coluna_geral_4,
    coluna_geral_5,
) = st.columns(5)


with coluna_geral_1:

    renderizar_metrica(
        titulo="Clientes analisados",
        valor=formatar_numero(
            quantidade_registros
        ),
        texto=(
            "Registros utilizados nas análises "
            "e no desenvolvimento do modelo."
        ),
        cor="#38bdf8",
    )


with coluna_geral_2:

    renderizar_metrica(
        titulo="Inadimplentes",
        valor=formatar_numero(
            quantidade_inadimplentes
        ),
        texto=(
            "Clientes que ficaram inadimplentes "
            "no período-alvo."
        ),
        cor="#ef4444",
    )


with coluna_geral_3:

    renderizar_metrica(
        titulo="Taxa de inadimplência",
        valor=formatar_percentual(
            taxa_inadimplencia,
            2,
        ),
        texto=(
            "Participação da classe minoritária "
            "na base processada."
        ),
        cor="#f59e0b",
    )


with coluna_geral_4:

    renderizar_metrica(
        titulo="Idade mediana",
        valor=f"{idade_mediana:.0f} anos",
        texto=(
            "Metade dos clientes possui idade "
            "abaixo desse valor."
        ),
        cor="#a855f7",
    )


with coluna_geral_5:

    renderizar_metrica(
        titulo="Limite mediano",
        valor=formatar_valor(
            limite_mediano
        ),
        texto=(
            "Valor central do limite de crédito "
            "disponível na carteira."
        ),
        cor="#22c55e",
    )


with st.expander(
    "Ver qualidade e preparação da base"
):

    (
        coluna_qualidade_1,
        coluna_qualidade_2,
        coluna_qualidade_3,
        coluna_qualidade_4,
    ) = st.columns(4)


    with coluna_qualidade_1:

        html(
            f"""
            <div class="ad-quality-box">
                <div class="ad-quality-value">
                    {
                        formatar_numero(
                            registros_originais
                        )
                    }
                </div>

                <div class="ad-quality-label">
                    Registros originais
                </div>
            </div>
            """
        )


    with coluna_qualidade_2:

        html(
            f"""
            <div class="ad-quality-box">
                <div class="ad-quality-value">
                    {
                        formatar_numero(
                            duplicados_removidos
                        )
                    }
                </div>

                <div class="ad-quality-label">
                    Duplicados removidos
                </div>
            </div>
            """
        )


    with coluna_qualidade_3:

        html(
            f"""
            <div class="ad-quality-box">
                <div class="ad-quality-value">
                    {quantidade_variaveis}
                </div>

                <div class="ad-quality-label">
                    Variáveis explicativas
                </div>
            </div>
            """
        )


    with coluna_qualidade_4:

        html(
            f"""
            <div class="ad-quality-box">
                <div class="ad-quality-value">
                    {quantidade_ausentes}
                </div>

                <div class="ad-quality-label">
                    Valores ausentes
                </div>
            </div>
            """
        )


    st.caption(
        "A base processada possui "
        f"{quantidade_duplicados_processados} duplicados "
        "remanescentes."
    )


# ============================================================
# DISTRIBUIÇÃO DA VARIÁVEL-ALVO
# ============================================================

html(
    """
    <div class="ad-kicker">
        Variável-alvo
    </div>

    <h2 class="ad-section-title">
        Quantos clientes ficaram inadimplentes?
    </h2>

    <p class="ad-description">
        A variável-alvo separa os clientes que permaneceram
        adimplentes daqueles que ficaram inadimplentes
        no mês seguinte.
    </p>
    """
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


distribuicao_alvo[
    "Percentual"
] = (
    distribuicao_alvo[
        "Quantidade"
    ]
    / distribuicao_alvo[
        "Quantidade"
    ].sum()
)


coluna_grafico_alvo, coluna_texto_alvo = st.columns(
    [
        0.9,
        1.1,
    ]
)


with coluna_grafico_alvo:

    grafico_rosca = (
        alt.Chart(
            distribuicao_alvo
        )
        .mark_arc(
            innerRadius=72,
            outerRadius=120,
        )
        .encode(
            theta=alt.Theta(
                "Quantidade:Q",
            ),

            color=alt.Color(
                "Situação:N",
                title=None,
                scale=alt.Scale(
                    domain=[
                        "Adimplente",
                        "Inadimplente",
                    ],
                    range=[
                        "#22c55e",
                        "#ef4444",
                    ],
                ),
            ),

            tooltip=[
                alt.Tooltip(
                    "Situação:N",
                    title="Situação",
                ),

                alt.Tooltip(
                    "Quantidade:Q",
                    title="Clientes",
                    format=",",
                ),

                alt.Tooltip(
                    "Percentual:Q",
                    title="Percentual",
                    format=".2%",
                ),
            ],
        )
        .properties(
            height=320,
        )
    )


    st.altair_chart(
        aplicar_tema(
            grafico_rosca
        ),
        use_container_width=True,
        theme=None,
    )


with coluna_texto_alvo:

    html(
        f"""
        <div class="ad-insight">
            <div class="ad-insight-title">
                Por que essa distribuição importa?
            </div>

            A classe inadimplente representa
            <strong>
                {
                    formatar_percentual(
                        taxa_inadimplencia,
                        1
                    )
                }
            </strong>
            dos clientes.

            Isso significa que a base é desbalanceada:
            existem muito mais adimplentes do que
            inadimplentes.

            Por esse motivo, métricas como
            <strong>recall, precisão e PR AUC</strong>
            são mais informativas do que analisar apenas
            a acurácia.
        </div>
        """
    )


    (
        coluna_alvo_1,
        coluna_alvo_2,
    ) = st.columns(2)


    coluna_alvo_1.metric(
        "Adimplentes",
        formatar_numero(
            quantidade_adimplentes
        ),
        formatar_percentual(
            1 - taxa_inadimplencia,
            1,
        ),
    )


    coluna_alvo_2.metric(
        "Inadimplentes",
        formatar_numero(
            quantidade_inadimplentes
        ),
        formatar_percentual(
            taxa_inadimplencia,
            1,
        ),
    )


# ============================================================
# COMPORTAMENTO FINANCEIRO
# ============================================================

html(
    """
    <div class="ad-kicker">
        Comportamento financeiro
    </div>

    <h2 class="ad-section-title">
        O que diferencia adimplentes e inadimplentes?
    </h2>

    <p class="ad-description">
        As comparações abaixo resumem atrasos, utilização
        do limite, cobertura dos pagamentos e limite
        disponível nos dois grupos.
    </p>
    """
)


(
    coluna_comparacao_1,
    coluna_comparacao_2,
    coluna_comparacao_3,
    coluna_comparacao_4,
) = st.columns(4)


with coluna_comparacao_1:

    renderizar_comparacao(
        titulo="Clientes com pelo menos um mês de atraso",
        valor_adimplente=formatar_percentual(
            resumo_adimplente[
                "percentual_com_atraso"
            ],
            1,
        ),
        valor_inadimplente=formatar_percentual(
            resumo_inadimplente[
                "percentual_com_atraso"
            ],
            1,
        ),
        ajuda=(
            "Percentual de clientes com algum código "
            "positivo de atraso nos seis meses."
        ),
    )


with coluna_comparacao_2:

    renderizar_comparacao(
        titulo="Utilização mediana do limite em setembro",
        valor_adimplente=formatar_percentual(
            resumo_adimplente[
                "utilizacao_mediana"
            ],
            1,
        ),
        valor_inadimplente=formatar_percentual(
            resumo_inadimplente[
                "utilizacao_mediana"
            ],
            1,
        ),
        ajuda=(
            "Fatura mais recente dividida pelo limite "
            "de crédito disponível."
        ),
    )


with coluna_comparacao_3:

    renderizar_comparacao(
        titulo="Cobertura mediana dos pagamentos",
        valor_adimplente=formatar_percentual(
            resumo_adimplente[
                "cobertura_mediana"
            ],
            1,
        ),
        valor_inadimplente=formatar_percentual(
            resumo_inadimplente[
                "cobertura_mediana"
            ],
            1,
        ),
        ajuda=(
            "Total pago nos seis meses dividido pelo "
            "total positivo das faturas."
        ),
    )


with coluna_comparacao_4:

    renderizar_comparacao(
        titulo="Limite de crédito mediano",
        valor_adimplente=formatar_valor(
            resumo_adimplente[
                "limite_mediano"
            ]
        ),
        valor_inadimplente=formatar_valor(
            resumo_inadimplente[
                "limite_mediano"
            ]
        ),
        ajuda=(
            "Comparação do valor mediano do limite "
            "disponível entre os grupos."
        ),
    )


taxa_atraso_adimplente = formatar_percentual(
    resumo_adimplente[
        "percentual_com_atraso"
    ],
    1,
)

taxa_atraso_inadimplente = formatar_percentual(
    resumo_inadimplente[
        "percentual_com_atraso"
    ],
    1,
)


html(
    f"""
    <div class="ad-insight">
        <div class="ad-insight-title">
            Principal leitura comportamental
        </div>

        Na base analisada,
        <strong>{taxa_atraso_inadimplente}</strong>
        dos inadimplentes apresentaram pelo menos um mês
        com atraso positivo, contra
        <strong>{taxa_atraso_adimplente}</strong>
        entre os adimplentes.

        Essa diferença ajuda a explicar por que o histórico
        recente de pagamentos é tão relevante para o modelo.
    </div>
    """
)


# ============================================================
# STATUS DE PAGAMENTO MAIS RECENTE
# ============================================================

html(
    """
    <div class="ad-kicker">
        Histórico de pagamento
    </div>

    <h2 class="ad-section-title">
        Como o atraso mais recente se relaciona com o risco?
    </h2>

    <p class="ad-description">
        Setembro é o mês mais recente disponível na base
        e uma das informações mais importantes do modelo.
    </p>
    """
)


analise_status_setembro = (
    dados_analise
    .groupby(
        "status_pagamento_set",
        observed=True,
    )[
        "inadimplente"
    ]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
    .sort_values(
        "status_pagamento_set"
    )
)


analise_status_setembro[
    "Status"
] = (
    analise_status_setembro[
        "status_pagamento_set"
    ]
    .map(
        MAPA_STATUS_PAGAMENTO
    )
    .fillna(
        "Outro código"
    )
)


ordem_status = analise_status_setembro[
    "Status"
].tolist()


grafico_status = (
    alt.Chart(
        analise_status_setembro
    )
    .mark_bar(
        cornerRadiusEnd=5,
    )
    .encode(
        y=alt.Y(
            "Status:N",
            title=None,
            sort=ordem_status,
        ),

        x=alt.X(
            "Taxa:Q",
            title="Taxa de inadimplência",
            axis=alt.Axis(
                format=".0%",
            ),
        ),

        color=alt.Color(
            "Taxa:Q",
            title="Taxa",
            scale=alt.Scale(
                scheme="redyellowgreen",
                reverse=True,
            ),
        ),

        tooltip=[
            alt.Tooltip(
                "Status:N",
                title="Status",
            ),

            alt.Tooltip(
                "Registros:Q",
                title="Clientes",
                format=",",
            ),

            alt.Tooltip(
                "Inadimplentes:Q",
                title="Inadimplentes",
                format=",",
            ),

            alt.Tooltip(
                "Taxa:Q",
                title="Taxa",
                format=".2%",
            ),
        ],
    )
    .properties(
        height=max(
            360,
            len(
                analise_status_setembro
            )
            * 37,
        ),
    )
)


st.altair_chart(
    aplicar_tema(
        grafico_status
    ),
    use_container_width=True,
    theme=None,
)


html(
    """
    <div class="ad-warning">
        ⚠️ O gráfico mostra associação: atrasos maiores
        aparecem acompanhados de taxas mais altas de
        inadimplência. Isso não significa que uma única
        variável determine sozinha o resultado do cliente.
    </div>
    """
)


with st.expander(
    "Ver tabela do status de pagamento"
):

    tabela_status = (
        analise_status_setembro[
            [
                "Status",
                "Registros",
                "Inadimplentes",
                "Taxa",
            ]
        ]
        .copy()
    )


    tabela_status[
        "Taxa"
    ] = tabela_status[
        "Taxa"
    ].map(
        lambda valor: formatar_percentual(
            valor,
            2,
        )
    )


    tabela_status = tabela_status.rename(
        columns={
            "Taxa": "Taxa de inadimplência",
        }
    )


    st.dataframe(
        tabela_status,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# EVOLUÇÃO DAS FATURAS E PAGAMENTOS
# ============================================================

html(
    """
    <div class="ad-kicker">
        Evolução mensal
    </div>

    <h2 class="ad-section-title">
        Como faturas e pagamentos evoluíram?
    </h2>

    <p class="ad-description">
        Os gráficos comparam os valores médios observados
        entre clientes adimplentes e inadimplentes.
    </p>
    """
)


linhas_faturas = []

linhas_pagamentos = []


for situacao in [
    "Adimplente",
    "Inadimplente",
]:

    dados_grupo = dados_analise[
        dados_analise[
            "Situação"
        ]
        == situacao
    ]


    for (
        codigo_mes,
        nome_mes,
        coluna_fatura,
        coluna_pagamento,
    ) in MESES_CRONOLOGICOS:

        linhas_faturas.append(
            {
                "Mês": nome_mes,
                "Situação": situacao,
                "Valor médio": float(
                    dados_grupo[
                        coluna_fatura
                    ].mean()
                ),
            }
        )


        linhas_pagamentos.append(
            {
                "Mês": nome_mes,
                "Situação": situacao,
                "Valor médio": float(
                    dados_grupo[
                        coluna_pagamento
                    ].mean()
                ),
            }
        )


dataframe_faturas = pd.DataFrame(
    linhas_faturas
)

dataframe_pagamentos = pd.DataFrame(
    linhas_pagamentos
)


cores_situacao = alt.Scale(
    domain=[
        "Adimplente",
        "Inadimplente",
    ],
    range=[
        "#22c55e",
        "#ef4444",
    ],
)


grafico_faturas = (
    alt.Chart(
        dataframe_faturas
    )
    .mark_line(
        point=True,
        strokeWidth=3,
    )
    .encode(
        x=alt.X(
            "Mês:N",
            title=None,
            sort=ORDEM_MESES,
        ),

        y=alt.Y(
            "Valor médio:Q",
            title="Fatura média em NT$",
            axis=alt.Axis(
                format="~s",
            ),
        ),

        color=alt.Color(
            "Situação:N",
            title=None,
            scale=cores_situacao,
        ),

        tooltip=[
            alt.Tooltip(
                "Mês:N",
                title="Mês",
            ),

            alt.Tooltip(
                "Situação:N",
                title="Situação",
            ),

            alt.Tooltip(
                "Valor médio:Q",
                title="Fatura média",
                format=",.0f",
            ),
        ],
    )
    .properties(
        height=330,
        title="Faturas médias",
    )
)


grafico_pagamentos = (
    alt.Chart(
        dataframe_pagamentos
    )
    .mark_line(
        point=True,
        strokeWidth=3,
    )
    .encode(
        x=alt.X(
            "Mês:N",
            title=None,
            sort=ORDEM_MESES,
        ),

        y=alt.Y(
            "Valor médio:Q",
            title="Pagamento médio em NT$",
            axis=alt.Axis(
                format="~s",
            ),
        ),

        color=alt.Color(
            "Situação:N",
            title=None,
            scale=cores_situacao,
        ),

        tooltip=[
            alt.Tooltip(
                "Mês:N",
                title="Mês",
            ),

            alt.Tooltip(
                "Situação:N",
                title="Situação",
            ),

            alt.Tooltip(
                "Valor médio:Q",
                title="Pagamento médio",
                format=",.0f",
            ),
        ],
    )
    .properties(
        height=330,
        title="Pagamentos médios",
    )
)


coluna_faturas, coluna_pagamentos = st.columns(2)


with coluna_faturas:

    st.altair_chart(
        aplicar_tema(
            grafico_faturas
        ),
        use_container_width=True,
        theme=None,
    )


with coluna_pagamentos:

    st.altair_chart(
        aplicar_tema(
            grafico_pagamentos
        ),
        use_container_width=True,
        theme=None,
    )


html(
    """
    <div class="ad-insight">
        <div class="ad-insight-title">
            Como interpretar estes gráficos?
        </div>

        Faturas elevadas não significam automaticamente
        inadimplência. O risco depende da combinação entre
        valor devido, limite disponível, pagamentos realizados
        e histórico de atrasos.
    </div>
    """
)


# ============================================================
# IDADE E LIMITE
# ============================================================

html(
    """
    <div class="ad-kicker">
        Perfil da carteira
    </div>

    <h2 class="ad-section-title">
        Como idade e limite aparecem na base?
    </h2>

    <p class="ad-description">
        As faixas abaixo mostram quantidade de clientes
        e taxa de inadimplência observada.
    </p>
    """
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
        Faixa=faixas_idade
    )
    .groupby(
        "Faixa",
        observed=True,
    )[
        "inadimplente"
    ]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
)


analise_idade[
    "Faixa"
] = analise_idade[
    "Faixa"
].astype(
    str
)


ordem_idade = analise_idade[
    "Faixa"
].tolist()


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
        Faixa=faixas_limite
    )
    .groupby(
        "Faixa",
        observed=True,
    )[
        "inadimplente"
    ]
    .agg(
        Registros="count",
        Inadimplentes="sum",
        Taxa="mean",
    )
    .reset_index()
)


analise_limite[
    "Faixa"
] = analise_limite[
    "Faixa"
].astype(
    str
)


ordem_limite = analise_limite[
    "Faixa"
].tolist()


grafico_idade = (
    alt.Chart(
        analise_idade
    )
    .mark_bar(
        cornerRadiusEnd=5,
        color="#2563eb",
    )
    .encode(
        x=alt.X(
            "Faixa:N",
            title="Faixa de idade",
            sort=ordem_idade,
            axis=alt.Axis(
                labelAngle=-28,
            ),
        ),

        y=alt.Y(
            "Taxa:Q",
            title="Taxa de inadimplência",
            axis=alt.Axis(
                format=".0%",
            ),
        ),

        tooltip=[
            alt.Tooltip(
                "Faixa:N",
                title="Faixa",
            ),

            alt.Tooltip(
                "Registros:Q",
                title="Clientes",
                format=",",
            ),

            alt.Tooltip(
                "Taxa:Q",
                title="Taxa",
                format=".2%",
            ),
        ],
    )
    .properties(
        height=350,
        title="Taxa por faixa de idade",
    )
)


grafico_limite = (
    alt.Chart(
        analise_limite
    )
    .mark_bar(
        cornerRadiusEnd=5,
        color="#a855f7",
    )
    .encode(
        x=alt.X(
            "Faixa:N",
            title="Faixa de limite",
            sort=ordem_limite,
            axis=alt.Axis(
                labelAngle=-28,
            ),
        ),

        y=alt.Y(
            "Taxa:Q",
            title="Taxa de inadimplência",
            axis=alt.Axis(
                format=".0%",
            ),
        ),

        tooltip=[
            alt.Tooltip(
                "Faixa:N",
                title="Faixa",
            ),

            alt.Tooltip(
                "Registros:Q",
                title="Clientes",
                format=",",
            ),

            alt.Tooltip(
                "Taxa:Q",
                title="Taxa",
                format=".2%",
            ),
        ],
    )
    .properties(
        height=350,
        title="Taxa por faixa de limite",
    )
)


coluna_idade, coluna_limite = st.columns(2)


with coluna_idade:

    st.altair_chart(
        aplicar_tema(
            grafico_idade
        ),
        use_container_width=True,
        theme=None,
    )


with coluna_limite:

    st.altair_chart(
        aplicar_tema(
            grafico_limite
        ),
        use_container_width=True,
        theme=None,
    )


html(
    """
    <div class="ad-warning">
        ⚠️ Idade e limite podem apresentar associação com
        inadimplência, mas não devem ser interpretados
        isoladamente. O modelo combina diversas informações
        comportamentais e financeiras.
    </div>
    """
)


# ============================================================
# VARIÁVEIS DEMOGRÁFICAS
# ============================================================

with st.expander(
    "Explorar sexo, escolaridade e estado civil"
):

    st.info(
        "Estas variáveis são analisadas para compreensão "
        "da base e avaliação de equidade. Elas não são "
        "utilizadas diretamente pelo modelo reduzido da "
        "página Início."
    )


    variavel_demografica = st.selectbox(
        "Escolha uma variável",
        options=[
            "Sexo",
            "Escolaridade",
            "Estado civil",
        ],
    )


    analise_demografica = (
        dados_analise
        .groupby(
            variavel_demografica,
            observed=True,
        )[
            "inadimplente"
        ]
        .agg(
            Registros="count",
            Inadimplentes="sum",
            Taxa="mean",
        )
        .reset_index()
        .sort_values(
            "Registros",
            ascending=False,
        )
    )


    ordem_demografica = analise_demografica[
        variavel_demografica
    ].tolist()


    grafico_demografico = (
        alt.Chart(
            analise_demografica
        )
        .mark_bar(
            cornerRadiusEnd=5,
            color="#38bdf8",
        )
        .encode(
            y=alt.Y(
                f"{variavel_demografica}:N",
                title=None,
                sort=ordem_demografica,
            ),

            x=alt.X(
                "Taxa:Q",
                title="Taxa de inadimplência",
                axis=alt.Axis(
                    format=".0%",
                ),
            ),

            tooltip=[
                alt.Tooltip(
                    f"{variavel_demografica}:N",
                    title=variavel_demografica,
                ),

                alt.Tooltip(
                    "Registros:Q",
                    title="Clientes",
                    format=",",
                ),

                alt.Tooltip(
                    "Inadimplentes:Q",
                    title="Inadimplentes",
                    format=",",
                ),

                alt.Tooltip(
                    "Taxa:Q",
                    title="Taxa",
                    format=".2%",
                ),
            ],
        )
        .properties(
            height=max(
                250,
                len(
                    analise_demografica
                )
                * 60,
            ),
        )
    )


    st.altair_chart(
        aplicar_tema(
            grafico_demografico
        ),
        use_container_width=True,
        theme=None,
    )


    tabela_demografica = (
        analise_demografica
        .copy()
    )


    tabela_demografica[
        "Taxa"
    ] = tabela_demografica[
        "Taxa"
    ].map(
        lambda valor: formatar_percentual(
            valor,
            2,
        )
    )


    tabela_demografica = tabela_demografica.rename(
        columns={
            "Taxa": "Taxa de inadimplência",
        }
    )


    st.dataframe(
        tabela_demografica,
        use_container_width=True,
        hide_index=True,
    )


    st.warning(
        "Diferenças entre grupos não provam que a variável "
        "demográfica seja a causa da inadimplência. Outros "
        "fatores e desigualdades presentes nos dados podem "
        "estar relacionados aos resultados."
    )


# ============================================================
# CORRELAÇÃO
# ============================================================

with st.expander(
    "Explorar correlações lineares"
):

    st.markdown(
        """
        A correlação mede associação linear entre uma
        variável e a inadimplência.

        Valores próximos de zero não significam
        necessariamente que a variável seja inútil para
        modelos não lineares, como o Random Forest.
        """
    )


    correlacoes = (
        dados_analise[
            list(
                NOMES_AMIGAVEIS.keys()
            )
            + [
                "inadimplente"
            ]
        ]
        .corr(
            numeric_only=True
        )[
            "inadimplente"
        ]
        .drop(
            "inadimplente"
        )
        .reset_index()
    )


    correlacoes.columns = [
        "Variável original",
        "Correlação",
    ]


    correlacoes[
        "Variável"
    ] = correlacoes[
        "Variável original"
    ].map(
        NOMES_AMIGAVEIS
    )


    correlacoes[
        "Magnitude"
    ] = correlacoes[
        "Correlação"
    ].abs()


    top_correlacoes = (
        correlacoes
        .nlargest(
            12,
            "Magnitude",
        )
        .sort_values(
            "Correlação"
        )
        .copy()
    )


    ordem_correlacoes = top_correlacoes[
        "Variável"
    ].tolist()


    grafico_correlacoes = (
        alt.Chart(
            top_correlacoes
        )
        .mark_bar(
            cornerRadiusEnd=4,
        )
        .encode(
            y=alt.Y(
                "Variável:N",
                title=None,
                sort=ordem_correlacoes,
            ),

            x=alt.X(
                "Correlação:Q",
                title="Correlação com a inadimplência",
                scale=alt.Scale(
                    domain=[
                        min(
                            -0.05,
                            float(
                                top_correlacoes[
                                    "Correlação"
                                ].min()
                            ),
                        ),

                        max(
                            0.05,
                            float(
                                top_correlacoes[
                                    "Correlação"
                                ].max()
                            ),
                        ),
                    ]
                ),
            ),

            color=alt.condition(
                alt.datum.Correlação >= 0,
                alt.value(
                    "#ef4444"
                ),
                alt.value(
                    "#22c55e"
                ),
            ),

            tooltip=[
                alt.Tooltip(
                    "Variável:N",
                    title="Variável",
                ),

                alt.Tooltip(
                    "Correlação:Q",
                    title="Correlação",
                    format=".4f",
                ),
            ],
        )
        .properties(
            height=430,
        )
    )


    st.altair_chart(
        aplicar_tema(
            grafico_correlacoes
        ),
        use_container_width=True,
        theme=None,
    )


    st.caption(
        "Barras vermelhas representam associação linear "
        "positiva com a inadimplência; barras verdes "
        "representam associação negativa."
    )


# ============================================================
# ESTATÍSTICAS E REGISTROS
# ============================================================

with st.expander(
    "Ver estatísticas descritivas"
):

    estatisticas = (
        dados[
            [
                "limite_credito",
                "idade",
            ]
            + COLUNAS_STATUS
            + COLUNAS_FATURAS
            + COLUNAS_PAGAMENTOS
        ]
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


    estatisticas[
        "Variável"
    ] = estatisticas[
        "Variável"
    ].map(
        NOMES_AMIGAVEIS
    )


    st.dataframe(
        estatisticas,
        use_container_width=True,
        hide_index=True,
    )


with st.expander(
    "Visualizar registros da base"
):

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
        "inadimplente"
    ] = dados_exibicao[
        "inadimplente"
    ].map(
        {
            0: "Não",
            1: "Sim",
        }
    )


    colunas_exibidas = [
        "limite_credito",
        "idade",
        "Sexo",
        "Escolaridade",
        "Estado civil",
        "status_pagamento_set",
        "valor_fatura_set",
        "valor_pagamento_set",
        "inadimplente",
    ]


    dados_exibicao = dados_exibicao[
        colunas_exibidas
    ].rename(
        columns={
            "limite_credito": "Limite de crédito",
            "idade": "Idade",
            "status_pagamento_set": (
                "Status de pagamento — setembro"
            ),
            "valor_fatura_set": "Fatura — setembro",
            "valor_pagamento_set": "Pagamento — setembro",
            "inadimplente": "Inadimplente",
        }
    )


    st.dataframe(
        dados_exibicao,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# CONCLUSÃO
# ============================================================

html(
    """
    <div class="ad-final">
        <div class="ad-final-title">
            O que concluímos sobre os dados?
        </div>

        <p class="ad-final-text">
            A base mostra que o risco de inadimplência está
            relacionado principalmente ao comportamento
            financeiro recente: atrasos, utilização do limite,
            valores das faturas e capacidade de pagamento.

            Nenhuma dessas informações deve ser interpretada
            isoladamente. O modelo combina os sinais dos seis
            meses para produzir uma estimativa de risco
            comportamental para o mês seguinte.
        </p>
    </div>
    """
)


# ============================================================
# AVISO FINAL
# ============================================================

st.divider()


st.caption(
    "A base contém dados históricos de clientes de cartão "
    "de crédito de Taiwan. Os padrões observados descrevem "
    "esse conjunto específico e não devem ser generalizados "
    "automaticamente para outras populações, períodos ou "
    "mercados."
)