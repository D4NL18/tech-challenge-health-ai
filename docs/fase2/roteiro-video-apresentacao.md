# Roteiro para Vídeo de Demonstração (Fase 2 - Tech Challenge) 🎥⏱️

> **Duração Máxima:** Até 15 minutos (conforme edital do Tech Challenge)  
> **Plataforma de Envio:** YouTube / Vimeo (público ou não listado)  
> **Objetivo:** Demonstrar o sistema em execução, explicar os componentes da Fase 2, apresentar os resultados de ambos os projetos (Algoritmos Genéticos para Diagnóstico e Rotas Médicas) e a integração com LLMs.

---

## Estrutura da Apresentação com Minutagem

### Bloco 1: Introdução e Visão Geral (00:00 - 02:00)
- **Fala Sugerida:**
  - "Olá a todos! Sejam bem-vindos à apresentação do Tech Challenge Fase 2 da pós-graduação em Inteligência Artificial para a Saúde.
  - Na Fase 1, construímos uma plataforma serverless para triagem diagnóstica preditiva (Câncer de Mama e SOP).
  - Na Fase 2, fomos desafiados a solucionar dois grandes problemas com Algoritmos Genéticos e Processamento de Linguagem Natural:
    1. A otimização hiperparamétrica dos modelos de diagnóstico médico focada em sensibilidade clínica e explicabilidade com LLM;
    2. O problema de roteamento logístico hospitalar (VRP) para distribuição de medicamentos e insumos sobre malha de mapas reais com grafos viários e relatórios por LLM.
  - Decidimos implementar e entregar **ambos os projetos** no mesmo ecossistema integrado."

---

### Bloco 2: Projeto 1 - Otimização de Modelos com Algoritmo Genético (02:00 - 05:30)
- **O que mostrar na tela:**
  - Código do Algoritmo Genético em `backend/app/genetic/hyperopt/`.
  - Painel Administrativo do sistema (`/admin`) na seção de Algoritmos Genéticos.
- **Tópicos a Abordar:**
  - **Representação Genética:** Codificação cromossômica híbrida (genes inteiros, contínuos e categóricos para Random Forest, SVM e Gradient Boosting).
  - **Operadores Genéticos:** Seleção por Torneio ($k=3$), Crossover Uniforme/Aritmético e Mutação Gaussiana com limites rígidos.
  - **Função Fitness Clínica ($F_2$-Score):** Explicar por que no contexto médico o Recall (Sensibilidade) tem peso 4 vezes maior do que a precisão (falsos negativos são inaceitáveis).
  - **Apresentação dos 3 Experimentos:**
    - Exibir a tabela comparativa: Linha de Base da Fase 1 vs. Experimento 1 (Pop 20/Gen 10), Experimento 2 (Pop 40/Gen 20) e Experimento 3 (Pop 80/Gen 30).
    - Destacar o salto de **Recall de 90.48% para 95.76%** e **F2-Score de 91.35% para 95.66%**.

---

### Bloco 3: Projeto 1 - Interpretação Diagnóstica com LLM (05:30 - 07:30)
- **O que mostrar na tela:**
  - Tela de Diagnóstico/Dashboard (`/dashboard`).
  - Clicar no botão *"Gerar Laudo Médico Explicativo (LLM - Fase 2)"*.
- **Tópicos a Abordar:**
  - Como a LLM (Google Gemini Flash / OpenAI) transforma o percentual estatístico em um laudo estruturado e compreensível para o médico assistente.
  - Apresentar as seções geradas: Resumo do Caso, Top 3 Fatores de Risco Determinantes, Raciocínio Clínico, Condutas Sugeridas e Disclaimer Ético.
  - Destacar as técnicas de Prompt Engineering com Chain-of-Thought e saída estrita em JSON com esquemas Pydantic.

---

### Bloco 4: Projeto 2 - Roteamento Médico VRP com OSRM e Algoritmo Genético (07:30 - 11:30)
- **O que mostrar na tela:**
  - Nova rota da aplicação: `/routes`.
  - O mapa interativo Leaflet.js exibindo o Hub Central (Hospital das Clínicas) e as 9 unidades de saúde.
  - Clicar em *"Otimizar Rotas com AG"*.
- **Tópicos a Abordar:**
  - **Grafo Viário Ponderado por Tempo (OSRM / OpenStreetMap):**
    - Explicar por que escolhemos OSRM: custo zero, mapas reais com sentidos viários e velocidades nominais.
    - Demonstrar a arquitetura em 2 camadas: 1 única requisição batch constrói a matriz $N \times N$, com cache SQLite local persistente, permitindo que o AG execute milhares de iterações em RAM em frações de segundo sem risco de esgotar APIs.
  - **Restrições Médicas no Algoritmo Genético:**
    - Medicamentos de urgência crítica priorizados no início das rotas.
    - Capacidade limitada do baú térmico/refrigerado dos veículos (kg/caixas).
    - Limite de autonomia em km e divisão entre múltiplos veículos da frota.
  - **Operadores de Permutação:**
    - Crossover OX (Order Crossover) garantindo que nenhum hospital/paciente seja duplicado ou esquecido.
    - Mutações 2-opt de inversão de trajeto.

---

### Bloco 5: Projeto 2 - Assistente Logístico e Relatórios com LLM (11:30 - 13:30)
- **O que mostrar na tela:**
  - Alternar entre as abas na tela de rotas:
    - Aba *"Roteiro do Motorista"*: itinerário detalhado com alertas de conservação térmica (2°C a 8°C).
    - Aba *"Relatório Executivo"*: relatório com estimativa de tempo e combustível economizados e mitigação de CO2.
    - Aba *"Chat com a IA"*: fazer uma pergunta em linguagem natural (ex: *"Quais medicamentos de urgência serão entregues primeiro?"*) e mostrar a resposta em tempo real.

---

### Bloco 6: Conclusão, Arquitetura e Considerações Finais (13:30 - 15:00)
- **Tópicos a Abordar:**
  - Suíte de testes automatizados com `pytest` (11 testes cobrindo operadores genéticos, fitness, cache e rotas da API).
  - Conformidade arquitetural e de governança (Clean Code, separação de documentações, conformidade com a LGPD e Privacy by Design).
  - Encerramento e agradecimentos à banca avaliadora.
