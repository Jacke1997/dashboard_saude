"""
dashboard.py
------------
Camada de visualização: imprime tabelas/KPIs no terminal, gera gráficos
(PNG, com matplotlib) e monta o relatório final de análise de gargalos.
"""

import os
import matplotlib
matplotlib.use("Agg")  # backend sem interface gráfica (necessário em servidor/terminal)
import matplotlib.pyplot as plt

import rules
import storage

PASTA_EXPORTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")


def _linha(char="-", tamanho=60):
    print(char * tamanho)


def exibir_kpis(inicio: str = None, fim: str = None) -> dict:
    """Imprime um resumo textual dos KPIs principais no terminal e retorna os dados."""
    kpis = rules.kpis_gerais(inicio, fim)

    _linha("=")
    titulo = "DASHBOARD - GESTÃO EM SAÚDE"
    if inicio or fim:
        titulo += f"  (período: {inicio or 'início'} a {fim or 'hoje'})"
    print(titulo)
    _linha("=")

    print("\n📊 Volume de consultas por tipo:")
    if kpis["volume_por_tipo"]:
        for tipo, qtd in kpis["volume_por_tipo"].items():
            print(f"   {tipo:<12}: {qtd} consulta(s)")
    else:
        print("   Nenhuma consulta registrada.")

    print("\n💰 Receita total por tipo (consultas realizadas):")
    if kpis["receita_por_tipo"]:
        for tipo, valor in kpis["receita_por_tipo"].items():
            print(f"   {tipo:<12}: R$ {valor:,.2f}")
    else:
        print("   Nenhuma receita registrada.")

    print("\n🎫 Ticket médio por tipo:")
    if kpis["ticket_medio_por_tipo"]:
        for tipo, valor in kpis["ticket_medio_por_tipo"].items():
            print(f"   {tipo:<12}: R$ {valor:,.2f}")
    else:
        print("   Sem dados suficientes.")

    print(f"\n⚠️  Taxa de cancelamento: {kpis['taxa_cancelamento']}%")
    print(f"⚠️  Taxa de glosa: {kpis['taxa_glosa']}%")

    saldo = kpis["saldo_financeiro"]
    print("\n🧾 Saldo financeiro:")
    print(f"   Faturado : R$ {saldo['faturado']:,.2f}")
    print(f"   Recebido : R$ {saldo['recebido']:,.2f}")
    print(f"   Pendente : R$ {saldo['pendente']:,.2f}")
    print(f"   Glosado  : R$ {saldo['glosado']:,.2f}")
    print(f"   Saldo    : R$ {saldo['saldo']:,.2f}")

    print("\n🚧 Gargalos identificados:")
    for g in kpis["gargalos"]:
        print(f"   - {g}")

    _linha("=")
    return kpis


def exibir_tabela_consultas(consultas: list) -> None:
    """Imprime uma tabela simples (formatada) de consultas — usada na listagem filtrável."""
    if not consultas:
        print("Nenhuma consulta encontrada para esse filtro.")
        return

    cabecalho = f"{'ID':<5}{'Paciente':<12}{'Profissional':<14}{'Data':<12}{'Tipo':<12}{'Status':<12}{'Valor':>10}"
    print(cabecalho)
    print("-" * len(cabecalho))
    for c in consultas:
        print(f"{c.id:<5}{c.paciente_id:<12}{c.profissional_id:<14}{c.data:<12}{c.tipo:<12}{c.status:<12}R$ {c.valor:>7,.2f}")


def gerar_graficos(inicio: str = None, fim: str = None) -> list:
    """Gera gráficos PNG (volume por tipo, receita por tipo) e salva em exports/."""
    os.makedirs(PASTA_EXPORTS, exist_ok=True)
    arquivos_gerados = []

    volumes = rules.volume_consultas_por_tipo(inicio, fim)
    receitas = rules.receita_total_por_tipo(inicio, fim)

    # Gráfico 1: volume de consultas por tipo (barras)
    if volumes:
        plt.figure(figsize=(6, 4))
        plt.bar(volumes.keys(), volumes.values(), color="#4C72B0")
        plt.title("Volume de Consultas por Tipo")
        plt.ylabel("Quantidade")
        plt.tight_layout()
        caminho = os.path.join(PASTA_EXPORTS, "grafico_volume_consultas.png")
        plt.savefig(caminho)
        plt.close()
        arquivos_gerados.append(caminho)

    # Gráfico 2: receita por tipo (pizza)
    if receitas:
        plt.figure(figsize=(6, 4))
        plt.pie(receitas.values(), labels=receitas.keys(), autopct="%1.1f%%",
                colors=["#55A868", "#C44E52", "#8172B2"])
        plt.title("Participação na Receita por Tipo")
        plt.tight_layout()
        caminho = os.path.join(PASTA_EXPORTS, "grafico_receita_por_tipo.png")
        plt.savefig(caminho)
        plt.close()
        arquivos_gerados.append(caminho)

    # Gráfico 3: comparativo financeiro (faturado x recebido x pendente x glosado)
    saldo = rules.saldo_financeiro(inicio, fim)
    categorias = ["Faturado", "Recebido", "Pendente", "Glosado"]
    valores = [saldo["faturado"], saldo["recebido"], saldo["pendente"], saldo["glosado"]]
    if any(valores):
        plt.figure(figsize=(6, 4))
        plt.bar(categorias, valores, color=["#4C72B0", "#55A868", "#DD8452", "#C44E52"])
        plt.title("Comparativo Financeiro")
        plt.ylabel("R$")
        plt.tight_layout()
        caminho = os.path.join(PASTA_EXPORTS, "grafico_comparativo_financeiro.png")
        plt.savefig(caminho)
        plt.close()
        arquivos_gerados.append(caminho)

    return arquivos_gerados


