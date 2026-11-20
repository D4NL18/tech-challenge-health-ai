<!-- Hallmark Â· pre-emit critique: P5 H4 E5 S5 R5 V4 Â· theme: custom "ProntuÃ¡rio" Â· contrast: pass (40â€“41) Â· tokens: pass (48) Â· icons: pass (30) -->

# Design System Oficial â€” HealthAI Â· Kit "ProntuÃ¡rio"

> **LocalizaÃ§Ã£o MandatÃ³ria:** `.agents/docs/design/DESIGN_SYSTEM.md`
> **Status:** Ativo Â· v2.0 (proposta do zero, substitui integralmente o kit "Soft SaaS Premium" v1)
> **ResponsÃ¡vel:** Designer (`designer.md`) / `uiux-expert`
> **Auditor:** UX Reviewer (`ux_reviewer.md`)
> **GovernanÃ§a:** `.agents/rules/frontend-ui-rules.md` e `.agents/rules/frontend-ui-rules.md`
> **Specimen visual:** [`specimen/prontuario-kit.html`](specimen/prontuario-kit.html) (abrir no navegador)
> **Base conceitual:** `docs/fase1/relatorio-tecnico-fase1.md` e `docs/fase2/relatorio-tecnico-fase2.md` â€” o cÃ³digo atual do frontend **nÃ£o** foi usado como referÃªncia.

---

## 1. Conceito

O HealthAI faz trÃªs coisas: **triagem preditiva** (cÃ¢ncer de mama e SOP, com dados tabulares, mamografia e relato livre), **explicaÃ§Ã£o clÃ­nica** (laudos gerados por LLM sobre as probabilidades) e **logÃ­stica hospitalar** (rotas CVRP com cadeia de frio 2â€“8 Â°C). Os usuÃ¡rios sÃ£o profissionais de saÃºde, gestores e motoristas â€” gente que lÃª laudos, preenche formulÃ¡rios e confere planilhas.

Por isso o kit se chama **ProntuÃ¡rio**: a interface se comporta como um documento clÃ­nico bem diagramado, nÃ£o como um app de IA. Papel levemente quente, tinta grafite, linhas finas de formulÃ¡rio, nÃºmeros em fonte de mÃ¡quina de escrever tÃ©cnica e **uma Ãºnica caneta azul** para marcar o que estÃ¡ selecionado.

### 1.1 Cinco princÃ­pios

| # | PrincÃ­pio | ConsequÃªncia prÃ¡tica |
| :--- | :--- | :--- |
| 1 | **Papel, nÃ£o tela.** | SuperfÃ­cies separadas por *hairlines* (1px), nÃ£o por sombras. CartÃµes quase nÃ£o existem; o que existe sÃ£o **seÃ§Ãµes de formulÃ¡rio** e **tabelas**. Sombra sÃ³ em camadas que flutuam (popover, modal). |
| 2 | **Tinta para agir, caneta para marcar.** | BotÃ£o primÃ¡rio Ã© grafite (`--color-ink`). O azul de acento Ã© reservado a foco, seleÃ§Ã£o, links e item ativo â€” nunca preenche Ã¡reas grandes (â‰¤ 3% da viewport). |
| 3 | **Cor Ã© diagnÃ³stico.** | Cor sÃ³ aparece quando carrega significado: nÃ­vel de risco, cadeia de frio, veÃ­culo no mapa. Nada Ã© colorido por decoraÃ§Ã£o. Todo significado cromÃ¡tico tem tambÃ©m um texto ou forma (WCAG 1.4.1). |
| 4 | **NÃºmero Ã© cidadÃ£o de primeira classe.** | Probabilidades, mÃ©tricas (F2, Recall, ROC-AUC), hiperparÃ¢metros, ETAs e coordenadas usam fonte mono com algarismos tabulares, alinhados Ã  direita. |
| 5 | **Incerteza declarada.** | Todo resultado de IA mostra o valor, a escala, a composiÃ§Ã£o das fontes (tabular/texto/imagem) e o aviso de apoio Ã  decisÃ£o. O design nunca faz uma estimativa parecer um diagnÃ³stico. |

### 1.2 ProibiÃ§Ãµes explÃ­citas deste kit

- Sem emojis em qualquer lugar da interface (incluindo status, toasts, empty states e chat).
- Sem glassmorphism: nada de `backdrop-filter: blur`, fundos translÃºcidos sobre conteÃºdo ou bordas "vidro".
- Sem gradientes de cor: nenhum `linear-gradient`/`radial-gradient` que misture duas cores ou dois tons. ExceÃ§Ã£o Ãºnica e controlada: **hachuras** (padrÃµes de listras com *hard stops* da mesma cor), usadas como textura de dados acessÃ­vel para daltÃ´nicos â€” ver Â§8.3.
- Sem brilho/glow, sem sombra colorida, sem texto com `background-clip: text`.
- Sem Ã­cone de "sparkle", cÃ©rebro, robÃ´ ou varinha mÃ¡gica para representar IA. A IA Ã© identificada por texto ("Estimativa do modelo", "Laudo gerado por IA").
- Sem cabeÃ§alhos em itÃ¡lico, sem palavra enfatizada em itÃ¡lico dentro de tÃ­tulo.
- Sem hero centralizado, sem grade de 3 cartÃµes iguais com Ã­cone em cima.
- Sem mÃ©tricas inventadas na copy. SÃ³ aparecem nÃºmeros produzidos pelo sistema.
- Sem moldura falsa de navegador/celular/terminal.

---

## 2. Cor

Todas as cores sÃ£o definidas em **OKLCH** (com HEX equivalente calculado para referÃªncia). Contrastes validados numericamente (WCAG 2.1). Neutros claros puxam levemente para o amarelo do papel de formulÃ¡rio (matiz 95); tintas e cinzas de texto puxam para o grafite azulado (matiz 250). Nenhum neutro tem croma zero.

### 2.1 Papel e tinta (modo claro â€” padrÃ£o)

| Token | OKLCH | HEX | Uso |
| :--- | :--- | :--- | :--- |
| `--color-surface` | `oklch(99% 0.004 95)` | `#FCFCF9` | Campos de formulÃ¡rio, tabelas, modais, Ã¡rea de leitura do laudo |
| `--color-paper` | `oklch(97.4% 0.006 95)` | `#F8F6F2` | Fundo da pÃ¡gina |
| `--color-paper-2` | `oklch(95% 0.008 95)` | `#F0EEE9` | Trilho de navegaÃ§Ã£o, cabeÃ§alho de tabela, linhas zebradas |
| `--color-paper-3` | `oklch(91.6% 0.010 95)` | `#E5E3DC` | Hover de linha, base de skeleton, trilho de barras |
| `--color-rule` | `oklch(86% 0.010 95)` | `#D3D1CA` | Hairlines de divisÃ£o (decorativas) |
| `--color-rule-strong` | `oklch(62% 0.012 95)` | `#88867E` | Borda de inputs, checkboxes e limites de componentes (3,4:1 â€” passa 1.4.11) |
| `--color-neutral` | `oklch(52.5% 0.012 250)` | `#656B71` | Placeholder, texto auxiliar, Ã­cones inativos (5,0:1) |
| `--color-muted` | `oklch(45% 0.014 250)` | `#50565D` | Labels, metadados, legendas (6,9:1) |
| `--color-ink-2` | `oklch(32% 0.016 250)` | `#2D343B` | Texto de corpo longo (11,7:1) |
| `--color-ink` | `oklch(21% 0.018 250)` | `#121920` | TÃ­tulos, texto principal, **botÃ£o primÃ¡rio** (16,4:1) |
| `--color-ink-hover` | `oklch(29% 0.020 250)` | `#242C35` | Hover do botÃ£o primÃ¡rio |

### 2.2 Acento â€” "caneta"

Um Ãºnico acento: o azul de caneta esferogrÃ¡fica usada em prontuÃ¡rios. NÃ£o Ã© o azul-roxo "AI" (matiz 262, croma moderado, sem violeta).

