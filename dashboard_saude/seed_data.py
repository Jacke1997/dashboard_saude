"""
seed_data.py
------------
Script auxiliar para popular o sistema com dados de EXEMPLO, usado na
fase de Testes do projeto (casos de uso e dados de exemplo).

Executar com:
    python3 seed_data.py
"""

import storage
import services

def popular():
    storage.garantir_estrutura()

    # Zera os dados antes de popular (evita duplicar ao rodar 2x)
    for entidade in storage.ARQUIVOS:
        storage.salvar_tudo(entidade, [])

    print("Cadastrando pacientes...")
    pacientes = [
        services.cadastrar_paciente("Maria Silva", "12/03/1985", "11999990001", "Nenhum"),
        services.cadastrar_paciente("João Pereira", "25/07/1990", "11999990002", "Unimed"),
        services.cadastrar_paciente("Ana Costa", "08/11/1978", "11999990003", "Nenhum"),
        services.cadastrar_paciente("Carlos Souza", "30/01/2000", "11999990004", "Bradesco Saúde"),
        services.cadastrar_paciente("Beatriz Lima", "14/05/1995", "11999990005", "Nenhum"),
    ]

    print("Cadastrando profissionais...")
    profissionais = [
        services.cadastrar_profissional("Dr. Pedro Alves", "Clínico Geral", "CRM-12345"),
        services.cadastrar_profissional("Dra. Fernanda Rocha", "Cardiologia", "CRM-23456"),
        services.cadastrar_profissional("Dra. Juliana Mendes", "Pediatria", "CRM-34567"),
    ]

    print("Cadastrando consultas...")
    consultas_dados = [
        (1, 1, "05/01/2026", "SUS", "Realizada", 0.0),
        (2, 2, "06/01/2026", "Convenio", "Realizada", 180.0),
        (3, 1, "07/01/2026", "Particular", "Realizada", 250.0),
        (4, 3, "10/01/2026", "Convenio", "Cancelada", 200.0),
        (5, 2, "12/01/2026", "SUS", "Realizada", 0.0),
        (1, 1, "15/01/2026", "Particular", "Realizada", 300.0),
        (2, 3, "18/01/2026", "Convenio", "Realizada", 220.0),
        (3, 2, "20/01/2026", "SUS", "Cancelada", 0.0),
        (4, 1, "22/01/2026", "Particular", "Realizada", 280.0),
        (5, 3, "25/01/2026", "Convenio", "Realizada", 190.0),
        (1, 2, "28/01/2026", "SUS", "Agendada", 0.0),
        (2, 1, "30/01/2026", "Convenio", "Realizada", 210.0),
    ]
    consultas = []
    for paciente_id, profissional_id, data, tipo, status, valor in consultas_dados:
        c = services.cadastrar_consulta(paciente_id, profissional_id, data, tipo, status, valor)
        consultas.append(c)

    print("Cadastrando pagamentos...")
    # Cria pagamentos apenas para consultas realizadas e com valor > 0
    pagamentos_dados = [
        (2, 180.0, "10/01/2026", "Pago"),
        (3, 250.0, "12/01/2026", "Pago"),
        (6, 300.0, "20/01/2026", "Pago"),
        (7, 220.0, "22/01/2026", "Glosado"),
        (9, 280.0, "28/01/2026", "Pendente"),
        (10, 190.0, "30/01/2026", "Pago"),
        (12, 210.0, "02/02/2026", "Pendente"),
    ]
    for consulta_id, valor_pago, data_pagamento, status in pagamentos_dados:
        services.cadastrar_pagamento(consulta_id, valor_pago, data_pagamento, status)

    print("\n✅ Dados de exemplo cadastrados com sucesso!")
    print(f"   {len(pacientes)} pacientes, {len(profissionais)} profissionais, "
          f"{len(consultas)} consultas, {len(pagamentos_dados)} pagamentos.")


if __name__ == "__main__":
    popular()
