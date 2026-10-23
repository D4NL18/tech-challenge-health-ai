# 4. Frontend e Angular

*Read this in other languages: [English](../docs_en/4-frontend-angular.md) | [Português](4-frontend-angular.md)*

Neste documento detalho as decisões arquiteturais da interface com o usuário (Frontend). O objetivo foi criar uma tela amigável, rápida e escalável utilizando **Angular**, sem depender de pesados frameworks CSS pré-prontos.

---

## 4.1. Single Page Application (SPA)
O Angular compila tudo em uma Single Page Application. Isso significa que, do ponto de vista do Servidor (Firebase Hosting), existe apenas um arquivo genérico `index.html`.

Toda a mágica acontece no navegador do usuário via JavaScript. Quando o médico transita entre a tela de "Fazer Diagnóstico" e a tela de "Configurações (Admin)", a página não pisca e não carrega novamente. O Angular simplesmente apaga o componente antigo da memória e desenha o novo instantaneamente. Isso aumenta drásticamente a percepção de velocidade.

---

## 4.2. Standalone Components
Em versões antigas do Angular, existia um conceito chamado `NgModule`, onde todos os componentes tinham que ser declarados em um arquivo central gigantesco. Isso era muito verboso e dificultava o reaproveitamento de código.

Neste projeto, utilizei a abordagem moderna do Angular: **Standalone Components**.
Cada componente (ex: `admin-dashboard.component.ts`) é auto-suficiente. Ele importa apenas o que ele mesmo precisa usar (ex: `CommonModule`, `FormsModule`). Isso gera os seguintes benefícios:
*   Deixa o código muito mais limpo.
*   Permite o **Tree Shaking** mais eficiente (o Angular apaga código não usado na hora do build final).
*   Melhora o tempo de carregamento da aplicação (Lazy Loading mais fácil).

---

## 4.3. Sistema de Formulários (Reactive Forms e ngModel)
O preenchimento de anamnese é o núcleo da plataforma.

Para o formulário de Inteligência Artificial, utilizei o `ngModel` (Template-driven Forms) para facilitar a amarração direta de variáveis entre o HTML e o Typescript (Two-Way Data Binding).
Isso me permite, por exemplo, mudar dinamicamente as perguntas que aparecem na tela dependendo de se o usuário selecionou "Avaliar Câncer de Mama" ou "Avaliar SOP" no seletor principal.

---

## 4.4. A Camada de Serviços (Services e HttpClient)
O arquivo `anamnesis.component.ts` (Componente) não sabe qual é a URL do meu Backend, nem como a rede funciona. Ele só sabe como desenhar botões na tela e reagir a cliques.

Quem gerencia a chamada à Internet é o **Serviço** (`inference.service.ts`).
Essa arquitetura respeita o *Princípio de Responsabilidade Única*. 

1. Quando o paciente clica em "Enviar", o Componente passa os dados brutos para o Serviço.
2. O Serviço constrói o `FormData` em formato **Multipart** (anexando a imagem do raio-x e um JSON com os sintomas).
3. O Serviço usa a classe `HttpClient` do Angular para bater na API do FastAPI.
4. O Serviço lida com problemas de rede (se o servidor caiu) e retorna um *Observable*.
5. O Componente escuta o *Observable* e só atualiza a tela para exibir os resultados quando os dados chegam.

---

## 4.5. Estilização: Design System "Prontuário", Tokens SCSS e Padrão BEM
Não utilizei frameworks pré-fabricados genéricos como Bootstrap ou Tailwind. Preferi ter controle estético e funcional total criando o **Design System "Prontuário"**, um design kit documental clínico padronizado em `.agents/docs/design/DESIGN_SYSTEM.md` e testado no espécime visual interativo `.agents/docs/design/specimen/prontuario-kit.html`.

