import json
from pathlib import Path
from textwrap import dedent

import altair as alt
import joblib
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Credit Risk",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)


def html(conteudo: str) -> None:
    st.html(dedent(conteudo).strip())


html(
    """
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 85% 0%,
                    rgba(37, 99, 235, .12),
                    transparent 28rem
                ),
                #080d15;
        }

        section[data-testid="stSidebar"] {
            background: #101621;
            border-right: 1px solid #293244;
        }

        .block-container {
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div > div {
            background: #171e2d;
            border-color: #303a4e;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            min-height: 3rem;
            border: 0;
            border-radius: 10px;
            background: linear-gradient(
                90deg,
                #1d4ed8,
                #2563eb
            );
            font-weight: 800;
        }

        div[data-testid="stExpander"] {
            border: 1px solid #273247;
            border-radius: 14px;
            background: rgba(15, 23, 42, .62);
        }

        .badge {
            display: inline-flex;
            margin-bottom: .8rem;
            padding: .38rem .75rem;
            border: 1px solid rgba(56, 189, 248, .28);
            border-radius: 999px;
            background: rgba(14, 116, 144, .12);
            color: #7dd3fc;
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .07em;
            text-transform: uppercase;
        }

        .title {
            margin: 0;
            color: #f8fafc;
            font-size: clamp(2.2rem, 4vw, 3.4rem);
            font-weight: 900;
            line-height: 1.05;
        }

        .subtitle {
            max-width: 900px;
            margin: .75rem 0 1.2rem;
            color: #cbd5e1;
            font-size: 1.08rem;
            line-height: 1.6;
        }

        .kicker {
            margin-top: 1.2rem;
            color: #60a5fa;
            font-size: .76rem;
            font-weight: 850;
            letter-spacing: .09em;
            text-transform: uppercase;
        }

        .section-title {
            margin: .25rem 0 .35rem;
            color: #f8fafc;
            font-size: 1.65rem;
            font-weight: 850;
        }

        .section-description {
            margin: 0 0 1rem;
            color: #94a3b8;
            line-height: 1.5;
        }

        .scenario-box,
        .guide,
        .summary-card,
        .risk-card,
        .panel {
            border: 1px solid #273247;
            border-radius: 15px;
            background: rgba(17, 24, 39, .88);
        }

        .scenario-box {
            margin: .6rem 0 1rem;
            padding: 1rem;
            border-color: rgba(56, 189, 248, .25);
            background: rgba(14, 116, 144, .08);
        }

        .scenario-name {
            color: #7dd3fc;
            font-weight: 850;
        }

        .scenario-text {
            margin: .3rem 0 0;
            color: #cbd5e1;
            font-size: .84rem;
        }

        .guide {
            margin: .9rem 0;
            padding: .9rem 1rem;
            border-left: 4px solid #2563eb;
            color: #bfdbfe;
        }

        .summary-card {
            margin: 1rem 0;
            padding: 1rem;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(
                4,
                minmax(0, 1fr)
            );
            gap: .75rem;
        }

        .summary-item {
            padding: .75rem;
            border: 1px solid rgba(148, 163, 184, .12);
            border-radius: 10px;
            background: rgba(30, 41, 59, .52);
        }

        .summary-label {
            color: #94a3b8;
            font-size: .72rem;
        }

        .summary-value {
            margin-top: .2rem;
            color: #f8fafc;
            font-weight: 850;
        }

        .risk-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 2rem;
            margin: .5rem 0 1rem;
            padding: 1.6rem 1.8rem;
            border-color: var(--risk-border);
            background: linear-gradient(
                125deg,
                var(--risk-bg),
                rgba(15, 23, 42, .97) 62%
            );
        }

        .risk-small {
            color: var(--risk-color);
            font-size: .76rem;
            font-weight: 850;
            letter-spacing: .1em;
            text-transform: uppercase;
        }

        .risk-number {
            margin: .25rem 0 .55rem;
            color: var(--risk-color);
            font-size: clamp(3rem, 6vw, 5.2rem);
            font-weight: 950;
            letter-spacing: -.06em;
            line-height: 1;
        }

        .risk-label {
            display: inline-block;
            padding: .4rem .72rem;
            border: 1px solid var(--risk-border);
            border-radius: 7px;
            background: var(--risk-badge);
            color: var(--risk-color);
            font-size: .76rem;
            font-weight: 900;
        }

        .risk-message {
            max-width: 680px;
            color: #dbe4f0;
        }

        .gauge {
            width: 300px;
            min-width: 270px;
            text-align: center;
        }

        .gauge-value {
            fill: #f8fafc;
            font-size: 25px;
            font-weight: 900;
            text-anchor: middle;
        }

        .gauge-caption {
            fill: #94a3b8;
            font-size: 9px;
            text-anchor: middle;
        }

        .panel {
            height: 100%;
            padding: 1.1rem;
        }

        .panel-title {
            margin-bottom: .8rem;
            color: #f8fafc;
            font-weight: 850;
        }

        .row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: .62rem 0;
            border-bottom: 1px solid rgba(
                148,
                163,
                184,
                .12
            );
        }

        .row:last-child {
            border-bottom: 0;
        }

        .row-label {
            color: #94a3b8;
            font-size: .8rem;
        }

        .row-value {
            color: #f8fafc;
            font-size: .82rem;
            font-weight: 850;
            text-align: right;
        }

        .note,
        .alert,
        .success {
            margin-top: .75rem;
            padding: .8rem .95rem;
            border-radius: 10px;
        }

        .note {
            border: 1px solid rgba(56, 189, 248, .18);
            background: rgba(14, 116, 144, .08);
            color: #bae6fd;
            font-size: .78rem;
        }

        .alert {
            border-left: 4px solid #f59e0b;
            background: rgba(120, 53, 15, .12);
            color: #fde68a;
        }

        .success {
            border-left: 4px solid #22c55e;
            background: rgba(20, 83, 45, .15);
            color: #bbf7d0;
        }

        @media (max-width: 900px) {
            .risk-card {
                flex-direction: column;
                align-items: stretch;
            }

            .gauge {
                width: 100%;
            }

            .summary-grid {
                grid-template-columns: repeat(
                    2,
                    minmax(0, 1fr)
                );
            }
        }
    </style>
    """
)


