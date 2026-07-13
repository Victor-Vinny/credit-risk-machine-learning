import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# CONFIGURAÇÕES
# ============================================================

RANDOM_STATE = 42

RECALL_MINIMO = 0.70

VARIAVEIS_DEMOGRAFICAS_REMOVIDAS = [
    "sexo",
    "escolaridade",
    "estado_civil",
]


# ============================================================
# CAMINHOS
# ============================================================

CAMINHO_BASE = (
    Path("data")
    / "processed"
    / "credit_default_real.csv"
)

CAMINHO_MODELO_COMPLETO = (
    Path("models")
    / "credit_risk_real_model.joblib"
)

CAMINHO_POLITICA_COMPLETA = (
    Path("reports")
    / "real_threshold_policy.json"
)

PASTA_MODELOS = Path("models")

PASTA_RELATORIOS = Path("reports")


CAMINHO_MODELO_REDUZIDO = (
    PASTA_MODELOS
    / "credit_risk_reduced_model.joblib"
)

CAMINHO_COMPARACAO = (
    PASTA_RELATORIOS
    / "sensitive_feature_model_comparison.csv"
)

CAMINHO_THRESHOLDS_REDUZIDO = (
    PASTA_RELATORIOS
    / "reduced_model_threshold_analysis.csv"
)

CAMINHO_POLITICA_REDUZIDA = (
    PASTA_RELATORIOS
    / "reduced_model_threshold_policy.json"
)

CAMINHO_EQUIDADE = (
    PASTA_RELATORIOS
    / "sensitive_feature_fairness.csv"
)

CAMINHO_DIFERENCAS_EQUIDADE = (
    PASTA_RELATORIOS
    / "sensitive_feature_fairness_gaps.csv"
)