| Token | OKLCH | HEX | Uso |
| :--- | :--- | :--- | :--- |
| `--color-accent` | `oklch(47% 0.165 262)` | `#2253B5` | Links, item de navegaÃ§Ã£o ativo, foco, seleÃ§Ã£o, marcador da rÃ©gua de risco (6,6:1 no papel) |
| `--color-accent-hover` | `oklch(41% 0.150 262)` | `#17439A` | Hover de link |
| `--color-accent-soft` | `oklch(94% 0.025 262)` | `#E2ECFD` | Fundo de linha/opÃ§Ã£o selecionada (texto acento sobre ele: 5,9:1) |
| `--color-accent-ink` | `= --color-surface` | `#FCFCF9` | Texto sobre preenchimento de acento (6,9:1) |
| `--color-focus` | `= --color-accent` | `#2253B5` | Anel de foco (2px, offset 2px) |

### 2.3 SemÃ¢ntica clÃ­nica (risco) e logÃ­stica (cadeia de frio)

Paleta derivada de esquemas seguros para daltÃ´nicos (vermelho-Ã³xido, ocre, pinho, ciano-gelo), sempre acompanhada de rÃ³tulo textual e/ou forma.

| Significado | Token texto/Ã­cone | HEX | Token fundo suave | HEX | Contraste texto/fundo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Risco alto** / erro / destrutivo | `--color-risk-high` `oklch(50% 0.165 28)` | `#AE2E27` | `--color-risk-high-soft` `oklch(94.5% 0.025 28)` | `#FDE7E4` | 5,5:1 |
| **Risco moderado** / atenÃ§Ã£o | `--color-risk-mid` `oklch(50.5% 0.105 70)` | `#8A580C` | `--color-risk-mid-soft` `oklch(95% 0.035 85)` | `#F9EDD5` | 5,2:1 |
| Preenchimento ocre (barras, faixa da rÃ©gua) | `--color-risk-mid-fill` `oklch(76% 0.135 78)` | `#E0A53E` | â€” | â€” | tinta sobre ele 8,1:1 |
| **Risco baixo** / sucesso | `--color-risk-low` `oklch(50% 0.095 155)` | `#2E734B` | `--color-risk-low-soft` `oklch(95% 0.025 155)` | `#E2F4E7` | 5,0:1 |
| **Cadeia de frio 2â€“8 Â°C** (termolÃ¡bil) | `--color-cold` `oklch(52% 0.095 220)` | `#00758F` | `--color-cold-soft` `oklch(95% 0.022 220)` | `#DFF2F9` | 4,6:1 |

Aliases funcionais: `--color-danger = --color-risk-high`, `--color-warning = --color-risk-mid`, `--color-success = --color-risk-low`, `--color-info = --color-accent`.

**Regra de redundÃ¢ncia:** risco alto usa tambÃ©m o rÃ³tulo "Alto" + Ã­cone `triangle-alert`; moderado, "Moderado" + `circle-alert`; baixo, "Baixo" + `circle-check`; cadeia de frio, a etiqueta mono `2â€“8 Â°C` + Ã­cone `thermometer-snowflake` + borda tracejada.

### 2.4 Paleta categÃ³rica de veÃ­culos (mapa e grÃ¡ficos)

Para distinguir rotas de atÃ© 6 veÃ­culos no mapa. Todas â‰¥ 5:1 sobre o papel (linhas de 4px). Escolhidas para nÃ£o colidir com os tons semÃ¢nticos de risco.

| Token | HEX | Nome |
| :--- | :--- | :--- |
| `--color-route-1` | `#332288` | Ãndigo |
| `--color-route-2` | `#117733` | Verde-musgo |
| `--color-route-3` | `#882255` | Vinho |
| `--color-route-4` | `#6B6B19` | Oliva |
| `--color-route-5` | `#1F6E8C` | PetrÃ³leo |
| `--color-route-6` | `#AA3377` | Rosa-escuro |

Cada veÃ­culo tambÃ©m recebe um **padrÃ£o de traÃ§o** (contÃ­nuo, tracejado 8-4, pontilhado 2-4, traÃ§o-pontoâ€¦) para leitura em impressÃ£o P&B e por daltÃ´nicos.

### 2.5 Modo escuro (opcional â€” painel de operaÃ§Ã£o / sala de despacho)

Mesmo matiz, sÃ³ luminÃ¢ncia e croma mudam. SuperfÃ­cies mais altas sÃ£o mais claras.

| Token | OKLCH | HEX |
| :--- | :--- | :--- |
| `--color-paper` | `oklch(17% 0.012 250)` | `#0B1015` |
| `--color-paper-2` | `oklch(21% 0.014 250)` | `#13191F` |
| `--color-surface` / `--color-paper-3` | `oklch(25% 0.015 250)` | `#1C2229` |
| `--color-rule` | `oklch(33% 0.014 250)` | `#30363C` |
| `--color-muted` | `oklch(72% 0.012 250)` | `#9FA5AC` (7,7:1) |
| `--color-ink` | `oklch(94% 0.008 95)` | `#EDEBE5` (16:1) |
| `--color-accent` | `oklch(70% 0.130 262)` | `#719DEF` (7,1:1) |
| `--color-risk-high` / `-mid` / `-low` / `--color-cold` | `oklch(68% .150 28)` / `oklch(78% .130 78)` / `oklch(72% .110 155)` / `oklch(74% .100 220)` | `#E66F62` / `#E5AC4C` / `#68B986` / `#58BAD6` |

No escuro, o peso do corpo cai de 400 para 380 (fonte variÃ¡vel) para compensar a irradiaÃ§Ã£o.

---

## 3. Tipografia

TrÃªs famÃ­lias, cada uma com um papel inegociÃ¡vel. Todas open source (Google Fonts), com eixos variÃ¡veis.

| Papel | FamÃ­lia | Por quÃª | Token |
| :--- | :--- | :--- | :--- |
| **TÃ­tulos e leitura de laudo** | **Source Serif 4** (opsz variÃ¡vel) | Serifa de texto sÃ³bria, de tradiÃ§Ã£o editorial/cientÃ­fica. DÃ¡ autoridade de documento aos tÃ­tulos e ao laudo explicativo sem soar "luxo". | `--font-display` |
| **Interface e corpo** | **Public Sans** | Grotesca institucional (origem governamental), neutra, legÃ­vel em tamanhos pequenos, sem a cara de "startup". | `--font-body` |
| **Dados e nÃºmeros** | **IBM Plex Mono** | Algarismos tabulares claros, distinÃ§Ã£o 0/O e 1/l, bom em tabelas de mÃ©tricas, IDs, coordenadas, ETAs. | `--font-mono` |

Fallbacks: `'Source Serif 4', 'Iowan Old Style', Georgia, serif` Â· `'Public Sans', 'Segoe UI', system-ui, sans-serif` Â· `'IBM Plex Mono', ui-monospace, 'Cascadia Mono', monospace`.

### 3.1 Escala (razÃ£o 1,25 â€” terÃ§a maior)

| Token | rem / px | FamÃ­lia | Peso | Line-height | Tracking | Uso |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `--text-display` | `clamp(2.25rem, 1.6rem + 2vw, 2.566rem)` / 36â€“41 | display | 600 | 1.08 | -0.015em | TÃ­tulo de pÃ¡gina (uma vez por tela) |
| `--text-3xl` | 2.063rem / 33 | display | 600 | 1.12 | -0.012em | Valor herÃ³i do resultado (ex.: risco estimado) â€” sempre ao lado de texto |
| `--text-2xl` | 1.625rem / 26 | display | 600 | 1.2 | -0.01em | TÃ­tulo de seÃ§Ã£o |
| `--text-xl` | 1.313rem / 21 | display | 600 | 1.3 | -0.005em | TÃ­tulo de bloco, tÃ­tulo de modal |
| `--text-lg` | 1.125rem / 18 | body / display (laudo) | 400 | 1.6 | 0 | Corpo do laudo (serifa), lede |
| `--text-md` | 1rem / 16 | body | 400 | 1.5 | 0 | Corpo padrÃ£o, inputs, botÃµes |
| `--text-sm` | 0.875rem / 14 | body | 400/500 | 1.45 | 0.005em | Tabelas, texto auxiliar, helper |
| `--text-xs` | 0.8125rem / 13 | mono | 500 | 1.4 | 0 | MÃ©tricas inline, IDs, timestamps |
| `--text-label` | 0.75rem / 12 | body | 600 | 1.3 | 0.06em, **CAIXA ALTA** | RÃ³tulos de seÃ§Ã£o de formulÃ¡rio, cabeÃ§alhos de tabela |