# ============================================================
# CAMINHOS E CONSTANTES
# ============================================================

CAMINHO_MODELO = (
    Path("models")
    / "credit_risk_reduced_model.joblib"
)

CAMINHO_POLITICA = (
    Path("reports")
    / "reduced_model_threshold_policy.json"
)

CAMINHO_COMPARACAO = (
    Path("reports")
    / "sensitive_feature_model_comparison.csv"
)


MESES = [
    ("set", "Setembro"),
    ("ago", "Agosto"),
    ("jul", "Julho"),
    ("jun", "Junho"),
    ("mai", "Maio"),
    ("abr", "Abril"),
]


ROTULOS_STATUS = {
    -2: "Sem consumo no mês",
    -1: "Pagamento integral / em dia",
    0: "Sem atraso registrado",
    1: "1 mês de atraso",
    2: "2 meses de atraso",
    3: "3 meses de atraso",
    4: "4 meses de atraso",
    5: "5 meses de atraso",
    6: "6 meses de atraso",
    7: "7 meses de atraso",
    8: "8 meses de atraso",
    9: "9 meses ou mais de atraso",
}


CENARIOS = {
    "Perfil saudável": {
        "descricao": (
            "Utilização moderada, sem atrasos relevantes "
            "e pagamentos elevados."
        ),
        "limite": 150_000,
        "idade": 35,
        "status": {
            "set": -1,
            "ago": -1,
            "jul": 0,
            "jun": -1,
            "mai": 0,
            "abr": -1,
        },
        "faturas": {
            "set": 30_000,
            "ago": 28_000,
            "jul": 25_000,
            "jun": 22_000,
            "mai": 20_000,
            "abr": 18_000,
        },
        "pagamentos": {
            "set": 30_000,
            "ago": 28_000,
            "jul": 25_000,
            "jun": 22_000,
            "mai": 20_000,
            "abr": 18_000,
        },
    },

    "Perfil intermediário": {
        "descricao": (
            "Alta utilização, alguns atrasos recentes "
            "e pagamentos parciais."
        ),
        "limite": 80_000,
        "idade": 40,
        "status": {
            "set": 1,
            "ago": 0,
            "jul": 1,
            "jun": 0,
            "mai": 0,
            "abr": 0,
        },
        "faturas": {
            "set": 65_000,
            "ago": 62_000,
            "jul": 60_000,
            "jun": 57_000,
            "mai": 54_000,
            "abr": 50_000,
        },
        "pagamentos": {
            "set": 8_000,
            "ago": 7_000,
            "jul": 6_000,
            "jun": 6_000,
            "mai": 5_000,
            "abr": 5_000,
        },
    },

    "Perfil de alto risco": {
        "descricao": (
            "Atrasos consecutivos, limite quase utilizado "
            "e pagamentos reduzidos."
        ),
        "limite": 50_000,
        "idade": 30,
        "status": {
            "set": 2,
            "ago": 2,
            "jul": 1,
            "jun": 1,
            "mai": 0,
            "abr": 0,
        },
        "faturas": {
            "set": 48_000,
            "ago": 47_000,
            "jul": 46_000,
            "jun": 45_000,
            "mai": 44_000,
            "abr": 43_000,
        },
        "pagamentos": {
            "set": 1_000,
            "ago": 1_000,
            "jul": 1_000,
            "jun": 1_000,
            "mai": 1_000,
            "abr": 1_000,
        },
    },
}


