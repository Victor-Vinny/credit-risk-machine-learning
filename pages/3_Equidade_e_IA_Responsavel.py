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
    page_title="Equidade e IA responsável",
    page_icon="⚖️",
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
            --eq-background: #080d15;
            --eq-surface: #111827;
            --eq-border: #273247;
            --eq-text: #f8fafc;
            --eq-muted: #94a3b8;
            --eq-blue: #2563eb;
            --eq-cyan: #38bdf8;
            --eq-green: #22c55e;
            --eq-yellow: #f59e0b;
            --eq-red: #ef4444;
            --eq-purple: #a855f7;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 84% 0%,
                    rgba(37, 99, 235, 0.12),
                    transparent 28rem
                ),
                var(--eq-background);
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
            border: 1px solid var(--eq-border);
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.62);
        }

        .eq-badge {
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

        .eq-title {
            margin: 0;
            color: var(--eq-text);
            font-size: clamp(2.2rem, 4vw, 3.45rem);
            font-weight: 900;
            line-height: 1.05;
        }

        .eq-subtitle {
            max-width: 980px;
            margin: 0.75rem 0 1.2rem;
            color: #cbd5e1;
            font-size: 1.08rem;
            line-height: 1.65;
        }

        .eq-kicker {
            margin-top: 1.45rem;
            margin-bottom: 0.3rem;
            color: #60a5fa;
            font-size: 0.76rem;
            font-weight: 850;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .eq-section-title {
            margin: 0 0 0.35rem;
            color: var(--eq-text);
            font-size: 1.7rem;
            font-weight: 850;
        }

        .eq-description {
            margin: 0 0 1.1rem;
            color: var(--eq-muted);
            line-height: 1.55;
        }

        .eq-metric-card {
            height: 100%;
            min-height: 155px;
            padding: 1.05rem 1.1rem;
            border: 1px solid var(--eq-border);
            border-top: 3px solid var(--card-color);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.90);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
        }

        .eq-metric-label {
            margin-bottom: 0.45rem;
            color: var(--eq-muted);
            font-size: 0.78rem;
            font-weight: 750;
        }

        .eq-metric-value {
            color: var(--card-color);
            font-size: 1.8rem;
            font-weight: 900;
            line-height: 1.15;
        }

        .eq-metric-text {
            margin-top: 0.6rem;
            color: #cbd5e1;
            font-size: 0.78rem;
            line-height: 1.45;
        }

        .eq-model-card {
            height: 100%;
            padding: 1.15rem;
            border: 1px solid var(--eq-border);
            border-top: 4px solid var(--model-color);
            border-radius: 15px;
            background: rgba(17, 24, 39, 0.88);
        }

        .eq-model-name {
            margin-bottom: 0.75rem;
            color: var(--model-color);
            font-size: 1.05rem;
            font-weight: 900;
        }

        .eq-model-text {
            min-height: 3.6rem;
            color: #cbd5e1;
            font-size: 0.82rem;
            line-height: 1.5;
        }

        .eq-model-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.64rem 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        }

        .eq-model-row:last-child {
            border-bottom: none;
        }

        .eq-model-label {
            color: var(--eq-muted);
            font-size: 0.78rem;
        }

        .eq-model-value {
            color: var(--eq-text);
            font-size: 0.8rem;
            font-weight: 850;
            text-align: right;
        }

        .eq-concept-card {
            height: 100%;
            min-height: 195px;
            padding: 1.05rem;
            border: 1px solid var(--eq-border);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.86);
        }

        .eq-concept-icon {
            margin-bottom: 0.55rem;
            font-size: 1.55rem;
        }

        .eq-concept-title {
            margin-bottom: 0.45rem;
            color: var(--eq-text);
            font-size: 0.98rem;
            font-weight: 850;
        }

        .eq-concept-text {
            color: var(--eq-muted);
            font-size: 0.8rem;
            line-height: 1.5;
        }

        .eq-info,
        .eq-warning,
        .eq-success,
        .eq-conclusion {
            margin: 0.9rem 0;
            padding: 0.95rem 1rem;
            border-radius: 11px;
            line-height: 1.58;
        }

        .eq-info {
            border: 1px solid rgba(56, 189, 248, 0.22);
            border-left: 4px solid #38bdf8;
            background: rgba(14, 116, 144, 0.09);
            color: #bae6fd;
        }

        .eq-warning {
            border: 1px solid rgba(245, 158, 11, 0.22);
            border-left: 4px solid #f59e0b;
            background: rgba(120, 53, 15, 0.12);
            color: #fde68a;
        }

        .eq-success {
            border: 1px solid rgba(34, 197, 94, 0.22);
            border-left: 4px solid #22c55e;
            background: rgba(20, 83, 45, 0.13);
            color: #bbf7d0;
        }

        .eq-conclusion {
            border: 1px solid rgba(37, 99, 235, 0.30);
            border-left: 5px solid #2563eb;
            background:
                linear-gradient(
                    120deg,
                    rgba(30, 64, 175, 0.18),
                    rgba(15, 23, 42, 0.92)
                );
            color: #dbeafe;
        }

        .eq-conclusion-title {
            margin-bottom: 0.45rem;
            color: #93c5fd;
            font-weight: 900;
        }

        .eq-detail-card {
            height: 100%;
            padding: 1.05rem;
            border: 1px solid var(--eq-border);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.86);
        }

        .eq-detail-title {
            margin-bottom: 0.75rem;
            color: var(--eq-text);
            font-weight: 850;
        }

        .eq-detail-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.62rem 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        }

        .eq-detail-row:last-child {
            border-bottom: none;
        }

        .eq-detail-label {
            color: var(--eq-muted);
            font-size: 0.78rem;
        }

        .eq-detail-value {
            color: var(--eq-text);
            font-size: 0.8rem;
            font-weight: 850;
            text-align: right;
        }

        @media (max-width: 900px) {
            .eq-metric-card,
            .eq-concept-card {
                min-height: auto;
            }

            .eq-model-text {
                min-height: auto;
            }
        }
    </style>
    """
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
# MAPEAMENTOS
# ============================================================

MAPA_MODELOS = {
    "Modelo completo": "Modelo completo",
    "Modelo sem variáveis demográficas": "Modelo reduzido",
}


MAPA_ATRIBUTOS = {
    "sexo": "Sexo",
    "escolaridade": "Escolaridade",
    "estado_civil": "Estado civil",
    "estado civil": "Estado civil",
    "faixa_idade": "Faixa de idade",
    "faixa de idade": "Faixa de idade",
    "idade": "Faixa de idade",
}


METRICAS_DIFERENCA = {
    "diferenca_classificacao_alto_risco": (
        "Classificação de alto risco"
    ),
    "diferenca_recall": "Recall",
    "diferenca_falso_positivo": (
        "Taxa de falso positivo"
    ),
    "diferenca_falso_negativo": (
        "Taxa de falso negativo"
    ),
}


METRICAS_GRUPO = {
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
    "precisao": "Precisão",
    "taxa_inadimplencia_real": (
        "Taxa real de inadimplência"
    ),
}


CORES_MODELOS = alt.Scale(
    domain=[
        "Modelo completo",
        "Modelo reduzido",
    ],
    range=[
        "#a855f7",
        "#38bdf8",
    ],
)


# ============================================================
# FUNÇÕES DE CARREGAMENTO
# ============================================================

@st.cache_data
def carregar_csv(
    caminho: Path,
):
    """
    Carrega um arquivo CSV.
    """

    if not caminho.exists():
        return None

    return pd.read_csv(
        caminho
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
    casas: int = 2,
) -> str:
    """
    Formata um valor decimal como percentual.
    """

    return format(
        float(valor),
        f".{casas}%",
    )


def formatar_diferenca_pp(
    valor,
) -> str:
    """
    Formata diferença como pontos percentuais.
    """

    pontos = float(
        valor
    ) * 100

    return f"{pontos:+.2f} p.p."


def formatar_diferenca_auc(
    valor,
) -> str:
    """
    Formata diferença de AUC.
    """

    return f"{float(valor):+.4f}"


def nome_atributo(
    valor,
) -> str:
    """
    Converte o nome técnico de um atributo.
    """

    texto = str(
        valor
    )

    texto_normalizado = (
        texto
        .strip()
        .lower()
    )

    return MAPA_ATRIBUTOS.get(
        texto_normalizado,
        texto.replace(
            "_",
            " ",
        ).title(),
    )


def preparar_nomes(
    tabela: pd.DataFrame,
) -> pd.DataFrame:
    """
    Adiciona nomes amigáveis para modelos e atributos.
    """

    resultado = tabela.copy()

    resultado[
        "modelo_exibicao"
    ] = (
        resultado[
            "modelo"
        ]
        .replace(
            MAPA_MODELOS
        )
    )

    if "atributo" in resultado.columns:

        resultado[
            "atributo_exibicao"
        ] = resultado[
            "atributo"
        ].map(
            nome_atributo
        )

    return resultado


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
            class="eq-metric-card"
            style="--card-color: {cor};"
        >
            <div class="eq-metric-label">
                {titulo}
            </div>

            <div class="eq-metric-value">
                {valor}
            </div>

            <div class="eq-metric-text">
                {texto}
            </div>
        </div>
        """
    )