### 3.2 Regras

- TÃ­tulos sempre romanos (sem itÃ¡lico). ÃŠnfase em tÃ­tulo = peso 700 ou cor `--color-accent`, nunca itÃ¡lico.
- ItÃ¡lico sÃ³ dentro de parÃ¡grafos de corpo (ex.: nomes cientÃ­ficos em um laudo).
- NÃºmeros em tabelas e mÃ©tricas: `font-family: var(--font-mono); font-variant-numeric: tabular-nums;` alinhados Ã  direita.
- Percentuais com vÃ­rgula decimal pt-BR e espaÃ§o fino antes de `%` quando em destaque: `96,66 %`.
- Medida de leitura: corpo 60â€“72ch; laudo `max-width: 68ch`.
- TÃ­tulos com `text-wrap: balance`; parÃ¡grafos com `text-wrap: pretty`; `overflow-wrap: anywhere; min-width: 0` em tÃ­tulos.
- MÃ¡ximo de 3 famÃ­lias por tela (as trÃªs acima). Nada de quarta fonte para "destaque".

---

## 4. EspaÃ§amento, grid e densidade

### 4.1 Escala de espaÃ§o (base 4px)

| Token | px | Uso tÃ­pico |
| :--- | :--- | :--- |
| `--space-3xs` | 2 | Ajuste Ã³ptico (Ã­cone/texto em badge) |
| `--space-2xs` | 4 | Gap Ã­coneâ€“texto, padding vertical de badge |
| `--space-xs` | 8 | Gap entre label e input, gap em grupos de chips |
| `--space-sm` | 12 | Padding horizontal de badge e de cÃ©lula compacta |
| `--space-md` | 16 | Padding de cÃ©lula de tabela, gap entre campos na mesma linha |
| `--space-lg` | 24 | Padding de seÃ§Ã£o de formulÃ¡rio, gap entre campos empilhados |
| `--space-xl` | 32 | DistÃ¢ncia entre blocos dentro de uma seÃ§Ã£o |
| `--space-2xl` | 48 | DistÃ¢ncia entre seÃ§Ãµes da pÃ¡gina |
| `--space-3xl` | 64 | Margem superior de pÃ¡gina / respiro antes do rodapÃ© |
| `--space-4xl` | 96 | Respiro de telas de entrada (login, inÃ­cio da triagem) |

Nenhum padding/gap/margin fora desta escala.

### 4.2 Ritmo vertical (gaps padrÃ£o)

| RelaÃ§Ã£o | Gap |
| :--- | :--- |
| Label â†’ campo | `--space-xs` (8) |
| Campo â†’ helper/erro | `--space-2xs` (4) â€” slot com `min-height: 1lh` reservado |
| Campo â†’ campo (empilhado) | `--space-lg` (24) |
| Campos lado a lado | `--space-md` (16) |
| TÃ­tulo de seÃ§Ã£o â†’ conteÃºdo | `--space-md` (16) + hairline |
| SeÃ§Ã£o â†’ seÃ§Ã£o | `--space-2xl` (48) |
| BotÃµes em grupo | `--space-xs` (8) |

### 4.3 Grid e containers

| Token | Valor | Uso |
| :--- | :--- | :--- |
| `--container-read` | 720px | Laudo, login, telas de leitura |
| `--container-form` | 960px | Anamnese (formulÃ¡rio + resumo lateral) |
| `--container-wide` | 1360px | Painel de modelos, rotas |
| `--rail-width` | 232px (colapsa para 64px) | Trilho de navegaÃ§Ã£o lateral |
| `--gutter` | `clamp(16px, 2.5vw, 32px)` | Margem lateral da pÃ¡gina |

Grid de 12 colunas com `grid-template-columns: repeat(12, minmax(0, 1fr))` e gap `--space-lg`. Layouts recomendados:

- **Anamnese:** formulÃ¡rio 8 colunas + resumo fixo da triagem 4 colunas (o resumo vira acordeÃ£o no mobile).
- **Resultado:** coluna de leitura 7 + coluna de evidÃªncias (composiÃ§Ã£o, mÃ©tricas do modelo) 5.
- **Rotas:** mapa ocupa a Ã¡rea principal; painel de paradas 400px Ã  direita (desktop) ou *bottom sheet* (mobile).
- **Modelos (admin):** tabela comparativa de largura total; detalhe em painel lateral (drawer), nÃ£o em modal sobre modal.

### 4.4 Breakpoints

| Token | Largura | Comportamento |
| :--- | :--- | :--- |
| `--bp-sm` | 480px | Campos lado a lado viram empilhados |
| `--bp-md` | 768px | Trilho vira barra inferior de 4 itens; painÃ©is laterais viram bottom sheet |
| `--bp-lg` | 1024px | Trilho colapsado (64px, sÃ³ Ã­cones + tooltip) |
| `--bp-xl` | 1280px | Trilho expandido; layouts de 2 colunas |

VerificaÃ§Ã£o obrigatÃ³ria em 320 / 375 / 414 / 768 px. `overflow-x: clip` em `html` e `body`.

### 4.5 Densidade

Dois modos via atributo `data-density` no container:

| | `comfortable` (padrÃ£o â€” triagem, laudo) | `compact` (tabelas admin, lista de paradas) |
| :--- | :--- | :--- |
| Altura de controle | 44px | 36px (sÃ³ dentro de tabelas/toolbars) |
| Altura de linha de tabela | 48px | 36px |
| Padding de cÃ©lula | 12px 16px | 8px 12px |
| Tamanho de texto em tabela | `--text-sm` | `--text-sm` |

Inputs de formulÃ¡rio nunca descem de 44px.

---

## 5. Forma: bordas, raios, elevaÃ§Ã£o & sombras

### 5.1 Raios â€” pequenos e hierÃ¡rquicos

Documento clÃ­nico tem cantos quase retos. Arredondamento grande Ã© expressamente proibido.

| Token | Valor | Uso |
| :--- | :--- | :--- |
| `--radius-xs` | 2px | Badges, etiquetas, cÃ©lulas da matriz de confusÃ£o |
| `--radius-sm` | 4px | BotÃµes, inputs, selects, checkboxes |
| `--radius-md` | 6px | PainÃ©is, drawer, modal, popover, dropzone |
| `--radius-round` | 999px | **SÃ³** pontos de status (6â€“8px) e marcador de mapa |

### 5.2 Bordas

| Token | Valor | Finalidade |
| :--- | :--- | :--- |
| `--border-hairline` | `1px solid var(--color-rule)` | DivisÃµes estruturais entre blocos e seÃ§Ãµes |
| `--border-control` | `1px solid var(--color-rule-strong)` | Borda padrÃ£o de inputs, selects e botÃµes secundÃ¡rios |
| `--border-strong` | `1px solid var(--color-ink)` | SeÃ§Ã£o ativa, botÃ£o secundÃ¡rio em hover |
| `--border-cold` | `1px dashed var(--color-cold)` | Itens termolÃ¡beis e cadeia de frio (2 a 8 Â°C) |

Largura de borda nunca muda entre estados (sem *layout shift*). Estados mudam cor de borda, fundo ou `outline`.

### 5.3 PadronizaÃ§Ã£o de Sombras (ElevaÃ§Ã£o FÃ­sica Funcional)

O kit "ProntuÃ¡rio" rejeita qualquer sombra difusa artificial, "glow" colorido ou borrÃµes de IA. As sombras seguem um modelo fÃ­sico de **dupla camada de projeÃ§Ã£o** (luz direta de foco + luz ambiente difusa), renderizadas exclusivamente na tinta grafite `--color-ink` com opacidade atenuada.