OPCOES_CENARIO = [
    "Perfil saudável",
    "Perfil intermediário",
    "Perfil de alto risco",
    "Preenchimento personalizado",
]


# ============================================================
# FUNÇÕES
# ============================================================

def formatar_valor(valor: float) -> str:
    numero = f"{valor:,.0f}".replace(
        ",",
        ".",
    )

    return f"NT$ {numero}"


@st.cache_resource
def carregar_modelo():
    if not CAMINHO_MODELO.exists():
        return None

    return joblib.load(
        CAMINHO_MODELO
    )


@st.cache_data
def carregar_json(caminho: Path):
    if not caminho.exists():
        return None

    with caminho.open(
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(
            arquivo
        )


@st.cache_data
def carregar_comparacao():
    if not CAMINHO_COMPARACAO.exists():
        return None

    return pd.read_csv(
        CAMINHO_COMPARACAO
    )


def aplicar_cenario(nome: str) -> None:
    if nome not in CENARIOS:
        return

    cenario = CENARIOS[
        nome
    ]

    st.session_state[
        "entrada_limite"
    ] = cenario[
        "limite"
    ]

    st.session_state[
        "entrada_idade"
    ] = cenario[
        "idade"
    ]

    for codigo, _ in MESES:
        st.session_state[
            f"entrada_status_{codigo}"
        ] = cenario[
            "status"
        ][codigo]

        st.session_state[
            f"entrada_fatura_{codigo}"
        ] = cenario[
            "faturas"
        ][codigo]

        st.session_state[
            f"entrada_pagamento_{codigo}"
        ] = cenario[
            "pagamentos"
        ][codigo]


def alterar_cenario() -> None:
    nome = st.session_state[
        "cenario_selecionado"
    ]

    if nome in CENARIOS:
        aplicar_cenario(
            nome
        )

    st.session_state[
        "analise_credito"
    ] = None


def marcar_personalizado() -> None:
    st.session_state[
        "cenario_selecionado"
    ] = "Preenchimento personalizado"

    st.session_state[
        "analise_credito"
    ] = None


def classificar_risco(
    probabilidade: float,
    threshold: float,
) -> dict:

    limite_aprovacao = max(
        0.0,
        threshold - 0.10,
    )

    if probabilidade < limite_aprovacao:

        return {
            "decisao": "APROVAÇÃO SUGERIDA",
            "mensagem": (
                "A probabilidade ficou abaixo da faixa "
                "de análise manual."
            ),
            "cor": "#22c55e",
            "fundo": "rgba(20,83,45,.23)",
            "borda": "rgba(34,197,94,.40)",
            "badge": "rgba(34,197,94,.14)",
        }

    if probabilidade < threshold:

        return {
            "decisao": "ANÁLISE MANUAL",
            "mensagem": (
                "O perfil ficou próximo do threshold "
                "e requer avaliação complementar."
            ),
            "cor": "#f59e0b",
            "fundo": "rgba(120,53,15,.23)",
            "borda": "rgba(245,158,11,.40)",
            "badge": "rgba(245,158,11,.14)",
        }

    return {
        "decisao": "ALTO RISCO",
        "mensagem": (
            "A probabilidade ultrapassou o threshold "
            "de alto risco."
        ),
        "cor": "#ef4444",
        "fundo": "rgba(127,29,29,.25)",
        "borda": "rgba(239,68,68,.42)",
        "badge": "rgba(239,68,68,.15)",
    }


def criar_gauge(
    probabilidade: float,
    cor: str,
) -> str:

    percentual = min(
        max(
            probabilidade * 100,
            0,
        ),
        100,
    )

    return f"""
        <svg
            width="270"
            height="165"
            viewBox="0 0 200 120"
        >
            <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="#303847"
                stroke-width="20"
                stroke-linecap="round"
                pathLength="100"
            />

            <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="{cor}"
                stroke-width="20"
                stroke-linecap="round"
                pathLength="100"
                stroke-dasharray="
                    {percentual:.1f}
                    {100 - percentual:.1f}
                "
            />

            <text
                x="100"
                y="82"
                class="gauge-value"
            >
                {percentual:.1f}%
            </text>

            <text
                x="100"
                y="99"
                class="gauge-caption"
            >
                probabilidade estimada
            </text>

            <text
                x="14"
                y="118"
                class="gauge-caption"
            >
                0%
            </text>

            <text
                x="186"
                y="118"
                class="gauge-caption"
            >
                100%
            </text>
        </svg>
    """


def assinatura(
    limite: int,
    idade: int,
    status: dict,
    faturas: dict,
    pagamentos: dict,
) -> tuple:

    return (
        limite,
        idade,

        *[
            status[codigo]
            for codigo, _ in MESES
        ],

        *[
            faturas[codigo]
            for codigo, _ in MESES
        ],

        *[
            pagamentos[codigo]
            for codigo, _ in MESES
        ],
    )


# ============================================================
# CARREGAMENTO
# ============================================================

modelo = carregar_modelo()

politica = carregar_json(
    CAMINHO_POLITICA
)

comparacao = carregar_comparacao()


if modelo is None:
    st.error(
        "Modelo não encontrado. Execute: "
        "python compare_sensitive_features.py"
    )

    st.stop()


if politica is None:
    st.error(
        "Política não encontrada. Execute: "
        "python compare_sensitive_features.py"
    )

    st.stop()


threshold = float(
    politica[
        "threshold_recomendado"
    ]
)


metricas_modelo = None


if comparacao is not None:

    linha = comparacao[
        comparacao[
            "modelo"
        ]
        == "Modelo sem variáveis demográficas"
    ]

    if not linha.empty:

        metricas_modelo = linha.iloc[
            0
        ]


# ============================================================
# ESTADO INICIAL
# ============================================================

if "cenario_selecionado" not in st.session_state:

    st.session_state[
        "cenario_selecionado"
    ] = "Perfil saudável"


if "formulario_inicializado" not in st.session_state:

    aplicar_cenario(
        "Perfil saudável"
    )

    st.session_state[
        "formulario_inicializado"
    ] = True


if "analise_credito" not in st.session_state:

    st.session_state[
        "analise_credito"
    ] = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## Modelo em produção"
    )

    st.write(
        "**Algoritmo:** Random Forest"
    )

    st.write(
        "**Versão:** modelo reduzido"
    )

    st.write(
        "**Threshold:**",
        f"{threshold:.0%}",
    )

    if metricas_modelo is not None:

        st.write(
            "**Recall no teste:**",
            f"{metricas_modelo['recall']:.2%}",
        )

        st.write(
            "**Precisão no teste:**",
            f"{metricas_modelo['precisao']:.2%}",
        )

        st.write(
            "**ROC AUC:**",
            f"{metricas_modelo['roc_auc']:.4f}",
        )

        st.write(
            "**PR AUC:**",
            f"{metricas_modelo['pr_auc']:.4f}",
        )

    st.divider()

    st.markdown(
        "### Variáveis não utilizadas"
    )

    st.markdown(
        """
        - Sexo
        - Escolaridade
        - Estado civil
        """
    )

    st.caption(
        "A idade continua sendo utilizada."
    )

    st.divider()

    st.caption(
        "Projeto educacional e de portfólio."
    )


