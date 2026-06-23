from datetime import datetime


class Formatador:
    @staticmethod
    def moeda(valor: float) -> str:
        if valor < 0:
            return f"- R$ {abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def moeda_simples(valor: float) -> str:
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def percentual(valor: float) -> str:
        return f"{valor:.1f}%"

    @staticmethod
    def data_br(data_str: str) -> str:
        try:
            dt = datetime.strptime(data_str, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return data_str

    @staticmethod
    def data_relativa(data_str: str) -> str:
        try:
            dt = datetime.strptime(data_str, "%Y-%m-%d")
            hoje = datetime.now().date()
            delta = (hoje - dt.date()).days
            if delta == 0:
                return "Hoje"
            elif delta == 1:
                return "Ontem"
            elif delta < 7:
                return f"{delta} dias atrás"
            elif delta < 30:
                semanas = delta // 7
                return f"{semanas} semana{'s' if semanas > 1 else ''} atrás"
            else:
                return dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return data_str

    @staticmethod
    def hora_atual() -> str:
        return datetime.now().strftime("%H:%M")

    # ─── Aliases (usados por utils/components.py) ───
    @staticmethod
    def formatar_valor(valor: float) -> str:
        return Formatador.moeda(valor)

    @staticmethod
    def formatar_data(data_str: str) -> str:
        return Formatador.data_relativa(data_str)
