"""
main.py
-------
Ponto de entrada do sistema. Contém o menu principal e o fluxo de
navegação entre cadastro, listagem, busca, regras/KPIs e dashboard.

Para executar:
    python3 main.py
"""

import storage
import services
import rules
import dashboard
from models import TIPOS_CONSULTA, STATUS_CONSULTA, STATUS_PAGAMENTO


# ---------------------------------------------------------------------------
# Funções auxiliares de entrada (com validação e tratamento de erro)
# ---------------------------------------------------------------------------

def ler_texto(mensagem: str, obrigatorio: bool = True) -> str:
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print("⚠️  Este campo é obrigatório. Tente novamente.")


def ler_inteiro(mensagem: str) -> int:
    while True:
        try:
            return int(input(mensagem).strip())
        except ValueError:
            print("⚠️  Digite um número inteiro válido.")


def ler_float(mensagem: str) -> float:
    while True:
        try:
            return float(input(mensagem).strip().replace(",", "."))
        except ValueError:
            print("⚠️  Digite um valor numérico válido (ex.: 150.00).")


def ler_opcao_conjunto(mensagem: str, opcoes: set) -> str:
    opcoes_str = "/".join(sorted(opcoes))
    while True:
        valor = input(f"{mensagem} ({opcoes_str}): ").strip()
        # aceita correspondência sem diferenciar maiúsculas/minúsculas
        for opcao in opcoes:
            if valor.lower() == opcao.lower():
                return opcao
        print(f"⚠️  Opção inválida. Escolha entre: {opcoes_str}")


def ler_data_opcional(mensagem: str) -> str:
    """Lê uma data opcional para filtros de período (pode ficar em branco)."""
    valor = input(f"{mensagem} (DD/MM/AAAA ou Enter para ignorar): ").strip()
    return valor if valor else None


def pausar():
    input("\nPressione Enter para continuar...")


def cadastrar_consultas_em_lote():
    """
    Permite cadastrar várias consultas em sequência, sem voltar ao menu a
    cada uma. Demonstra o uso natural de 'break' (encerrar o lote) e
    'continue' (pular um cadastro com erro e seguir para o próximo).
    """
    print("\n--- CADASTRO EM LOTE DE CONSULTAS ---")
    print("Digite os dados de cada consulta. A qualquer momento, digite 'fim' no ID do paciente para encerrar.\n")

    cadastradas = []  # lista de tuplas (id, tipo, valor) só para o resumo final

    while True:
        entrada_paciente = ler_texto("ID do paciente (ou 'fim' para encerrar o lote): ")
        if entrada_paciente.lower() == "fim":
            break  # usuário decidiu parar o cadastro em lote

        try:
            paciente_id = int(entrada_paciente)
        except ValueError:
            print("⚠️  ID inválido, vamos pular esta consulta.")
            continue  # não interrompe o lote, só pula este item

        profissional_id = ler_inteiro("ID do profissional: ")
        data = ler_texto("Data da consulta (DD/MM/AAAA): ")
        tipo = ler_opcao_conjunto("Tipo", TIPOS_CONSULTA)
        status = ler_opcao_conjunto("Status", STATUS_CONSULTA)
        valor = ler_float("Valor (R$): ")

        try:
            c = services.cadastrar_consulta(paciente_id, profissional_id, data, tipo, status, valor)
        except ValueError as e:
            print(f"❌ Não foi possível cadastrar: {e}")
            continue  # erro de validação não derruba o lote inteiro

        cadastradas.append((c.id, c.tipo, c.valor))
        print(f"✅ Consulta {c.id} cadastrada. Próxima (ou 'fim' para encerrar).\n")

    if not cadastradas:
        print("\nNenhuma consulta foi cadastrada neste lote.")
        return

    # list comprehension para somar os valores das consultas cadastradas no lote
    total_lote = sum(valor for (_id, _tipo, valor) in cadastradas)
    print(f"\nResumo do lote: {len(cadastradas)} consulta(s) cadastrada(s), totalizando R$ {total_lote:,.2f}.")
    # outra list comprehension, para listar só os IDs cadastrados
    ids_cadastrados = [str(id_) for (id_, _tipo, _valor) in cadastradas]
    print("IDs: " + ", ".join(ids_cadastrados))


# ---------------------------------------------------------------------------
# MENU: PACIENTES
# ---------------------------------------------------------------------------