# ============================================================
# CABEÇALHO
# ============================================================

html(
    """
    <div class="badge">
        ● Machine Learning aplicado a crédito
    </div>

    <h1 class="title">
        💳 Credit Risk
    </h1>

    <p class="subtitle">
        Escolha um cenário pronto ou personalize o perfil
        financeiro para estimar a probabilidade de
        inadimplência.
    </p>
    """
)


st.info(
    "O modelo não utiliza diretamente sexo, escolaridade "
    "ou estado civil. A idade e as informações financeiras "
    "continuam sendo consideradas."
)


with st.expander(
    "Entenda esta página em 30 segundos"
):

    st.markdown(
        """
        1. Escolha um cenário.
        2. Revise ou altere os dados.
        3. Clique em **Executar análise de risco**.
        4. Veja a probabilidade, a decisão e os alertas.
        """
    )


# ============================================================
# ETAPA 1 — CENÁRIO
# ============================================================

html(
    """
    <div class="kicker">
        Etapa 1
    </div>

    <h2 class="section-title">
        Escolha um cenário
    </h2>

    <p class="section-description">
        Os cenários facilitam a demonstração e todos os
        campos continuam editáveis.
    </p>
    """
)


cenario = st.radio(
    "Cenário",
    options=OPCOES_CENARIO,
    horizontal=True,
    key="cenario_selecionado",
    on_change=alterar_cenario,
    label_visibility="collapsed",
)


descricao = (
    CENARIOS[
        cenario
    ][
        "descricao"
    ]
    if cenario in CENARIOS
    else (
        "Os valores atuais serão preservados "
        "para edição manual."
    )
)