def exibir_comparativo(inicio: str, fim: str) -> dict:
    """Imprime a comparação dos KPIs do período informado contra o período anterior equivalente."""
    resultado = rules.comparar_com_periodo_anterior(inicio, fim)
    p_atual = resultado["periodo_atual"]
    p_anterior = resultado["periodo_anterior"]

    NOMES_LEGIVEIS = {
        "receita_total": ("Receita total", "R$"),
        "volume_consultas": ("Volume de consultas", ""),
        "taxa_cancelamento": ("Taxa de cancelamento", "%"),
        "taxa_glosa": ("Taxa de glosa", "%"),
        "saldo_financeiro": ("Saldo financeiro", "R$"),
    }

    _linha("=")
    print(f"COMPARATIVO DE PERÍODOS")
    print(f"  Atual    : {p_atual[0]} a {p_atual[1]}")
    print(f"  Anterior : {p_anterior[0]} a {p_anterior[1]}")
    _linha("=")

    for chave, (rotulo, unidade) in NOMES_LEGIVEIS.items():
        dados = resultado["comparativo"][chave]
        atual, anterior, variacao = dados["atual"], dados["anterior"], dados["variacao_percentual"]

        if unidade == "R$":
            valor_atual_fmt = f"R$ {atual:,.2f}"
            valor_anterior_fmt = f"R$ {anterior:,.2f}"
        elif unidade == "%":
            valor_atual_fmt = f"{atual}%"
            valor_anterior_fmt = f"{anterior}%"
        else:
            valor_atual_fmt = str(atual)
            valor_anterior_fmt = str(anterior)

        if variacao is None:
            seta = "—"
        elif variacao > 0:
            seta = f"▲ +{variacao}%"
        elif variacao < 0:
            seta = f"▼ {variacao}%"
        else:
            seta = "= 0%"

        print(f"\n{rotulo}:")
        print(f"   Atual    : {valor_atual_fmt}")
        print(f"   Anterior : {valor_anterior_fmt}")
        print(f"   Variação : {seta}")

    _linha("=")
    return resultado

def gerar_relatorio_completo(inicio: str = None, fim: str = None) -> str:
    """
    Gera o relatório de análise de gargalos em formato texto (.txt),
    além dos gráficos e de uma exportação dos KPIs em JSON.
    Retorna o caminho do relatório de texto gerado.
    """
    kpis = rules.kpis_gerais(inicio, fim)
    graficos = gerar_graficos(inicio, fim)
    storage.exportar_json("kpis.json", kpis)

    os.makedirs(PASTA_EXPORTS, exist_ok=True)
    caminho_relatorio = os.path.join(PASTA_EXPORTS, "relatorio_gargalos.txt")

    linhas = []
    linhas.append("RELATÓRIO DE ANÁLISE - GESTÃO EM SAÚDE")
    if inicio or fim:
        linhas.append(f"Período: {inicio or 'início'} a {fim or 'hoje'}")
    linhas.append("=" * 60)
    linhas.append("")
    linhas.append("VOLUME DE CONSULTAS POR TIPO:")
    for tipo, qtd in kpis["volume_por_tipo"].items():
        linhas.append(f"  - {tipo}: {qtd}")
    linhas.append("")
    linhas.append("RECEITA POR TIPO:")
    for tipo, valor in kpis["receita_por_tipo"].items():
        linhas.append(f"  - {tipo}: R$ {valor:,.2f}")
    linhas.append("")
    linhas.append(f"TAXA DE CANCELAMENTO: {kpis['taxa_cancelamento']}%")
    linhas.append(f"TAXA DE GLOSA: {kpis['taxa_glosa']}%")
    linhas.append("")
    saldo = kpis["saldo_financeiro"]
    linhas.append("SALDO FINANCEIRO:")
    linhas.append(f"  Faturado : R$ {saldo['faturado']:,.2f}")
    linhas.append(f"  Recebido : R$ {saldo['recebido']:,.2f}")
    linhas.append(f"  Pendente : R$ {saldo['pendente']:,.2f}")
    linhas.append(f"  Glosado  : R$ {saldo['glosado']:,.2f}")
    linhas.append(f"  Saldo    : R$ {saldo['saldo']:,.2f}")
    linhas.append("")
    linhas.append("GARGALOS IDENTIFICADOS:")
    for g in kpis["gargalos"]:
        linhas.append(f"  - {g}")
    linhas.append("")
    linhas.append("GRÁFICOS GERADOS:")
    for g in graficos:
        linhas.append(f"  - {os.path.basename(g)}")

    try:
        with open(caminho_relatorio, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas))
    except OSError as e:
        print(f"[ERRO] Não foi possível gerar o relatório: {e}")

    return caminho_relatorio
