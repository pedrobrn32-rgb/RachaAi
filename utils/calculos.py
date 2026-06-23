from typing import Dict, List, Tuple
from models.participante import Participante
from models.despesa import Despesa
from models.grupo import Grupo


class Calculadora:
    def __init__(self, grupo: Grupo):
        self.grupo = grupo

    def total_gasto(self) -> float:
        return sum(d.valor for d in self.grupo.despesas)

    def numero_despesas(self) -> int:
        return len(self.grupo.despesas)

    def numero_participantes(self) -> int:
        return len(self.grupo.participantes)

    def media_por_pessoa(self) -> float:
        total = self.total_gasto()
        n = self.numero_participantes()
        if n == 0:
            return 0.0
        return total / n

    def total_pago_por(self, participante_id: str) -> float:
        return sum(
            d.valor for d in self.grupo.despesas
            if d.pagador_id == participante_id
        )

    def total_consumido_por(self, participante_id: str) -> float:
        total = 0.0
        for d in self.grupo.despesas:
            if participante_id in d.participantes_ids:
                total += d.valor / len(d.participantes_ids)
        return total

    def saldo_participante(self, participante_id: str) -> float:
        pago = self.total_pago_por(participante_id)
        consumido = self.total_consumido_por(participante_id)
        return pago - consumido

    def saldos(self) -> Dict[str, float]:
        return {
            p.id: self.saldo_participante(p.id)
            for p in self.grupo.participantes
        }

    def maior_despesa(self) -> Despesa:
        if not self.grupo.despesas:
            return None
        return max(self.grupo.despesas, key=lambda d: d.valor)

    def quem_mais_pagou(self) -> Tuple[Participante, float]:
        if not self.grupo.participantes:
            return None, 0.0
        max_pago = 0.0
        pessoa = None
        for p in self.grupo.participantes:
            pago = self.total_pago_por(p.id)
            if pago > max_pago:
                max_pago = pago
                pessoa = p
        return pessoa, max_pago

    def quem_menos_pagou(self) -> Tuple[Participante, float]:
        if not self.grupo.participantes:
            return None, 0.0
        min_pago = float('inf')
        pessoa = None
        for p in self.grupo.participantes:
            pago = self.total_pago_por(p.id)
            if pago < min_pago:
                min_pago = pago
                pessoa = p
        return pessoa, min_pago

    def quem_mais_consumiu(self) -> Tuple[Participante, float]:
        if not self.grupo.participantes:
            return None, 0.0
        max_consumo = 0.0
        pessoa = None
        for p in self.grupo.participantes:
            consumido = self.total_consumido_por(p.id)
            if consumido > max_consumo:
                max_consumo = consumido
                pessoa = p
        return pessoa, max_consumo

    def quem_mais_deve(self) -> Tuple[Participante, float]:
        if not self.grupo.participantes:
            return None, 0.0
        min_saldo = 0.0
        pessoa = None
        for p in self.grupo.participantes:
            saldo = self.saldo_participante(p.id)
            if saldo < min_saldo:
                min_saldo = saldo
                pessoa = p
        return pessoa, abs(min_saldo)

    def quem_mais_recebe(self) -> Tuple[Participante, float]:
        if not self.grupo.participantes:
            return None, 0.0
        max_saldo = 0.0
        pessoa = None
        for p in self.grupo.participantes:
            saldo = self.saldo_participante(p.id)
            if saldo > max_saldo:
                max_saldo = saldo
                pessoa = p
        return pessoa, max_saldo

    def gastos_por_categoria(self) -> Dict[str, float]:
        categorias = {}
        for d in self.grupo.despesas:
            categorias[d.categoria] = categorias.get(d.categoria, 0.0) + d.valor
        return dict(sorted(categorias.items(), key=lambda x: x[1], reverse=True))

    def categoria_mais_cara(self) -> Tuple[str, float]:
        categorias = self.gastos_por_categoria()
        if not categorias:
            return "", 0.0
        cat = max(categorias, key=categorias.get)
        return cat, categorias[cat]

    def gastos_por_participante(self) -> Dict[str, float]:
        return {
            p.nome: self.total_pago_por(p.id)
            for p in self.grupo.participantes
        }

    def kpis(self) -> dict:
        maior = self.maior_despesa()
        quem_pagou, valor_pagou = self.quem_mais_pagou()
        quem_consumiu, valor_consumiu = self.quem_mais_consumiu()
        return {
            "total_gasto": self.total_gasto(),
            "num_participantes": self.numero_participantes(),
            "media_por_pessoa": self.media_por_pessoa(),
            "maior_despesa": maior.valor if maior else 0.0,
            "maior_despesa_desc": maior.descricao if maior else "-",
            "quem_mais_pagou": quem_pagou.nome if quem_pagou else "-",
            "valor_mais_pagou": valor_pagou,
            "quem_mais_consumiu": quem_consumiu.nome if quem_consumiu else "-",
            "valor_mais_consumiu": valor_consumiu,
            "num_despesas": self.numero_despesas(),
        }
