from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# CAMINHOS
# ============================================================

CAMINHO_MODELO = (
    Path("models")
    / "credit_risk_real_model.joblib"
)

PASTA_RELATORIOS = Path("reports")

CAMINHO_IMPORTANCIA_DETALHADA = (
    PASTA_RELATORIOS
    / "real_feature_importance_detailed.csv"
)

CAMINHO_IMPORTANCIA_AGRUPADA = (
    PASTA_RELATORIOS
    / "real_feature_importance_grouped.csv"
)


# ============================================================
# VERIFICAÇÃO DO MODELO
# ============================================================

if not CAMINHO_MODELO.exists():

    raise FileNotFoundError(
        "O modelo real não foi encontrado. "
        "Execute primeiro: python train_real_models.py"
    )


# ============================================================
# CARREGAMENTO
# ============================================================

pipeline = joblib.load(
    CAMINHO_MODELO
)


if "preprocessamento" not in pipeline.named_steps:

    raise KeyError(
        "O pipeline não possui a etapa "
        "'preprocessamento'."
    )


if "classificador" not in pipeline.named_steps:

    raise KeyError(
        "O pipeline não possui a etapa "
        "'classificador'."
    )


preprocessador = pipeline.named_steps[
    "preprocessamento"
]

classificador = pipeline.named_steps[
    "classificador"
]


# ============================================================
# VERIFICAÇÃO DO TIPO DE MODELO
# ============================================================

if not hasattr(
    classificador,
    "feature_importances_",
):

    raise AttributeError(
        "O classificador selecionado não possui "
        "o atributo feature_importances_."
    )


# ============================================================
# RECUPERAÇÃO DOS NOMES DAS VARIÁVEIS
# ============================================================

nomes_variaveis = (
    preprocessador
    .get_feature_names_out()
)

importancias = (
    classificador
    .feature_importances_
)


if len(nomes_variaveis) != len(importancias):

    raise ValueError(
        "A quantidade de nomes das variáveis é diferente "
        "da quantidade de importâncias retornadas pelo modelo."
    )


# ============================================================
# TABELA DETALHADA
# ============================================================

importancia_detalhada = pd.DataFrame(
    {
        "variavel_transformada": nomes_variaveis,
        "importancia": importancias,
    }
)


importancia_detalhada[
    "variavel_transformada"
] = (
    importancia_detalhada[
        "variavel_transformada"
    ]
    .str.replace(
        "numerico__",
        "",
        regex=False,
    )
    .str.replace(
        "categorico__",
        "",
        regex=False,
    )
)


# ============================================================
# IDENTIFICAÇÃO DA VARIÁVEL ORIGINAL
# ============================================================

def identificar_variavel_original(
    nome_variavel,
):
    """
    Identifica a variável original quando o nome contém
    categorias geradas pelo One-Hot Encoding.
    """

    variaveis_categoricas = [
        "sexo",
        "escolaridade",
        "estado_civil",
    ]


    for variavel in variaveis_categoricas:

        if nome_variavel.startswith(
            f"{variavel}_"
        ):

            return variavel


    return nome_variavel


importancia_detalhada[
    "variavel_original"
] = (
    importancia_detalhada[
        "variavel_transformada"
    ]
    .apply(
        identificar_variavel_original
    )
)


# ============================================================
# NOMES AMIGÁVEIS
# ============================================================

nomes_amigaveis = {
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

    "valor_fatura_set": "Valor da fatura — setembro",
    "valor_fatura_ago": "Valor da fatura — agosto",
    "valor_fatura_jul": "Valor da fatura — julho",
    "valor_fatura_jun": "Valor da fatura — junho",
    "valor_fatura_mai": "Valor da fatura — maio",
    "valor_fatura_abr": "Valor da fatura — abril",

    "valor_pagamento_set": "Valor pago — setembro",
    "valor_pagamento_ago": "Valor pago — agosto",
    "valor_pagamento_jul": "Valor pago — julho",
    "valor_pagamento_jun": "Valor pago — junho",
    "valor_pagamento_mai": "Valor pago — maio",
    "valor_pagamento_abr": "Valor pago — abril",
}


importancia_detalhada[
    "nome_amigavel"
] = (
    importancia_detalhada[
        "variavel_original"
    ]
    .map(
        nomes_amigaveis
    )
    .fillna(
        importancia_detalhada[
            "variavel_original"
        ]
    )
)


# Ordena da maior para a menor importância
importancia_detalhada = (
    importancia_detalhada
    .sort_values(
        by="importancia",
        ascending=False,
    )
    .reset_index(drop=True)
)


# ============================================================
# TABELA AGRUPADA
# ============================================================

importancia_agrupada = (
    importancia_detalhada
    .groupby(
        [
            "variavel_original",
            "nome_amigavel",
        ],
        as_index=False,
    )["importancia"]
    .sum()
    .sort_values(
        by="importancia",
        ascending=False,
    )
    .reset_index(drop=True)
)


# Percentual relativo de importância
importancia_agrupada[
    "percentual_importancia"
] = (
    importancia_agrupada[
        "importancia"
    ]
    / importancia_agrupada[
        "importancia"
    ].sum()
)


# Posição no ranking
importancia_agrupada[
    "posicao"
] = (
    importancia_agrupada.index
    + 1
)


importancia_agrupada = importancia_agrupada[
    [
        "posicao",
        "variavel_original",
        "nome_amigavel",
        "importancia",
        "percentual_importancia",
    ]
]


# ============================================================
# SALVAMENTO
# ============================================================

PASTA_RELATORIOS.mkdir(
    exist_ok=True
)


importancia_detalhada.to_csv(
    CAMINHO_IMPORTANCIA_DETALHADA,
    index=False,
)


importancia_agrupada.to_csv(
    CAMINHO_IMPORTANCIA_AGRUPADA,
    index=False,
)


# ============================================================
# EXIBIÇÃO NO TERMINAL
# ============================================================

print()
print("IMPORTÂNCIA DAS VARIÁVEIS — MODELO REAL")
print("=" * 95)


tabela_terminal = (
    importancia_agrupada
    .head(15)
    .copy()
)


tabela_terminal[
    "percentual_importancia"
] = tabela_terminal[
    "percentual_importancia"
].map(
    lambda valor: f"{valor:.2%}"
)


tabela_terminal[
    "importancia"
] = tabela_terminal[
    "importancia"
].map(
    lambda valor: f"{valor:.6f}"
)


print(
    tabela_terminal[
        [
            "posicao",
            "nome_amigavel",
            "importancia",
            "percentual_importancia",
        ]
    ].to_string(
        index=False
    )
)


print("=" * 95)

print()
print(
    "Variável mais importante:",
    importancia_agrupada.iloc[0][
        "nome_amigavel"
    ],
)

print(
    "Importância relativa:",
    (
        f"{importancia_agrupada.iloc[0]['percentual_importancia']:.2%}"
    ),
)

print()
print("Arquivos criados:")

print(
    f"Importância detalhada: "
    f"{CAMINHO_IMPORTANCIA_DETALHADA}"
)

print(
    f"Importância agrupada: "
    f"{CAMINHO_IMPORTANCIA_AGRUPADA}"
)