No papel (`--shadow-0`), os elementos sÃ£o delimitados por bordas hairline, e nÃ£o por sombras. Sombras sÃ³ surgem quando um elemento fisicamente flutua ou se sobrepÃµe ao plano do documento.

| Token | Camada 1: Luz Focal (Key Light) | Camada 2: Luz Ambiente (Ambient) | ElevaÃ§Ã£o | Uso Recomendado |
| :--- | :--- | :--- | :---: | :--- |
| `--shadow-0` | `none` | `none` | 0dp | Tudo que estÃ¡ no plano do papel (cards, tabelas, seÃ§Ãµes de formulÃ¡rio) |
| `--shadow-1` | `0 1px 2px oklch(21% 0.018 250 / 0.08)` | `0 2px 4px oklch(21% 0.018 250 / 0.04)` | 2dp | Tooltips, chips com aÃ§Ã£o, botÃµes ativos, toasts no rodapÃ© |
| `--shadow-2` | `0 2px 4px oklch(21% 0.018 250 / 0.08)` | `0 6px 16px oklch(21% 0.018 250 / 0.06)` | 4dp | Menus suspensos, dropdowns abertos, popovers de ajuda |
| `--shadow-3` | `0 4px 8px oklch(21% 0.018 250 / 0.08)` | `0 16px 36px oklch(21% 0.018 250 / 0.12)` | 8dp | Caixas de diÃ¡logo modais centralizadas, alertas de confirmaÃ§Ã£o |
| `--shadow-4` | `0 8px 16px oklch(21% 0.018 250 / 0.08)` | `0 24px 48px oklch(21% 0.018 250 / 0.14)` | 16dp | PainÃ©is laterais deslizantes (Drawers de detalhes de modelo) |
| `--shadow-drawer-left` | `-4px 0 16px oklch(21% 0.018 250 / 0.10)` | `-12px 0 32px oklch(21% 0.018 250 / 0.08)` | 16dp | ProjeÃ§Ã£o lateral esquerda para drawers ancorados Ã  direita |

```css
/* DefiniÃ§Ã£o canÃ´nica em :root */
--shadow-0: none;
--shadow-1: 0 1px 2px oklch(21% 0.018 250 / 0.08), 0 2px 4px oklch(21% 0.018 250 / 0.04);
--shadow-2: 0 2px 4px oklch(21% 0.018 250 / 0.08), 0 6px 16px oklch(21% 0.018 250 / 0.06);
--shadow-3: 0 4px 8px oklch(21% 0.018 250 / 0.08), 0 16px 36px oklch(21% 0.018 250 / 0.12);
--shadow-4: 0 8px 16px oklch(21% 0.018 250 / 0.08), 0 24px 48px oklch(21% 0.018 250 / 0.14);
--shadow-drawer-left: -4px 0 16px oklch(21% 0.018 250 / 0.10), -12px 0 32px oklch(21% 0.018 250 / 0.08);
```

#### Regras de Sombra no Modo Escuro (Dark Mode)
- No modo escuro, a fÃ­sica de elevaÃ§Ã£o inverte a prioridade: superfÃ­cies mais altas ficam **mais claras** (`--color-surface` passa de `oklch(17% ...)` para `oklch(25% ...)`).
- A sombra no dark mode atua como silhueta de recorte:
  `--shadow-3-dark: 0 4px 12px oklch(0% 0 0 / 0.40), 0 16px 40px oklch(0% 0 0 / 0.35);`

Overlay de modal: `oklch(21% 0.018 250 / 0.48)` sÃ³lido â€” **sem blur (proibido backdrop-filter)**.

### 5.4 Z-Index (Hierarquia de Camadas)

`--z-base: 0` &middot; `--z-sticky: 200` &middot; `--z-nav: 300` &middot; `--z-map-controls: 400` &middot; `--z-drawer: 500` &middot; `--z-modal: 600` &middot; `--z-toast: 700` &middot; `--z-tooltip: 800`.

---

## 6. Movimento & AnimaÃ§Ãµes (Coreografia MecÃ¢nica)

O movimento no sistema tem propÃ³sito cognitivo estrito: orientar o olhar do mÃ©dico ou operador logÃ­stico, indicar causalidade de aÃ§Ãµes e confirmar integridade de processamento. AnimaÃ§Ãµes puramente decorativas (loops infinitos, bounces ou pulos de escala) sÃ£o proibidas.

### 6.1 Os Quatro PrincÃ­pios MecÃ¢nicos

1. **AceleraÃ§Ã£o Desacelerada:** Elementos que entram no campo visual desaceleram atÃ© o repouso (`--ease-out`). Elementos que saem aceleram para fora da tela (`--ease-in`) em 75% do tempo de entrada.
2. **GPU Compositing Estrito:** Apenas as propriedades `transform` e `opacity` sÃ£o animadas. Jamais anime `height`, `width`, `top`, `left`, `margin` ou `padding` (evita *reflow* e quedas de FPS em telas complexas com mapa).
3. **Foco InstantÃ¢neo:** AnÃ©is de foco de acessibilidade via teclado (`:focus-visible`) aparecem com duraÃ§Ã£o de **0ms** (imediatismo de controle).
4. **Respeito a PreferÃªncias de Acessibilidade:** Em `@media (prefers-reduced-motion: reduce)`, todas as transiÃ§Ãµes espaciais colapsam imediatamente para `1ms`.

### 6.2 Escala de DuraÃ§Ãµes Padronizadas

| Token | DuraÃ§Ã£o | Natureza | AplicaÃ§Ã£o ObrigatÃ³ria |
| :--- | :---: | :--- | :--- |
| `--dur-instant` | `0ms` | InstantÃ¢neo | AnÃ©is de foco teclado (`:focus-visible`), tooltips por foco |
| `--dur-micro` | `120ms` | Micro-interaÃ§Ã£o | Pressionamento de botÃ£o (`:active`), tick de checkbox, shift de cor |
| `--dur-short` | `200ms` | TransiÃ§Ã£o rÃ¡pida | Abertura de menus, troca de abas, tooltips por hover, hover de botÃ£o |
| `--dur-medium` | `280ms` | TransiÃ§Ã£o mecÃ¢nica | AcordeÃµes, transiÃ§Ã£o entre passos da anamnese, expansÃ£o de tabela |
| `--dur-long` | `360ms` | TransiÃ§Ã£o estrutural | Abertura de modais, entrada de drawer lateral, bottom sheet mobile |
| `--dur-reveal` | `640ms` | Momento-assinatura | Deslizamento da rÃ©gua de risco, traÃ§ado da rota OSRM no mapa |

### 6.3 Curvas de AceleraÃ§Ã£o (Easings Curados)

```css
:root {
  /* Entradas naturais: desaceleraÃ§Ã£o progressiva */
  --ease-out:    cubic-bezier(0.16, 1, 0.3, 1);
  
  /* SaÃ­das de tela: aceleraÃ§Ã£o de escape */
  --ease-in:     cubic-bezier(0.7, 0, 0.84, 0);
  
  /* AlternÃ¢ncias de estado contÃ­nuo (acordeÃµes, tabs) */
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  
  /* SensaÃ§Ã£o mecÃ¢nica de clique/encaixe documental */
  --ease-snap:   cubic-bezier(0.2, 0.8, 0.2, 1);
}
```

### 6.4 Receitas Padronizadas de TransiÃ§Ã£o (Code Recipes)

#### Receita 1: Pressionamento de BotÃ£o (`:active`)
```css
.btn {
  transition: background-color var(--dur-micro) var(--ease-out),
              border-color var(--dur-micro) var(--ease-out),
              transform var(--dur-micro) var(--ease-snap);
}
.btn:active:not(:disabled) {
  transform: translateY(1px);
}
```

#### Receita 2: Entrada e SaÃ­da de Modal
```css
/* Overlay escuro */
.modal-backdrop {
  opacity: 0;
  transition: opacity var(--dur-long) var(--ease-out);
}
.modal-backdrop.is-open {
  opacity: 1;
}

/* Caixa de diÃ¡logo */
.modal-dialog {
  opacity: 0;
  transform: scale(0.98) translateY(8px);
  transition: opacity var(--dur-long) var(--ease-out),
              transform var(--dur-long) var(--ease-out);
}
.modal-dialog.is-open {
  opacity: 1;
  transform: scale(1) translateY(0);
}
```

