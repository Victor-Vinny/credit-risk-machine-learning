import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

RANDOM_STATE = 42

RECALL_MINIMO = 0.70


# ============================================================
# CAMINHOS
# ============================================================

caminho_base = (
    Path("data")
    / "processed"
    / "credit_default_real.csv"
)

pasta_modelos = Path("models")

pasta_relatorios = Path("reports")


caminho_modelo_final = (
    pasta_modelos
    / "credit_risk_real_model.joblib"
)

caminho_comparacao = (
    pasta_relatorios
    / "real_model_comparison.csv"
)

caminho_thresholds = (
    pasta_relatorios
    / "real_threshold_analysis.csv"
)

caminho_politica = (
    pasta_relatorios
    / "real_threshold_policy.json"
)

caminho_metricas_teste = (
    pasta_relatorios
    / "real_test_metrics.json"
)

caminho_matriz_teste = (
    pasta_relatorios
    / "real_test_confusion_matrix.csv"
)

caminho_relatorio_teste = (
    pasta_relatorios
    / "real_test_classification_report.csv"
)

caminho_metadata = (
    pasta_relatorios
    / "real_model_metadata.json"
)


# ============================================================
# VERIFICAÇÃO DA BASE
# ============================================================

if not caminho_base.exists():

    raise FileNotFoundError(
        "A base real processada não foi encontrada. "
        "Execute primeiro: python prepare_real_data.py"
    )


# ============================================================
# CARREGAMENTO E LIMPEZA
# ============================================================

dados = pd.read_csv(
    caminho_base
)


quantidade_original = len(
    dados
)


quantidade_duplicados = int(
    dados.duplicated().sum()
)


dados = (
    dados.drop_duplicates()
    .reset_index(drop=True)
)


quantidade_final = len(
    dados
)


# ============================================================
# VARIÁVEIS
# ============================================================

coluna_alvo = "inadimplente"


colunas_categoricas = [
    "sexo",
    "escolaridade",
    "estado_civil",
]


colunas_numericas = [
    coluna
    for coluna in dados.columns
    if coluna not in (
        colunas_categoricas
        + [coluna_alvo]
    )
]


X = dados.drop(
    columns=[coluna_alvo]
)

y = dados[
    coluna_alvo
]


# ============================================================
# DIVISÃO TREINO, VALIDAÇÃO E TESTE
# ============================================================

# 80% ficam temporariamente para desenvolvimento.
# 20% ficam totalmente isolados para o teste final.

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


# Dos 80% de desenvolvimento:
# 75% serão treino e 25% serão validação.
#
# Resultado total:
# 60% treino
# 20% validação
# 20% teste

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
# PRÉ-PROCESSAMENTO
# ============================================================

