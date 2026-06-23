---
name: DivideAí
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3c4a42'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#6c7a71'
  outline-variant: '#bbcabf'
  surface-tint: '#006c49'
  primary: '#006c49'
  on-primary: '#ffffff'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#4edea3'
  secondary: '#545f73'
  on-secondary: '#ffffff'
  secondary-container: '#d5e0f8'
  on-secondary-container: '#586377'
  tertiary: '#5c5f61'
  on-tertiary: '#ffffff'
  tertiary-container: '#a0a3a5'
  on-tertiary-container: '#36393b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#d8e3fb'
  secondary-fixed-dim: '#bcc7de'
  on-secondary-fixed: '#111c2d'
  on-secondary-fixed-variant: '#3c475a'
  tertiary-fixed: '#e0e3e5'
  tertiary-fixed-dim: '#c4c7c9'
  on-tertiary-fixed: '#191c1e'
  on-tertiary-fixed-variant: '#444749'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin-mobile: 20px
  margin-desktop: 40px
---

## Marca e Estilo

Este sistema de design foi concebido para um aplicativo de divisão de despesas que prioriza a clareza financeira e a harmonia social. A personalidade da marca é **vibrante, confiável e descomplicada**, removendo o atrito matemático e emocional de dividir contas.

O estilo visual baseia-se no **Minimalismo Moderno** com toques de **Glassmorphism** sutil. A interface utiliza espaços generosos, tipografia geométrica e uma hierarquia visual clara para garantir que o usuário entenda instantaneamente quem deve a quem. A experiência deve evocar um sentimento de organização, transparência e modernidade tecnológica.

## Cores

A paleta de cores é fundamentada no equilíbrio entre a vitalidade do dinheiro e a seriedade da gestão financeira.

- **Primária (Verde Esmeralda):** Utilizada para ações principais, saldos positivos e botões de confirmação. Transmite crescimento e confiança.
- **Secundária (Azul Profundo):** Aplicada em textos de cabeçalho, ícones estruturais e elementos que exigem peso visual. Transmite estabilidade.
- **Neutros (Escala de Cinzas):** Utilizados para textos secundários, bordas sutis e superfícies de fundo.
- **Feedback:** 
  - *Vermelho Coral (#F43F5E):* Exclusivo para valores negativos (débitos) e alertas de erro.
  - *Branco Puro (#FFFFFF):* Base fundamental para os cards e áreas de conteúdo, garantindo limpeza visual.

## Tipografia

A tipografia utiliza a **Plus Jakarta Sans**, uma sans-serif geométrica moderna que oferece excelente legibilidade em telas pequenas e um tom amigável.

Os pesos são usados estrategicamente: **Bold/ExtraBold** para valores monetários e títulos de seção para facilitar o escaneamento visual; **Medium/Regular** para textos de apoio e descrições de transações. Para valores monetários de destaque (saldos), recomenda-se o uso de kerning ligeiramente mais apertado para manter a coesão visual.

## Layout e Espaçamento

O sistema de layout utiliza uma **grade fluida baseada em 8px**, garantindo proporções consistentes entre todos os elementos.

- **Mobile:** Grade de 4 colunas com margens laterais de 20px. Os cards geralmente ocupam a largura total da grade (4 colunas).
- **Desktop/Tablet:** Grade de 12 colunas, centralizada, com largura máxima de 1200px.
- **Ritmo Vertical:** O espaçamento entre cards de transação deve ser de `sm` (12px), enquanto o espaçamento entre seções lógicas (ex: "Amigos" e "Grupos") deve ser de `xl` (32px) para criar uma clara separação visual.

## Elevação e Profundidade

A hierarquia é comunicada através de **sombras suaves e camadas tonais**, evitando o uso de bordas pesadas.

- **Nível 0 (Fundo):** Cor de fundo `tertiary_color_hex` (#F8FAFC).
- **Nível 1 (Cards):** Fundo branco com sombra projetada muito difusa: `y: 4px, blur: 20px, color: rgba(30, 41, 59, 0.05)`.
- **Nível 2 (Modais/Menus):** Sombra mais pronunciada para indicar interatividade e foco: `y: 10px, blur: 30px, color: rgba(30, 41, 59, 0.1)`.
- **Interação:** Ao pressionar um card ou botão, o elemento deve reduzir levemente sua elevação (efeito de compressão) para feedback tátil visual.

## Formas

O sistema adota uma estética **altamente arredondada**, reforçando o aspecto amigável e moderno do aplicativo.

- **Cards de Despesas:** Utilizam `rounded-lg` (16px) para criar uma aparência de "bolha" de informação.
- **Botões e Inputs:** Utilizam `rounded-md` (8px) para botões de ação secundária e `pill` para o botão de ação principal (CTA).
- **Avatares:** Devem ser sempre circulares, com uma borda branca de 2px quando sobrepostos em pilhas de avatares (grupos).

## Componentes

### Botões
- **Primário:** Preenchimento total em Verde Esmeralda, texto em Branco. Forma arredondada (pill).
- **Secundário:** Fundo Azul Profundo suave (10% de opacidade) com texto em Azul Profundo.

### Cards de Transação
Devem conter o ícone da categoria à esquerda (em um círculo colorido suave), o nome da despesa e data no centro, e o valor à direita. Se o usuário deve dinheiro, o valor é Vermelho Coral; se deve receber, Verde Esmeralda.

### Inputs de Valor
Campos numéricos grandes, sem bordas, apenas com uma linha de base sutil que se transforma em Verde Esmeralda quando focada. O símbolo da moeda (R$) deve ser menor que o valor numérico.

### Chips de Filtro
Pequenas pílulas para alternar entre "Tudo", "Devo", "Me devem". Quando ativos, ganham fundo Azul Profundo e texto Branco.

### Listas de Amigos
Itens de lista com altura mínima de 64px, separadores lineares ultra-finos (1px) em cinza claro, com foco no avatar e no nome do contato.

### Feedback Visual
Utilizar micro-interações de "check" verde ao liquidar uma dívida, proporcionando uma sensação de recompensa ao usuário.