#### Receita 3: Painel Lateral Deslizante (Drawer)
```css
.drawer-panel {
  transform: translateX(100%);
  transition: transform var(--dur-long) var(--ease-out);
  box-shadow: var(--shadow-drawer-left);
}
.drawer-panel.is-open {
  transform: translateX(0);
}
```

#### Receita 4: TransiÃ§Ã£o de Passos da Anamnese (Stepper)
```css
/* Passo que sai */
.step-slide-exit {
  opacity: 0;
  transform: translateX(-16px);
  transition: opacity 150ms var(--ease-in),
              transform 150ms var(--ease-in);
}
/* Passo que entra */
.step-slide-enter {
  opacity: 1;
  transform: translateX(0);
  transition: opacity var(--dur-medium) var(--ease-out),
              transform var(--dur-medium) var(--ease-out);
}
```

#### Receita 5: AcordeÃ£o sem Animar Altura Direta
```css
/* Utiliza grid-template-rows para evitar reflows de height */
.accordion-wrapper {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows var(--dur-medium) var(--ease-in-out);
}
.accordion-wrapper.is-expanded {
  grid-template-rows: 1fr;
}
.accordion-content {
  overflow: hidden;
}
```

#### Receita 6: Skeleton Loader (Sem Shimmer em Gradiente)
```css
@keyframes pulse-block {
  0%, 100% { opacity: 0.85; }
  50% { opacity: 0.45; }
}
.skeleton-box {
  background-color: var(--color-paper-3);
  border-radius: var(--radius-xs);
  animation: pulse-block 1.4s infinite ease-in-out;
}
```

### 6.5 Momentos-Assinatura (Os Ãšnicos Movimentos Expressivos de 640ms)

1. **RÃ©gua de Risco:** Ao exibir o resultado da triagem, o marcador em triÃ¢ngulo preto desliza da posiÃ§Ã£o 0 atÃ© o percentual exato (`transform: translateX(calc(N% - 50%))`) com `--dur-reveal` e `--ease-out`. O nÃºmero textual ao lado surge jÃ¡ com o valor exato (sem contadores saltitantes).
2. **TraÃ§ado de Rota ViÃ¡ria (OSRM):** A linha de cada van Ã© renderizada no Leaflet animando `stroke-dashoffset` em `--dur-reveal`. Os marcadores de parada aparecem via opacidade logo apÃ³s o tÃ©rmino do traÃ§o.
3. **Curva de ConvergÃªncia do AG:** No painel de modelos, a linha de melhor $F_2$-Score Ã© desenhada progressivamente na primeira abertura do drawer de auditoria.

