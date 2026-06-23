from typing import List, Tuple
from dataclasses import dataclass
from models.grupo import Grupo
from models.participante import Participante
from utils.calculos import Calculadora


@dataclass
class Transferencia:
    de: Participante
    para: Participante
    valor: float


class AlgoritmoDivisao:
    """
    Algoritmo greedy para minimizar o número de transferências.
    Sempre pareia o maior devedor com o maior credor até zerar.
    """

    def __init__(self, grupo: Grupo):
        self.grupo = grupo
        self.calculadora = Calculadora(grupo)

    def calcular_transferencias(self) -> List[Transferencia]:
        saldos = self.calculadora.saldos()

        devedores = []
        credores = []

        for pid, saldo in saldos.items():
            if saldo < -0.01:
                devedores.append([pid, abs(saldo)])
            elif saldo > 0.01:
                credores.append([pid, saldo])

        devedores.sort(key=lambda x: x[1], reverse=True)
        credores.sort(key=lambda x: x[1], reverse=True)

        transferencias = []

        i, j = 0, 0
        while i < len(devedores) and j < len(credores):
            devedor_id, divida = devedores[i]
            credor_id, credito = credores[j]

            valor_transferencia = min(divida, credito)

            if valor_transferencia > 0.01:
                devedor = self.grupo.get_participante(devedor_id)
                credor = self.grupo.get_participante(credor_id)

                if devedor and credor:
                    transferencias.append(
                        Transferencia(
                            de=devedor,
                            para=credor,
                            valor=round(valor_transferencia, 2)
                        )
                    )

            devedores[i][1] -= valor_transferencia
            credores[j][1] -= valor_transferencia

            if devedores[i][1] < 0.01:
                i += 1
            if credores[j][1] < 0.01:
                j += 1

        return transferencias

    def resumo_textual(self) -> List[str]:
        transferencias = self.calcular_transferencias()
        linhas = []
        for t in transferencias:
            linhas.append(
                f"{t.de.nome} deve enviar R$ {t.valor:,.2f} para {t.para.nome}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
        return linhas
