from pathlib import Path

import pandas as pd

from ucimlrepo import fetch_ucirepo


# ============================================================
# CONFIGURAÇÃO DAS PASTAS
# ============================================================

pasta_data = Path("data")

pasta_raw = (
    pasta_data
    / "raw"
)

pasta_processed = (
    pasta_data
    / "processed"
)


pasta_raw.mkdir(
    parents=True,
    exist_ok=True,
)

pasta_processed.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CAMINHOS DOS ARQUIVOS
# ============================================================

caminho_base_bruta = (
    pasta_raw
    / "credit_default_uci_raw.csv"
)

caminho_variaveis = (
    pasta_raw
    / "uci_variables.csv"
)

caminho_base_processada = (
    pasta_processed
    / "credit_default_real.csv"
)


# ============================================================
# DOWNLOAD DO DATASET
# ============================================================

print()
print("Baixando dataset da UCI...")

dataset = fetch_ucirepo(
    id=350
)


# ============================================================
# EXTRAÇÃO DOS DADOS
# ============================================================

X = dataset.data.features.copy()

y = dataset.data.targets.copy()


if X is None or X.empty:

    raise ValueError(
        "As variáveis do dataset não foram carregadas."
    )


if y is None or y.empty:

    raise ValueError(
        "A variável-alvo do dataset não foi carregada."
    )


print(
    "Dataset baixado com sucesso!"
)


# ============================================================
# SALVAMENTO DA DOCUMENTAÇÃO DAS VARIÁVEIS
# ============================================================

variaveis_dataset = dataset.variables.copy()

variaveis_dataset.to_csv(
    caminho_variaveis,
    index=False,
)


# ============================================================
# CRIAÇÃO DA BASE BRUTA
# ============================================================

nome_coluna_alvo_original = (
    y.columns[0]
)

base_bruta = X.copy()

base_bruta[
    nome_coluna_alvo_original
] = y.iloc[:, 0].values


base_bruta.to_csv(
    caminho_base_bruta,
    index=False,
)


# ============================================================
# TRADUÇÃO DOS NOMES DAS VARIÁVEIS
# ============================================================

novos_nomes = [
    "limite_credito",
    "sexo",
    "escolaridade",
    "estado_civil",
    "idade",
    "status_pagamento_set",
    "status_pagamento_ago",
    "status_pagamento_jul",
    "status_pagamento_jun",
    "status_pagamento_mai",
    "status_pagamento_abr",
    "valor_fatura_set",
    "valor_fatura_ago",
    "valor_fatura_jul",
    "valor_fatura_jun",
    "valor_fatura_mai",
    "valor_fatura_abr",
    "valor_pagamento_set",
    "valor_pagamento_ago",
    "valor_pagamento_jul",
    "valor_pagamento_jun",
    "valor_pagamento_mai",
    "valor_pagamento_abr",
]


if len(X.columns) != len(novos_nomes):

    raise ValueError(
        "A quantidade de variáveis recebidas da UCI "
        "é diferente da quantidade esperada.\n"
        f"Quantidade recebida: {len(X.columns)}\n"
        f"Quantidade esperada: {len(novos_nomes)}"
    )


base_processada = X.copy()

base_processada.columns = (
    novos_nomes
)


# ============================================================
# PREPARAÇÃO DA VARIÁVEL-ALVO
# ============================================================

base_processada[
    "inadimplente"
] = (
    y.iloc[:, 0]
    .astype(int)
    .values
)


# ============================================================
# CORREÇÃO DAS CATEGORIAS NÃO DOCUMENTADAS
# ============================================================

# Escolaridade:
# 1 = Pós-graduação
# 2 = Universidade
# 3 = Ensino médio
# 4 = Outros
#
# Os valores 0, 5 e 6 são agrupados como "Outros".

base_processada[
    "escolaridade"
] = (
    base_processada[
        "escolaridade"
    ]
    .replace(
        {
            0: 4,
            5: 4,
            6: 4,
        }
    )
)


# Estado civil:
# 1 = Casado
# 2 = Solteiro
# 3 = Outros
#
# O valor 0 é agrupado como "Outros".

base_processada[
    "estado_civil"
] = (
    base_processada[
        "estado_civil"
    ]
    .replace(
        {
            0: 3,
        }
    )
)


# ============================================================
# VERIFICAÇÃO DOS TIPOS
# ============================================================

colunas_inteiras = [
    "limite_credito",
    "sexo",
    "escolaridade",
    "estado_civil",
    "idade",
    "status_pagamento_set",
    "status_pagamento_ago",
    "status_pagamento_jul",
    "status_pagamento_jun",
    "status_pagamento_mai",
    "status_pagamento_abr",
    "valor_fatura_set",
    "valor_fatura_ago",
    "valor_fatura_jul",
    "valor_fatura_jun",
    "valor_fatura_mai",
    "valor_fatura_abr",
    "valor_pagamento_set",
    "valor_pagamento_ago",
    "valor_pagamento_jul",
    "valor_pagamento_jun",
    "valor_pagamento_mai",
    "valor_pagamento_abr",
    "inadimplente",
]


for coluna in colunas_inteiras:

    base_processada[coluna] = (
        pd.to_numeric(
            base_processada[coluna],
            errors="raise",
        )
        .astype(int)
    )


# ============================================================
# VALIDAÇÕES DA BASE
# ============================================================

quantidade_registros = len(
    base_processada
)

quantidade_variaveis = len(
    base_processada.columns
)

quantidade_ausentes = int(
    base_processada
    .isna()
    .sum()
    .sum()
)

quantidade_duplicados = int(
    base_processada
    .duplicated()
    .sum()
)


valores_alvo = set(
    base_processada[
        "inadimplente"
    ]
    .unique()
)


if not valores_alvo.issubset(
    {0, 1}
):

    raise ValueError(
        "A variável inadimplente contém "
        "valores diferentes de 0 e 1."
    )


# ============================================================
# SALVAMENTO DA BASE PROCESSADA
# ============================================================

base_processada.to_csv(
    caminho_base_processada,
    index=False,
)


# ============================================================
# EXIBIÇÃO DOS RESULTADOS
# ============================================================

distribuicao_alvo = (
    base_processada[
        "inadimplente"
    ]
    .value_counts()
    .sort_index()
)


taxa_inadimplencia = (
    base_processada[
        "inadimplente"
    ]
    .mean()
)


print()
print("PREPARAÇÃO DA BASE REAL CONCLUÍDA")
print("=" * 65)

print(
    f"Quantidade de registros: "
    f"{quantidade_registros:,}"
    .replace(",", ".")
)

print(
    f"Quantidade de colunas: "
    f"{quantidade_variaveis}"
)

print(
    f"Variáveis explicativas: "
    f"{quantidade_variaveis - 1}"
)

print(
    f"Valores ausentes: "
    f"{quantidade_ausentes}"
)

print(
    f"Registros duplicados: "
    f"{quantidade_duplicados}"
)

print(
    f"Taxa de inadimplência: "
    f"{taxa_inadimplencia:.2%}"
)

print()
print("Distribuição da variável-alvo:")

print(
    distribuicao_alvo
)

print()
print("Primeiras linhas:")

print(
    base_processada.head()
)

print()
print("Arquivos criados:")

print(
    f"Base bruta: "
    f"{caminho_base_bruta}"
)

print(
    f"Documentação das variáveis: "
    f"{caminho_variaveis}"
)

print(
    f"Base processada: "
    f"{caminho_base_processada}"
)

print("=" * 65)