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
    page_title="Desempenho do modelo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# FUNÇÕES VISUAIS
# ============================================================

def html(conteudo: str) -> None:
    """
    Renderiza HTML e CSS na página.
    """

    st.html(
        dedent(conteudo).strip()
    )


html(
    """
    <style>
        :root {
            --background: #080d15;
            --surface: #111827;
            --border: #273247;
            --text: #f8fafc;
            --muted: #94a3b8;
            --blue: #2563eb;
            --cyan: #38bdf8;
            --green: #22c55e;
            --yellow: #f59e0b;
            --red: #ef4444;
            --purple: #a855f7;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 84% 0%,
                    rgba(37, 99, 235, 0.12),
                    transparent 28rem
                ),
                var(--background);
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
            border: 1px solid var(--border);
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.62);
        }

        .badge {
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

        .title {
            margin: 0;
            color: var(--text);
            font-size: clamp(2.2rem, 4vw, 3.45rem);
            font-weight: 900;
            line-height: 1.05;
        }

        .subtitle {
            max-width: 950px;
            margin: 0.75rem 0 1.2rem;
            color: #cbd5e1;
            font-size: 1.08rem;
            line-height: 1.65;
        }

        .kicker {
            margin-top: 1.4rem;
            margin-bottom: 0.3rem;
            color: #60a5fa;
            font-size: 0.76rem;
            font-weight: 850;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .section-title {
            margin: 0 0 0.35rem;
            color: var(--text);
            font-size: 1.7rem;
            font-weight: 850;
        }

        .description {
            margin: 0 0 1.1rem;
            color: var(--muted);
            line-height: 1.55;
        }

        .metric-card {
            height: 100%;
            min-height: 170px;
            padding: 1.05rem 1.1rem;
            border: 1px solid var(--border);
            border-top: 3px solid var(--card-color);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.90);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
        }

        .metric-label {
            margin-bottom: 0.45rem;
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 750;
        }

        .metric-value {
            color: var(--card-color);
            font-size: 1.9rem;
            font-weight: 900;
            line-height: 1.15;
        }

        .metric-text {
            margin-top: 0.65rem;
            color: #cbd5e1;
            font-size: 0.8rem;
            line-height: 1.45;
        }

        .explanation-card {
            height: 100%;
            min-height: 185px;
            padding: 1.05rem 1.1rem;
            border: 1px solid var(--border);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.86);
        }

        .explanation-icon {
            margin-bottom: 0.55rem;
            font-size: 1.6rem;
        }

        .explanation-title {
            margin-bottom: 0.45rem;
            color: var(--text);
            font-size: 1rem;
            font-weight: 850;
        }

        .explanation-text {
            color: var(--muted);
            font-size: 0.82rem;
            line-height: 1.5;
        }

        .summary-box {
            height: 100%;
            padding: 1.1rem;
            border: 1px solid var(--border);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.86);
        }

        .summary-title {
            margin-bottom: 0.8rem;
            color: var(--text);
            font-size: 1rem;
            font-weight: 850;
        }

        .summary-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.67rem 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        }

        .summary-row:last-child {
            border-bottom: none;
        }

        .summary-label {
            color: var(--muted);
            font-size: 0.8rem;
        }

        .summary-value {
            color: var(--text);
            font-size: 0.82rem;
            font-weight: 850;
            text-align: right;
        }

        .confusion-card {
            height: 100%;
            min-height: 175px;
            padding: 1.05rem;
            border: 1px solid var(--border);
            border-left: 5px solid var(--confusion-color);
            border-radius: 14px;
            background: rgba(17, 24, 39, 0.88);
        }

        .confusion-name {
            color: var(--muted);
            font-size: 0.76rem;
            font-weight: 750;
        }

        .confusion-number {
            margin: 0.3rem 0 0.55rem;
            color: var(--confusion-color);
            font-size: 2rem;
            font-weight: 900;
        }

        .confusion-description {
            color: #cbd5e1;
            font-size: 0.78rem;
            line-height: 1.45;
        }

        .info-box,
        .warning-box,
        .success-box,
        .verdict-box {
            margin: 0.9rem 0;
            padding: 0.95rem 1rem;
            border-radius: 11px;
            line-height: 1.55;
        }

        .info-box {
            border: 1px solid rgba(56, 189, 248, 0.22);
            border-left: 4px solid #38bdf8;
            background: rgba(14, 116, 144, 0.09);
            color: #bae6fd;
        }

        .warning-box {
            border: 1px solid rgba(245, 158, 11, 0.22);
            border-left: 4px solid #f59e0b;
            background: rgba(120, 53, 15, 0.12);
            color: #fde68a;
        }

        .success-box {
            border: 1px solid rgba(34, 197, 94, 0.22);
            border-left: 4px solid #22c55e;
            background: rgba(20, 83, 45, 0.13);
            color: #bbf7d0;
        }

        .verdict-box {
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

        .verdict-title {
            margin-bottom: 0.4rem;
            color: #93c5fd;
            font-weight: 900;
        }

        @media (max-width: 900px) {
            .metric-card,
            .explanation-card,
            .confusion-card {
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
# CARREGAMENTO
# ============================================================

@st.cache_data
def carregar_csv(
    caminho: Path,
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
    Formata um número inteiro no padrão brasileiro.
    """

    return f"{int(valor):,}".replace(
        ",",
        ".",
    )


def renderizar_card(
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
            class="metric-card"
            style="--card-color: {cor};"
        >
            <div class="metric-label">
                {titulo}
            </div>

            <div class="metric-value">
                {valor}
            </div>

            <div class="metric-text">
                {texto}
            </div>
        </div>
        """
    )


def renderizar_confusao(
    titulo: str,
    valor: int,
    descricao: str,
    cor: str,
) -> None:
    """
    Renderiza um cartão da matriz de confusão.
    """

    valor_formatado = formatar_numero(
        valor
    )

    html(
        f"""
        <div
            class="confusion-card"
            style="--confusion-color: {cor};"
        >
            <div class="confusion-name">
                {titulo}
            </div>

            <div class="confusion-number">
                {valor_formatado}
            </div>

            <div class="confusion-description">
                {descricao}
            </div>
        </div>
        """
    )


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
    for nome, conteudo
    in arquivos_obrigatorios.items()
    if conteudo is None
]


if arquivos_ausentes:

    st.error(
        "Alguns relatórios necessários não foram encontrados."
    )

    st.write(
        "**Arquivos ausentes:**",
        ", ".join(
            arquivos_ausentes
        ),
    )

    st.code(
        "python train_real_models.py\n"
        "python real_feature_importance.py"
    )

    st.stop()


# ============================================================
# MÉTRICAS
# ============================================================

acuracia = float(
    metricas_teste["acuracia"]
)

precisao = float(
    metricas_teste["precisao"]
)

recall = float(
    metricas_teste["recall"]
)

f1_score = float(
    metricas_teste["f1_score"]
)

roc_auc = float(
    metricas_teste["roc_auc"]
)

pr_auc = float(
    metricas_teste["pr_auc"]
)

threshold = float(
    politica["threshold_recomendado"]
)

taxa_base = float(
    metadata["taxa_inadimplencia_teste"]
)

taxa_total = float(
    metadata["taxa_inadimplencia_total"]
)


verdadeiros_negativos = int(
    metricas_teste["verdadeiros_negativos"]
)

falsos_positivos = int(
    metricas_teste["falsos_positivos"]
)

falsos_negativos = int(
    metricas_teste["falsos_negativos"]
)

verdadeiros_positivos = int(
    metricas_teste["verdadeiros_positivos"]
)


total_inadimplentes = (
    verdadeiros_positivos
    + falsos_negativos
)

total_adimplentes = (
    verdadeiros_negativos
    + falsos_positivos
)


taxa_nao_deteccao = (
    falsos_negativos
    / total_inadimplentes
    if total_inadimplentes > 0
    else 0
)

taxa_falso_alerta_adimplentes = (
    falsos_positivos
    / total_adimplentes
    if total_adimplentes > 0
    else 0
)

ganho_pr_auc = (
    pr_auc
    / taxa_base
    if taxa_base > 0
    else 0
)


# Textos previamente formatados.
# Isso evita o erro de formatação dentro do HTML.

acuracia_texto = f"{acuracia:.2%}"
precisao_texto = f"{precisao:.2%}"
recall_texto = f"{recall:.2%}"
f1_texto = f"{f1_score:.2%}"
roc_auc_texto = f"{roc_auc:.4f}"
pr_auc_texto = f"{pr_auc:.4f}"
threshold_texto = f"{threshold:.0%}"
taxa_base_texto = f"{taxa_base:.2%}"
taxa_total_texto = f"{taxa_total:.2%}"
taxa_nao_deteccao_texto = f"{taxa_nao_deteccao:.1%}"
taxa_falso_alerta_texto = (
    f"{taxa_falso_alerta_adimplentes:.1%}"
)


# ============================================================
# CABEÇALHO
# ============================================================

html(
    """
    <div class="badge">
        ● Avaliação técnica do Behavioral Score
    </div>

    <h1 class="title">
        📊 Desempenho do modelo
    </h1>

    <p class="subtitle">
        Entenda quanto o modelo consegue identificar clientes
        com risco de inadimplência, quais erros ele comete e
        por que o threshold de decisão foi definido em 36%.
    </p>
    """
)


st.info(
    "Esta página detalha o modelo completo de referência. "
    "A página Início utiliza a versão reduzida, sem uso direto "
    "de sexo, escolaridade ou estado civil."
)


# ============================================================
# RESPOSTA RÁPIDA
# ============================================================

html(
    """
    <div class="kicker">
        Resposta rápida
    </div>

    <h2 class="section-title">
        O que o modelo consegue fazer?
    </h2>

    <p class="description">
        As métricas foram calculadas em uma base de teste
        que não participou da escolha do algoritmo nem
        da escolha do threshold.
    </p>
    """
)


(
    coluna_card_1,
    coluna_card_2,
    coluna_card_3,
    coluna_card_4,
) = st.columns(4)


with coluna_card_1:

    renderizar_card(
        titulo="Inadimplentes identificados",
        valor=recall_texto,
        texto=(
            "De cada 100 clientes que realmente ficaram "
            "inadimplentes, o modelo identificou "
            f"aproximadamente {recall * 100:.0f}."
        ),
        cor="#38bdf8",
    )


with coluna_card_2:

    renderizar_card(
        titulo="Alertas que estavam corretos",
        valor=precisao_texto,
        texto=(
            "De cada 100 clientes classificados como alto "
            "risco, aproximadamente "
            f"{precisao * 100:.0f} ficaram inadimplentes."
        ),
        cor="#f59e0b",
    )


with coluna_card_3:

    renderizar_card(
        titulo="PR AUC",
        valor=pr_auc_texto,
        texto=(
            "Resultado aproximadamente "
            f"{ganho_pr_auc:.1f} vezes superior à taxa-base "
            "de inadimplência do teste."
        ),
        cor="#a855f7",
    )


with coluna_card_4:

    renderizar_card(
        titulo="Threshold de alto risco",
        valor=threshold_texto,
        texto=(
            "Probabilidades iguais ou superiores a esse "
            "valor são classificadas como alto risco."
        ),
        cor="#ef4444",
    )


html(
    f"""
    <div class="verdict-box">
        <div class="verdict-title">
            Conclusão em linguagem simples
        </div>

        O modelo encontra aproximadamente
        <strong>{recall * 100:.0f}% dos inadimplentes</strong>,
        mas também produz falsos alertas. Por isso, ele é
        mais indicado para triagem, monitoramento e priorização
        de análise do que para tomar sozinho uma decisão
        definitiva sobre o cliente.
    </div>
    """
)


# ============================================================
# SIGNIFICADO DAS MÉTRICAS
# ============================================================

html(
    """
    <div class="kicker">
        Entendendo as métricas
    </div>

    <h2 class="section-title">
        O que significam recall, precisão e AUC?
    </h2>

    <p class="description">
        Estas são as métricas mais importantes para avaliar
        um problema de classificação de risco.
    </p>
    """
)


(
    coluna_explicacao_1,
    coluna_explicacao_2,
    coluna_explicacao_3,
) = st.columns(3)


with coluna_explicacao_1:

    html(
        """
        <div class="explanation-card">
            <div class="explanation-icon">
                🔎
            </div>

            <div class="explanation-title">
                Recall
            </div>

            <div class="explanation-text">
                Mede quantos inadimplentes reais o modelo
                conseguiu encontrar.
                <br><br>
                Recall alto reduz a quantidade de clientes
                de risco que passam sem identificação.
            </div>
        </div>
        """
    )


with coluna_explicacao_2:

    html(
        """
        <div class="explanation-card">
            <div class="explanation-icon">
                🎯
            </div>

            <div class="explanation-title">
                Precisão
            </div>

            <div class="explanation-text">
                Mede quantos dos clientes sinalizados como
                alto risco realmente ficaram inadimplentes.
                <br><br>
                Precisão baixa representa maior quantidade
                de falsos alertas.
            </div>
        </div>
        """
    )


with coluna_explicacao_3:

    html(
        """
        <div class="explanation-card">
            <div class="explanation-icon">
                📈
            </div>

            <div class="explanation-title">
                ROC AUC e PR AUC
            </div>

            <div class="explanation-text">
                Avaliam a capacidade de separação do modelo
                em vários thresholds.
                <br><br>
                O PR AUC foi priorizado porque a classe
                inadimplente é minoritária.
            </div>
        </div>
        """
    )


# ============================================================
# ESTRUTURA DO EXPERIMENTO
# ============================================================

html(
    """
    <div class="kicker">
        Estrutura do experimento
    </div>

    <h2 class="section-title">
        Como os dados foram utilizados?
    </h2>

    <p class="description">
        A base foi dividida para separar o aprendizado,
        a escolha das decisões e a avaliação final.
    </p>
    """
)


(
    coluna_resumo,
    coluna_divisoes,
) = st.columns(
    [
        0.85,
        1.15,
    ]
)


with coluna_resumo:

    modelo_selecionado = metadata[
        "modelo_selecionado"
    ]

    registros_utilizados = formatar_numero(
        metadata["registros_utilizados"]
    )

    duplicados_removidos = formatar_numero(
        metadata["duplicados_removidos"]
    )

    html(
        f"""
        <div class="summary-box">
            <div class="summary-title">
                Visão geral da base
            </div>

            <div class="summary-row">
                <span class="summary-label">
                    Modelo selecionado
                </span>

                <span class="summary-value">
                    {modelo_selecionado}
                </span>
            </div>

            <div class="summary-row">
                <span class="summary-label">
                    Registros utilizados
                </span>

                <span class="summary-value">
                    {registros_utilizados}
                </span>
            </div>

            <div class="summary-row">
                <span class="summary-label">
                    Taxa de inadimplência
                </span>

                <span class="summary-value">
                    {taxa_total_texto}
                </span>
            </div>

            <div class="summary-row">
                <span class="summary-label">
                    Duplicados removidos
                </span>

                <span class="summary-value">
                    {duplicados_removidos}
                </span>
            </div>
        </div>
        """
    )


with coluna_divisoes:

    (
        coluna_divisao_1,
        coluna_divisao_2,
        coluna_divisao_3,
    ) = st.columns(3)


    with coluna_divisao_1:

        renderizar_card(
            titulo="Treinamento",
            valor=formatar_numero(
                metadata["registros_treino"]
            ),
            texto=(
                "Utilizado para o aprendizado inicial "
                "dos algoritmos."
            ),
            cor="#2563eb",
        )


    with coluna_divisao_2:

        renderizar_card(
            titulo="Validação",
            valor=formatar_numero(
                metadata["registros_validacao"]
            ),
            texto=(
                "Utilizada para comparar os algoritmos "
                "e escolher o threshold."
            ),
            cor="#a855f7",
        )


    with coluna_divisao_3:

        renderizar_card(
            titulo="Teste isolado",
            valor=formatar_numero(
                metadata["registros_teste"]
            ),
            texto=(
                "Utilizado somente para a avaliação "
                "final do modelo."
            ),
            cor="#22c55e",
        )


html(
    """
    <div class="info-box">
        A separação evita avaliar o modelo nos mesmos dados
        utilizados durante o treinamento e as decisões
        de desenvolvimento.
    </div>
    """
)


# ============================================================
# COMPARAÇÃO DOS ALGORITMOS
# ============================================================

html(
    """
    <div class="kicker">
        Escolha do algoritmo
    </div>

    <h2 class="section-title">
        Qual modelo apresentou o melhor resultado?
    </h2>

    <p class="description">
        Regressão Logística, Random Forest e
        HistGradientBoosting foram comparados na validação.
    </p>
    """
)


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


comparacao_grafico["metrica"] = (
    comparacao_grafico["metrica"].map(
        {
            "roc_auc": "ROC AUC",
            "pr_auc": "PR AUC",
        }
    )
)


grafico_modelos = (
    alt.Chart(
        comparacao_grafico
    )
    .mark_bar(
        cornerRadiusEnd=5
    )
    .encode(
        y=alt.Y(
            "modelo:N",
            title=None,
        ),

        x=alt.X(
            "valor:Q",
            title="Resultado da métrica",
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
            "metrica:N",
            title=None,
            scale=alt.Scale(
                domain=[
                    "ROC AUC",
                    "PR AUC",
                ],
                range=[
                    "#2563eb",
                    "#a855f7",
                ],
            ),
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
        height=285,
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
    grafico_modelos,
    use_container_width=True,
    theme=None,
)


html(
    """
    <div class="success-box">
        ✅ O Random Forest foi selecionado porque apresentou
        o maior PR AUC na base de validação.
    </div>
    """
)


with st.expander(
    "Ver tabela completa dos modelos"
):

    tabela_comparacao = comparacao.copy()


    for coluna in [
        "acuracia",
        "precisao",
        "recall",
        "f1_score",
    ]:

        tabela_comparacao[coluna] = (
            tabela_comparacao[coluna].map(
                lambda valor: f"{valor:.2%}"
            )
        )


    for coluna in [
        "roc_auc",
        "pr_auc",
    ]:

        tabela_comparacao[coluna] = (
            tabela_comparacao[coluna].map(
                lambda valor: f"{valor:.4f}"
            )
        )


    tabela_comparacao = tabela_comparacao.rename(
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


    st.dataframe(
        tabela_comparacao[
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
# RESULTADOS FINAIS
# ============================================================

html(
    """
    <div class="kicker">
        Avaliação final
    </div>

    <h2 class="section-title">
        Resultados na base de teste isolada
    </h2>
    """
)


(
    coluna_resultado_1,
    coluna_resultado_2,
    coluna_resultado_3,
    coluna_resultado_4,
    coluna_resultado_5,
    coluna_resultado_6,
) = st.columns(6)


coluna_resultado_1.metric(
    "Acurácia",
    acuracia_texto,
)

coluna_resultado_2.metric(
    "Precisão",
    precisao_texto,
)

coluna_resultado_3.metric(
    "Recall",
    recall_texto,
)

coluna_resultado_4.metric(
    "F1-score",
    f1_texto,
)

coluna_resultado_5.metric(
    "ROC AUC",
    roc_auc_texto,
)

coluna_resultado_6.metric(
    "PR AUC",
    pr_auc_texto,
)


html(
    f"""
    <div class="info-box">
        A taxa de inadimplência no teste era
        <strong>{taxa_base_texto}</strong>.
        O modelo atingiu PR AUC de
        <strong>{pr_auc_texto}</strong>, aproximadamente
        <strong>{ganho_pr_auc:.2f} vezes</strong> a taxa-base.
    </div>
    """
)


# ============================================================
# MATRIZ DE CONFUSÃO
# ============================================================

html(
    """
    <div class="kicker">
        Tipos de acertos e erros
    </div>

    <h2 class="section-title">
        O que aconteceu com os clientes do teste?
    </h2>

    <p class="description">
        A matriz de confusão separa os acertos e os erros
        cometidos pelo modelo.
    </p>
    """
)


(
    coluna_confusao_1,
    coluna_confusao_2,
    coluna_confusao_3,
    coluna_confusao_4,
) = st.columns(4)


with coluna_confusao_1:

    renderizar_confusao(
        titulo="Adimplentes identificados corretamente",
        valor=verdadeiros_negativos,
        descricao=(
            "Permaneceram adimplentes e não foram "
            "sinalizados como alto risco."
        ),
        cor="#22c55e",
    )


with coluna_confusao_2:

    renderizar_confusao(
        titulo="Falsos alertas",
        valor=falsos_positivos,
        descricao=(
            "Permaneceram adimplentes, mas foram "
            "classificados como alto risco."
        ),
        cor="#f59e0b",
    )


with coluna_confusao_3:

    renderizar_confusao(
        titulo="Inadimplentes não identificados",
        valor=falsos_negativos,
        descricao=(
            "Ficaram inadimplentes, mas não foram "
            "identificados pelo modelo."
        ),
        cor="#ef4444",
    )


with coluna_confusao_4:

    renderizar_confusao(
        titulo="Inadimplentes identificados corretamente",
        valor=verdadeiros_positivos,
        descricao=(
            "Ficaram inadimplentes e foram corretamente "
            "classificados como alto risco."
        ),
        cor="#38bdf8",
    )


total_inadimplentes_texto = formatar_numero(
    total_inadimplentes
)

verdadeiros_positivos_texto = formatar_numero(
    verdadeiros_positivos
)

falsos_negativos_texto = formatar_numero(
    falsos_negativos
)

total_adimplentes_texto = formatar_numero(
    total_adimplentes
)

falsos_positivos_texto = formatar_numero(
    falsos_positivos
)


html(
    f"""
    <div class="warning-box">
        ⚠️ Dos <strong>{total_inadimplentes_texto}</strong>
        clientes que ficaram inadimplentes,
        <strong>{verdadeiros_positivos_texto}</strong>
        foram identificados e
        <strong>{falsos_negativos_texto}</strong>
        não foram detectados.

        A taxa de não detecção foi de
        <strong>{taxa_nao_deteccao_texto}</strong>.
    </div>
    """
)


html(
    f"""
    <div class="info-box">
        Entre os <strong>{total_adimplentes_texto}</strong>
        clientes que permaneceram adimplentes,
        <strong>{falsos_positivos_texto}</strong>
        foram sinalizados incorretamente.

        Isso representa
        <strong>{taxa_falso_alerta_texto}</strong>
        dos clientes adimplentes.
    </div>
    """
)


with st.expander(
    "Ver matriz de confusão original"
):

    st.dataframe(
        matriz_teste,
        use_container_width=True,
    )


# ============================================================
# THRESHOLD
# ============================================================

html(
    """
    <div class="kicker">
        Política de decisão
    </div>

    <h2 class="section-title">
        Por que o threshold é 36%?
    </h2>

    <p class="description">
        O threshold transforma a probabilidade produzida
        pelo modelo em uma classificação de alto risco.
    </p>
    """
)


metricas_validacao = politica[
    "metricas_validacao"
]


recall_validacao_texto = (
    f"{metricas_validacao['recall']:.2%}"
)

precisao_validacao_texto = (
    f"{metricas_validacao['precisao']:.2%}"
)

f1_validacao_texto = (
    f"{metricas_validacao['f1_score']:.2%}"
)


(
    coluna_threshold_1,
    coluna_threshold_2,
    coluna_threshold_3,
    coluna_threshold_4,
) = st.columns(4)


with coluna_threshold_1:

    renderizar_card(
        titulo="Threshold escolhido",
        valor=threshold_texto,
        texto=(
            "Ponto utilizado para transformar a "
            "probabilidade em classificação."
        ),
        cor="#ef4444",
    )


with coluna_threshold_2:

    renderizar_card(
        titulo="Recall na validação",
        valor=recall_validacao_texto,
        texto=(
            "Percentual de inadimplentes identificados "
            "na escolha do threshold."
        ),
        cor="#38bdf8",
    )


with coluna_threshold_3:

    renderizar_card(
        titulo="Precisão na validação",
        valor=precisao_validacao_texto,
        texto=(
            "Percentual dos alertas que correspondiam "
            "a inadimplentes."
        ),
        cor="#f59e0b",
    )


with coluna_threshold_4:

    renderizar_card(
        titulo="F1-score na validação",
        valor=f1_validacao_texto,
        texto=(
            "Métrica que combina recall e precisão."
        ),
        cor="#a855f7",
    )


html(
    """
    <div class="verdict-box">
        <div class="verdict-title">
            O efeito prático do threshold
        </div>

        Diminuir o threshold aumenta a identificação de
        inadimplentes, mas também aumenta os falsos alertas.

        Aumentar o threshold reduz os falsos alertas, porém
        deixa mais inadimplentes sem identificação.
    </div>
    """
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


thresholds_grafico["metrica"] = (
    thresholds_grafico["metrica"].map(
        {
            "precisao": "Precisão",
            "recall": "Recall",
            "f1_score": "F1-score",
        }
    )
)


grafico_metricas_threshold = (
    alt.Chart(
        thresholds_grafico
    )
    .mark_line(
        strokeWidth=3,
    )
    .encode(
        x=alt.X(
            "limite:Q",
            title="Threshold",
            axis=alt.Axis(
                format=".0%",
            ),
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
            "metrica:N",
            title=None,
            scale=alt.Scale(
                domain=[
                    "Precisão",
                    "Recall",
                    "F1-score",
                ],
                range=[
                    "#f59e0b",
                    "#38bdf8",
                    "#a855f7",
                ],
            ),
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


dataframe_linha = pd.DataFrame(
    {
        "limite": [
            threshold
        ]
    }
)


linha_threshold = (
    alt.Chart(
        dataframe_linha
    )
    .mark_rule(
        color="#ef4444",
        strokeWidth=2,
        strokeDash=[
            7,
            5,
        ],
    )
    .encode(
        x="limite:Q",
    )
)


grafico_threshold = (
    alt.layer(
        grafico_metricas_threshold,
        linha_threshold,
    )
    .properties(
        height=360,
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
    grafico_threshold,
    use_container_width=True,
    theme=None,
)


st.caption(
    f"Critério registrado no treinamento: "
    f"{politica['criterio']}"
)


# ============================================================
# IMPORTÂNCIA DAS VARIÁVEIS
# ============================================================

html(
    """
    <div class="kicker">
        Funcionamento interno
    </div>

    <h2 class="section-title">
        Quais informações o modelo mais utilizou?
    </h2>

    <p class="description">
        A importância global indica quais variáveis foram
        mais utilizadas nas divisões realizadas pelas árvores.
    </p>
    """
)


quantidade_importancias = min(
    12,
    len(
        importancia_variaveis
    ),
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
    .mark_bar(
        cornerRadiusEnd=5,
        color="#2563eb",
    )
    .encode(
        y=alt.Y(
            "nome_amigavel:N",
            title=None,
            sort="-x",
        ),

        x=alt.X(
            "percentual_importancia:Q",
            title="Importância global",
            axis=alt.Axis(
                format=".0%",
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
            370,
            quantidade_importancias * 31,
        ),
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
)


st.altair_chart(
    grafico_importancia,
    use_container_width=True,
    theme=None,
)


html(
    """
    <div class="warning-box">
        ⚠️ A importância apresentada é global. Ela não informa
        se determinado valor aumentou ou reduziu o risco de
        um cliente, não explica individualmente uma previsão
        e não representa causalidade.
    </div>
    """
)


with st.expander(
    "Ver ranking completo das variáveis"
):

    tabela_importancia = (
        importancia_variaveis[
            [
                "posicao",
                "nome_amigavel",
                "percentual_importancia",
            ]
        ]
        .copy()
    )


    tabela_importancia[
        "percentual_importancia"
    ] = tabela_importancia[
        "percentual_importancia"
    ].map(
        lambda valor: f"{valor:.2%}"
    )


    tabela_importancia = tabela_importancia.rename(
        columns={
            "posicao": "Posição",
            "nome_amigavel": "Variável",
            "percentual_importancia": (
                "Importância global"
            ),
        }
    )


    st.dataframe(
        tabela_importancia,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# METODOLOGIA
# ============================================================

html(
    """
    <div class="kicker">
        Processo de Ciência de Dados
    </div>

    <h2 class="section-title">
        Como o resultado foi produzido?
    </h2>
    """
)


with st.expander(
    "Ver metodologia completa"
):

    st.markdown(
        """
        ### 1. Preparação dos dados

        - carregamento da base real da UCI;
        - tradução e organização das variáveis;
        - remoção de registros duplicados;
        - validação da variável-alvo;
        - verificação dos tipos de dados.

        ### 2. Separação dos dados

        - 60% para treinamento;
        - 20% para validação;
        - 20% para teste final;
        - separação estratificada pela variável-alvo.

        ### 3. Comparação dos algoritmos

        Foram comparados:

        - Regressão Logística;
        - Random Forest;
        - HistGradientBoosting.

        O algoritmo foi selecionado pelo PR AUC
        calculado na validação.

        ### 4. Seleção do threshold

        O threshold foi escolhido na validação,
        buscando recall próximo de 70% com a maior
        precisão possível.

        ### 5. Avaliação final

        O modelo foi avaliado na base de teste isolada,
        que não participou das decisões anteriores.
        """
    )


# ============================================================
# CONCLUSÃO
# ============================================================

html(
    f"""
    <div class="verdict-box">
        <div class="verdict-title">
            O que concluímos?
        </div>

        O Random Forest demonstrou capacidade útil de
        priorização de risco, identificando aproximadamente
        <strong>{recall * 100:.0f} de cada 100</strong>
        clientes que ficaram inadimplentes.

        Entretanto, aproximadamente
        <strong>{precisao * 100:.0f} de cada 100</strong>
        alertas estavam corretos.

        Portanto, o modelo deve ser utilizado como apoio
        para monitoramento e análise, e não como decisão
        automática de crédito.
    </div>
    """
)


# ============================================================
# AVISO FINAL
# ============================================================

st.divider()


st.caption(
    "Os resultados foram obtidos com dados históricos "
    "de clientes de cartão de crédito de Taiwan. "
    "O projeto possui finalidade educacional e de portfólio "
    "e não representa uma política real de crédito."
)