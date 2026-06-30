"""
services.py
-----------
Lógica de CADASTRO, LISTAGEM e BUSCA para todas as entidades do sistema.
Este módulo conversa com storage.py (I/O) e models.py (validação/estrutura),
mas não faz leitura/gravação de arquivo diretamente.
"""

from typing import Optional
import storage
from models import Paciente, Profissional, Consulta, Pagamento


# ---------------------------------------------------------------------------
# PACIENTES
# ---------------------------------------------------------------------------

def cadastrar_paciente(nome: str, data_nascimento: str, telefone: str, convenio: str = "Nenhum") -> Paciente:
    novo_id = storage.proximo_id("pacientes")
    paciente = Paciente(novo_id, nome, data_nascimento, telefone, convenio)  # valida no __post_init__
    registros = storage.carregar("pacientes")
    registros.append(paciente.to_dict())
    storage.salvar_tudo("pacientes", registros)
    return paciente


def listar_pacientes() -> list[Paciente]:
    return [Paciente.from_dict(r) for r in storage.carregar("pacientes")]


def buscar_paciente(termo: str) -> list[Paciente]:
    """Busca por ID exato OU por nome/convênio (parcial, sem diferenciar maiúsculas)."""
    termo_lower = termo.strip().lower()
    encontrados = []
    for p in listar_pacientes():
        if termo_lower == str(p.id) or termo_lower in p.nome.lower() or termo_lower in p.convenio.lower():
            encontrados.append(p)
    return encontrados


# ---------------------------------------------------------------------------
# PROFISSIONAIS
# ---------------------------------------------------------------------------

def cadastrar_profissional(nome: str, especialidade: str, registro: str) -> Profissional:
    novo_id = storage.proximo_id("profissionais")
    profissional = Profissional(novo_id, nome, especialidade, registro)
    registros = storage.carregar("profissionais")
    registros.append(profissional.to_dict())
    storage.salvar_tudo("profissionais", registros)
    return profissional


def listar_profissionais() -> list[Profissional]:
    return [Profissional.from_dict(r) for r in storage.carregar("profissionais")]


def buscar_profissional(termo: str) -> list[Profissional]:
    termo_lower = termo.strip().lower()
    encontrados = []
    for p in listar_profissionais():
        if termo_lower == str(p.id) or termo_lower in p.nome.lower() or termo_lower in p.especialidade.lower():
            encontrados.append(p)
    return encontrados


# ---------------------------------------------------------------------------
# CONSULTAS
# ---------------------------------------------------------------------------

def cadastrar_consulta(paciente_id: int, profissional_id: int, data: str,
                        tipo: str, status: str, valor: float) -> Consulta:
    # Validação de regra de negócio: paciente e profissional precisam existir
    if not any(p.id == paciente_id for p in listar_pacientes()):
        raise ValueError(f"Paciente com ID {paciente_id} não encontrado.")
    if not any(p.id == profissional_id for p in listar_profissionais()):
        raise ValueError(f"Profissional com ID {profissional_id} não encontrado.")

    novo_id = storage.proximo_id("consultas")
    consulta = Consulta(novo_id, paciente_id, profissional_id, data, tipo, status, valor)
    registros = storage.carregar("consultas")
    registros.append(consulta.to_dict())
    storage.salvar_tudo("consultas", registros)
    return consulta


def listar_consultas(tipo: Optional[str] = None, status: Optional[str] = None) -> list[Consulta]:
    """Lista consultas, podendo filtrar por tipo e/ou status."""
    consultas = [Consulta.from_dict(r) for r in storage.carregar("consultas")]
    if tipo:
        consultas = [c for c in consultas if c.tipo.lower() == tipo.lower()]
    if status:
        consultas = [c for c in consultas if c.status.lower() == status.lower()]
    return consultas


def buscar_consulta(termo: str) -> list[Consulta]:
    """Busca por ID, data, tipo ou status."""
    termo_lower = termo.strip().lower()
    encontrados = []
    for c in listar_consultas():
        if (termo_lower == str(c.id) or termo_lower == str(c.paciente_id)
                or termo_lower in c.data.lower() or termo_lower in c.tipo.lower()
                or termo_lower in c.status.lower()):
            encontrados.append(c)
    return encontrados


def atualizar_status_consulta(consulta_id: int, novo_status: str) -> bool:
    """Atualiza o status de uma consulta (ex.: Agendada -> Realizada/Cancelada)."""
    from models import STATUS_CONSULTA
    if novo_status not in STATUS_CONSULTA:
        raise ValueError(f"Status inválido: '{novo_status}'. Use um de {STATUS_CONSULTA}.")

    registros = storage.carregar("consultas")
    encontrado = False
    for r in registros:
        if int(r["id"]) == consulta_id:
            r["status"] = novo_status
            encontrado = True
            break
    if encontrado:
        storage.salvar_tudo("consultas", registros)
    return encontrado


# ---------------------------------------------------------------------------
# PAGAMENTOS
# ---------------------------------------------------------------------------

def cadastrar_pagamento(consulta_id: int, valor_pago: float, data_pagamento: str, status: str) -> Pagamento:
    if not any(c.id == consulta_id for c in listar_consultas()):
        raise ValueError(f"Consulta com ID {consulta_id} não encontrada.")

    novo_id = storage.proximo_id("pagamentos")
    pagamento = Pagamento(novo_id, consulta_id, valor_pago, data_pagamento, status)
    registros = storage.carregar("pagamentos")
    registros.append(pagamento.to_dict())
    storage.salvar_tudo("pagamentos", registros)
    return pagamento


def listar_pagamentos(status: Optional[str] = None) -> list[Pagamento]:
    pagamentos = [Pagamento.from_dict(r) for r in storage.carregar("pagamentos")]
    if status:
        pagamentos = [p for p in pagamentos if p.status.lower() == status.lower()]
    return pagamentos


def buscar_pagamento(termo: str) -> list[Pagamento]:
    termo_lower = termo.strip().lower()
    encontrados = []
    for p in listar_pagamentos():
        if (termo_lower == str(p.id) or termo_lower == str(p.consulta_id)
                or termo_lower in p.status.lower() or termo_lower in p.data_pagamento.lower()):
            encontrados.append(p)
    return encontrados