### Fundamentos Visuais do Design System:
- **Tríade Tipográfica Médica:**
  - `Source Serif 4`: Cabeçalhos clínicos, títulos de seções e laudos diagnósticos, conferindo sobriedade editorial.
  - `Public Sans`: Labels de formulários, botões, chips e elementos de interface com máxima legibilidade.
  - `IBM Plex Mono`: Telemetria, coordenadas geográficas, percentuais de risco, tempos de trajeto e dados tabulares com alinhamento tabular (`font-variant-numeric: tabular-nums`).
- **Elevações e Sombras Físicas (Dupla Camada):**
  Tokens de `--shadow-0` (flat com borda hairline) a `--shadow-4` (drawers laterais de auditoria), utilizando projeções mecânicas sem halos luminosos ou *glows* artificiais.
- **Coreografia Mecânica de Movimento:**
  Transições espaciais aceleradas por hardware (GPU compositing via `transform` e `opacity`), botões com recuo tátil mecânico (`translateY(1px)` no clique) e respeito estrito a `@media (prefers-reduced-motion: reduce)`.
- **Metodologia BEM (Block, Element, Modifier):**
  - **Block:** O componente estrutural, ex: `.c-card`, `.c-button`
  - **Element:** Sub-elemento dependente, ex: `.c-card__header`, `.c-button__label`
  - **Modifier:** Estado ou variação, ex: `.c-button--secondary`, `.c-badge--urgent`

---

## 4.6. Módulo de Roteamento Médico e Leaflet.js (`pages/medical-routes/`)
**Arquivo de Referência:** `frontend/src/app/pages/medical-routes/medical-routes.component.ts`

Na Fase 2, criamos uma nova rota (`/routes`) e uma página rica para despacho de equipes de saúde domiciliar:
- **Mapa Interativo com Leaflet.js e OpenStreetMap:** Renderização de marcadores dinâmicos (verde para depósito/posto de saúde, vermelho/laranja para pacientes prioritários com numeração da ordem de parada) e traçado da polyline real da rota em azul vibrante.
- **Painel de Controle e Parâmetros Genéticos:** Permite ao operador ajustar tamanho da população (10 a 200), gerações (10 a 100), taxa de mutação e pesos de prioridade clínica vs. tempo de deslocamento.
- **Cenário Demonstrativo Imediato:** Botão "Carregar Cenário Demo (São Paulo)" que popula instantaneamente 6 pacientes reais (Grajaú, Capão Redondo, Itaquera, etc.) com diferentes prioridades e janelas de tempo.
- **Assistente LLM Integrado:** Abas com "Instruções Passo a Passo", "Chat com o Assistente de Campo" e "Relatório Executivo Hospitalar".

---

## 4.7. Auditoria de Experimentos Genéticos no Admin Dashboard
**Arquivo de Referência:** `frontend/src/app/pages/admin-dashboard/admin-dashboard.component.ts`

O painel administrativo agora consome a rota de experimentos hiperparamétricos e exibe:
- Tabela comparativa entre o Baseline (GridSearch Fase 1) e os 3 experimentos do Algoritmo Genético.
- Indicadores visuais de ganho percentual de $F_2$-Score e Recall (redução de falsos negativos).
- Card explicativo da função fitness ponderada para a tomada de decisão médica.

---

## 4.8. Laudo Clínico Explicativo com LLM no Dashboard
**Arquivo de Referência:** `frontend/src/app/pages/dashboard/dashboard.component.ts`

Após a realização de um diagnóstico multimodal no dashboard principal:
- Um botão estilizado com gradiente permite ao médico solicitar a "Geração de Laudo Explicativo (LLM - Fase 2)".
- O laudo é renderizado em um card com tipografia clínica, dividindo o caso em: Síntese Diagnóstica, Fatores Determinantes, Recomendações e Diretrizes Éticas.

---

**Próximo Passo:**
Para ver como a IA foi treinada e gerida fora da API web, acesse [5-mlops-treinamento.md](./5-mlops-treinamento.md).
