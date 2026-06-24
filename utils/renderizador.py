import os
from typing import List
from models.grupo import Grupo
from models.participante import Participante
from models.despesa import Despesa
from utils.calculos import Calculadora
from utils.algoritmo_divisao import AlgoritmoDivisao
from utils.formatacao import Formatador


TAILWIND_HEAD = """<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style>
    .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
    .glass-card { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
    .custom-shadow { box-shadow: 0 4px 20px rgba(30, 41, 59, 0.05); }
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8f9ff; }
    .success-checkmark { animation: checkmark 0.8s cubic-bezier(0.65, 0, 0.45, 1) forwards; }
    @keyframes checkmark { 0% { transform: scale(0); opacity: 0; } 50% { transform: scale(1.2); } 100% { transform: scale(1); opacity: 1; } }
</style>
<script>
tailwind.config = { darkMode: "class", theme: { extend: {
    "colors": { "primary": "#006c49", "on-primary": "#ffffff", "primary-container": "#10b981",
        "on-primary-container": "#00422b", "secondary": "#545f73", "on-secondary": "#ffffff",
        "secondary-container": "#d5e0f8", "on-secondary-container": "#586377",
        "tertiary": "#5c5f61", "on-tertiary": "#ffffff", "tertiary-container": "#a0a3a5",
        "on-tertiary-container": "#36393b", "error": "#ba1a1a", "on-error": "#ffffff",
        "error-container": "#ffdad6", "on-error-container": "#93000a",
        "surface": "#f8f9ff", "on-surface": "#0b1c30", "on-surface-variant": "#3c4a42",
        "surface-container-lowest": "#ffffff", "surface-container-low": "#eff4ff",
        "surface-container": "#e5eeff", "surface-container-high": "#dce9ff",
        "surface-container-highest": "#d3e4fe", "surface-dim": "#cbdbf5",
        "outline": "#6c7a71", "outline-variant": "#bbcabf",
        "inverse-surface": "#213145", "inverse-on-surface": "#eaf1ff",
        "background": "#f8f9ff", "on-background": "#0b1c30", "primary-fixed": "#6ffbbe",
        "primary-fixed-dim": "#4edea3", "surface-variant": "#d3e4fe" },
    "borderRadius": { "DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px" },
    "spacing": { "lg": "24px", "sm": "12px", "md": "16px", "base": "4px", "xs": "8px",
        "gutter": "16px", "margin-desktop": "40px", "xl": "32px", "margin-mobile": "20px" },
    "fontSize": {
        "label-sm": ["12px", {"lineHeight": "1.4", "fontWeight": "500"}],
        "label-md": ["14px", {"lineHeight": "1.4", "letterSpacing": "0.01em", "fontWeight": "600"}],
        "body-md": ["16px", {"lineHeight": "1.5", "fontWeight": "400"}],
        "body-lg": ["18px", {"lineHeight": "1.6", "fontWeight": "400"}],
        "headline-md": ["20px", {"lineHeight": "1.3", "fontWeight": "600"}],
        "headline-lg-mobile": ["24px", {"lineHeight": "1.2", "fontWeight": "700"}],
        "headline-lg": ["32px", {"lineHeight": "1.2", "letterSpacing": "-0.01em", "fontWeight": "700"}],
        "display-lg": ["48px", {"lineHeight": "1.1", "letterSpacing": "-0.02em", "fontWeight": "800"}]
    }
}}}
</script>
</head>
<body class="bg-background text-on-surface min-h-screen pb-24">
"""

BODY_CLOSE = """</body></html>"""

fmt = Formatador()


