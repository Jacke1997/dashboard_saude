"""
rules.py
--------
Regras de negócio e cálculos: volumes, receitas, ticket médio, taxas de
cancelamento/glosa e saldo financeiro. Todas as funções aqui são "puras"
(recebem dados e devolvem um resultado, sem ler/gravar arquivo).
"""

from datetime import datetime, timedelta
from collections import defaultdict
import services
import storage

# Limiares padrão usados para identificar gargalos. Podem ser sobrescritos
# pelo arquivo config.json (chave "limiares"), permitindo calibrar as regras
# sem alterar código.
LIMIARES_PADRAO = {
    "taxa_cancelamento_max": 15.0,     # %
    "taxa_glosa_max": 10.0,            # %
    "percentual_pendente_max": 20.0,   # % do faturado
    "concentracao_tipo_max": 70.0,     # % de um único tipo de consulta
}


def _obter_limiares() -> dict:
    config = storage.carregar_config()
    limiares = dict(LIMIARES_PADRAO)
    limiares.update(config.get("limiares", {}))
    return limiares


def _data_no_periodo(data_str: str, inicio: str = None, fim: str = None) -> bool:
    """Verifica se uma data (DD/MM/AAAA) está dentro do período [inicio, fim]."""
    data = datetime.strptime(data_str, "%d/%m/%Y")
    if inicio:
        if data < datetime.strptime(inicio, "%d/%m/%Y"):
            return False
    if fim:
        if data > datetime.strptime(fim, "%d/%m/%Y"):
            return False
    return True


def volume_consultas_por_tipo(inicio: str = None, fim: str = None) -> dict:
    """Quantidade de consultas por tipo (SUS, Particular, Convenio)."""
    contagem = defaultdict(int)
    for c in services.listar_consultas():
        if _data_no_periodo(c.data, inicio, fim):
            contagem[c.tipo] += 1
    return dict(contagem)


def receita_total_por_tipo(inicio: str = None, fim: str = None) -> dict:
    """Soma do valor das consultas REALIZADAS, agrupado por tipo."""
    receita = defaultdict(float)
    for c in services.listar_consultas(status="Realizada"):
        if _data_no_periodo(c.data, inicio, fim):
            receita[c.tipo] += c.valor
    return dict(receita)


def ticket_medio_por_tipo(inicio: str = None, fim: str = None) -> dict:
    """Valor médio por consulta realizada, agrupado por tipo."""
    soma = defaultdict(float)
    qtd = defaultdict(int)
    for c in services.listar_consultas(status="Realizada"):
        if _data_no_periodo(c.data, inicio, fim):
            soma[c.tipo] += c.valor
            qtd[c.tipo] += 1
    return {tipo: round(soma[tipo] / qtd[tipo], 2) for tipo in soma if qtd[tipo] > 0}


def taxa_cancelamento(inicio: str = None, fim: str = None) -> float:
    """Percentual de consultas com status 'Cancelada' sobre o total de consultas."""
    todas = [c for c in services.listar_consultas() if _data_no_periodo(c.data, inicio, fim)]
    if not todas:
        return 0.0
    canceladas = sum(1 for c in todas if c.status == "Cancelada")
    return round(100 * canceladas / len(todas), 2)


def taxa_glosa(inicio: str = None, fim: str = None) -> float:
    """Percentual de pagamentos com status 'Glosado' sobre o total de pagamentos."""
    pagamentos = services.listar_pagamentos()
    if inicio or fim:
        pagamentos = [p for p in pagamentos if _data_no_periodo(p.data_pagamento, inicio, fim)]
    if not pagamentos:
        return 0.0
    glosados = sum(1 for p in pagamentos if p.status == "Glosado")
    return round(100 * glosados / len(pagamentos), 2)


def saldo_financeiro(inicio: str = None, fim: str = None) -> dict:
    """
    Saldo financeiro do período: total faturado (consultas realizadas) vs.
    total efetivamente recebido (pagamentos com status 'Pago').
    """
    faturado = sum(receita_total_por_tipo(inicio, fim).values())

    recebido = 0.0
    pendente = 0.0
    glosado = 0.0
    for p in services.listar_pagamentos():
        if _data_no_periodo(p.data_pagamento, inicio, fim):
            if p.status == "Pago":
                recebido += p.valor_pago
            elif p.status == "Pendente":
                pendente += p.valor_pago
            elif p.status == "Glosado":
                glosado += p.valor_pago

    return {
        "faturado": round(faturado, 2),
        "recebido": round(recebido, 2),
        "pendente": round(pendente, 2),
        "glosado": round(glosado, 2),
        "saldo": round(recebido - glosado, 2),
    }