html(
    f"""
    <div class="scenario-box">
        <div class="scenario-name">
            {cenario}
        </div>

        <p class="scenario-text">
            {descricao}
        </p>
    </div>
    """
)


# ============================================================
# ETAPA 2 — DADOS
# ============================================================

html(
    """
    <div class="kicker">
        Etapa 2
    </div>

    <h2 class="section-title">
        Revise os dados do cliente
    </h2>

    <p class="section-description">
        Os valores financeiros estão em NT$, a moeda
        original da base de Taiwan.
    </p>
    """
)


coluna_1, coluna_2 = st.columns(
    2
)


with coluna_1:

    limite_credito = st.number_input(
        "Limite de crédito (NT$)",
        min_value=1_000,
        max_value=2_000_000,
        step=10_000,
        key="entrada_limite",
        on_change=marcar_personalizado,
    )


with coluna_2:

    idade = st.number_input(
        "Idade",
        min_value=18,
        max_value=100,
        step=1,
        key="entrada_idade",
        on_change=marcar_personalizado,
    )


html(
    """
    <div class="guide">
        Para uma demonstração rápida, escolha um cenário
        e execute a análise. Abra as seções abaixo apenas
        para revisar ou personalizar o histórico.
    </div>
    """
)


# ============================================================
# HISTÓRICO DE ATRASOS
# ============================================================

status_pagamento = {}


with st.expander(
    "1. Histórico de atrasos",
    expanded=True,
):

    st.caption(
        "Os códigos técnicos foram substituídos "
        "por descrições simples."
    )

    for inicio in (
        0,
        3,
    ):

        colunas = st.columns(
            3
        )

        for coluna, (
            codigo,
            nome,
        ) in zip(
            colunas,
            MESES[
                inicio:
                inicio + 3
            ],
        ):

            with coluna:

                status_pagamento[
                    codigo
                ] = st.selectbox(
                    nome,
                    options=list(
                        ROTULOS_STATUS
                    ),
                    format_func=lambda valor: (
                        ROTULOS_STATUS[
                            valor
                        ]
                    ),
                    key=f"entrada_status_{codigo}",
                    on_change=marcar_personalizado,
                )


# ============================================================
# FATURAS
# ============================================================

valores_faturas = {}


with st.expander(
    "2. Faturas dos últimos 6 meses"
):

    st.caption(
        "Informe o valor total de cada fatura em NT$."
    )

    for inicio in (
        0,
        3,
    ):

        colunas = st.columns(
            3
        )

        for coluna, (
            codigo,
            nome,
        ) in zip(
            colunas,
            MESES[
                inicio:
                inicio + 3
            ],
        ):

            with coluna:

                valores_faturas[
                    codigo
                ] = st.number_input(
                    f"{nome} (NT$)",
                    min_value=-2_000_000,
                    max_value=10_000_000,
                    step=1_000,
                    key=f"entrada_fatura_{codigo}",
                    on_change=marcar_personalizado,
                )


# ============================================================
# PAGAMENTOS
# ============================================================

valores_pagamentos = {}


with st.expander(
    "3. Pagamentos dos últimos 6 meses"
):

    st.caption(
        "Informe quanto foi efetivamente pago "
        "em cada mês."
    )

    for inicio in (
        0,
        3,
    ):

        colunas = st.columns(
            3
        )

        for coluna, (
            codigo,
            nome,
        ) in zip(
            colunas,
            MESES[
                inicio:
                inicio + 3
            ],
        ):

            with coluna:

                valores_pagamentos[
                    codigo
                ] = st.number_input(
                    f"{nome} (NT$)",
                    min_value=0,
                    max_value=10_000_000,
                    step=1_000,
                    key=f"entrada_pagamento_{codigo}",
                    on_change=marcar_personalizado,
                )


# ============================================================
# RESUMO PRÉVIO
# ============================================================

total_faturas_previo = sum(
    max(
        valor,
        0,
    )
    for valor in valores_faturas.values()
)


total_pagamentos_previo = sum(
    valores_pagamentos.values()
)


meses_atraso_previo = sum(
    valor > 0
    for valor in status_pagamento.values()
)


utilizacao_previa = (
    max(
        valores_faturas["set"],
        0,
    )
    / limite_credito
)


cobertura_previa = (
    total_pagamentos_previo
    / total_faturas_previo
    if total_faturas_previo > 0
    else 0
)