class Renderizador:
    def __init__(self, grupo: Grupo):
        self.grupo = grupo
        self.calc = Calculadora(grupo)
        self.divisao = AlgoritmoDivisao(grupo)

    def _header(self, title="Racha Aí!"):
        return f"""
<header class="bg-surface shadow-sm top-0 sticky z-50">
<div class="flex items-center justify-between px-margin-mobile h-16 w-full max-w-7xl mx-auto">
<div class="flex items-center gap-3">
<span class="material-symbols-outlined text-primary text-headline-md">account_balance_wallet</span>
<h1 class="text-headline-md font-bold text-primary">{title}</h1>
</div>
<div class="flex items-center gap-4">
<div class="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container font-bold text-sm">
{self.grupo.participantes[0].iniciais if self.grupo.participantes else "?"}
</div>
</div>
</div>
</header>"""

    def _kpi_card(self, label, value, icon, gradient, sublabel=""):
        sub_html = f'<p class="text-label-sm text-white/80 mt-base font-medium">{sublabel}</p>' if sublabel else ""
        return f"""
<div class="custom-shadow p-lg rounded-2xl flex flex-col justify-between min-h-[150px] text-white relative overflow-hidden" style="background:{gradient}">
<div class="absolute -right-6 -top-6 w-24 h-24 rounded-full bg-white/10"></div>
<div class="flex items-center justify-between relative">
<p class="text-label-md text-white/90 font-semibold">{label}</p>
<span class="material-symbols-outlined bg-white/20 rounded-full p-1.5 text-white text-[20px]">{icon}</span>
</div>
<div class="relative">
<p class="text-[34px] font-extrabold leading-none tracking-tight">{value}</p>
{sub_html}
</div>
</div>"""

    def _despesa_card(self, despesa: Despesa):
        pagador = self.grupo.get_participante(despesa.pagador_id)
        nome_pagador = pagador.nome if pagador else "-"
        return f"""
<div class="bg-surface-container-lowest custom-shadow p-md rounded-xl flex items-center justify-between hover:bg-surface-container-low transition-colors cursor-pointer">
<div class="flex items-center gap-md">
<div class="w-12 h-12 rounded-full bg-{despesa.cor}-container/20 flex items-center justify-center">
<span class="material-symbols-outlined text-{despesa.cor}">{despesa.icone}</span>
</div>
<div>
<p class="text-body-md font-semibold text-on-surface">{despesa.descricao}</p>
<p class="text-label-sm text-on-surface-variant">Pago por {nome_pagador} &bull; {despesa.data_formatada}</p>
</div>
</div>
<div class="text-right">
<p class="text-body-md font-bold text-on-surface">{fmt.moeda(despesa.valor)}</p>
<p class="text-label-sm text-on-surface-variant">{len(despesa.participantes_ids)} pessoa(s)</p>
</div>
</div>"""

    def _participante_card(self, p: Participante):
        saldo = self.calc.saldo_participante(p.id)
        positivo = saldo >= 0
        sinal = "+" if positivo else ""
        badge_bg = "#dcfce7" if positivo else "#fee2e2"
        badge_tx = "#15803d" if positivo else "#b91c1c"
        avatar_grad = "linear-gradient(135deg,#10b981,#006c49)" if positivo else "linear-gradient(135deg,#fb7185,#ef4444)"
        label = "recebe" if positivo else "deve"
        return f"""
<div class="bg-surface-container-lowest custom-shadow p-md rounded-xl flex items-center gap-md border border-outline-variant/20">
<div class="w-11 h-11 rounded-full flex items-center justify-center font-bold text-sm text-white shrink-0" style="background:{avatar_grad}">{p.iniciais}</div>
<div class="flex-1 min-w-0">
<p class="text-label-md text-on-surface font-semibold truncate">{p.nome}</p>
<p class="text-label-sm text-on-surface-variant">{label}</p>
</div>
<span class="text-label-md font-bold px-3 py-1 rounded-full whitespace-nowrap" style="background:{badge_bg};color:{badge_tx}">{sinal}{fmt.moeda(saldo)}</span>
</div>"""

    def render_dashboard(self) -> str:
        kpis = self.calc.kpis()
        despesas_recentes = sorted(self.grupo.despesas, key=lambda d: d.data, reverse=True)[:5]

        kpi1 = self._kpi_card("Total do Grupo", fmt.moeda(kpis["total_gasto"]), "analytics", "linear-gradient(135deg,#006c49 0%,#10b981 100%)", f"{kpis['num_despesas']} despesas")
        kpi2 = self._kpi_card("Media por Pessoa", fmt.moeda(kpis["media_por_pessoa"]), "person", "linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%)", f"{kpis['num_participantes']} participantes")
        kpi3 = self._kpi_card("Maior Despesa", fmt.moeda(kpis["maior_despesa"]), "trending_up", "linear-gradient(135deg,#f97316 0%,#fb7185 100%)", kpis["maior_despesa_desc"])

        despesas_html = "".join(self._despesa_card(d) for d in despesas_recentes)
        participantes_html = "".join(self._participante_card(p) for p in self.grupo.participantes)

        avatars = ""
        for p in self.grupo.participantes[:4]:
            colors = ["primary-container", "secondary-container", "tertiary-container", "surface-container-highest"]
            idx = self.grupo.participantes.index(p) % len(colors)
            avatars += f'<div class="inline-block h-8 w-8 rounded-full ring-2 ring-white bg-{colors[idx]} flex items-center justify-center text-[10px] font-bold">{p.iniciais}</div>'

        html = TAILWIND_HEAD + self._header() + f"""
<main class="max-w-7xl mx-auto px-margin-mobile pt-lg">
<section class="mb-xl">
<div class="relative overflow-hidden rounded-2xl p-lg custom-shadow" style="background:linear-gradient(135deg,#004d2e 0%,#006c49 55%,#10b981 100%)">
<div class="absolute -right-8 -top-10 w-40 h-40 rounded-full bg-white/10"></div>
<div class="absolute -right-2 bottom-2 w-20 h-20 rounded-full bg-white/5"></div>
<div class="relative flex flex-col md:flex-row md:items-center justify-between gap-md">
<div>
<p class="text-label-sm text-white/70 uppercase tracking-widest mb-1">Grupo</p>
<h2 class="text-headline-lg-mobile md:text-headline-lg text-white mb-xs">{self.grupo.nome}</h2>
<div class="flex -space-x-2 overflow-hidden py-1">{avatars}</div>
</div>
<span class="material-symbols-outlined text-white/30 text-[64px] hidden md:block">savings</span>
</div>
</div>
</section>
<section class="grid grid-cols-1 md:grid-cols-3 gap-md mb-xl">
{kpi1}{kpi2}{kpi3}
</section>
<section>
<div class="flex items-center justify-between mb-md">
<h3 class="text-headline-md text-on-surface">Despesas Recentes</h3>
</div>
<div class="space-y-sm">{despesas_html}</div>
</section>
<section class="mt-xl">
<h3 class="text-headline-md text-on-surface mb-md">Participantes</h3>
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-md">{participantes_html}</div>
</section>
</main>""" + BODY_CLOSE
        return html

    def render_fechamento(self) -> str:
        transferencias = self.divisao.calcular_transferencias()
        total = self.calc.total_gasto()
        n = self.calc.numero_participantes()

        cards_html = ""
        for t in transferencias:
            cards_html += f"""
<div class="bg-white p-md rounded-xl shadow-[0_4px_20px_rgba(30,41,59,0.05)] border border-outline-variant/30 transition-transform active:scale-[0.98]">
<div class="flex items-center justify-between mb-md">
<div class="flex items-center gap-3">
<div class="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container font-bold">{t.de.iniciais}</div>
<div>
<p class="text-body-md font-semibold"><span class="text-error">{t.de.nome}</span> deve pagar para <span class="text-primary">{t.para.nome}</span></p>
<p class="text-label-sm text-on-surface-variant">PIX: {t.para.chave_pix_formatada}</p>
</div>
</div>
<p class="text-headline-md text-on-surface">{fmt.moeda(t.valor)}</p>
</div>
<button onclick="navigator.clipboard.writeText('{t.para.chave_pix}');document.getElementById('toast').classList.remove('opacity-0');setTimeout(()=>document.getElementById('toast').classList.add('opacity-0'),2000)"
class="w-full flex items-center justify-center gap-2 py-3 bg-primary-container/10 text-primary text-label-md rounded-full hover:bg-primary-container/20 transition-colors active:scale-95">
<span class="material-symbols-outlined text-[18px]">content_copy</span>Copiar Chave PIX
</button>
</div>"""

        html = TAILWIND_HEAD + self._header() + f"""
<main class="max-w-2xl mx-auto px-margin-mobile pt-xl">
<section class="text-center mb-xl">
<div class="success-checkmark inline-flex items-center justify-center w-20 h-20 bg-primary-container rounded-full text-on-primary-container mb-md shadow-lg shadow-primary-container/20">
<span class="material-symbols-outlined text-[40px]" style="font-variation-settings: 'wght' 600;">check</span>
</div>
<h2 class="text-headline-lg-mobile text-on-surface mb-xs">Resumo do Acerto</h2>
<p class="text-body-md text-on-surface-variant">Tudo calculado! Veja como zerar as pendencias do grupo.</p>
</section>
<section class="grid grid-cols-2 gap-sm mb-xl">
<div class="col-span-2 bg-surface-container-lowest p-md rounded-xl shadow-[0_4px_20px_rgba(30,41,59,0.05)] flex items-center justify-between border-l-4 border-primary">
<div>
<p class="text-label-sm text-on-surface-variant uppercase tracking-wider">Total do Grupo</p>
<p class="text-headline-md text-primary">{fmt.moeda(total)}</p>
</div>
<div class="bg-primary-container/10 p-xs rounded-full">
<span class="material-symbols-outlined text-primary">analytics</span>
</div>
</div>
<div class="bg-surface-container-lowest p-md rounded-xl shadow-[0_4px_20px_rgba(30,41,59,0.05)] border-l-4 border-secondary">
<p class="text-label-sm text-on-surface-variant">Transferencias</p>
<p class="text-body-lg font-bold">{len(transferencias)} pagamento(s)</p>
</div>
<div class="bg-surface-container-lowest p-md rounded-xl shadow-[0_4px_20px_rgba(30,41,59,0.05)] border-l-4 border-tertiary">
<p class="text-label-sm text-on-surface-variant">Participantes</p>
<p class="text-body-lg font-bold">{n} pessoas</p>
</div>
</section>
<section class="mb-xl">
<div class="flex items-center gap-2 mb-md">
<span class="material-symbols-outlined text-primary">payments</span>
<h3 class="text-headline-md">Pagamentos Sugeridos</h3>
</div>
<div class="space-y-sm">{cards_html}</div>
</section>
</main>
<div class="fixed bottom-24 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface px-6 py-3 rounded-full text-label-md shadow-xl opacity-0 transition-all duration-300 z-[100]" id="toast">Chave PIX copiada!</div>
""" + BODY_CLOSE
        return html
