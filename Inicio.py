import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Credit Risk",
    page_icon="💳",
    layout="wide",
)


# ============================================================
# CAMINHOS
# ============================================================

CAMINHO_MODELO = (
    Path("models")
    / "credit_risk_reduced_model.joblib"
)

CAMINHO_POLITICA = (
    Path("reports")
    / "reduced_model_threshold_policy.json"
)

CAMINHO_RESUMO = (
    Path("reports")
    / "sensitive_feature_comparison_summary.json"
)

CAMINHO_COMPARACAO = (
    Path("reports")
    / "sensitive_feature_model_comparison.csv"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def formatar_numero(valor):
    """
    Formata números inteiros utilizando
    separador brasileiro.
    """

    return f"{valor:,.0f}".replace(
        ",",
        ".",
    )


def formatar_valor_monetario(valor):
    """
    Formata valores na moeda original da base.
    """

    return f"NT$ {formatar_numero(valor)}"


@st.cache_resource
def carregar_modelo():
    """
    Carrega o modelo reduzido treinado.
    """

    if not CAMINHO_MODELO.exists():
        return None

    return joblib.load(
        CAMINHO_MODELO
    )


@st.cache_data
def carregar_json(caminho):
    """
    Carrega arquivos JSON.
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


@st.cache_data
def carregar_comparacao():
    """
    Carrega a comparação dos modelos.
    """

    if not CAMINHO_COMPARACAO.exists():
        return None

    return pd.read_csv(
        CAMINHO_COMPARACAO
    )


def classificar_risco(
    probabilidade,
    threshold,
):
    """
    Transforma a probabilidade prevista
    em uma recomendação operacional.
    """

    margem_analise_manual = 0.10

    limite_aprovacao = max(
        0,
        threshold - margem_analise_manual,
    )

    if probabilidade < limite_aprovacao:

        return {
            "decisao": "APROVAÇÃO SUGERIDA",
            "nivel": "Baixo risco estimado",
            "tipo": "success",
            "mensagem": (
                "O perfil ficou abaixo da faixa "
                "de análise manual."
            ),
            "limite_aprovacao": limite_aprovacao,
        }

    if probabilidade < threshold:

        return {
            "decisao": "ANÁLISE MANUAL",
            "nivel": "Risco intermediário",
            "tipo": "warning",
            "mensagem": (
                "O perfil está próximo do limite "
                "de classificação de alto risco."
            ),
            "limite_aprovacao": limite_aprovacao,
        }

    return {
        "decisao": "ALTO RISCO",
        "nivel": "Risco elevado de inadimplência",
        "tipo": "error",
        "mensagem": (
            "A probabilidade ultrapassou o threshold "
            "recomendado pelo modelo."
        ),
        "limite_aprovacao": limite_aprovacao,
    }


# ============================================================
# CARREGAMENTO DOS ARTEFATOS
# ============================================================

modelo = carregar_modelo()

politica = carregar_json(
    CAMINHO_POLITICA
)

resumo = carregar_json(
    CAMINHO_RESUMO
)

comparacao = carregar_comparacao()


# ============================================================
# VERIFICAÇÃO
# ============================================================

if modelo is None:

    st.error(
        "O modelo reduzido não foi encontrado. "
        "Execute: python compare_sensitive_features.py"
    )

    st.stop()


if politica is None:

    st.error(
        "A política do modelo reduzido não foi encontrada. "
        "Execute: python compare_sensitive_features.py"
    )

    st.stop()


threshold = float(
    politica[
        "threshold_recomendado"
    ]
)


# ============================================================
# MÉTRICAS DO MODELO REDUZIDO
# ============================================================

metricas_modelo = None


if comparacao is not None:

    linha_modelo = comparacao[
        comparacao[
            "modelo"
        ]
        == "Modelo sem variáveis demográficas"
    ]

    if not linha_modelo.empty:

        metricas_modelo = (
            linha_modelo.iloc[0]
        )


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "💳 Credit Risk"
)

st.subheader(
    "Análise de risco de inadimplência"
)

st.write(
    "Aplicação de Machine Learning treinada com dados reais "
    "do dataset Default of Credit Card Clients."
)


st.info(
    "A versão principal não utiliza diretamente sexo, "
    "escolaridade ou estado civil para calcular o risco."
)


# ============================================================
# BARRA LATERAL
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
        "A idade continua sendo utilizada pelo modelo."
    )


# ============================================================
# POLÍTICA DE DECISÃO
# ============================================================

limite_aprovacao = max(
    0,
    threshold - 0.10,
)


with st.expander(
    "Ver política de decisão"
):

    st.markdown(
        f"""
        - **Aprovação sugerida:** probabilidade abaixo de
          {limite_aprovacao:.0%}.

        - **Análise manual:** probabilidade entre
          {limite_aprovacao:.0%} e menos de {threshold:.0%}.

        - **Alto risco:** probabilidade igual ou superior a
          {threshold:.0%}.
        """
    )

    st.write(
        "**Critério do threshold:**",
        politica.get(
            "criterio",
            "Não informado",
        ),
    )

    st.caption(
        "A faixa de análise manual é uma regra operacional "
        "adicional e não uma classe produzida originalmente "
        "pelo modelo."
    )


# ============================================================
# STATUS DE PAGAMENTO
# ============================================================

opcoes_status_pagamento = {
    -2: "Código -2 — sem atraso positivo",
    -1: "Código -1 — pagamento em dia",
    0: "Código 0 — sem atraso positivo",
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


meses = [
    ("set", "Setembro"),
    ("ago", "Agosto"),
    ("jul", "Julho"),
    ("jun", "Junho"),
    ("mai", "Maio"),
    ("abr", "Abril"),
]


# ============================================================
# FORMULÁRIO
# ============================================================

with st.form(
    "formulario_credito_reduzido"
):

    st.markdown(
        "## Dados do cliente"
    )

    coluna_cliente_1, coluna_cliente_2 = (
        st.columns(2)
    )


    with coluna_cliente_1:

        limite_credito = st.number_input(
            "Limite de crédito",
            min_value=1_000,
            max_value=2_000_000,
            value=100_000,
            step=10_000,
            help=(
                "Valor na unidade monetária original "
                "do dataset."
            ),
        )


    with coluna_cliente_2:

        idade = st.number_input(
            "Idade",
            min_value=18,
            max_value=100,
            value=35,
            step=1,
        )


    st.divider()

    st.markdown(
        "## Histórico de pagamento"
    )

    st.caption(
        "Valores positivos representam meses de atraso. "
        "Valores iguais ou inferiores a zero representam "
        "códigos sem atraso positivo."
    )


    colunas_status = st.columns(
        6
    )

    status_pagamento = {}


    for indice, (
        codigo_mes,
        nome_mes,
    ) in enumerate(meses):

        with colunas_status[indice]:

            status_pagamento[
                codigo_mes
            ] = st.selectbox(
                nome_mes,
                options=list(
                    opcoes_status_pagamento.keys()
                ),
                index=2,
                format_func=lambda valor: (
                    opcoes_status_pagamento[
                        valor
                    ]
                ),
                key=f"status_{codigo_mes}",
            )


    st.divider()

    st.markdown(
        "## Valores das faturas"
    )

    st.caption(
        "Informe os valores na unidade monetária "
        "original do dataset."
    )


    colunas_faturas = st.columns(
        6
    )

    valores_faturas = {}


    valores_padrao_faturas = {
        "set": 50_000,
        "ago": 48_000,
        "jul": 45_000,
        "jun": 42_000,
        "mai": 40_000,
        "abr": 38_000,
    }


    for indice, (
        codigo_mes,
        nome_mes,
    ) in enumerate(meses):

        with colunas_faturas[indice]:

            valores_faturas[
                codigo_mes
            ] = st.number_input(
                nome_mes,
                min_value=-2_000_000,
                max_value=10_000_000,
                value=(
                    valores_padrao_faturas[
                        codigo_mes
                    ]
                ),
                step=1_000,
                key=f"fatura_{codigo_mes}",
            )


    st.divider()

    st.markdown(
        "## Valores pagos"
    )


    colunas_pagamentos = st.columns(
        6
    )

    valores_pagamentos = {}


    for indice, (
        codigo_mes,
        nome_mes,
    ) in enumerate(meses):

        with colunas_pagamentos[indice]:

            valores_pagamentos[
                codigo_mes
            ] = st.number_input(
                nome_mes,
                min_value=0,
                max_value=10_000_000,
                value=5_000,
                step=1_000,
                key=f"pagamento_{codigo_mes}",
            )


    botao_analisar = st.form_submit_button(
        "Executar análise de risco",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# RESULTADO
# ============================================================

if botao_analisar:

    st.divider()

    st.markdown(
        "## Resultado da análise"
    )


    # O modelo reduzido recebe apenas 20 variáveis.
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


    dados_dataframe = pd.DataFrame(
        [
            dados_cliente
        ]
    )


    probabilidade_inadimplencia = float(
        modelo.predict_proba(
            dados_dataframe
        )[0][1]
    )


    score_interno = round(
        (
            1
            - probabilidade_inadimplencia
        )
        * 1000
    )


    resultado = classificar_risco(
        probabilidade=(
            probabilidade_inadimplencia
        ),
        threshold=threshold,
    )


    # ========================================================
    # INDICADORES COMPLEMENTARES
    # ========================================================

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


    meses_com_atraso = sum(
        status > 0
        for status in status_pagamento.values()
    )


    maior_atraso = max(
        status_pagamento.values()
    )


    utilizacao_limite = (
        max(
            valores_faturas["set"],
            0,
        )
        / limite_credito
    )


    if total_faturas > 0:

        cobertura_pagamentos = (
            total_pagamentos
            / total_faturas
        )

    else:

        cobertura_pagamentos = 0


    # ========================================================
    # MÉTRICAS PRINCIPAIS
    # ========================================================

    (
        coluna_resultado_1,
        coluna_resultado_2,
        coluna_resultado_3,
        coluna_resultado_4,
    ) = st.columns(4)


    with coluna_resultado_1:

        st.metric(
            "Probabilidade de inadimplência",
            f"{probabilidade_inadimplencia:.1%}",
        )


    with coluna_resultado_2:

        st.metric(
            "Score interno ilustrativo",
            f"{score_interno}/1000",
        )


    with coluna_resultado_3:

        st.metric(
            "Threshold",
            f"{threshold:.0%}",
        )


    with coluna_resultado_4:

        st.metric(
            "Decisão recomendada",
            resultado[
                "decisao"
            ],
        )


    # ========================================================
    # MENSAGEM
    # ========================================================

    if resultado["tipo"] == "success":

        st.success(
            resultado["mensagem"]
        )

    elif resultado["tipo"] == "warning":

        st.warning(
            resultado["mensagem"]
        )

    else:

        st.error(
            resultado["mensagem"]
        )


    # ========================================================
    # INDICADORES DO PERFIL
    # ========================================================

    st.markdown(
        "### Indicadores complementares"
    )


    (
        coluna_indicador_1,
        coluna_indicador_2,
        coluna_indicador_3,
        coluna_indicador_4,
    ) = st.columns(4)


    with coluna_indicador_1:

        st.metric(
            "Meses com atraso",
            meses_com_atraso,
        )


    with coluna_indicador_2:

        st.metric(
            "Maior atraso",
            (
                f"{maior_atraso} meses"
                if maior_atraso > 0
                else "Sem atraso positivo"
            ),
        )


    with coluna_indicador_3:

        st.metric(
            "Uso do limite em setembro",
            f"{utilizacao_limite:.1%}",
        )


    with coluna_indicador_4:

        st.metric(
            "Pagamentos sobre faturas",
            f"{cobertura_pagamentos:.1%}",
        )


    # ========================================================
    # ALERTAS COMPLEMENTARES
    # ========================================================

    alertas = []


    if meses_com_atraso >= 1:

        alertas.append(
            f"Foram identificados {meses_com_atraso} "
            "meses com atraso positivo."
        )


    if maior_atraso >= 2:

        alertas.append(
            "Existe registro de atraso igual ou superior "
            "a dois meses."
        )


    if utilizacao_limite >= 0.80:

        alertas.append(
            "A fatura mais recente representa 80% ou mais "
            "do limite de crédito."
        )


    if (
        total_faturas > 0
        and cobertura_pagamentos < 0.10
    ):

        alertas.append(
            "Os pagamentos representam menos de 10% "
            "do total das faturas informadas."
        )


    if alertas:

        for alerta in alertas:

            st.warning(
                alerta
            )

    else:

        st.success(
            "Nenhum alerta complementar crítico "
            "foi identificado."
        )


    # ========================================================
    # DETALHAMENTO TÉCNICO
    # ========================================================

    with st.expander(
        "Ver detalhes técnicos"
    ):

        st.write(
            "**Modelo:** Random Forest reduzido"
        )

        st.write(
            "**Variáveis utilizadas:**",
            len(
                dados_dataframe.columns
            ),
        )

        st.write(
            "**Probabilidade prevista:**",
            f"{probabilidade_inadimplencia:.4f}",
        )

        st.write(
            "**Limite para aprovação sugerida:**",
            f"{resultado['limite_aprovacao']:.0%}",
        )

        st.write(
            "**Threshold de alto risco:**",
            f"{threshold:.0%}",
        )

        st.write(
            "**Total das faturas:**",
            formatar_valor_monetario(
                total_faturas
            ),
        )

        st.write(
            "**Total dos pagamentos:**",
            formatar_valor_monetario(
                total_pagamentos
            ),
        )

        st.markdown(
            "#### Dados enviados ao modelo"
        )

        st.dataframe(
            dados_dataframe,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# AVISO FINAL
# ============================================================

st.divider()


st.caption(
    "Projeto educacional desenvolvido com dados históricos "
    "de clientes de cartão de crédito de Taiwan. "
    "O modelo não utiliza diretamente sexo, escolaridade "
    "ou estado civil. A idade e outras variáveis ainda podem "
    "conter efeitos indiretos relacionados a grupos. "
    "A previsão não deve ser utilizada isoladamente para "
    "decisões reais de crédito."
)