def aplicar_tema(
    grafico,
):
    """
    Aplica o tema visual aos gráficos Altair.
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


def formatar_tabela_equidade(
    tabela: pd.DataFrame,
) -> pd.DataFrame:
    """
    Formata a tabela detalhada por grupo.
    """

    resultado = tabela.copy()

    colunas_percentuais = [
        "taxa_inadimplencia_real",
        "taxa_classificacao_alto_risco",
        "precisao",
        "recall",
        "taxa_falso_positivo",
        "taxa_falso_negativo",
    ]

    for coluna in colunas_percentuais:

        resultado[
            coluna
        ] = resultado[
            coluna
        ].map(
            lambda valor: formatar_percentual(
                valor,
                2,
            )
        )

    resultado = resultado.rename(
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

    return resultado[
        [
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


arquivos = {
    "comparação dos modelos": comparacao,
    "análise detalhada de equidade": equidade,
    "diferenças de equidade": diferencas,
    "resumo da comparação": resumo,
}


arquivos_ausentes = [
    nome
    for nome, conteudo
    in arquivos.items()
    if conteudo is None
]


if arquivos_ausentes:

    st.error(
        "Alguns arquivos da análise não foram encontrados."
    )

    st.write(
        "**Arquivos ausentes:**",
        ", ".join(
            arquivos_ausentes
        ),
    )

    st.code(
        "python compare_sensitive_features.py"
    )

    st.stop()


# ============================================================
# PREPARAÇÃO DAS TABELAS
# ============================================================

comparacao = preparar_nomes(
    comparacao
)

equidade = preparar_nomes(
    equidade
)

diferencas = preparar_nomes(
    diferencas
)


linha_completo = (
    comparacao[
        comparacao[
            "modelo_exibicao"
        ]
        == "Modelo completo"
    ]
    .iloc[0]
)


linha_reduzido = (
    comparacao[
        comparacao[
            "modelo_exibicao"
        ]
        == "Modelo reduzido"
    ]
    .iloc[0]
)


modelo_completo = resumo[
    "modelo_completo"
]

modelo_reduzido = resumo[
    "modelo_reduzido"
]


# ============================================================
# DIFERENÇAS DE DESEMPENHO
# ============================================================

diferenca_pr_auc = float(
    resumo[
        "diferenca_pr_auc"
    ]
)

diferenca_roc_auc = float(
    resumo[
        "diferenca_roc_auc"
    ]
)

diferenca_recall = float(
    resumo[
        "diferenca_recall"
    ]
)

diferenca_precisao = float(
    resumo[
        "diferenca_precisao"
    ]
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## Objetivo da página"
    )

    st.write(
        "Comparar desempenho e diferenças entre grupos."
    )

    st.divider()

    st.markdown(
        "### Modelo reduzido"
    )

    st.write(
        "Não utiliza diretamente:"
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
        "Menor diferença entre grupos não significa "
        "automaticamente justiça ou ausência de viés."
    )


# ============================================================
# CABEÇALHO
# ============================================================

html(
    """
    <div class="eq-badge">
        ● Governança, equidade e risco de modelo
    </div>

    <h1 class="eq-title">
        ⚖️ Equidade e IA responsável
    </h1>

    <p class="eq-subtitle">
        Compare o modelo completo com uma versão que não
        utiliza diretamente sexo, escolaridade ou estado
        civil e observe como desempenho e diferenças entre
        grupos foram afetados.
    </p>
    """
)


html(
    """
    <div class="eq-warning">
        ⚠️ Remover variáveis demográficas não garante
        automaticamente um modelo justo. Outras informações
        podem funcionar como proxies, e a versão reduzida
        continua utilizando idade.
    </div>
    """
)


with st.expander(
    "Entenda esta página em 30 segundos"
):

    st.markdown(
        """
        1. O **modelo completo** utiliza todas as variáveis
           disponíveis.

        2. O **modelo reduzido** retira sexo, escolaridade
           e estado civil.

        3. Comparamos quanto de desempenho foi perdido.

        4. Depois medimos recall, falsos positivos e falsos
           negativos entre diferentes grupos.

        5. A análise não declara um modelo como
           universalmente justo ou injusto.
        """
    )


# ============================================================
# PERGUNTA CENTRAL
# ============================================================

html(
    """
    <div class="eq-kicker">
        Pergunta central
    </div>

    <h2 class="eq-section-title">
        É possível retirar atributos demográficos sem
        comprometer o desempenho?
    </h2>

    <p class="eq-description">
        As diferenças abaixo representam o resultado do
        modelo reduzido menos o resultado do modelo completo.
    </p>
    """
)


(
    coluna_metrica_1,
    coluna_metrica_2,
    coluna_metrica_3,
    coluna_metrica_4,
) = st.columns(4)


with coluna_metrica_1:

    renderizar_metrica(
        titulo="Diferença de PR AUC",
        valor=formatar_diferenca_auc(
            diferenca_pr_auc
        ),
        texto=(
            "Variação na métrica priorizada durante "
            "a seleção do modelo."
        ),
        cor="#a855f7",
    )


with coluna_metrica_2:

    renderizar_metrica(
        titulo="Diferença de ROC AUC",
        valor=formatar_diferenca_auc(
            diferenca_roc_auc
        ),
        texto=(
            "Variação na capacidade geral de separar "
            "as duas classes."
        ),
        cor="#2563eb",
    )


with coluna_metrica_3:

    renderizar_metrica(
        titulo="Diferença de recall",
        valor=formatar_diferenca_pp(
            diferenca_recall
        ),
        texto=(
            "Mudança na proporção de inadimplentes "
            "corretamente identificados."
        ),
        cor="#38bdf8",
    )


with coluna_metrica_4:

    renderizar_metrica(
        titulo="Diferença de precisão",
        valor=formatar_diferenca_pp(
            diferenca_precisao
        ),
        texto=(
            "Mudança na proporção de alertas que "
            "realmente correspondiam a inadimplentes."
        ),
        cor="#f59e0b",
    )


if abs(
    diferenca_pr_auc
) < 0.01:

    html(
        """
        <div class="eq-success">
            ✅ A retirada das três variáveis provocou uma
            perda pequena de desempenho preditivo. Isso
            permitiu usar o modelo reduzido como versão
            principal da aplicação sem alteração relevante
            na capacidade global de previsão.
        </div>
        """
    )

else:

    html(
        """
        <div class="eq-warning">
            ⚠️ A retirada das variáveis provocou uma
            alteração relevante de desempenho e exigiria
            análise adicional antes da escolha da versão
            principal.
        </div>
        """
    )


# ============================================================
# CONFIGURAÇÃO DOS MODELOS
# ============================================================

html(
    """
    <div class="eq-kicker">
        Configuração
    </div>

    <h2 class="eq-section-title">
        Qual é a diferença entre os dois modelos?
    </h2>
    """
)


(
    coluna_modelo_completo,
    coluna_modelo_reduzido,
) = st.columns(2)


with coluna_modelo_completo:

    threshold_completo = formatar_percentual(
        linha_completo[
            "threshold"
        ],
        0,
    )

    pr_auc_completo = (
        f"{linha_completo['pr_auc']:.4f}"
    )

    recall_completo = formatar_percentual(
        linha_completo[
            "recall"
        ],
        2,
    )

    precisao_completo = formatar_percentual(
        linha_completo[
            "precisao"
        ],
        2,
    )

    html(
        f"""
        <div
            class="eq-model-card"
            style="--model-color: #a855f7;"
        >
            <div class="eq-model-name">
                Modelo completo
            </div>

            <div class="eq-model-text">
                Utiliza todas as variáveis disponíveis,
                inclusive sexo, escolaridade e estado civil.
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    Variáveis
                </span>

                <span class="eq-model-value">
                    23
                </span>
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    Threshold
                </span>

                <span class="eq-model-value">
                    {threshold_completo}
                </span>
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    Recall
                </span>

                <span class="eq-model-value">
                    {recall_completo}
                </span>
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    Precisão
                </span>

                <span class="eq-model-value">
                    {precisao_completo}
                </span>
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    PR AUC
                </span>

                <span class="eq-model-value">
                    {pr_auc_completo}
                </span>
            </div>
        </div>
        """
    )


with coluna_modelo_reduzido:

    threshold_reduzido = formatar_percentual(
        linha_reduzido[
            "threshold"
        ],
        0,
    )

    pr_auc_reduzido = (
        f"{linha_reduzido['pr_auc']:.4f}"
    )

    recall_reduzido = formatar_percentual(
        linha_reduzido[
            "recall"
        ],
        2,
    )

    precisao_reduzido = formatar_percentual(
        linha_reduzido[
            "precisao"
        ],
        2,
    )

    html(
        f"""
        <div
            class="eq-model-card"
            style="--model-color: #38bdf8;"
        >
            <div class="eq-model-name">
                Modelo reduzido
            </div>

            <div class="eq-model-text">
                Não utiliza diretamente sexo, escolaridade
                ou estado civil. A idade permanece no modelo.
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    Variáveis
                </span>

                <span class="eq-model-value">
                    20
                </span>
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    Threshold
                </span>

                <span class="eq-model-value">
                    {threshold_reduzido}
                </span>
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    Recall
                </span>

                <span class="eq-model-value">
                    {recall_reduzido}
                </span>
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    Precisão
                </span>

                <span class="eq-model-value">
                    {precisao_reduzido}
                </span>
            </div>

            <div class="eq-model-row">
                <span class="eq-model-label">
                    PR AUC
                </span>

                <span class="eq-model-value">
                    {pr_auc_reduzido}
                </span>
            </div>
        </div>
        """
    )


# ============================================================
# COMPARAÇÃO DE DESEMPENHO
# ============================================================

html(
    """
    <div class="eq-kicker">
        Desempenho preditivo
    </div>

    <h2 class="eq-section-title">
        Quanto o modelo reduzido perdeu?
    </h2>

    <p class="eq-description">
        Quanto mais próximas estiverem as barras, menor foi
        o impacto da retirada das variáveis.
    </p>
    """
)


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
    .mark_bar(
        cornerRadiusEnd=5,
    )
    .encode(
        x=alt.X(
            "metrica:N",
            title=None,
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
                format=".0%",
            ),
        ),

        color=alt.Color(
            "modelo_exibicao:N",
            title=None,
            scale=CORES_MODELOS,
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
                format=".4f",
            ),
        ],
    )
    .properties(
        height=410,
    )
)


st.altair_chart(
    aplicar_tema(
        grafico_desempenho
    ),
    use_container_width=True,
    theme=None,
)


with st.expander(
    "Ver tabela completa de desempenho"
):

    comparacao_formatada = (
        comparacao.copy()
    )


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

        comparacao_formatada[
            coluna
        ] = comparacao_formatada[
            coluna
        ].map(
            lambda valor: formatar_percentual(
                valor,
                2,
            )
        )


    for coluna in [
        "roc_auc",
        "pr_auc",
    ]:

        comparacao_formatada[
            coluna
        ] = comparacao_formatada[
            coluna
        ].map(
            lambda valor: f"{valor:.4f}"
        )


    comparacao_formatada = (
        comparacao_formatada.rename(
            columns={
                "modelo_exibicao": "Modelo",
                "usa_variaveis_demograficas": (
                    "Usa variáveis removidas"
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
                "Usa variáveis removidas",
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
# CONCEITOS DE EQUIDADE
# ============================================================

html(
    """
    <div class="eq-kicker">
        Entendendo a análise
    </div>

    <h2 class="eq-section-title">
        Quais métricas são comparadas entre os grupos?
    </h2>
    """
)


(
    coluna_conceito_1,
    coluna_conceito_2,
    coluna_conceito_3,
    coluna_conceito_4,
) = st.columns(4)


with coluna_conceito_1:

    html(
        """
        <div class="eq-concept-card">
            <div class="eq-concept-icon">
                🚨
            </div>

            <div class="eq-concept-title">
                Classificação de alto risco
            </div>

            <div class="eq-concept-text">
                Percentual de pessoas do grupo classificadas
                pelo modelo como alto risco.

                Diferenças grandes mostram que os grupos
                recebem alertas em proporções diferentes.
            </div>
        </div>
        """
    )


with coluna_conceito_2:

    html(
        """
        <div class="eq-concept-card">
            <div class="eq-concept-icon">
                🔎
            </div>

            <div class="eq-concept-title">
                Recall
            </div>

            <div class="eq-concept-text">
                Entre os inadimplentes reais de cada grupo,
                mede quantos foram identificados.

                Recall diferente significa capacidade de
                detecção diferente entre os grupos.
            </div>
        </div>
        """
    )


with coluna_conceito_3:

    html(
        """
        <div class="eq-concept-card">
            <div class="eq-concept-icon">
                ⚠️
            </div>

            <div class="eq-concept-title">
                Falso positivo
            </div>

            <div class="eq-concept-text">
                Cliente adimplente classificado como alto
                risco.

                Em um cenário real, isso poderia provocar
                análise adicional ou restrição indevida.
            </div>
        </div>
        """
    )


with coluna_conceito_4:

    html(
        """
        <div class="eq-concept-card">
            <div class="eq-concept-icon">
                🕳️
            </div>

            <div class="eq-concept-title">
                Falso negativo
            </div>

            <div class="eq-concept-text">
                Cliente inadimplente que não foi identificado.

                Em um cenário real, representa risco que
                passou sem sinalização preventiva.
            </div>
        </div>
        """
    )


html(
    """
    <div class="eq-info">
        Uma diferença menor entre grupos pode ser desejável,
        mas nenhuma métrica isolada define equidade. Melhorar
        uma medida pode piorar outra, especialmente quando
        as taxas reais de inadimplência diferem entre grupos.
    </div>
    """
)


# ============================================================
# DIFERENÇAS ENTRE GRUPOS
# ============================================================

html(
    """
    <div class="eq-kicker">
        Comparação das disparidades
    </div>

    <h2 class="eq-section-title">
        As diferenças entre grupos diminuíram?
    </h2>

    <p class="eq-description">
        Cada barra mostra a distância entre o grupo com maior
        resultado e o grupo com menor resultado. Valores
        menores indicam menor diferença naquela métrica.
    </p>
    """
)


metrica_diferenca = st.selectbox(
    "Escolha a métrica de diferença",
    options=list(
        METRICAS_DIFERENCA.keys()
    ),
    format_func=lambda valor: (
        METRICAS_DIFERENCA[
            valor
        ]
    ),
)


dados_grafico_diferencas = (
    diferencas[
        [
            "modelo_exibicao",
            "atributo_exibicao",
            metrica_diferenca,
        ]
    ]
    .copy()
    .rename(
        columns={
            metrica_diferenca: "valor"
        }
    )
)


grafico_diferencas = (
    alt.Chart(
        dados_grafico_diferencas
    )
    .mark_bar(
        cornerRadiusEnd=5,
    )
    .encode(
        x=alt.X(
            "atributo_exibicao:N",
            title=None,
        ),

        y=alt.Y(
            "valor:Q",
            title="Diferença entre grupos",
            axis=alt.Axis(
                format=".0%",
            ),
        ),

        color=alt.Color(
            "modelo_exibicao:N",
            title=None,
            scale=CORES_MODELOS,
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
                "atributo_exibicao:N",
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
        height=410,
    )
)


st.altair_chart(
    aplicar_tema(
        grafico_diferencas
    ),
    use_container_width=True,
    theme=None,
)


# ============================================================
# RESUMO DINÂMICO DAS MUDANÇAS
# ============================================================

comparacao_mudancas = (
    diferencas[
        [
            "modelo_exibicao",
            "atributo_exibicao",
            metrica_diferenca,
        ]
    ]
    .pivot(
        index="atributo_exibicao",
        columns="modelo_exibicao",
        values=metrica_diferenca,
    )
    .reset_index()
)


comparacao_mudancas[
    "mudanca"
] = (
    comparacao_mudancas[
        "Modelo reduzido"
    ]
    - comparacao_mudancas[
        "Modelo completo"
    ]
)


quantidade_reducoes = int(
    (
        comparacao_mudancas[
            "mudanca"
        ]
        < 0
    ).sum()
)


quantidade_aumentos = int(
    (
        comparacao_mudancas[
            "mudanca"
        ]
        > 0
    ).sum()
)


if quantidade_reducoes > 0:

    atributo_maior_reducao = (
        comparacao_mudancas
        .sort_values(
            "mudanca"
        )
        .iloc[0]
    )

    reducao_texto = formatar_diferenca_pp(
        atributo_maior_reducao[
            "mudanca"
        ]
    )

    atributo_reducao_texto = (
        atributo_maior_reducao[
            "atributo_exibicao"
        ]
    )

else:

    reducao_texto = "0,00 p.p."

    atributo_reducao_texto = (
        "Nenhum atributo"
    )


if quantidade_aumentos > 0:

    atributo_maior_aumento = (
        comparacao_mudancas
        .sort_values(
            "mudanca",
            ascending=False,
        )
        .iloc[0]
    )

    aumento_texto = formatar_diferenca_pp(
        atributo_maior_aumento[
            "mudanca"
        ]
    )

    atributo_aumento_texto = (
        atributo_maior_aumento[
            "atributo_exibicao"
        ]
    )

else:

    aumento_texto = "0,00 p.p."

    atributo_aumento_texto = (
        "Nenhum atributo"
    )


html(
    f"""
    <div class="eq-info">
        Para a métrica
        <strong>
            {METRICAS_DIFERENCA[metrica_diferenca]}
        </strong>,
        o modelo reduzido diminuiu a diferença em
        <strong>{quantidade_reducoes}</strong> atributo(s)
        e aumentou em
        <strong>{quantidade_aumentos}</strong>.

        A maior redução ocorreu em
        <strong>{atributo_reducao_texto}</strong>
        ({reducao_texto}), enquanto o maior aumento ocorreu
        em <strong>{atributo_aumento_texto}</strong>
        ({aumento_texto}).
    </div>
    """
)


with st.expander(
    "Ver todas as diferenças em tabela"
):

    tabela_diferencas = (
        diferencas.copy()
    )


    for coluna in [
        "diferenca_classificacao_alto_risco",
        "diferenca_recall",
        "diferenca_falso_positivo",
        "diferenca_falso_negativo",
    ]:

        tabela_diferencas[
            coluna
        ] = tabela_diferencas[
            coluna
        ].map(
            lambda valor: formatar_percentual(
                valor,
                2,
            )
        )


    tabela_diferencas = tabela_diferencas.rename(
        columns={
            "modelo_exibicao": "Modelo",
            "atributo_exibicao": "Atributo",
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


    st.dataframe(
        tabela_diferencas[
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
# ANÁLISE DETALHADA POR GRUPO
# ============================================================

html(
    """
    <div class="eq-kicker">
        Investigação detalhada
    </div>

    <h2 class="eq-section-title">
        Como cada grupo foi afetado?
    </h2>

    <p class="eq-description">
        Escolha um atributo e uma métrica para comparar os
        resultados de cada grupo nos dois modelos.
    </p>
    """
)


atributos_disponiveis = (
    equidade[
        [
            "atributo",
            "atributo_exibicao",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        "atributo_exibicao"
    )
)


mapa_selecao_atributos = dict(
    zip(
        atributos_disponiveis[
            "atributo_exibicao"
        ],
        atributos_disponiveis[
            "atributo"
        ],
    )
)


coluna_selecao_1, coluna_selecao_2 = st.columns(2)


with coluna_selecao_1:

    atributo_exibicao_selecionado = st.selectbox(
        "Atributo analisado",
        options=list(
            mapa_selecao_atributos.keys()
        ),
    )


with coluna_selecao_2:

    metrica_grupo = st.selectbox(
        "Métrica detalhada",
        options=list(
            METRICAS_GRUPO.keys()
        ),
        format_func=lambda valor: (
            METRICAS_GRUPO[
                valor
            ]
        ),
    )


atributo_original_selecionado = (
    mapa_selecao_atributos[
        atributo_exibicao_selecionado
    ]
)


equidade_atributo = (
    equidade[
        equidade[
            "atributo"
        ]
        == atributo_original_selecionado
    ]
    .copy()
)


equidade_atributo[
    "grupo"
] = equidade_atributo[
    "grupo"
].astype(
    str
)


grupos_pequenos = (
    equidade_atributo[
        equidade_atributo[
            "registros"
        ]
        < 100
    ][
        [
            "grupo",
            "registros",
        ]
    ]
    .drop_duplicates()
)


if not grupos_pequenos.empty:

    grupos_texto = ", ".join(
        f"{linha['grupo']} "
        f"({formatar_numero(linha['registros'])} registros)"
        for _, linha in grupos_pequenos.iterrows()
    )

    html(
        f"""
        <div class="eq-warning">
            ⚠️ Grupos com amostra pequena:
            <strong>{grupos_texto}</strong>.

            Métricas calculadas com poucos registros são
            mais instáveis e devem ser interpretadas com
            cautela.
        </div>
        """
    )


dados_grafico_grupos = (
    equidade_atributo[
        [
            "modelo_exibicao",
            "grupo",
            "registros",
            metrica_grupo,
        ]
    ]
    .rename(
        columns={
            metrica_grupo: "valor"
        }
    )
)


grafico_grupos = (
    alt.Chart(
        dados_grafico_grupos
    )
    .mark_bar(
        cornerRadiusEnd=5,
    )
    .encode(
        x=alt.X(
            "grupo:N",
            title=atributo_exibicao_selecionado,
        ),

        y=alt.Y(
            "valor:Q",
            title=METRICAS_GRUPO[
                metrica_grupo
            ],
            scale=alt.Scale(
                domain=[
                    0,
                    1,
                ]
            ),
            axis=alt.Axis(
                format=".0%",
            ),
        ),

        color=alt.Color(
            "modelo_exibicao:N",
            title=None,
            scale=CORES_MODELOS,
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
                "registros:Q",
                title="Registros",
                format=",",
            ),

            alt.Tooltip(
                "valor:Q",
                title=METRICAS_GRUPO[
                    metrica_grupo
                ],
                format=".2%",
            ),
        ],
    )
    .properties(
        height=430,
    )
)


st.altair_chart(
    aplicar_tema(
        grafico_grupos
    ),
    use_container_width=True,
    theme=None,
)


# ============================================================
# LEITURA DO MODELO REDUZIDO
# ============================================================

dados_reduzidos_atributo = (
    equidade_atributo[
        equidade_atributo[
            "modelo_exibicao"
        ]
        == "Modelo reduzido"
    ]
    .copy()
)


if not dados_reduzidos_atributo.empty:

    grupo_maior_resultado = (
        dados_reduzidos_atributo
        .sort_values(
            metrica_grupo,
            ascending=False,
        )
        .iloc[0]
    )


    grupo_menor_resultado = (
        dados_reduzidos_atributo
        .sort_values(
            metrica_grupo,
            ascending=True,
        )
        .iloc[0]
    )


    maior_resultado_texto = (
        formatar_percentual(
            grupo_maior_resultado[
                metrica_grupo
            ],
            2,
        )
    )


    menor_resultado_texto = (
        formatar_percentual(
            grupo_menor_resultado[
                metrica_grupo
            ],
            2,
        )
    )


    diferenca_detalhada = (
        float(
            grupo_maior_resultado[
                metrica_grupo
            ]
        )
        - float(
            grupo_menor_resultado[
                metrica_grupo
            ]
        )
    )


    diferenca_detalhada_texto = (
        formatar_percentual(
            diferenca_detalhada,
            2,
        )
    )


    html(
        f"""
        <div class="eq-info">
            No modelo reduzido, o maior resultado de
            <strong>
                {METRICAS_GRUPO[metrica_grupo]}
            </strong>
            foi observado no grupo
            <strong>{grupo_maior_resultado['grupo']}</strong>
            ({maior_resultado_texto}).

            O menor resultado apareceu no grupo
            <strong>{grupo_menor_resultado['grupo']}</strong>
            ({menor_resultado_texto}).

            A diferença entre eles foi de
            <strong>{diferenca_detalhada_texto}</strong>.
        </div>
        """
    )


with st.expander(
    "Ver tabela detalhada dos grupos"
):

    tabela_equidade = (
        formatar_tabela_equidade(
            equidade_atributo
        )
    )


    st.dataframe(
        tabela_equidade,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# INTERPRETAÇÃO
# ============================================================

html(
    """
    <div class="eq-kicker">
        Interpretação responsável
    </div>

    <h2 class="eq-section-title">
        O modelo reduzido é automaticamente mais justo?
    </h2>
    """
)


html(
    """
    <div class="eq-conclusion">
        <div class="eq-conclusion-title">
            Não necessariamente
        </div>

        A retirada de sexo, escolaridade e estado civil
        reduz o uso direto dessas informações e preserva
        quase todo o desempenho preditivo.

        Entretanto, algumas diferenças entre grupos diminuem
        enquanto outras podem aumentar. Além disso, idade,
        histórico financeiro, limite e outras variáveis podem
        carregar relações indiretas com características
        demográficas.
    </div>
    """
)


(
    coluna_interpretacao_1,
    coluna_interpretacao_2,
) = st.columns(2)


with coluna_interpretacao_1:

    html(
        """
        <div class="eq-detail-card">
            <div class="eq-detail-title">
                O que a versão reduzida melhora?
            </div>

            <div class="eq-detail-row">
                <span class="eq-detail-label">
                    Uso direto de sexo
                </span>

                <span class="eq-detail-value">
                    Removido
                </span>
            </div>

            <div class="eq-detail-row">
                <span class="eq-detail-label">
                    Uso direto de escolaridade
                </span>

                <span class="eq-detail-value">
                    Removido
                </span>
            </div>

            <div class="eq-detail-row">
                <span class="eq-detail-label">
                    Uso direto de estado civil
                </span>

                <span class="eq-detail-value">
                    Removido
                </span>
            </div>

            <div class="eq-detail-row">
                <span class="eq-detail-label">
                    Perda de desempenho
                </span>

                <span class="eq-detail-value">
                    Pequena
                </span>
            </div>
        </div>
        """
    )


with coluna_interpretacao_2:

    html(
        """
        <div class="eq-detail-card">
            <div class="eq-detail-title">
                O que ainda exige atenção?
            </div>

            <div class="eq-detail-row">
                <span class="eq-detail-label">
                    Idade
                </span>

                <span class="eq-detail-value">
                    Continua no modelo
                </span>
            </div>

            <div class="eq-detail-row">
                <span class="eq-detail-label">
                    Variáveis proxy
                </span>

                <span class="eq-detail-value">
                    Podem existir
                </span>
            </div>

            <div class="eq-detail-row">
                <span class="eq-detail-label">
                    Grupos pequenos
                </span>

                <span class="eq-detail-value">
                    Métricas instáveis
                </span>
            </div>

            <div class="eq-detail-row">
                <span class="eq-detail-label">
                    Monitoramento
                </span>

                <span class="eq-detail-value">
                    Necessário
                </span>
            </div>
        </div>
        """
    )


# ============================================================
# GOVERNANÇA
# ============================================================

html(
    """
    <div class="eq-kicker">
        Aplicação real
    </div>

    <h2 class="eq-section-title">
        O que seria necessário antes de usar este modelo?
    </h2>
    """
)


with st.expander(
    "Ver controles recomendados para uma aplicação real",
    expanded=True,
):

    st.markdown(
        """
        ### Validação técnica

        - validação temporal e em uma população atual;
        - análise de calibração das probabilidades;
        - testes de estabilidade;
        - avaliação de drift;
        - revisão de variáveis proxy;
        - análise de explicabilidade individual.

        ### Governança

        - documentação da finalidade do modelo;
        - definição clara de responsáveis;
        - registro das versões;
        - aprovação por risco e compliance;
        - revisão periódica do threshold;
        - monitoramento de impacto por grupo.

        ### Decisão de negócio

        - participação de especialistas de crédito;
        - análise humana para casos sensíveis;
        - canal de contestação;
        - definição de consequências para falsos positivos;
        - proibição de decisão automática baseada somente
          no score.

        ### Aspectos jurídicos e regulatórios

        - análise da legislação aplicável;
        - revisão de privacidade e proteção de dados;
        - avaliação de não discriminação;
        - validação por jurídico e compliance.
        """
    )


# ============================================================
# LIMITAÇÕES
# ============================================================

with st.expander(
    "Ver limitações desta análise"
):

    st.markdown(
        """
        1. A base representa clientes históricos de Taiwan.

        2. O modelo reduzido ainda utiliza idade.

        3. Retirar atributos não elimina proxies.

        4. Alguns grupos possuem poucos registros.

        5. As métricas não comprovam causalidade.

        6. As taxas reais de inadimplência diferem entre
           grupos.

        7. Diferentes conceitos de equidade podem produzir
           conclusões diferentes.

        8. Os resultados não foram validados para o mercado
           brasileiro.

        9. O projeto não avalia todas as exigências
           regulatórias de uma operação real.
        """
    )


# ============================================================
# CONCLUSÃO
# ============================================================

html(
    """
    <div class="eq-conclusion">
        <div class="eq-conclusion-title">
            O que concluímos?
        </div>

        O modelo reduzido é uma escolha defensável para este
        projeto porque não utiliza diretamente sexo,
        escolaridade ou estado civil e apresenta desempenho
        praticamente igual ao modelo completo.

        Essa escolha reduz um risco de governança, mas não
        comprova equidade. As métricas mostram resultados
        mistos entre grupos, tornando necessário monitorar
        continuamente falsos positivos, falsos negativos e
        outras diferenças ao longo do tempo.
    </div>
    """
)


# ============================================================
# AVISO FINAL
# ============================================================

st.divider()


st.caption(
    "Análise educacional de IA responsável. Os resultados "
    "não validam uma política real de crédito e não devem "
    "ser utilizados isoladamente para conceder, negar ou "
    "alterar condições de crédito."
)