CAMINHO_RESUMO = (
    PASTA_RELATORIOS
    / "sensitive_feature_comparison_summary.json"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def divisao_segura(
    numerador,
    denominador,
):
    """
    Evita divisão por zero.
    """

    if denominador == 0:
        return 0.0

    return numerador / denominador


def criar_modelo_reduzido():
    """
    Cria o modelo que não utiliza sexo,
    escolaridade e estado civil.
    """

    return Pipeline(
        steps=[
            (
                "preenchimento",
                SimpleImputer(
                    strategy="median",
                ),
            ),
            (
                "padronizacao",
                StandardScaler(),
            ),
            (
                "classificador",
                RandomForestClassifier(
                    n_estimators=400,
                    max_depth=14,
                    min_samples_leaf=8,
                    class_weight="balanced_subsample",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def calcular_metricas(
    nome_modelo,
    usa_variaveis_demograficas,
    y_real,
    probabilidades,
    threshold,
):
    """
    Calcula as métricas gerais de um modelo.
    """

    previsoes = (
        probabilidades
        >= threshold
    ).astype(int)


    matriz = confusion_matrix(
        y_real,
        previsoes,
        labels=[0, 1],
    )


    verdadeiros_negativos = int(
        matriz[0][0]
    )

    falsos_positivos = int(
        matriz[0][1]
    )

    falsos_negativos = int(
        matriz[1][0]
    )

    verdadeiros_positivos = int(
        matriz[1][1]
    )


    return {
        "modelo": nome_modelo,

        "usa_variaveis_demograficas": (
            usa_variaveis_demograficas
        ),

        "threshold": float(
            threshold
        ),

        "acuracia": accuracy_score(
            y_real,
            previsoes,
        ),

        "precisao": precision_score(
            y_real,
            previsoes,
            zero_division=0,
        ),

        "recall": recall_score(
            y_real,
            previsoes,
            zero_division=0,
        ),

        "f1_score": f1_score(
            y_real,
            previsoes,
            zero_division=0,
        ),

        "roc_auc": roc_auc_score(
            y_real,
            probabilidades,
        ),

        "pr_auc": average_precision_score(
            y_real,
            probabilidades,
        ),

        "verdadeiros_negativos": (
            verdadeiros_negativos
        ),

        "falsos_positivos": (
            falsos_positivos
        ),

        "falsos_negativos": (
            falsos_negativos
        ),

        "verdadeiros_positivos": (
            verdadeiros_positivos
        ),
    }


def analisar_thresholds(
    y_real,
    probabilidades,
):
    """
    Testa diferentes thresholds e seleciona
    o de maior precisão entre os que atingem
    recall mínimo de 70%.
    """

    limites = np.round(
        np.arange(
            0.10,
            0.91,
            0.01,
        ),
        2,
    )


    resultados = []


    for limite in limites:

        previsoes = (
            probabilidades
            >= limite
        ).astype(int)


        matriz = confusion_matrix(
            y_real,
            previsoes,
            labels=[0, 1],
        )


        resultados.append(
            {
                "limite": float(
                    limite
                ),

                "acuracia": accuracy_score(
                    y_real,
                    previsoes,
                ),

                "precisao": precision_score(
                    y_real,
                    previsoes,
                    zero_division=0,
                ),

                "recall": recall_score(
                    y_real,
                    previsoes,
                    zero_division=0,
                ),

                "f1_score": f1_score(
                    y_real,
                    previsoes,
                    zero_division=0,
                ),

                "verdadeiros_negativos": int(
                    matriz[0][0]
                ),

                "falsos_positivos": int(
                    matriz[0][1]
                ),

                "falsos_negativos": int(
                    matriz[1][0]
                ),

                "verdadeiros_positivos": int(
                    matriz[1][1]
                ),
            }
        )


    tabela = pd.DataFrame(
        resultados
    )


    candidatos = tabela[
        tabela["recall"]
        >= RECALL_MINIMO
    ].copy()


    if candidatos.empty:

        melhor_linha = tabela.loc[
            tabela[
                "f1_score"
            ].idxmax()
        ]

        criterio = (
            "Maior F1-score, pois nenhum threshold "
            "atingiu o recall mínimo."
        )

    else:

        candidatos = (
            candidatos.sort_values(
                by=[
                    "precisao",
                    "f1_score",
                    "limite",
                ],
                ascending=[
                    False,
                    False,
                    False,
                ],
            )
        )


        melhor_linha = (
            candidatos.iloc[0]
        )


        criterio = (
            f"Maior precisão entre os thresholds "
            f"com recall mínimo de "
            f"{RECALL_MINIMO:.0%}."
        )


    return (
        tabela,
        melhor_linha,
        criterio,
    )


def calcular_metricas_grupo(
    dados_grupo,
):
    """
    Calcula métricas de classificação para
    um grupo específico.
    """

    matriz = confusion_matrix(
        dados_grupo[
            "real"
        ],
        dados_grupo[
            "previsao"
        ],
        labels=[0, 1],
    )


    verdadeiros_negativos = int(
        matriz[0][0]
    )

    falsos_positivos = int(
        matriz[0][1]
    )

    falsos_negativos = int(
        matriz[1][0]
    )

    verdadeiros_positivos = int(
        matriz[1][1]
    )


    total = len(
        dados_grupo
    )


    total_adimplentes = (
        verdadeiros_negativos
        + falsos_positivos
    )


    total_inadimplentes = (
        verdadeiros_positivos
        + falsos_negativos
    )


    total_alto_risco = (
        verdadeiros_positivos
        + falsos_positivos
    )


    return {
        "registros": total,

        "taxa_inadimplencia_real": (
            divisao_segura(
                total_inadimplentes,
                total,
            )
        ),

        "taxa_classificacao_alto_risco": (
            divisao_segura(
                total_alto_risco,
                total,
            )
        ),

        "precisao": divisao_segura(
            verdadeiros_positivos,
            total_alto_risco,
        ),

        "recall": divisao_segura(
            verdadeiros_positivos,
            total_inadimplentes,
        ),

        "taxa_falso_positivo": (
            divisao_segura(
                falsos_positivos,
                total_adimplentes,
            )
        ),

        "taxa_falso_negativo": (
            divisao_segura(
                falsos_negativos,
                total_inadimplentes,
            )
        ),

        "verdadeiros_negativos": (
            verdadeiros_negativos
        ),

        "falsos_positivos": (
            falsos_positivos
        ),

        "falsos_negativos": (
            falsos_negativos
        ),

        "verdadeiros_positivos": (
            verdadeiros_positivos
        ),
    }


def analisar_equidade(
    nome_modelo,
    y_real,
    previsoes,
    grupos,
    atributo,
):
    """
    Calcula as métricas para cada grupo
    de um atributo.
    """

    grupos_serie = pd.Series(
        grupos
    ).astype(
        "object"
    )


    grupos_serie = grupos_serie.where(
        grupos_serie.notna(),
        "Não informado",
    )


    dados_avaliacao = pd.DataFrame(
        {
            "grupo": grupos_serie.astype(
                str
            ).to_numpy(),

            "real": np.asarray(
                y_real
            ),

            "previsao": np.asarray(
                previsoes
            ),
        }
    )


    resultados = []


    for grupo, dados_grupo in (
        dados_avaliacao.groupby(
            "grupo",
            dropna=False,
        )
    ):

        metricas = calcular_metricas_grupo(
            dados_grupo
        )


        metricas[
            "modelo"
        ] = nome_modelo


        metricas[
            "atributo"
        ] = atributo


        metricas[
            "grupo"
        ] = str(
            grupo
        )


        resultados.append(
            metricas
        )


    return pd.DataFrame(
        resultados
    )


def calcular_diferencas_equidade(
    tabela_equidade,
):
    """
    Calcula a amplitude entre o maior e o menor
    resultado observado em cada atributo.
    """

    resultados = []


    for (
        nome_modelo,
        atributo,
    ), grupo in tabela_equidade.groupby(
        [
            "modelo",
            "atributo",
        ]
    ):

        resultados.append(
            {
                "modelo": nome_modelo,

                "atributo": atributo,

                "diferenca_classificacao_alto_risco": float(
                    grupo[
                        "taxa_classificacao_alto_risco"
                    ].max()
                    - grupo[
                        "taxa_classificacao_alto_risco"
                    ].min()
                ),

                "diferenca_recall": float(
                    grupo[
                        "recall"
                    ].max()
                    - grupo[
                        "recall"
                    ].min()
                ),

                "diferenca_falso_positivo": float(
                    grupo[
                        "taxa_falso_positivo"
                    ].max()
                    - grupo[
                        "taxa_falso_positivo"
                    ].min()
                ),

                "diferenca_falso_negativo": float(
                    grupo[
                        "taxa_falso_negativo"
                    ].max()
                    - grupo[
                        "taxa_falso_negativo"
                    ].min()
                ),
            }
        )


    return pd.DataFrame(
        resultados
    )


# ============================================================
# VERIFICAÇÃO DOS ARQUIVOS
# ============================================================

if not CAMINHO_BASE.exists():

    raise FileNotFoundError(
        "A base real não foi encontrada. "
        "Execute: python prepare_real_data.py"
    )


if not CAMINHO_MODELO_COMPLETO.exists():

    raise FileNotFoundError(
        "O modelo completo não foi encontrado. "
        "Execute: python train_real_models.py"
    )


if not CAMINHO_POLITICA_COMPLETA.exists():

    raise FileNotFoundError(
        "A política do modelo completo não foi encontrada. "
        "Execute: python train_real_models.py"
    )


# ============================================================
# CARREGAMENTO
# ============================================================

dados = pd.read_csv(
    CAMINHO_BASE
)


dados = (
    dados.drop_duplicates()
    .reset_index(drop=True)
)


modelo_completo = joblib.load(
    CAMINHO_MODELO_COMPLETO
)


with open(
    CAMINHO_POLITICA_COMPLETA,
    "r",
    encoding="utf-8",
) as arquivo:

    politica_completa = json.load(
        arquivo
    )


threshold_completo = float(
    politica_completa[
        "threshold_recomendado"
    ]
)


# ============================================================
# SEPARAÇÃO DOS DADOS
# ============================================================

X = dados.drop(
    columns=[
        "inadimplente"
    ]
)

y = dados[
    "inadimplente"
]


(
    X_desenvolvimento,
    X_teste,
    y_desenvolvimento,
    y_teste,
) = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)


(
    X_treino,
    X_validacao,
    y_treino,
    y_validacao,
) = train_test_split(
    X_desenvolvimento,
    y_desenvolvimento,
    test_size=0.25,
    random_state=RANDOM_STATE,
    stratify=y_desenvolvimento,
)


# ============================================================
# BASE SEM VARIÁVEIS DEMOGRÁFICAS
# ============================================================

X_treino_reduzido = X_treino.drop(
    columns=VARIAVEIS_DEMOGRAFICAS_REMOVIDAS
)

X_validacao_reduzido = X_validacao.drop(
    columns=VARIAVEIS_DEMOGRAFICAS_REMOVIDAS
)

X_desenvolvimento_reduzido = (
    X_desenvolvimento.drop(
        columns=VARIAVEIS_DEMOGRAFICAS_REMOVIDAS
    )
)

X_teste_reduzido = X_teste.drop(
    columns=VARIAVEIS_DEMOGRAFICAS_REMOVIDAS
)


# ============================================================
# TREINAMENTO INICIAL DO MODELO REDUZIDO
# ============================================================

print()
print(
    "Treinando modelo sem sexo, escolaridade "
    "e estado civil..."
)


modelo_reduzido_validacao = (
    criar_modelo_reduzido()
)


modelo_reduzido_validacao.fit(
    X_treino_reduzido,
    y_treino,
)


probabilidades_validacao_reduzido = (
    modelo_reduzido_validacao.predict_proba(
        X_validacao_reduzido
    )[:, 1]
)


(
    tabela_thresholds_reduzido,
    linha_threshold_reduzido,
    criterio_threshold_reduzido,
) = analisar_thresholds(
    y_real=y_validacao,
    probabilidades=(
        probabilidades_validacao_reduzido
    ),
)


threshold_reduzido = float(
    linha_threshold_reduzido[
        "limite"
    ]
)


# ============================================================
# TREINAMENTO FINAL DO MODELO REDUZIDO
# ============================================================

modelo_reduzido_final = (
    criar_modelo_reduzido()
)


modelo_reduzido_final.fit(
    X_desenvolvimento_reduzido,
    y_desenvolvimento,
)


# ============================================================
# PREVISÕES NO TESTE ISOLADO
# ============================================================

probabilidades_completo = (
    modelo_completo.predict_proba(
        X_teste
    )[:, 1]
)


probabilidades_reduzido = (
    modelo_reduzido_final.predict_proba(
        X_teste_reduzido
    )[:, 1]
)


previsoes_completo = (
    probabilidades_completo
    >= threshold_completo
).astype(int)


previsoes_reduzido = (
    probabilidades_reduzido
    >= threshold_reduzido
).astype(int)


# ============================================================
# COMPARAÇÃO GERAL
# ============================================================

metricas_completo = calcular_metricas(
    nome_modelo=(
        "Modelo completo"
    ),
    usa_variaveis_demograficas=True,
    y_real=y_teste,
    probabilidades=(
        probabilidades_completo
    ),
    threshold=(
        threshold_completo
    ),
)


metricas_reduzido = calcular_metricas(
    nome_modelo=(
        "Modelo sem variáveis demográficas"
    ),
    usa_variaveis_demograficas=False,
    y_real=y_teste,
    probabilidades=(
        probabilidades_reduzido
    ),
    threshold=(
        threshold_reduzido
    ),
)


comparacao_modelos = pd.DataFrame(
    [
        metricas_completo,
        metricas_reduzido,
    ]
)


# ============================================================
# GRUPOS PARA A ANÁLISE DE EQUIDADE
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


grupo_sexo = (
    X_teste[
        "sexo"
    ]
    .map(
        mapa_sexo
    )
    .fillna(
        "Não informado"
    )
)


grupo_escolaridade = (
    X_teste[
        "escolaridade"
    ]
    .map(
        mapa_escolaridade
    )
    .fillna(
        "Não informado"
    )
)


grupo_estado_civil = (
    X_teste[
        "estado_civil"
    ]
    .map(
        mapa_estado_civil
    )
    .fillna(
        "Não informado"
    )
)


grupo_idade = pd.cut(
    X_teste[
        "idade"
    ],
    bins=[
        17,
        25,
        35,
        45,
        55,
        65,
        100,
    ],
    labels=[
        "18 a 25",
        "26 a 35",
        "36 a 45",
        "46 a 55",
        "56 a 65",
        "Acima de 65",
    ],
)


# ============================================================
# EQUIDADE DO MODELO COMPLETO
# ============================================================

resultados_equidade = []


for atributo, grupos in [
    (
        "Sexo",
        grupo_sexo,
    ),
    (
        "Escolaridade",
        grupo_escolaridade,
    ),
    (
        "Estado civil",
        grupo_estado_civil,
    ),
    (
        "Faixa de idade",
        grupo_idade,
    ),
]:

    resultados_equidade.append(
        analisar_equidade(
            nome_modelo=(
                "Modelo completo"
            ),
            y_real=y_teste,
            previsoes=(
                previsoes_completo
            ),
            grupos=grupos,
            atributo=atributo,
        )
    )


# ============================================================
# EQUIDADE DO MODELO REDUZIDO
# ============================================================

for atributo, grupos in [
    (
        "Sexo",
        grupo_sexo,
    ),
    (
        "Escolaridade",
        grupo_escolaridade,
    ),
    (
        "Estado civil",
        grupo_estado_civil,
    ),
    (
        "Faixa de idade",
        grupo_idade,
    ),
]:

    resultados_equidade.append(
        analisar_equidade(
            nome_modelo=(
                "Modelo sem variáveis demográficas"
            ),
            y_real=y_teste,
            previsoes=(
                previsoes_reduzido
            ),
            grupos=grupos,
            atributo=atributo,
        )
    )


tabela_equidade = pd.concat(
    resultados_equidade,
    ignore_index=True,
)


diferencas_equidade = (
    calcular_diferencas_equidade(
        tabela_equidade
    )
)


# ============================================================
# RESUMO
# ============================================================

resumo = {
    "variaveis_removidas": (
        VARIAVEIS_DEMOGRAFICAS_REMOVIDAS
    ),

    "modelo_completo": {
        "threshold": float(
            threshold_completo
        ),

        "roc_auc": float(
            metricas_completo[
                "roc_auc"
            ]
        ),

        "pr_auc": float(
            metricas_completo[
                "pr_auc"
            ]
        ),

        "recall": float(
            metricas_completo[
                "recall"
            ]
        ),

        "precisao": float(
            metricas_completo[
                "precisao"
            ]
        ),
    },

    "modelo_reduzido": {
        "threshold": float(
            threshold_reduzido
        ),

        "criterio_threshold": (
            criterio_threshold_reduzido
        ),

        "roc_auc": float(
            metricas_reduzido[
                "roc_auc"
            ]
        ),

        "pr_auc": float(
            metricas_reduzido[
                "pr_auc"
            ]
        ),

        "recall": float(
            metricas_reduzido[
                "recall"
            ]
        ),

        "precisao": float(
            metricas_reduzido[
                "precisao"
            ]
        ),
    },

    "diferenca_pr_auc": float(
        metricas_reduzido[
            "pr_auc"
        ]
        - metricas_completo[
            "pr_auc"
        ]
    ),

    "diferenca_roc_auc": float(
        metricas_reduzido[
            "roc_auc"
        ]
        - metricas_completo[
            "roc_auc"
        ]
    ),

    "diferenca_recall": float(
        metricas_reduzido[
            "recall"
        ]
        - metricas_completo[
            "recall"
        ]
    ),

    "diferenca_precisao": float(
        metricas_reduzido[
            "precisao"
        ]
        - metricas_completo[
            "precisao"
        ]
    ),
}


# ============================================================
# SALVAMENTO
# ============================================================

PASTA_MODELOS.mkdir(
    exist_ok=True
)

PASTA_RELATORIOS.mkdir(
    exist_ok=True
)


joblib.dump(
    modelo_reduzido_final,
    CAMINHO_MODELO_REDUZIDO,
)


comparacao_modelos.to_csv(
    CAMINHO_COMPARACAO,
    index=False,
)


tabela_thresholds_reduzido.to_csv(
    CAMINHO_THRESHOLDS_REDUZIDO,
    index=False,
)


tabela_equidade.to_csv(
    CAMINHO_EQUIDADE,
    index=False,
)


diferencas_equidade.to_csv(
    CAMINHO_DIFERENCAS_EQUIDADE,
    index=False,
)


politica_reduzida = {
    "threshold_recomendado": (
        threshold_reduzido
    ),

    "recall_minimo": (
        RECALL_MINIMO
    ),

    "criterio": (
        criterio_threshold_reduzido
    ),

    "metricas_validacao": {
        "precisao": float(
            linha_threshold_reduzido[
                "precisao"
            ]
        ),

        "recall": float(
            linha_threshold_reduzido[
                "recall"
            ]
        ),

        "f1_score": float(
            linha_threshold_reduzido[
                "f1_score"
            ]
        ),

        "falsos_positivos": int(
            linha_threshold_reduzido[
                "falsos_positivos"
            ]
        ),

        "falsos_negativos": int(
            linha_threshold_reduzido[
                "falsos_negativos"
            ]
        ),
    },
}


with open(
    CAMINHO_POLITICA_REDUZIDA,
    "w",
    encoding="utf-8",
) as arquivo:

    json.dump(
        politica_reduzida,
        arquivo,
        ensure_ascii=False,
        indent=4,
    )


with open(
    CAMINHO_RESUMO,
    "w",
    encoding="utf-8",
) as arquivo:

    json.dump(
        resumo,
        arquivo,
        ensure_ascii=False,
        indent=4,
    )


# ============================================================
# EXIBIÇÃO NO TERMINAL
# ============================================================

print()
print(
    "COMPARAÇÃO — MODELO COMPLETO X MODELO REDUZIDO"
)

print("=" * 150)


tabela_terminal = (
    comparacao_modelos[
        [
            "modelo",
            "threshold",
            "acuracia",
            "precisao",
            "recall",
            "f1_score",
            "roc_auc",
            "pr_auc",
            "falsos_positivos",
            "falsos_negativos",
        ]
    ]
    .copy()
)


for coluna in [
    "threshold",
    "acuracia",
    "precisao",
    "recall",
    "f1_score",
]:

    tabela_terminal[
        coluna
    ] = tabela_terminal[
        coluna
    ].map(
        lambda valor: f"{valor:.2%}"
    )


for coluna in [
    "roc_auc",
    "pr_auc",
]:

    tabela_terminal[
        coluna
    ] = tabela_terminal[
        coluna
    ].map(
        lambda valor: f"{valor:.4f}"
    )


print(
    tabela_terminal.to_string(
        index=False
    )
)

print("=" * 150)


print()
print(
    "Threshold do modelo reduzido:",
    f"{threshold_reduzido:.0%}",
)

print(
    "Critério:",
    criterio_threshold_reduzido,
)


print()
print(
    "DIFERENÇA DO MODELO REDUZIDO "
    "EM RELAÇÃO AO MODELO COMPLETO"
)

print("=" * 75)

print(
    "PR AUC:",
    f"{resumo['diferenca_pr_auc']:+.4f}",
)

print(
    "ROC AUC:",
    f"{resumo['diferenca_roc_auc']:+.4f}",
)

print(
    "Recall:",
    f"{resumo['diferenca_recall']:+.2%}",
)

print(
    "Precisão:",
    f"{resumo['diferenca_precisao']:+.2%}",
)

print("=" * 75)


print()
print(
    "DIFERENÇAS DE EQUIDADE ENTRE GRUPOS"
)

print("=" * 130)


tabela_diferencas_terminal = (
    diferencas_equidade.copy()
)


for coluna in [
    "diferenca_classificacao_alto_risco",
    "diferenca_recall",
    "diferenca_falso_positivo",
    "diferenca_falso_negativo",
]:

    tabela_diferencas_terminal[
        coluna
    ] = tabela_diferencas_terminal[
        coluna
    ].map(
        lambda valor: f"{valor:.2%}"
    )


print(
    tabela_diferencas_terminal.to_string(
        index=False
    )
)

print("=" * 130)


print()
print("Arquivos criados:")

print(
    CAMINHO_MODELO_REDUZIDO
)

print(
    CAMINHO_COMPARACAO
)

print(
    CAMINHO_THRESHOLDS_REDUZIDO
)

print(
    CAMINHO_POLITICA_REDUZIDA
)

print(
    CAMINHO_EQUIDADE
)

print(
    CAMINHO_DIFERENCAS_EQUIDADE
)

print(
    CAMINHO_RESUMO
)