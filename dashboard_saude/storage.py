"""
storage.py
----------
Responsável por TODA a leitura e gravação em arquivo (CSV e JSON).
Nenhum outro módulo deve abrir arquivos diretamente — isso mantém
a responsabilidade de I/O isolada aqui (princípio de "separar I/O").
"""

import csv
import json
import os

# Pasta onde os dados ficam salvos
PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ARQUIVO_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

ARQUIVOS = {
    "pacientes": os.path.join(PASTA_DADOS, "pacientes.csv"),
    "profissionais": os.path.join(PASTA_DADOS, "profissionais.csv"),
    "consultas": os.path.join(PASTA_DADOS, "consultas.csv"),
    "pagamentos": os.path.join(PASTA_DADOS, "pagamentos.csv"),
}

CAMPOS = {
    "pacientes": ["id", "nome", "data_nascimento", "telefone", "convenio"],
    "profissionais": ["id", "nome", "especialidade", "registro"],
    "consultas": ["id", "paciente_id", "profissional_id", "data", "tipo", "status", "valor"],
    "pagamentos": ["id", "consulta_id", "valor_pago", "data_pagamento", "status"],
}


def garantir_estrutura() -> None:
    """Cria a pasta de dados, os arquivos CSV (com cabeçalho) e o config.json, se não existirem."""
    os.makedirs(PASTA_DADOS, exist_ok=True)
    for chave, caminho in ARQUIVOS.items():
        if not os.path.exists(caminho):
            try:
                with open(caminho, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(CAMPOS[chave])
            except OSError as e:
                print(f"[ERRO] Não foi possível criar o arquivo {caminho}: {e}")

    if not os.path.exists(ARQUIVO_CONFIG):
        config_padrao = {
            "nome_sistema": "Dashboard para Gestão em Saúde",
            "limiares": {
                "taxa_cancelamento_max": 15.0,
                "taxa_glosa_max": 10.0,
                "percentual_pendente_max": 20.0,
                "concentracao_tipo_max": 70.0,
            },
        }
        salvar_config(config_padrao)


def carregar(entidade: str) -> list[dict]:
    """Lê todos os registros (como lista de dicionários) de uma entidade."""
    caminho = ARQUIVOS.get(entidade)
    if caminho is None:
        raise ValueError(f"Entidade desconhecida: '{entidade}'")

    registros = []
    if not os.path.exists(caminho):
        return registros

    try:
        with open(caminho, "r", newline="", encoding="utf-8") as f:
            leitor = csv.DictReader(f)
            for linha in leitor:
                registros.append(linha)
    except OSError as e:
        print(f"[ERRO] Não foi possível ler {caminho}: {e}")
    except csv.Error as e:
        print(f"[ERRO] Arquivo CSV corrompido ({caminho}): {e}")
    return registros


def salvar_tudo(entidade: str, registros: list[dict]) -> bool:
    """Sobrescreve o arquivo CSV de uma entidade com a lista completa de registros."""
    caminho = ARQUIVOS.get(entidade)
    if caminho is None:
        raise ValueError(f"Entidade desconhecida: '{entidade}'")

    campos = CAMPOS[entidade]
    try:
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for registro in registros:
                writer.writerow({c: registro.get(c, "") for c in campos})
        return True
    except OSError as e:
        print(f"[ERRO] Não foi possível salvar em {caminho}: {e}")
        return False


def proximo_id(entidade: str) -> int:
    """Calcula o próximo ID disponível (max atual + 1) para uma entidade."""
    registros = carregar(entidade)
    if not registros:
        return 1
    try:
        return max(int(r["id"]) for r in registros) + 1
    except (KeyError, ValueError):
        return len(registros) + 1


def carregar_config() -> dict:
    """Carrega configurações gerais do sistema a partir de config.json."""
    if not os.path.exists(ARQUIVO_CONFIG):
        return {}
    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[ERRO] Não foi possível ler config.json: {e}")
        return {}


def salvar_config(config: dict) -> bool:
    """Salva configurações gerais do sistema em config.json."""
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"[ERRO] Não foi possível salvar config.json: {e}")
        return False


def exportar_json(nome_arquivo: str, dados) -> bool:
    """Exporta qualquer estrutura de dados (relatório, KPIs, etc.) para JSON na pasta exports/."""
    pasta_exports = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    os.makedirs(pasta_exports, exist_ok=True)
    caminho = os.path.join(pasta_exports, nome_arquivo)
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"[ERRO] Não foi possível exportar para {caminho}: {e}")
        return False


def exportar_csv(nome_arquivo: str, linhas: list[dict], campos: list[str]) -> bool:
    """Exporta uma lista de dicionários para CSV na pasta exports/."""
    pasta_exports = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    os.makedirs(pasta_exports, exist_ok=True)
    caminho = os.path.join(pasta_exports, nome_arquivo)
    try:
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for linha in linhas:
                writer.writerow(linha)
        return True
    except OSError as e:
        print(f"[ERRO] Não foi possível exportar para {caminho}: {e}")
        return False