### 6.6 Diretriz de Movimento Reduzido (Acessibilidade)

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 1ms !important;
  }
  .skeleton-box { animation: none; opacity: 0.7; }
  .meter-marker { transition: none !important; }
}
```

---

## 7. Iconografia e imagem

- **Biblioteca Ãºnica:** Lucide, traÃ§o `1.5px`, tamanhos 16 (inline/tabela), 20 (controles), 24 (navegaÃ§Ã£o). `stroke: currentColor`.
- Ãcone nunca sozinho como Ãºnica informaÃ§Ã£o (exceto botÃµes de Ã­cone com `aria-label` + tooltip).
- Ãcones de domÃ­nio sugeridos: `clipboard-list` (triagem), `file-text` (laudo), `route` (rotas), `truck` (veÃ­culo), `thermometer-snowflake` (cadeia de frio), `flask-conical` (modelos), `git-branch` (experimentos do AG), `scan` (mamografia), `table` (dados tabulares), `message-square-text` (relato livre).
- **Imagens reais apenas:** miniaturas de mamografia exibidas em escala de cinza original, com borda `--border-hairline`, fundo `--color-ink` (padrÃ£o de visualizador radiolÃ³gico). Nada de ilustraÃ§Ã£o 3D, avatar genÃ©rico ou foto de banco de imagens.
- **Mapa:** tiles OpenStreetMap com `filter: grayscale(0.9) contrast(0.95)` para que sÃ³ as rotas e marcadores tenham cor.

---

## 8. Componentes

Todos os componentes interativos implementam os **8 estados**: default, hover, focus-visible, active, disabled, loading, error, success. Desabilitado sempre em trÃªs canais: `opacity: 0.55` + `cursor: not-allowed` + atributo `disabled`/`aria-disabled`.

### 8.1 Controles base

**BotÃ£o** â€” altura 44px (36px no modo compacto), padding `0 var(--space-lg)`, `--radius-sm`, `--text-md` peso 600, `white-space: nowrap`.

| Variante | Default | Hover | Active | Focus-visible | Loading | Error | Success |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PrimÃ¡rio** (tinta) | fundo `--color-ink`, texto `--color-surface` | fundo `--color-ink-hover` | `translateY(1px)` | `outline: 2px solid var(--color-focus); outline-offset: 2px` | texto mantÃ©m largura, troca por "Analisandoâ€¦" + barra indeterminada de 2px na base; `aria-busy` | borda e texto `--color-risk-high` por 2s com mensagem inline | rÃ³tulo vira "ConcluÃ­do" + Ã­cone `check` por 1,6s (sÃ³ se o efeito nÃ£o for visÃ­vel na tela) |
| **SecundÃ¡rio** | fundo `--color-surface`, `--border-control`, texto `--color-ink` | borda `--color-ink` | fundo `--color-paper-2` | idem | idem | idem | idem |
| **Fantasma** | transparente, texto `--color-ink` | fundo `--color-paper-2` | fundo `--color-paper-3` | idem | idem | â€” | â€” |
| **Destrutivo** | fundo `--color-surface`, borda e texto `--color-risk-high` | fundo `--color-risk-high-soft` | `translateY(1px)` | idem | idem | â€” | â€” |
| **Link** | texto `--color-accent`, sublinhado 1px offset 3px | `--color-accent-hover`, sublinhado 2px | â€” | idem | â€” | â€” | â€” |

BotÃ£o de aÃ§Ã£o principal por tela: **um**. O acento azul nÃ£o preenche botÃµes.

**Input / Select / Textarea** â€” altura 44px, padding `0 var(--space-sm)`, fundo `--color-surface`, `--border-control`, `--radius-sm`, texto `--text-md`. Label acima (`--text-sm` 600 `--color-ink`), helper abaixo (`--text-sm` `--color-muted`).

| Estado | Tratamento |
| :--- | :--- |
| Hover | borda `--color-ink-2` |
| Focus-visible | borda `--color-accent` + `outline: 2px solid var(--color-focus); outline-offset: 1px` (outline transparente reservado em repouso) |
| Disabled | fundo `--color-paper-2`, texto `--color-neutral`, 3 canais |
| Read-only | sem borda, fundo `--color-paper-2`, valor em mono quando numÃ©rico |
| Error | borda `--color-risk-high`, Ã­cone `circle-alert` Ã  direita, mensagem no slot de helper em `--color-risk-high` dizendo **como corrigir** ("Informe um valor entre 0 e 50 mm") |
| Success | borda `--color-risk-low` sÃ³ apÃ³s validaÃ§Ã£o assÃ­ncrona (ex.: endereÃ§o geocodificado) |
| Loading | Ã­cone de progresso de 16px Ã  direita (ex.: busca de endereÃ§o), campo continua editÃ¡vel |

Campos numÃ©ricos clÃ­nicos mostram a **unidade como sufixo fixo** dentro do campo (`mm`, `kg/mÂ²`, `mIU/mL`) em `--color-muted` mono.

**Textarea de relato livre:** contador de caracteres em mono no canto inferior direito (`412 / 2000`), muda para `--color-risk-mid` a 90% e bloqueia no limite. Microcopy fixa abaixo: "Descreva sintomas com suas palavras. O texto Ã© analisado como dado, nÃ£o como instruÃ§Ã£o."

**Checkbox / Radio / Toggle** (variÃ¡veis booleanas do SOP) â€” caixa 18px, `--radius-xs` (checkbox) / cÃ­rculo (radio), borda `--color-rule-strong`; marcado = fundo `--color-ink` com check `--color-surface`. Ãrea clicÃ¡vel mÃ­nima 44Ã—44 incluindo o label. Para pares Sim/NÃ£o use **controle segmentado** de dois botÃµes (mais rÃ¡pido de ler que um toggle), segmento ativo com fundo `--color-ink`.

**Dropzone de mamografia** â€” Ã¡rea `--radius-md`, borda `1px dashed var(--color-rule-strong)`, fundo `--color-surface`. Hover/drag-over: borda `--color-accent` sÃ³lida + fundo `--color-accent-soft`. ApÃ³s upload: miniatura sobre fundo `--color-ink`, nome do arquivo em mono, tamanho, botÃ£o "Remover". Erro de formato: mensagem inline com formatos aceitos.

### 8.2 NavegaÃ§Ã£o e estrutura

**Trilho lateral (app shell)** â€” fundo `--color-paper-2`, hairline Ã  direita. Topo: logotipo tipogrÃ¡fico "HealthAI" em `--font-display` 600. Grupos rotulados em `--text-label`: *Atendimento* (Triagem, Laudos), *LogÃ­stica* (Rotas), *AdministraÃ§Ã£o* (Modelos, Experimentos). Item ativo: barra vertical de 2px `--color-accent` Ã  esquerda + texto `--color-ink` 600; inativo `--color-muted`. No mobile: barra inferior com 4 destinos (Ã­cone + rÃ³tulo curto, nunca quebra linha).

**CabeÃ§alho de pÃ¡gina** â€” tÃ­tulo `--text-display` alinhado Ã  esquerda; abaixo, uma linha de metadados em `--text-sm` `--color-muted` (ex.: "Triagem Â· CÃ¢ncer de mama Â· passo 2 de 4"). AÃ§Ãµes da pÃ¡gina alinhadas Ã  direita na mesma linha do tÃ­tulo no desktop, abaixo no mobile. Hairline inferior.

**Stepper da anamnese ("folha")** â€” lista horizontal numerada `01 IdentificaÃ§Ã£o Â· 02 Foco Â· 03 Dados Â· 04 Resultado`. NÃºmero em mono. ConcluÃ­do: nÃºmero `--color-ink` + Ã­cone `check` 16px; atual: texto `--color-ink` 600 + sublinhado 2px `--color-accent`; futuro: `--color-neutral`. No mobile: "Passo 2 de 4 â€” Foco da triagem" + barra de progresso segmentada (4 segmentos sÃ³lidos).

**Abas** â€” texto `--text-sm` 600, sublinhado 2px `--color-accent` na ativa, hairline de base. Usadas em Rotas (Mapa Â· Roteiro do motorista Â· RelatÃ³rio Â· Assistente).

**SeÃ§Ã£o de formulÃ¡rio** â€” sem cartÃ£o. RÃ³tulo de seÃ§Ã£o em `--text-label` `--color-muted`, hairline, campos abaixo. SeÃ§Ãµes sucessivas separadas por `--space-2xl`.

### 8.3 Componentes de domÃ­nio (assinatura do kit)

**RÃ©gua de risco** (resultado da triagem)
- Escala horizontal 0â€“100 com marcas a cada 10 (traÃ§os de 1px `--color-rule-strong`, rÃ³tulos mono `--text-xs` a cada 25).
- TrÃªs faixas sÃ³lidas de 6px de altura: 0â€“39 `--color-risk-low`, 40â€“69 `--color-risk-mid-fill`, 70â€“100 `--color-risk-high` (limiares de referÃªncia â€” confirmar com a regra de negÃ³cio do ensemble).
- Marcador: triÃ¢ngulo `--color-ink` + linha vertical `--color-accent` sobre a escala.
- Ao lado: valor herÃ³i `--text-3xl` em display + rÃ³tulo textual ("Risco estimado: Alto") + badge semÃ¢ntico.
- Abaixo, obrigatÃ³rio: "Estimativa de apoio Ã  decisÃ£o. NÃ£o substitui avaliaÃ§Ã£o mÃ©dica." em `--text-sm` `--color-muted`.

**Faixa de composiÃ§Ã£o das fontes** (tabular / texto / imagem â€” 50/25/25 redistribuÃ­dos)
- Barra horizontal de 12px dividida em segmentos sÃ³lidos com separaÃ§Ã£o de 2px `--color-surface`.
- Para nÃ£o depender de cor, cada modalidade tem textura prÃ³pria em tons de tinta: **Tabular** = sÃ³lido `--color-ink-2`; **Texto** = hachura 45Â° `--color-ink-2` sobre `--color-paper-3`; **Imagem** = pontilhado `--color-ink-2` sobre `--color-paper-3`. Hachuras sÃ£o *hard-stop* da mesma cor (ou SVG `<pattern>`), nunca transiÃ§Ã£o de cor.
- Legenda abaixo: nome da modalidade, peso efetivo e confianÃ§a individual em mono (`Tabular Â· 66,7 % Â· conf. 0,91`). Modalidade ausente aparece riscada em `--color-neutral` com "nÃ£o informado".

**Laudo explicativo** â€” coluna de leitura `--container-read`, fundo `--color-surface`, hairline superior grossa (2px `--color-ink`) como cabeÃ§alho de documento. CabeÃ§alho: "Laudo gerado por IA" em `--text-label` + modelo e provedor usados (ex.: provedor em fallback) em mono `--text-xs`. SeÃ§Ãµes fixas na ordem do schema: SÃ­ntese Â· Fatores de risco Â· Justificativa Â· Condutas recomendadas Â· Aviso. Corpo em `--font-display` `--text-lg`. Fatores de risco como lista numerada com valor do biomarcador em mono Ã  direita. O aviso Ã©tico fica em bloco prÃ³prio com hairline superior e texto `--color-muted` (borda lateral colorida Ã© padrÃ£o proibido).

**Tabela de modelos (admin)** â€” colunas: Modelo Â· Objetivo Â· F2 Â· Recall Â· AcurÃ¡cia Â· ROC-AUC Â· Origem (GridSearch / AG) Â· Status. NÃºmeros mono alinhados Ã  direita; melhor valor de cada coluna em peso 700 (nÃ£o em cor). Modelo ativo: badge "Em produÃ§Ã£o" (`--color-ink` texto, borda `--color-ink`). Linha clicÃ¡vel abre drawer com detalhe. OrdenaÃ§Ã£o por cabeÃ§alho com Ã­cone `arrow-up-down`.

**Matriz de confusÃ£o** â€” grade 2Ã—2 de cÃ©lulas quadradas, `--radius-xs`. Intensidade em **5 passos discretos** de `--color-accent` sobre `--color-surface` (tokens `--color-seq-1`â€¦`--color-seq-5`, ver Â§9), nunca escala contÃ­nua. Valor absoluto em mono no centro + percentual pequeno abaixo. RÃ³tulos "Real" / "Previsto" nos eixos. CÃ©lula de falso negativo recebe contorno 1px `--color-risk-high` e legenda "Falso negativo â€” erro clÃ­nico mais grave".

**GrÃ¡fico de convergÃªncia do AG** â€” linhas: melhor F2 (`--color-ink`, 2px), mÃ©dia da populaÃ§Ã£o (`--color-neutral`, 1,5px tracejado 4-3), diversidade (`--color-accent`, 1,5px, eixo secundÃ¡rio). Grade horizontal hairline, sem grade vertical. TÃ­tulo como insight ("Convergiu na geraÃ§Ã£o 16 com F2 de 95,66 %" â€” preenchido com dados reais do JSON do experimento).

**Etiqueta de prioridade logÃ­stica**

| Prioridade | Visual |
| :--- | :--- |
| CrÃ­tica â€” termolÃ¡bil | `--border-cold` tracejada, fundo `--color-cold-soft`, Ã­cone `thermometer-snowflake`, texto `--color-cold` + `2â€“8 Â°C` em mono |
| Alta | fundo `--color-risk-mid-soft`, texto `--color-risk-mid`, Ã­cone `chevrons-up` |
| Regular | borda `--color-rule-strong`, texto `--color-muted`, sem Ã­cone |

**Marcadores do mapa** â€” pino circular 24px fundo `--color-surface`, borda 2px na cor do veÃ­culo, nÃºmero da parada em mono 600 no centro. TermolÃ¡bil: anel externo tracejado `--color-cold`. Hub: quadrado 24px `--color-ink` com Ã­cone `warehouse` claro. Selecionado: escala via tamanho de Ã­cone 32px + `--shadow-1` (sem animaÃ§Ã£o de pulso infinito).

**Lista de paradas** â€” linha por parada: nÃºmero (mono) Â· hospital Â· etiqueta de prioridade Â· ETA (mono, alinhado Ã  direita) Â· carga (kg). Agrupada por veÃ­culo com cabeÃ§alho contendo amostra de traÃ§o da cor/padrÃ£o do veÃ­culo, distÃ¢ncia e tempo total.

**Roteiro do motorista** â€” formato de folha de bordo imprimÃ­vel: lista numerada grande (`--text-lg`), horÃ¡rio em mono Ã  esquerda, alertas de cadeia de frio em bloco `--color-cold-soft` com hairline superior `--color-cold`. BotÃ£o "Imprimir" gera folha em P&B legÃ­vel (padrÃµes de traÃ§o garantem a leitura).

**Assistente logÃ­stico (chat)** â€” sem avatares, sem bolhas arredondadas coloridas. Mensagens como registro: rÃ³tulo do autor em `--text-label` ("VocÃª" / "Assistente"), texto abaixo; mensagens do usuÃ¡rio com fundo `--color-paper-2`, do assistente sobre `--color-surface`, ambos `--radius-sm`. Campo de envio fixo na base com o mesmo padrÃ£o de input. Estado "gerando resposta": trÃªs traÃ§os em pulso de opacidade (nÃ£o pontinhos saltitantes).

### 8.4 Feedback

**Badge** â€” altura 22px, padding `0 var(--space-xs)`, `--radius-xs`, `--text-xs` 600, fundo suave da semÃ¢ntica + texto da semÃ¢ntica + Ã­cone 12px. Nunca sÃ³ ponto de cor.

**Banner inline** â€” fundo suave semÃ¢ntico, hairline superior 2px na cor semÃ¢ntica, Ã­cone + tÃ­tulo curto + texto + aÃ§Ã£o opcional. Usado para: falha de provedor LLM com fallback ativo ("Laudo gerado pelo modelo de contingÃªncia"), prompt bloqueado, rota sem soluÃ§Ã£o viÃ¡vel.

**Toast** â€” sÃ³ para falhas e efeitos invisÃ­veis (ex.: "Modelo ativo alterado para SVM"). Canto inferior esquerdo, fundo `--color-ink`, texto `--color-surface`, `--shadow-1`, 5s, pausa no hover/foco, botÃ£o fechar. Sucessos visÃ­veis na tela nÃ£o geram toast.

**Skeleton** â€” blocos sÃ³lidos `--color-paper-3` com a geometria exata do conteÃºdo (linhas de tabela, rÃ©gua de risco, parÃ¡grafos do laudo com larguras 100/92/96/60%). Pulso de opacidade. Para o laudo (pode levar segundos): skeleton + texto "Gerando laudo â€” consultando diretrizes clÃ­nicas" em `--color-muted`.

**Empty state** â€” sem ilustraÃ§Ã£o genÃ©rica. Estrutura: Ã­cone Lucide 24px `--color-neutral` Â· tÃ­tulo em `--text-xl` display Â· uma frase explicando o prÃ³ximo passo Â· um botÃ£o. Exemplos:
- Rotas: "Nenhuma entrega cadastrada" Â· "Adicione hospitais e cargas para calcular a melhor divisÃ£o entre os veÃ­culos." Â· [Adicionar entrega]
- Laudos: "Nenhum laudo nesta sessÃ£o" Â· "Conclua uma triagem para gerar a explicaÃ§Ã£o clÃ­nica." Â· [Iniciar triagem]

**Modal** â€” sÃ³ para confirmaÃ§Ãµes destrutivas ou decisÃµes irreversÃ­veis (ex.: "Colocar Random Forest em produÃ§Ã£o?"). Largura 480px, `--radius-md`, `--shadow-2`, overlay sÃ³lido. Detalhes de modelo vÃ£o em drawer, nÃ£o modal.

---

## 9. VisualizaÃ§Ã£o de dados

- **TÃ­tulos como insight**, preenchidos com dados reais; nunca "GrÃ¡fico 1".
- MÃ¡ximo 6 blocos de grÃ¡fico por tela; 15â€“20% de Ã¡rea livre.
- Escala sequencial discreta (matriz de confusÃ£o, densidade): `--color-seq-1` `oklch(96% 0.020 262)` Â· `--color-seq-2` `oklch(88% 0.050 262)` Â· `--color-seq-3` `oklch(76% 0.090 262)` Â· `--color-seq-4` `oklch(60% 0.130 262)` Â· `--color-seq-5` `oklch(47% 0.165 262)`. Texto sobre seq-4/5 usa `--color-surface`.
- ComparaÃ§Ãµes (Fase 1 Ã— Fase 2): barras lado a lado em `--color-neutral` (antes) e `--color-ink` (depois), delta em mono com sinal (`+5,28 p.p.`) e seta `â–²`/`â–¼` textual.
- Eixos e grade em `--color-rule`; rÃ³tulos `--text-xs` mono `--color-muted`.
- Sem Ã¡reas preenchidas com gradiente, sem 3D, sem pizza com mais de 3 fatias (preferir a faixa de composiÃ§Ã£o).

---

## 10. Copy e tom

- ClÃ­nico, direto, em pt-BR. Frases curtas. Verbo no imperativo nos botÃµes ("Analisar", "Calcular rotas", "Gerar laudo", "Colocar em produÃ§Ã£o").
- RÃ³tulos de botÃ£o com no mÃ¡ximo 3 palavras; nunca quebram linha.
- IA sempre nomeada pelo que faz: "Estimativa do modelo", "Laudo gerado por IA", "SugestÃ£o do assistente".
- Erros dizem o que aconteceu e o que fazer. Nada de "Ops!".
- Proibido: "revolucionÃ¡rio", "inteligente" como adjetivo vazio, "mÃ¡gica", "sem esforÃ§o", exclamaÃ§Ãµes, emojis.
- Dados pessoais: nome do paciente nunca aparece em tÃ­tulos, toasts ou URLs (Privacy by Default) â€” use "Paciente" + idade ou identificador de sessÃ£o.

---

## 11. Acessibilidade

- Contraste: corpo â‰¥ 4,5:1, componentes e texto grande â‰¥ 3:1 (validado na Â§2).
- Foco visÃ­vel em todo elemento interativo, apariÃ§Ã£o instantÃ¢nea, nunca removido.
- Alvos de toque â‰¥ 44Ã—44px.
- Cor nunca Ã© o Ãºnico canal (risco, prioridade, veÃ­culo, modalidade tÃªm texto/forma/padrÃ£o).
- RÃ©gua de risco exposta como `role="meter"` com `aria-valuenow`, `aria-valuemin`, `aria-valuemax` e `aria-valuetext="Risco alto, 82 por cento"`.
- Mapa sempre acompanhado da lista de paradas equivalente (conteÃºdo acessÃ­vel sem o mapa).
- Ordem de tabulaÃ§Ã£o segue a ordem visual; drawer e modal prendem o foco e devolvem ao gatilho.

---

## 12. Tokens exportÃ¡veis (`:root`)

```css
/* Hallmark Â· theme: ProntuÃ¡rio v2.0 Â· macrostructure: workbench (app shell) */
:root {
  /* Papel e tinta */
  --color-surface:      oklch(99% 0.004 95);
  --color-paper:        oklch(97.4% 0.006 95);
  --color-paper-2:      oklch(95% 0.008 95);
  --color-paper-3:      oklch(91.6% 0.010 95);
  --color-rule:         oklch(86% 0.010 95);
  --color-rule-strong:  oklch(62% 0.012 95);
  --color-neutral:      oklch(52.5% 0.012 250);
  --color-muted:        oklch(45% 0.014 250);
  --color-ink-2:        oklch(32% 0.016 250);
  --color-ink:          oklch(21% 0.018 250);
  --color-ink-hover:    oklch(29% 0.020 250);

  /* Acento â€” caneta */
  --color-accent:       oklch(47% 0.165 262);
  --color-accent-hover: oklch(41% 0.150 262);
  --color-accent-soft:  oklch(94% 0.025 262);
  --color-accent-ink:   var(--color-surface);
  --color-focus:        var(--color-accent);

  /* SemÃ¢ntica */
  --color-risk-high:      oklch(50% 0.165 28);
  --color-risk-high-soft: oklch(94.5% 0.025 28);
  --color-risk-mid:       oklch(50.5% 0.105 70);
  --color-risk-mid-fill:  oklch(76% 0.135 78);
  --color-risk-mid-soft:  oklch(95% 0.035 85);
  --color-risk-low:       oklch(50% 0.095 155);
  --color-risk-low-soft:  oklch(95% 0.025 155);
  --color-cold:           oklch(52% 0.095 220);
  --color-cold-soft:      oklch(95% 0.022 220);
  --color-danger:  var(--color-risk-high);
  --color-warning: var(--color-risk-mid);
  --color-success: var(--color-risk-low);
  --color-info:    var(--color-accent);

  /* Sequencial (5 passos discretos) */
  --color-seq-1: oklch(96% 0.020 262);
  --color-seq-2: oklch(88% 0.050 262);
  --color-seq-3: oklch(76% 0.090 262);
  --color-seq-4: oklch(60% 0.130 262);
  --color-seq-5: oklch(47% 0.165 262);

  /* VeÃ­culos */
  --color-route-1: #332288;
  --color-route-2: #117733;
  --color-route-3: #882255;
  --color-route-4: #6B6B19;
  --color-route-5: #1F6E8C;
  --color-route-6: #AA3377;

  /* Overlay e sombras de dupla camada (tinta com alfa â€” sem blur de IA) */
  --color-overlay: oklch(21% 0.018 250 / 0.48);
  --shadow-0: none;
  --shadow-1: 0 1px 2px oklch(21% 0.018 250 / 0.08), 0 2px 4px oklch(21% 0.018 250 / 0.04);
  --shadow-2: 0 2px 4px oklch(21% 0.018 250 / 0.08), 0 6px 16px oklch(21% 0.018 250 / 0.06);
  --shadow-3: 0 4px 8px oklch(21% 0.018 250 / 0.08), 0 16px 36px oklch(21% 0.018 250 / 0.12);
  --shadow-4: 0 8px 16px oklch(21% 0.018 250 / 0.08), 0 24px 48px oklch(21% 0.018 250 / 0.14);
  --shadow-drawer-left: -4px 0 16px oklch(21% 0.018 250 / 0.10), -12px 0 32px oklch(21% 0.018 250 / 0.08);

  /* Tipografia */
  --font-display: 'Source Serif 4', 'Iowan Old Style', Georgia, serif;
  --font-body:    'Public Sans', 'Segoe UI', system-ui, sans-serif;
  --font-mono:    'IBM Plex Mono', ui-monospace, 'Cascadia Mono', monospace;

  --text-display: clamp(2.25rem, 1.6rem + 2vw, 2.566rem);
  --text-3xl:   2.063rem;
  --text-2xl:   1.625rem;
  --text-xl:    1.313rem;
  --text-lg:    1.125rem;
  --text-md:    1rem;
  --text-sm:    0.875rem;
  --text-xs:    0.8125rem;
  --text-label: 0.75rem;

  --lh-tight: 1.08;
  --lh-heading: 1.2;
  --lh-body: 1.5;
  --lh-read: 1.6;
  --tracking-label: 0.06em;

  /* EspaÃ§o */
  --space-3xs: 2px;
  --space-2xs: 4px;
  --space-xs:  8px;
  --space-sm:  12px;
  --space-md:  16px;
  --space-lg:  24px;
  --space-xl:  32px;
  --space-2xl: 48px;
  --space-3xl: 64px;
  --space-4xl: 96px;

  /* Layout */
  --container-read: 720px;
  --container-form: 960px;
  --container-wide: 1360px;
  --rail-width: 232px;
  --rail-width-collapsed: 64px;
  --gutter: clamp(16px, 2.5vw, 32px);
  --control-height: 44px;
  --control-height-compact: 36px;

  /* Forma */
  --radius-xs: 2px;
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-round: 999px;
  --border-hairline: 1px solid var(--color-rule);
  --border-control:  1px solid var(--color-rule-strong);
  --border-strong:   1px solid var(--color-ink);
  --border-cold:     1px dashed var(--color-cold);

  /* Camadas */
  --z-sticky: 200;
  --z-nav: 300;
  --z-map-controls: 400;
  --z-drawer: 500;
  --z-modal: 600;
  --z-toast: 700;
  --z-tooltip: 800;

  /* Movimento & AnimaÃ§Ãµes */
  --ease-out:    cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in:     cubic-bezier(0.7, 0, 0.84, 0);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --ease-snap:   cubic-bezier(0.2, 0.8, 0.2, 1);

  --dur-instant: 0ms;
  --dur-micro:   120ms;
  --dur-short:   200ms;
  --dur-medium:  280ms;
  --dur-long:    360ms;
  --dur-reveal:  640ms;
}

