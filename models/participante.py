from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Participante:
    nome: str
    chave_pix: str = ""
    tipo_chave_pix: str = "CPF"  # CPF, E-mail, Telefone, Aleatória
    foto: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def iniciais(self) -> str:
        partes = self.nome.split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        return self.nome[:2].upper()

    @property
    def chave_pix_formatada(self) -> str:
        if not self.chave_pix:
            return "Não informada"
        if self.tipo_chave_pix == "CPF":
            cpf = self.chave_pix.replace(".", "").replace("-", "")
            if len(cpf) == 11:
                return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        elif self.tipo_chave_pix == "Telefone":
            tel = self.chave_pix.replace(" ", "").replace("-", "")
            if len(tel) >= 11:
                return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        return self.chave_pix

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "chave_pix": self.chave_pix,
            "tipo_chave_pix": self.tipo_chave_pix,
            "foto": self.foto,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Participante":
        return cls(
            nome=data["nome"],
            chave_pix=data.get("chave_pix", ""),
            tipo_chave_pix=data.get("tipo_chave_pix", "CPF"),
            foto=data.get("foto"),
            id=data.get("id", str(uuid.uuid4())[:8]),
        )
