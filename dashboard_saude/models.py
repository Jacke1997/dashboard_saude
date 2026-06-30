"""
models.py
---------
Estruturas de dados (classes) do sistema de Gestão em Saúde.

Cada classe representa uma entidade do domínio e sabe converter-se
de/para um dicionário simples, o que facilita a persistência em CSV/JSON
feita pelo módulo storage.py.
"""

from dataclasses import dataclass, asdict
from datetime import datetime


# Conjuntos (set) com os valores válidos para alguns campos.
# Usar 'set' aqui garante valores únicos e permite checagem rápida (in).
TIPOS_CONSULTA = {"SUS", "Particular", "Convenio"}
STATUS_CONSULTA = {"Agendada", "Realizada", "Cancelada"}
STATUS_PAGAMENTO = {"Pago", "Pendente", "Glosado"}


def _validar_data(data_str: str) -> str:
    """Valida e normaliza uma data no formato DD/MM/AAAA."""
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        raise ValueError(f"Data inválida: '{data_str}'. Use o formato DD/MM/AAAA.")
    return data_str


@dataclass
class Paciente:
    id: int
    nome: str
    data_nascimento: str
    telefone: str
    convenio: str = "Nenhum"

    def __post_init__(self):
        if not self.nome.strip():
            raise ValueError("Nome do paciente não pode ser vazio.")
        _validar_data(self.data_nascimento)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Paciente":
        return Paciente(
            id=int(d["id"]),
            nome=d["nome"],
            data_nascimento=d["data_nascimento"],
            telefone=d["telefone"],
            convenio=d.get("convenio", "Nenhum"),
        )


@dataclass
class Profissional:
    id: int
    nome: str
    especialidade: str
    registro: str  # CRM, COREN, etc.

    def __post_init__(self):
        if not self.nome.strip():
            raise ValueError("Nome do profissional não pode ser vazio.")

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Profissional":
        return Profissional(
            id=int(d["id"]),
            nome=d["nome"],
            especialidade=d["especialidade"],
            registro=d["registro"],
        )


@dataclass
class Consulta:
    id: int
    paciente_id: int
    profissional_id: int
    data: str
    tipo: str          # SUS, Particular, Convenio
    status: str        # Agendada, Realizada, Cancelada
    valor: float

    def __post_init__(self):
        _validar_data(self.data)
        if self.tipo not in TIPOS_CONSULTA:
            raise ValueError(f"Tipo de consulta inválido: '{self.tipo}'. Use um de {TIPOS_CONSULTA}.")
        if self.status not in STATUS_CONSULTA:
            raise ValueError(f"Status de consulta inválido: '{self.status}'. Use um de {STATUS_CONSULTA}.")
        if self.valor < 0:
            raise ValueError("Valor da consulta não pode ser negativo.")

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Consulta":
        return Consulta(
            id=int(d["id"]),
            paciente_id=int(d["paciente_id"]),
            profissional_id=int(d["profissional_id"]),
            data=d["data"],
            tipo=d["tipo"],
            status=d["status"],
            valor=float(d["valor"]),
        )


@dataclass
class Pagamento:
    id: int
    consulta_id: int
    valor_pago: float
    data_pagamento: str
    status: str  # Pago, Pendente, Glosado

    def __post_init__(self):
        _validar_data(self.data_pagamento)
        if self.status not in STATUS_PAGAMENTO:
            raise ValueError(f"Status de pagamento inválido: '{self.status}'. Use um de {STATUS_PAGAMENTO}.")
        if self.valor_pago < 0:
            raise ValueError("Valor pago não pode ser negativo.")

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Pagamento":
        return Pagamento(
            id=int(d["id"]),
            consulta_id=int(d["consulta_id"]),
            valor_pago=float(d["valor_pago"]),
            data_pagamento=d["data_pagamento"],
            status=d["status"],
        )