[data-theme="dark"] {
  --color-paper:       oklch(17% 0.012 250);
  --color-paper-2:     oklch(21% 0.014 250);
  --color-paper-3:     oklch(25% 0.015 250);
  --color-surface:     oklch(25% 0.015 250);
  --color-rule:        oklch(33% 0.014 250);
  --color-rule-strong: oklch(52% 0.014 250);
  --color-neutral:     oklch(64% 0.012 250);
  --color-muted:       oklch(72% 0.012 250);
  --color-ink-2:       oklch(86% 0.010 95);
  --color-ink:         oklch(94% 0.008 95);
  --color-ink-hover:   oklch(86% 0.010 95);
  --color-accent:      oklch(70% 0.130 262);
  --color-accent-hover:oklch(76% 0.110 262);
  --color-accent-soft: oklch(30% 0.050 262);
  --color-accent-ink:  oklch(17% 0.012 250);
  --color-risk-high:   oklch(68% 0.150 28);
  --color-risk-mid:    oklch(78% 0.130 78);
  --color-risk-low:    oklch(72% 0.110 155);
  --color-cold:        oklch(74% 0.100 220);
}

html, body { overflow-x: clip; }
```

---

## 13. Checklist de conformidade (UX Reviewer)

- [ ] Nenhum emoji, glassmorphism (`backdrop-filter`), gradiente de cor, glow ou texto em gradiente.
- [ ] Todas as cores e fontes vÃªm de tokens desta pÃ¡gina.
- [ ] BotÃ£o primÃ¡rio em tinta; acento azul â‰¤ 3% da viewport.
- [ ] Todo significado cromÃ¡tico tem texto, Ã­cone ou padrÃ£o.
- [ ] NÃºmeros em mono tabular, alinhados Ã  direita.
- [ ] Resultado de IA mostra valor + escala + composiÃ§Ã£o + aviso de apoio Ã  decisÃ£o.
- [ ] 8 estados implementados; desabilitado em 3 canais; foco instantÃ¢neo.
- [ ] Inputs e botÃµes do mesmo formulÃ¡rio com 44px.
- [ ] Skeleton com geometria real e pulso de opacidade (sem shimmer).
- [ ] Movimento sÃ³ em `transform`/`opacity` (+ `stroke-dashoffset` nos momentos-assinatura) com fallback de movimento reduzido.
- [ ] Sem scroll horizontal em 320/375/414/768 px; rÃ³tulos clicÃ¡veis em uma linha.
- [ ] TÃ­tulos romanos, nenhum itÃ¡lico em cabeÃ§alho.