html(
    f"""
    <div class="summary-card">
        <div class="panel-title">
            Resumo dos dados que serão analisados
        </div>

        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">
                    Limite
                </div>

                <div class="summary-value">
                    {formatar_valor(limite_credito)}
                </div>
            </div>

            <div class="summary-item">
                <div class="summary-label">
                    Meses com atraso
                </div>

                <div class="summary-value">
                    {meses_atraso_previo} de 6
                </div>
            </div>

            <div class="summary-item">
                <div class="summary-label">
                    Fatura mais recente
                </div>

                <div class="summary-value">
                    {
                        formatar_valor(
                            valores_faturas["set"]
                        )
                    }
                </div>
            </div>

            <div class="summary-item">
                <div class="summary-label">
                    Pagamento mais recente
                </div>

                <div class="summary-value">
                    {
                        formatar_valor(
                            valores_pagamentos["set"]
                        )
                    }
                </div>
            </div>

            <div class="summary-item">
                <div class="summary-label">
                    Utilização do limite
                </div>

                <div class="summary-value">
                    {utilizacao_previa:.1%}
                </div>
            </div>

            <div class="summary-item">
                <div class="summary-label">
                    Total das faturas
                </div>

                <div class="summary-value">
                    {
                        formatar_valor(
                            total_faturas_previo
                        )
                    }
                </div>
            </div>

            <div class="summary-item">
                <div class="summary-label">
                    Total pago
                </div>

                <div class="summary-value">
                    {
                        formatar_valor(
                            total_pagamentos_previo
                        )
                    }
                </div>
            </div>

            <div class="summary-item">
                <div class="summary-label">
                    Pagamentos / faturas
                </div>

                <div class="summary-value">
                    {cobertura_previa:.1%}
                </div>
            </div>
        </div>
    </div>
    """
)


assinatura_atual = assinatura(
    limite_credito,
    idade,
    status_pagamento,
    valores_faturas,
    valores_pagamentos,
)


analise_anterior = st.session_state[
    "analise_credito"
]


if (
    analise_anterior is not None
    and analise_anterior.get(
        "assinatura"
    )
    != assinatura_atual
):

    st.session_state[
        "analise_credito"
    ] = None


botao_analisar = st.button(
    "Executar análise de risco",
    type="primary",
    use_container_width=True,
)


# ============================================================
# PREVISÃO
# ============================================================

if botao_analisar:

    dados_cliente = {
        "limite_credito": limite_credito,
        "idade": idade,

        "status_pagamento_set": (
            status_pagamento["set"]
        ),

        "status_pagamento_ago": (
            status_pagamento["ago"]
        ),

        "status_pagamento_jul": (
            status_pagamento["jul"]
        ),

        "status_pagamento_jun": (
            status_pagamento["jun"]
        ),

        "status_pagamento_mai": (
            status_pagamento["mai"]
        ),

        "status_pagamento_abr": (
            status_pagamento["abr"]
        ),

        "valor_fatura_set": (
            valores_faturas["set"]
        ),

        "valor_fatura_ago": (
            valores_faturas["ago"]
        ),

        "valor_fatura_jul": (
            valores_faturas["jul"]
        ),

        "valor_fatura_jun": (
            valores_faturas["jun"]
        ),

        "valor_fatura_mai": (
            valores_faturas["mai"]
        ),

        "valor_fatura_abr": (
            valores_faturas["abr"]
        ),

        "valor_pagamento_set": (
            valores_pagamentos["set"]
        ),

        "valor_pagamento_ago": (
            valores_pagamentos["ago"]
        ),

        "valor_pagamento_jul": (
            valores_pagamentos["jul"]
        ),

        "valor_pagamento_jun": (
            valores_pagamentos["jun"]
        ),

        "valor_pagamento_mai": (
            valores_pagamentos["mai"]
        ),

        "valor_pagamento_abr": (
            valores_pagamentos["abr"]
        ),
    }


    dados_df = pd.DataFrame(
        [
            dados_cliente
        ]
    )


    probabilidade = float(
        modelo.predict_proba(
            dados_df
        )[0][1]
    )


    score = round(
        (
            1
            - probabilidade
        )
        * 1000
    )


    resultado = classificar_risco(
        probabilidade,
        threshold,
    )


    total_faturas = sum(
        max(
            valor,
            0,
        )
        for valor in valores_faturas.values()
    )


    total_pagamentos = sum(
        valores_pagamentos.values()
    )


    meses_atraso = sum(
        valor > 0
        for valor in status_pagamento.values()
    )


    maior_atraso = max(
        status_pagamento.values()
    )


    utilizacao = (
        max(
            valores_faturas["set"],
            0,
        )
        / limite_credito
    )


    cobertura = (
        total_pagamentos
        / total_faturas
        if total_faturas > 0
        else 0
    )


    alertas = []


    if meses_atraso:

        alertas.append(
            f"Foram identificados {meses_atraso} "
            "meses com atraso."
        )


    if maior_atraso >= 2:

        alertas.append(
            "Existe atraso igual ou superior "
            "a dois meses."
        )


    if utilizacao >= 0.80:

        alertas.append(
            "A fatura mais recente utiliza 80% "
            "ou mais do limite."
        )


    if (
        total_faturas > 0
        and cobertura < 0.10
    ):

        alertas.append(
            "Os pagamentos representam menos "
            "de 10% das faturas."
        )


    st.session_state[
        "analise_credito"
    ] = {
        "assinatura": assinatura_atual,
        "dados_df": dados_df,
        "probabilidade": probabilidade,
        "score": score,
        "resultado": resultado,
        "limite": limite_credito,
        "idade": idade,
        "faturas": valores_faturas.copy(),
        "pagamentos": valores_pagamentos.copy(),
        "total_faturas": total_faturas,
        "total_pagamentos": total_pagamentos,
        "meses_atraso": meses_atraso,
        "maior_atraso": maior_atraso,
        "utilizacao": utilizacao,
        "cobertura": cobertura,
        "alertas": alertas,
    }


