from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid


CATEGORIAS = [
    "Hotel",
    "Airbnb",
    "Restaurante",
    "Mercado",
    "Cerveja",
    "Gasolina",
    "Passeios",
    "Ingresso",
    "Outros",
]

ICONES_CATEGORIA = {
    "Hotel": "hotel",
    "Airbnb": "home",
    "Restaurante": "restaurant",
    "Mercado": "shopping_cart",
    "Cerveja": "sports_bar",
    "Gasolina": "local_gas_station",
    "Passeios": "hiking",
    "Ingresso": "confirmation_number",
    "Outros": "receipt_long",
}

CORES_CATEGORIA = {
    "Hotel": "secondary",
    "Airbnb": "primary",
    "Restaurante": "tertiary",
    "Mercado": "primary",
    "Cerveja": "secondary",
    "Gasolina": "tertiary",
    "Passeios": "primary",
    "Ingresso": "secondary",
    "Outros": "tertiary",
}


@dataclass
class Despesa:
    descricao: str
    categoria: str
    valor: float
    pagador_id: str
    participantes_ids: List[str]
    data: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def valor_por_pessoa(self) -> float:
        if not self.participantes_ids:
            return 0.0
        return self.valor / len(self.participantes_ids)

    @property
    def icone(self) -> str:
        return ICONES_CATEGORIA.get(self.categoria, "receipt_long")

    @property
    def cor(self) -> str:
        return CORES_CATEGORIA.get(self.categoria, "tertiary")

    @property
    def data_formatada(self) -> str:
        try:
            dt = datetime.strptime(self.data, "%Y-%m-%d")
            hoje = datetime.now().date()
            delta = (hoje - dt.date()).days
            if delta == 0:
                return "Hoje"
            elif delta == 1:
                return "Ontem"
            elif delta < 7:
                return f"{delta} dias atrás"
            else:
                return dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return self.data

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "valor": self.valor,
            "pagador_id": self.pagador_id,
            "participantes_ids": self.participantes_ids,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Despesa":
        return cls(
            descricao=data["descricao"],
            categoria=data["categoria"],
            valor=data["valor"],
            pagador_id=data["pagador_id"],
            participantes_ids=data["participantes_ids"],
            data=data.get("data", datetime.now().strftime("%Y-%m-%d")),
            id=data.get("id", str(uuid.uuid4())[:8]),
        )
