# Arquitetura do Frontend: Angular

Este documento detalha as decisões arquiteturais e metodologias empregadas no desenvolvimento do Frontend da plataforma **HealthAI**. O objetivo é prover uma estrutura escalável, de alta performance e desacoplada, utilizando as práticas modernas do framework Angular.

## 1. Single Page Application (SPA)
A plataforma é baseada no conceito de SPA, em que o conteúdo da interface de usuário (UI) é atualizado dinamicamente sem a necessidade de recarregamentos completos da página pelo navegador. Isso garante uma transição contínua e assíncrona entre os componentes, maximizando a reatividade do sistema e permitindo o envio de relatórios de anamnese de maneira instantânea e transparente ao usuário.

---

## 2. Componentes Standalone
A arquitetura do projeto descarta o uso tradicional de `NgModules` em favor da abordagem **Standalone Components** do Angular.
Neste paradigma, cada componente declara explicitamente suas próprias dependências de escopo. Essa decisão arquitetural resulta em:
*   Redução da complexidade estrutural e do boilerplace.
*   Aprimoramento das capacidades de **Tree Shaking** no processo de build, diminuindo a carga inicial da aplicação.
*   Maior facilidade na criação de bibliotecas internas de UI e isolamento de escopo.

---

## 3. Sistema de Estilização: SCSS e Metodologia BEM
A fim de garantir total controle sobre a identidade visual da aplicação e suportar customizações avançadas, não há uso de frameworks utilitários externos (como Bootstrap ou TailwindCSS). 
A estilização é regida pelos seguintes padrões:

*   **SCSS (Sassy CSS)**: Utilizado para gerenciar a consistência do sistema de design por intermédio de variáveis estruturadas, funções de cálculo de escala modular e aninhamento de seletores.
*   **Padrão BEM (Block, Element, Modifier)**: Todo o CSS gerado obedece estritamente à taxonomia BEM para evitar conflitos de especificidade, escopando os estilos pelo próprio nome da classe (ex: `.card__header` ou `.button--primary`).

---

## 4. Camada de Integração (Services)
A persistência de fluxo e comunicação de dados entre a UI e o Backend FastAPI ocorre pela **Camada de Serviço**.
Componentes visuais (Apresentacionais) não gerenciam chamadas diretas de rede. Os envios de formulários delegam essa responsabilidade para os Serviços (Injetáveis), que:
1. Recebem os dados estruturados do controlador do componente.
2. Utilizam a classe `HttpClient` nativa do Angular para formatar e disparar requisições HTTP REST (ex: métodos `POST`).
3. Interceptam, processam eventuais erros de payload e devolvem `Observables` assíncronos ao ecossistema do componente.

---

## 5. Infraestrutura de Build e Deploy
Ao ser otimizado via Ahead-of-Time Compilation (`ng build`), o código Typescript e as diretrizes de markup são transpilados para bundles estáticos minificados (HTML, CSS e JS). 
A publicação da aplicação (Hosting) será gerenciada pelo **Firebase Hosting**, provendo rede de distribuição de conteúdo (CDN) e acesso via protocolo HTTPS sem necessidade de manutenção ativa de servidores web tradicionais.