# ============================================================
# RESULTADO
# ============================================================

analise = st.session_state[
    "analise_credito"
]


if analise is not None:

    resultado = analise[
        "resultado"
    ]


    gauge = criar_gauge(
        analise[
            "probabilidade"
        ],
        resultado[
            "cor"
        ],
    )


    html(
        """
        <div class="kicker">
            Resultado do modelo
        </div>

        <h2 class="section-title">
            Resultado da análise
        </h2>

        <p class="section-description">
            Resultado da última simulação executada.
        </p>
        """
    )


    html(
        f"""
        <div
            class="risk-card"
            style="
                --risk-color: {resultado['cor']};
                --risk-bg: {resultado['fundo']};
                --risk-border: {resultado['borda']};
                --risk-badge: {resultado['badge']};
            "
        >
            <div>
                <div class="risk-small">
                    Risco de inadimplência
                </div>

                <div class="risk-number">
                    {analise['probabilidade']:.1%}
                </div>

                <span class="risk-label">
                    {resultado['decisao']}
                </span>

                <p class="risk-message">
                    {resultado['mensagem']}
                </p>
            </div>

            <div class="gauge">
                {gauge}
            </div>
        </div>
        """
    )


    (
        coluna_1,
        coluna_2,
        coluna_3,
        coluna_4,
    ) = st.columns(
        4
    )


    coluna_1.metric(
        "Score ilustrativo",
        f"{analise['score']}/1000",
    )


    coluna_2.metric(
        "Threshold",
        f"{threshold:.0%}",
    )


    coluna_3.metric(
        "Meses com atraso",
        analise[
            "meses_atraso"
        ],
    )


    coluna_4.metric(
        "Utilização do limite",
        f"{analise['utilizacao']:.1%}",
    )


    st.write("")


    painel_1, painel_2 = st.columns(
        [
            1.15,
            0.85,
        ]
    )


    with painel_1:

        with st.container(
            border=True
        ):

            st.markdown(
                "### Indicadores que merecem atenção"
            )


            st.write(
                f"**Frequência de atrasos:** "
                f"{analise['meses_atraso']} de 6 meses"
            )


            st.progress(
                min(
                    analise[
                        "meses_atraso"
                    ]
                    / 6,
                    1,
                )
            )


            maior_atraso_exibido = max(
                analise[
                    "maior_atraso"
                ],
                0,
            )


            st.write(
                f"**Maior atraso:** "
                f"{maior_atraso_exibido} meses"
            )


            st.progress(
                min(
                    maior_atraso_exibido
                    / 9,
                    1,
                )
            )


            st.write(
                f"**Utilização do limite:** "
                f"{analise['utilizacao']:.1%}"
            )


            st.progress(
                min(
                    analise[
                        "utilizacao"
                    ],
                    1,
                )
            )


            baixa_cobertura = (
                1
                - min(
                    analise[
                        "cobertura"
                    ]
                    / 0.50,
                    1,
                )
            )


            st.write(
                f"**Pagamentos sobre faturas:** "
                f"{analise['cobertura']:.1%}"
            )


            st.progress(
                baixa_cobertura
            )


            st.caption(
                "São indicadores descritivos do perfil, "
                "não uma explicação individual das decisões "
                "do Random Forest."
            )


    if analise["cobertura"] < 0.10:

        padrao = "Muito baixo"

    elif analise["cobertura"] < 0.30:

        padrao = "Baixo"

    elif analise["cobertura"] < 0.70:

        padrao = "Moderado"

    else:

        padrao = "Elevado"


    with painel_2:

        html(
            f"""
            <div class="panel">
                <div class="panel-title">
                    Resumo do cliente
                </div>

                <div class="row">
                    <span class="row-label">
                        Limite
                    </span>

                    <span class="row-value">
                        {formatar_valor(analise['limite'])}
                    </span>
                </div>

                <div class="row">
                    <span class="row-label">
                        Idade
                    </span>

                    <span class="row-value">
                        {analise['idade']} anos
                    </span>
                </div>

                <div class="row">
                    <span class="row-label">
                        Total das faturas
                    </span>

                    <span class="row-value">
                        {
                            formatar_valor(
                                analise[
                                    'total_faturas'
                                ]
                            )
                        }
                    </span>
                </div>

                <div class="row">
                    <span class="row-label">
                        Total pago
                    </span>

                    <span class="row-value">
                        {
                            formatar_valor(
                                analise[
                                    'total_pagamentos'
                                ]
                            )
                        }
                    </span>
                </div>

                <div class="row">
                    <span class="row-label">
                        Maior atraso
                    </span>

                    <span class="row-value">
                        {
                            max(
                                analise[
                                    'maior_atraso'
                                ],
                                0
                            )
                        } meses
                    </span>
                </div>

                <div class="row">
                    <span class="row-label">
                        Padrão de pagamento
                    </span>

                    <span class="row-value">
                        {padrao}
                    </span>
                </div>
            </div>
            """
        )


    html(
        """
        <div class="kicker">
            Histórico financeiro
        </div>

        <h3 class="section-title">
            Evolução mensal
        </h3>

        <p class="section-description">
            Comparação entre faturas e pagamentos.
        </p>
        """
    )


    ordem = [
        ("abr", "Abril"),
        ("mai", "Maio"),
        ("jun", "Junho"),
        ("jul", "Julho"),
        ("ago", "Agosto"),
        ("set", "Setembro"),
    ]


    dados_grafico = []


    for codigo, nome in ordem:

        dados_grafico.append(
            {
                "Mês": nome,
                "Tipo": "Fatura",
                "Valor": analise[
                    "faturas"
                ][codigo],
            }
        )


        dados_grafico.append(
            {
                "Mês": nome,
                "Tipo": "Pagamento",
                "Valor": analise[
                    "pagamentos"
                ][codigo],
            }
        )


    df_grafico = pd.DataFrame(
        dados_grafico
    )


    grafico = (
        alt.Chart(
            df_grafico
        )
        .mark_line(
            point=True,
            strokeWidth=3,
        )
        .encode(
            x=alt.X(
                "Mês:N",
                sort=[
                    "Abril",
                    "Maio",
                    "Junho",
                    "Julho",
                    "Agosto",
                    "Setembro",
                ],
                title=None,
            ),

            y=alt.Y(
                "Valor:Q",
                title="Valor em NT$",
                axis=alt.Axis(
                    format="~s",
                ),
            ),

            color=alt.Color(
                "Tipo:N",
                title=None,
                scale=alt.Scale(
                    domain=[
                        "Fatura",
                        "Pagamento",
                    ],
                    range=[
                        "#ef4444",
                        "#22c55e",
                    ],
                ),
            ),

            tooltip=[
                "Mês:N",
                "Tipo:N",
                alt.Tooltip(
                    "Valor:Q",
                    format=",.0f",
                ),
            ],
        )
        .properties(
            height=330,
        )
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
        )
    )


    st.altair_chart(
        grafico,
        use_container_width=True,
        theme=None,
    )


    html(
        """
        <div class="kicker">
            Sinais complementares
        </div>

        <h3 class="section-title">
            Alertas do perfil
        </h3>
        """
    )


    if analise["alertas"]:

        for alerta in analise[
            "alertas"
        ]:

            html(
                f"""
                <div class="alert">
                    ⚠️ {alerta}
                </div>
                """
            )

    else:

        html(
            """
            <div class="success">
                ✅ Nenhum alerta crítico foi identificado.
            </div>
            """
        )


    with st.expander(
        "Ver detalhes técnicos da previsão"
    ):

        st.write(
            "**Modelo:** Random Forest reduzido"
        )

        st.write(
            "**Variáveis utilizadas:**",
            len(
                analise[
                    "dados_df"
                ].columns
            ),
        )

        st.write(
            "**Probabilidade prevista:**",
            f"{analise['probabilidade']:.4f}",
        )

        st.write(
            "**Threshold:**",
            f"{threshold:.0%}",
        )

        st.dataframe(
            analise[
                "dados_df"
            ],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# AVISO FINAL
# ============================================================

st.divider()


st.caption(
    "Projeto educacional desenvolvido com dados históricos "
    "de Taiwan. O score é ilustrativo e o modelo não deve "
    "ser usado isoladamente em decisões reais de crédito."
)