def identificar_gargalos(inicio: str = None, fim: str = None) -> list[str]:
    """
    Aplica heurísticas simples de negócio para apontar possíveis gargalos
    administrativos/financeiros. Retorna uma lista de alertas em texto.
    """
    gargalos = []
    limiares = _obter_limiares()

    cancelamento = taxa_cancelamento(inicio, fim)
    if cancelamento > limiares["taxa_cancelamento_max"]:
        gargalos.append(
            f"Taxa de cancelamento alta: {cancelamento}% das consultas foram canceladas "
            f"(limite configurado: {limiares['taxa_cancelamento_max']}%; "
            "recomenda-se revisar processo de agendamento/confirmação)."
        )

    glosa = taxa_glosa(inicio, fim)
    if glosa > limiares["taxa_glosa_max"]:
        gargalos.append(
            f"Taxa de glosa elevada: {glosa}% dos pagamentos foram glosados "
            f"(limite configurado: {limiares['taxa_glosa_max']}%; "
            "recomenda-se revisar documentação/autorização junto aos convênios)."
        )

    saldo = saldo_financeiro(inicio, fim)
    if saldo["pendente"] > 0 and saldo["faturado"] > 0:
        percentual_pendente = round(100 * saldo["pendente"] / saldo["faturado"], 2)
        if percentual_pendente > limiares["percentual_pendente_max"]:
            gargalos.append(
                f"Recebíveis pendentes representam {percentual_pendente}% do faturado "
                "(possível atraso no fluxo de caixa)."
            )

    volumes = volume_consultas_por_tipo(inicio, fim)
    if volumes:
        tipo_dominante = max(volumes, key=volumes.get)
        total = sum(volumes.values())
        participacao = round(100 * volumes[tipo_dominante] / total, 2)
        if participacao > limiares["concentracao_tipo_max"]:
            gargalos.append(
                f"Forte concentração de consultas em '{tipo_dominante}' ({participacao}%) "
                "— pode indicar dependência excessiva de um único tipo de receita."
            )

    if not gargalos:
        gargalos.append("Nenhum gargalo crítico identificado no período analisado.")

    return gargalos


def kpis_gerais(inicio: str = None, fim: str = None) -> dict:
    """Consolida todos os KPIs principais em um único dicionário (usado pelo dashboard)."""
    return {
        "volume_por_tipo": volume_consultas_por_tipo(inicio, fim),
        "receita_por_tipo": receita_total_por_tipo(inicio, fim),
        "ticket_medio_por_tipo": ticket_medio_por_tipo(inicio, fim),
        "taxa_cancelamento": taxa_cancelamento(inicio, fim),
        "taxa_glosa": taxa_glosa(inicio, fim),
        "saldo_financeiro": saldo_financeiro(inicio, fim),
        "gargalos": identificar_gargalos(inicio, fim),
    }


def _periodo_anterior(inicio: str, fim: str) -> tuple[str, str]:
    """
    Calcula o período imediatamente anterior, com a MESMA duração em dias do
    período [inicio, fim] informado. Retorna uma tupla (inicio_anterior, fim_anterior).
    """
    data_inicio = datetime.strptime(inicio, "%d/%m/%Y")
    data_fim = datetime.strptime(fim, "%d/%m/%Y")
    duracao = data_fim - data_inicio  # timedelta

    fim_anterior = data_inicio - timedelta(days=1)
    inicio_anterior = fim_anterior - duracao

    return (inicio_anterior.strftime("%d/%m/%Y"), fim_anterior.strftime("%d/%m/%Y"))


def _variacao_percentual(atual: float, anterior: float) -> float | None:
    """Calcula a variação percentual entre dois valores. Retorna None se não for possível calcular."""
    if anterior == 0:
        return None
    return round(100 * (atual - anterior) / anterior, 2)


def comparar_com_periodo_anterior(inicio: str, fim: str) -> dict:
    """
    Compara os KPIs do período [inicio, fim] com o período anterior de mesma
    duração, calculando a variação percentual de cada indicador.

    Atende ao requisito de "histórico de períodos anteriores para comparação".
    """
    inicio_anterior, fim_anterior = _periodo_anterior(inicio, fim)

    atual = kpis_gerais(inicio, fim)
    anterior = kpis_gerais(inicio_anterior, fim_anterior)

    receita_atual = sum(atual["receita_por_tipo"].values())
    receita_anterior = sum(anterior["receita_por_tipo"].values())
    volume_atual = sum(atual["volume_por_tipo"].values())
    volume_anterior = sum(anterior["volume_por_tipo"].values())

    # Lista de tuplas (indicador, valor_atual, valor_anterior) — usada para
    # montar o comparativo de forma compacta com uma list comprehension.
    indicadores = [
        ("receita_total", receita_atual, receita_anterior),
        ("volume_consultas", volume_atual, volume_anterior),
        ("taxa_cancelamento", atual["taxa_cancelamento"], anterior["taxa_cancelamento"]),
        ("taxa_glosa", atual["taxa_glosa"], anterior["taxa_glosa"]),
        ("saldo_financeiro", atual["saldo_financeiro"]["saldo"], anterior["saldo_financeiro"]["saldo"]),
    ]

    comparativo = {
        nome: {
            "atual": valor_atual,
            "anterior": valor_anterior,
            "variacao_percentual": _variacao_percentual(valor_atual, valor_anterior),
        }
        for nome, valor_atual, valor_anterior in indicadores
    }

    return {
        "periodo_atual": (inicio, fim),
        "periodo_anterior": (inicio_anterior, fim_anterior),
        "comparativo": comparativo,
    }