def criar_preprocessador():

    pipeline_numerico = Pipeline(
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
        ]
    )


    pipeline_categorico = Pipeline(
        steps=[
            (
                "preenchimento",
                SimpleImputer(
                    strategy="most_frequent",
                ),
            ),
            (
                "one_hot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )


    return ColumnTransformer(
        transformers=[
            (
                "numerico",
                pipeline_numerico,
                colunas_numericas,
            ),
            (
                "categorico",
                pipeline_categorico,
                colunas_categoricas,
            ),
        ],
        remainder="drop",
    )


# ============================================================
# MODELOS CANDIDATOS
# ============================================================

classificadores = {
    "Regressão Logística": LogisticRegression(
        max_iter=3000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=400,
        max_depth=14,
        min_samples_leaf=8,
        class_weight="balanced_subsample",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),

    "HistGradientBoosting": HistGradientBoostingClassifier(
        max_iter=250,
        learning_rate=0.05,
        max_leaf_nodes=31,
        min_samples_leaf=20,
        l2_regularization=0.50,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    ),
}


# ============================================================
# COMPARAÇÃO NA BASE DE VALIDAÇÃO
# ============================================================

resultados_validacao = []

pipelines_candidatos = {}


for nome_modelo, classificador in classificadores.items():

    print()
    print(
        f"Treinando: {nome_modelo}"
    )


    pipeline = Pipeline(
        steps=[
            (
                "preprocessamento",
                criar_preprocessador(),
            ),
            (
                "classificador",
                classificador,
            ),
        ]
    )


    pipeline.fit(
        X_treino,
        y_treino,
    )


    previsoes_validacao = pipeline.predict(
        X_validacao
    )


    probabilidades_validacao = (
        pipeline.predict_proba(
            X_validacao
        )[:, 1]
    )


    matriz = confusion_matrix(
        y_validacao,
        previsoes_validacao,
        labels=[0, 1],
    )


    resultado = {
        "modelo": nome_modelo,

        "acuracia": accuracy_score(
            y_validacao,
            previsoes_validacao,
        ),

        "precisao": precision_score(
            y_validacao,
            previsoes_validacao,
            zero_division=0,
        ),

        "recall": recall_score(
            y_validacao,
            previsoes_validacao,
            zero_division=0,
        ),

        "f1_score": f1_score(
            y_validacao,
            previsoes_validacao,
            zero_division=0,
        ),

        "roc_auc": roc_auc_score(
            y_validacao,
            probabilidades_validacao,
        ),

        "pr_auc": average_precision_score(
            y_validacao,
            probabilidades_validacao,
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


    resultados_validacao.append(
        resultado
    )


    pipelines_candidatos[
        nome_modelo
    ] = pipeline


    print(
        f"PR AUC de validação: "
        f"{resultado['pr_auc']:.4f}"
    )

    print(
        f"ROC AUC de validação: "
        f"{resultado['roc_auc']:.4f}"
    )


# ============================================================
# SELEÇÃO DO MODELO
# ============================================================

tabela_comparacao = pd.DataFrame(
    resultados_validacao
)


tabela_comparacao = (
    tabela_comparacao.sort_values(
        by=[
            "pr_auc",
            "roc_auc",
        ],
        ascending=False,
    )
    .reset_index(drop=True)
)


melhor_modelo_nome = (
    tabela_comparacao.iloc[0][
        "modelo"
    ]
)


pipeline_validacao = (
    pipelines_candidatos[
        melhor_modelo_nome
    ]
)


# ============================================================
# ANÁLISE DO THRESHOLD NA VALIDAÇÃO
# ============================================================

probabilidades_validacao = (
    pipeline_validacao.predict_proba(
        X_validacao
    )[:, 1]
)


limites = np.round(
    np.arange(
        0.10,
        0.91,
        0.01,
    ),
    2,
)


resultados_threshold = []


for limite in limites:

    previsoes = (
        probabilidades_validacao
        >= limite
    ).astype(int)


    matriz = confusion_matrix(
        y_validacao,
        previsoes,
        labels=[0, 1],
    )


    resultados_threshold.append(
        {
            "limite": float(limite),

            "acuracia": accuracy_score(
                y_validacao,
                previsoes,
            ),

            "precisao": precision_score(
                y_validacao,
                previsoes,
                zero_division=0,
            ),

            "recall": recall_score(
                y_validacao,
                previsoes,
                zero_division=0,
            ),

            "f1_score": f1_score(
                y_validacao,
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


tabela_thresholds = pd.DataFrame(
    resultados_threshold
)


candidatos_recall = tabela_thresholds[
    tabela_thresholds["recall"]
    >= RECALL_MINIMO
].copy()


if candidatos_recall.empty:

    linha_threshold = tabela_thresholds.loc[
        tabela_thresholds[
            "f1_score"
        ].idxmax()
    ]

    criterio_threshold = (
        "Maior F1-score, pois nenhum threshold "
        "atingiu o recall mínimo."
    )

else:

    candidatos_recall = (
        candidatos_recall.sort_values(
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


    linha_threshold = (
        candidatos_recall.iloc[0]
    )


    criterio_threshold = (
        f"Maior precisão entre os thresholds "
        f"com recall mínimo de "
        f"{RECALL_MINIMO:.0%}."
    )


threshold_recomendado = float(
    linha_threshold[
        "limite"
    ]
)


# ============================================================
# TREINAMENTO FINAL
# ============================================================

pipeline_final = clone(
    pipeline_validacao
)


pipeline_final.fit(
    X_desenvolvimento,
    y_desenvolvimento,
)


# ============================================================
# AVALIAÇÃO NO TESTE ISOLADO
# ============================================================

probabilidades_teste = (
    pipeline_final.predict_proba(
        X_teste
    )[:, 1]
)


previsoes_teste = (
    probabilidades_teste
    >= threshold_recomendado
).astype(int)


matriz_teste = confusion_matrix(
    y_teste,
    previsoes_teste,
    labels=[0, 1],
)


metricas_teste = {
    "modelo": melhor_modelo_nome,

    "threshold": threshold_recomendado,

    "acuracia": float(
        accuracy_score(
            y_teste,
            previsoes_teste,
        )
    ),

    "precisao": float(
        precision_score(
            y_teste,
            previsoes_teste,
            zero_division=0,
        )
    ),

    "recall": float(
        recall_score(
            y_teste,
            previsoes_teste,
            zero_division=0,
        )
    ),

    "f1_score": float(
        f1_score(
            y_teste,
            previsoes_teste,
            zero_division=0,
        )
    ),

    "roc_auc": float(
        roc_auc_score(
            y_teste,
            probabilidades_teste,
        )
    ),

    "pr_auc": float(
        average_precision_score(
            y_teste,
            probabilidades_teste,
        )
    ),

    "verdadeiros_negativos": int(
        matriz_teste[0][0]
    ),

    "falsos_positivos": int(
        matriz_teste[0][1]
    ),

    "falsos_negativos": int(
        matriz_teste[1][0]
    ),

    "verdadeiros_positivos": int(
        matriz_teste[1][1]
    ),
}


matriz_teste_dataframe = pd.DataFrame(
    matriz_teste,
    index=[
        "Real: Adimplente",
        "Real: Inadimplente",
    ],
    columns=[
        "Previsto: Adimplente",
        "Previsto: Inadimplente",
    ],
)


relatorio_teste = classification_report(
    y_teste,
    previsoes_teste,
    target_names=[
        "Adimplente",
        "Inadimplente",
    ],
    output_dict=True,
    zero_division=0,
)


relatorio_teste_dataframe = (
    pd.DataFrame(
        relatorio_teste
    )
    .transpose()
    .reset_index()
    .rename(
        columns={
            "index": "classe",
        }
    )
)


# ============================================================
# METADADOS
# ============================================================

metadata = {
    "dataset": (
        "Default of Credit Card Clients - UCI"
    ),

    "modelo_selecionado": (
        melhor_modelo_nome
    ),

    "criterio_modelo": (
        "Maior PR AUC na base de validação, "
        "com ROC AUC como desempate."
    ),

    "threshold_recomendado": (
        threshold_recomendado
    ),

    "criterio_threshold": (
        criterio_threshold
    ),

    "recall_minimo_validacao": (
        RECALL_MINIMO
    ),

    "registros_originais": (
        quantidade_original
    ),

    "duplicados_removidos": (
        quantidade_duplicados
    ),

    "registros_utilizados": (
        quantidade_final
    ),

    "registros_treino": int(
        len(X_treino)
    ),

    "registros_validacao": int(
        len(X_validacao)
    ),

    "registros_teste": int(
        len(X_teste)
    ),

    "taxa_inadimplencia_total": float(
        y.mean()
    ),

    "taxa_inadimplencia_treino": float(
        y_treino.mean()
    ),

    "taxa_inadimplencia_validacao": float(
        y_validacao.mean()
    ),

    "taxa_inadimplencia_teste": float(
        y_teste.mean()
    ),

    "variaveis_categoricas": (
        colunas_categoricas
    ),

    "variaveis_numericas": (
        colunas_numericas
    ),
}


politica_threshold = {
    "threshold_recomendado": (
        threshold_recomendado
    ),

    "recall_minimo": (
        RECALL_MINIMO
    ),

    "criterio": (
        criterio_threshold
    ),

    "metricas_validacao": {
        "precisao": float(
            linha_threshold[
                "precisao"
            ]
        ),

        "recall": float(
            linha_threshold[
                "recall"
            ]
        ),

        "f1_score": float(
            linha_threshold[
                "f1_score"
            ]
        ),

        "falsos_positivos": int(
            linha_threshold[
                "falsos_positivos"
            ]
        ),

        "falsos_negativos": int(
            linha_threshold[
                "falsos_negativos"
            ]
        ),
    },
}


# ============================================================
# SALVAMENTO
# ============================================================

pasta_modelos.mkdir(
    exist_ok=True
)

pasta_relatorios.mkdir(
    exist_ok=True
)


joblib.dump(
    pipeline_final,
    caminho_modelo_final,
)


tabela_comparacao.to_csv(
    caminho_comparacao,
    index=False,
)


tabela_thresholds.to_csv(
    caminho_thresholds,
    index=False,
)


matriz_teste_dataframe.to_csv(
    caminho_matriz_teste,
)


relatorio_teste_dataframe.to_csv(
    caminho_relatorio_teste,
    index=False,
)


with open(
    caminho_politica,
    "w",
    encoding="utf-8",
) as arquivo:

    json.dump(
        politica_threshold,
        arquivo,
        ensure_ascii=False,
        indent=4,
    )


with open(
    caminho_metricas_teste,
    "w",
    encoding="utf-8",
) as arquivo:

    json.dump(
        metricas_teste,
        arquivo,
        ensure_ascii=False,
        indent=4,
    )


with open(
    caminho_metadata,
    "w",
    encoding="utf-8",
) as arquivo:

    json.dump(
        metadata,
        arquivo,
        ensure_ascii=False,
        indent=4,
    )


# ============================================================
# RESULTADOS NO TERMINAL
# ============================================================

print()
print("COMPARAÇÃO DOS MODELOS NA VALIDAÇÃO")
print("=" * 145)


print(
    tabela_comparacao.to_string(
        index=False,
        formatters={
            "acuracia": (
                lambda valor: f"{valor:.2%}"
            ),

            "precisao": (
                lambda valor: f"{valor:.2%}"
            ),

            "recall": (
                lambda valor: f"{valor:.2%}"
            ),

            "f1_score": (
                lambda valor: f"{valor:.2%}"
            ),

            "roc_auc": (
                lambda valor: f"{valor:.4f}"
            ),

            "pr_auc": (
                lambda valor: f"{valor:.4f}"
            ),
        },
    )
)


print("=" * 145)


print()
print("SELEÇÃO")

print(
    "Modelo selecionado:",
    melhor_modelo_nome,
)

print(
    "Threshold recomendado:",
    f"{threshold_recomendado:.0%}",
)

print(
    "Critério do threshold:",
    criterio_threshold,
)


print()
print("AVALIAÇÃO FINAL NO TESTE ISOLADO")
print("=" * 60)

print(
    f"Acurácia: "
    f"{metricas_teste['acuracia']:.2%}"
)

print(
    f"Precisão: "
    f"{metricas_teste['precisao']:.2%}"
)

print(
    f"Recall: "
    f"{metricas_teste['recall']:.2%}"
)

print(
    f"F1-score: "
    f"{metricas_teste['f1_score']:.2%}"
)

print(
    f"ROC AUC: "
    f"{metricas_teste['roc_auc']:.4f}"
)

print(
    f"PR AUC: "
    f"{metricas_teste['pr_auc']:.4f}"
)

print()
print("Matriz de confusão:")

print(
    matriz_teste_dataframe
)

print("=" * 60)


print()
print("ARQUIVOS CRIADOS")

print(
    f"Modelo: "
    f"{caminho_modelo_final}"
)

print(
    f"Comparação: "
    f"{caminho_comparacao}"
)

print(
    f"Thresholds: "
    f"{caminho_thresholds}"
)

print(
    f"Política: "
    f"{caminho_politica}"
)

print(
    f"Métricas finais: "
    f"{caminho_metricas_teste}"
)

print(
    f"Matriz final: "
    f"{caminho_matriz_teste}"
)

print(
    f"Metadados: "
    f"{caminho_metadata}"
)