from dataclasses import dataclass, field
from typing import List
import uuid

from models.participante import Participante
from models.despesa import Despesa


TIPOS_EVENTO = [
    "Viagem",
    "Churrasco",
    "Festa",
    "Restaurante",
    "Final de semana",
    "Formatura",
    "Casamento",
    "Despedida de solteiro",
    "Outro",
]


@dataclass
class Grupo:
    nome: str
    descricao: str = ""
    tipo_evento: str = "Viagem"
    participantes: List[Participante] = field(default_factory=list)
    despesas: List[Despesa] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    criado_por: str = ""

    def adicionar_participante(self, participante: Participante) -> None:
        self.participantes.append(participante)

    def remover_participante(self, participante_id: str) -> None:
        self.participantes = [p for p in self.participantes if p.id != participante_id]
        self.despesas = [
            d for d in self.despesas
            if d.pagador_id != participante_id
        ]
        for despesa in self.despesas:
            despesa.participantes_ids = [
                pid for pid in despesa.participantes_ids if pid != participante_id
            ]

    def adicionar_despesa(self, despesa: Despesa) -> None:
        self.despesas.append(despesa)

    def remover_despesa(self, despesa_id: str) -> None:
        self.despesas = [d for d in self.despesas if d.id != despesa_id]

    def get_participante(self, participante_id: str):
        for p in self.participantes:
            if p.id == participante_id:
                return p
        return None

    def get_participante_por_nome(self, nome: str):
        for p in self.participantes:
            if p.nome == nome:
                return p
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "tipo_evento": self.tipo_evento,
            "criado_por": self.criado_por,
            "participantes": [p.to_dict() for p in self.participantes],
            "despesas": [d.to_dict() for d in self.despesas],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Grupo":
        participantes = [Participante.from_dict(p) for p in data.get("participantes", [])]
        despesas = [Despesa.from_dict(d) for d in data.get("despesas", [])]
        return cls(
            nome=data["nome"],
            descricao=data.get("descricao", ""),
            tipo_evento=data.get("tipo_evento", "Viagem"),
            participantes=participantes,
            despesas=despesas,
            id=data.get("id", str(uuid.uuid4())[:8]),
            criado_por=data.get("criado_por", ""),
        )