def menu_pacientes():
    while True:
        print("\n--- PACIENTES ---")
        print("1. Cadastrar paciente")
        print("2. Listar pacientes")
        print("3. Buscar paciente")
        print("0. Voltar")
        escolha = ler_texto("Escolha uma opção: ")

        try:
            if escolha == "1":
                nome = ler_texto("Nome: ")
                nascimento = ler_texto("Data de nascimento (DD/MM/AAAA): ")
                telefone = ler_texto("Telefone: ")
                convenio = ler_texto("Convênio (Enter para 'Nenhum'): ", obrigatorio=False) or "Nenhum"
                p = services.cadastrar_paciente(nome, nascimento, telefone, convenio)
                print(f"✅ Paciente cadastrado com ID {p.id}.")

            elif escolha == "2":
                pacientes = services.listar_pacientes()
                if not pacientes:
                    print("Nenhum paciente cadastrado.")
                for p in pacientes:
                    print(f"  [{p.id}] {p.nome} | Nasc: {p.data_nascimento} | Tel: {p.telefone} | Convênio: {p.convenio}")

            elif escolha == "3":
                termo = ler_texto("Buscar por nome, ID ou convênio: ")
                resultados = services.buscar_paciente(termo)
                if not resultados:
                    print("Nenhum paciente encontrado.")
                for p in resultados:
                    print(f"  [{p.id}] {p.nome} | Nasc: {p.data_nascimento} | Tel: {p.telefone} | Convênio: {p.convenio}")

            elif escolha == "0":
                break
            else:
                print("⚠️  Opção inválida.")
        except ValueError as e:
            print(f"❌ Erro: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

        pausar()


# ---------------------------------------------------------------------------
# MENU: PROFISSIONAIS
# ---------------------------------------------------------------------------

def menu_profissionais():
    while True:
        print("\n--- PROFISSIONAIS ---")
        print("1. Cadastrar profissional")
        print("2. Listar profissionais")
        print("3. Buscar profissional")
        print("0. Voltar")
        escolha = ler_texto("Escolha uma opção: ")

        try:
            if escolha == "1":
                nome = ler_texto("Nome: ")
                especialidade = ler_texto("Especialidade: ")
                registro = ler_texto("Registro (CRM/COREN): ")
                p = services.cadastrar_profissional(nome, especialidade, registro)
                print(f"✅ Profissional cadastrado com ID {p.id}.")

            elif escolha == "2":
                profissionais = services.listar_profissionais()
                if not profissionais:
                    print("Nenhum profissional cadastrado.")
                for p in profissionais:
                    print(f"  [{p.id}] {p.nome} | {p.especialidade} | Registro: {p.registro}")

            elif escolha == "3":
                termo = ler_texto("Buscar por nome, ID ou especialidade: ")
                resultados = services.buscar_profissional(termo)
                if not resultados:
                    print("Nenhum profissional encontrado.")
                for p in resultados:
                    print(f"  [{p.id}] {p.nome} | {p.especialidade} | Registro: {p.registro}")

            elif escolha == "0":
                break
            else:
                print("⚠️  Opção inválida.")
        except ValueError as e:
            print(f"❌ Erro: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

        pausar()


# ---------------------------------------------------------------------------
# MENU: CONSULTAS
# ---------------------------------------------------------------------------

def menu_consultas():
    while True:
        print("\n--- CONSULTAS ---")
        print("1. Cadastrar consulta")
        print("2. Listar consultas (com filtro por tipo/status)")
        print("3. Buscar consulta")
        print("4. Atualizar status de uma consulta")
        print("5. Cadastrar várias consultas em lote")
        print("0. Voltar")
        escolha = ler_texto("Escolha uma opção: ")

        try:
            if escolha == "1":
                paciente_id = ler_inteiro("ID do paciente: ")
                profissional_id = ler_inteiro("ID do profissional: ")
                data = ler_texto("Data da consulta (DD/MM/AAAA): ")
                tipo = ler_opcao_conjunto("Tipo", TIPOS_CONSULTA)
                status = ler_opcao_conjunto("Status", STATUS_CONSULTA)
                valor = ler_float("Valor (R$): ")
                c = services.cadastrar_consulta(paciente_id, profissional_id, data, tipo, status, valor)
                print(f"✅ Consulta cadastrada com ID {c.id}.")

            elif escolha == "2":
                filtrar = ler_texto("Filtrar por tipo? (Enter para não filtrar): ", obrigatorio=False)
                tipo_filtro = filtrar if filtrar in TIPOS_CONSULTA else None
                filtrar_status = ler_texto("Filtrar por status? (Enter para não filtrar): ", obrigatorio=False)
                status_filtro = filtrar_status if filtrar_status in STATUS_CONSULTA else None
                consultas = services.listar_consultas(tipo=tipo_filtro, status=status_filtro)
                dashboard.exibir_tabela_consultas(consultas)

            elif escolha == "3":
                termo = ler_texto("Buscar por ID, paciente, data, tipo ou status: ")
                resultados = services.buscar_consulta(termo)
                dashboard.exibir_tabela_consultas(resultados)

            elif escolha == "4":
                consulta_id = ler_inteiro("ID da consulta: ")
                novo_status = ler_opcao_conjunto("Novo status", STATUS_CONSULTA)
                ok = services.atualizar_status_consulta(consulta_id, novo_status)
                print("✅ Status atualizado." if ok else "⚠️  Consulta não encontrada.")

            elif escolha == "5":
                cadastrar_consultas_em_lote()

            elif escolha == "0":
                break
            else:
                print("⚠️  Opção inválida.")
        except ValueError as e:
            print(f"❌ Erro: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

        pausar()


# ---------------------------------------------------------------------------
# MENU: PAGAMENTOS
# ---------------------------------------------------------------------------

def menu_pagamentos():
    while True:
        print("\n--- PAGAMENTOS ---")
        print("1. Cadastrar pagamento")
        print("2. Listar pagamentos (com filtro por status)")
        print("3. Buscar pagamento")
        print("0. Voltar")
        escolha = ler_texto("Escolha uma opção: ")

        try:
            if escolha == "1":
                consulta_id = ler_inteiro("ID da consulta: ")
                valor_pago = ler_float("Valor pago (R$): ")
                data_pagamento = ler_texto("Data do pagamento (DD/MM/AAAA): ")
                status = ler_opcao_conjunto("Status", STATUS_PAGAMENTO)
                p = services.cadastrar_pagamento(consulta_id, valor_pago, data_pagamento, status)
                print(f"✅ Pagamento cadastrado com ID {p.id}.")

            elif escolha == "2":
                filtrar_status = ler_texto("Filtrar por status? (Enter para não filtrar): ", obrigatorio=False)
                status_filtro = filtrar_status if filtrar_status in STATUS_PAGAMENTO else None
                pagamentos = services.listar_pagamentos(status=status_filtro)
                if not pagamentos:
                    print("Nenhum pagamento encontrado.")
                for p in pagamentos:
                    print(f"  [{p.id}] Consulta {p.consulta_id} | R$ {p.valor_pago:,.2f} | {p.data_pagamento} | {p.status}")

            elif escolha == "3":
                termo = ler_texto("Buscar por ID, consulta, data ou status: ")
                resultados = services.buscar_pagamento(termo)
                if not resultados:
                    print("Nenhum pagamento encontrado.")
                for p in resultados:
                    print(f"  [{p.id}] Consulta {p.consulta_id} | R$ {p.valor_pago:,.2f} | {p.data_pagamento} | {p.status}")

            elif escolha == "0":
                break
            else:
                print("⚠️  Opção inválida.")
        except ValueError as e:
            print(f"❌ Erro: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

        pausar()


# ---------------------------------------------------------------------------
# MENU: DASHBOARD / RELATÓRIOS
# ---------------------------------------------------------------------------

def menu_dashboard():
    while True:
        print("\n--- DASHBOARD ---")
        print("1. Exibir KPIs (todo o histórico)")
        print("2. Exibir KPIs por período")
        print("3. Gerar relatório completo (gráficos + texto + JSON)")
        print("4. Comparar com período anterior")
        print("0. Voltar")
        escolha = ler_texto("Escolha uma opção: ")

        try:
            if escolha == "1":
                dashboard.exibir_kpis()

            elif escolha == "2":
                inicio = ler_data_opcional("Data inicial")
                fim = ler_data_opcional("Data final")
                dashboard.exibir_kpis(inicio, fim)

            elif escolha == "3":
                inicio = ler_data_opcional("Data inicial")
                fim = ler_data_opcional("Data final")
                caminho = dashboard.gerar_relatorio_completo(inicio, fim)
                print(f"✅ Relatório gerado em: {caminho}")
                print("   Gráficos e KPIs (JSON) salvos na pasta 'exports/'.")

            elif escolha == "4":
                print("Informe o período atual (datas obrigatórias para calcular o período anterior).")
                inicio = ler_texto("Data inicial (DD/MM/AAAA): ")
                fim = ler_texto("Data final (DD/MM/AAAA): ")
                dashboard.exibir_comparativo(inicio, fim)

            elif escolha == "0":
                break
            else:
                print("⚠️  Opção inválida.")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

        pausar()


# ---------------------------------------------------------------------------
# MENU PRINCIPAL
# ---------------------------------------------------------------------------

def exibir_boas_vindas():
    print("=" * 60)
    print("   SISTEMA DE GESTÃO EM SAÚDE - DASHBOARD ADMINISTRATIVO")
    print("=" * 60)


def menu_principal():
    storage.garantir_estrutura()
    exibir_boas_vindas()

    opcoes = {
        "1": ("Pacientes", menu_pacientes),
        "2": ("Profissionais", menu_profissionais),
        "3": ("Consultas", menu_consultas),
        "4": ("Pagamentos", menu_pagamentos),
        "5": ("Dashboard / Relatórios", menu_dashboard),
    }

    while True:
        print("\n===== MENU PRINCIPAL =====")
        for chave, (rotulo, _) in opcoes.items():
            print(f"{chave}. {rotulo}")
        print("0. Sair")

        escolha = ler_texto("Escolha uma opção: ")

        if escolha == "0":
            print("\n👋 Encerrando o sistema. Até logo!")
            break
        elif escolha in opcoes:
            _, funcao = opcoes[escolha]
            funcao()
        else:
            print("⚠️  Opção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário. Até logo!")
    except EOFError:
        print("\n\n👋 Entrada finalizada. Encerrando o sistema.")
