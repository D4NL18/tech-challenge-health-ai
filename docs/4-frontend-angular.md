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

## 4.5. Estilização: SCSS e Padrão BEM
Não utilizei Bootstrap ou Tailwind. Preferi ter total controle do layout criando um **Design System Customizado** escrito puramente em SCSS.

O SCSS me permite criar variáveis (ex: `$color-primary`) e funções de cálculo (ex: clarear cores em X%).

Para não virar uma bagunça de classes no CSS, apliquei a **Metodologia BEM** (Block, Element, Modifier). 
*   **Block:** O elemento pai, ex: `.card`
*   **Element:** Um filho do pai, ex: `.card__title`
*   **Modifier:** Um estado, ex: `.card--highlighted`

Isso me garante que a classe CSS do botão da tela de Admin nunca vai quebrar ou sobrescrever a classe CSS do botão da tela Principal.

---

**Próximo Passo:**
Para ver como a IA foi treinada e gerida fora da API web, acesse [5-mlops-treinamento.md](./5-mlops-treinamento.md).
