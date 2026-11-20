# Regras de Negócio: Otimização de Modelos de Diagnóstico via Algoritmo Genético e LLM

> **Localização Mandatória:** `.agents/docs/business_rules/BR-010-algoritmo-genetico-hiperparametros.md`  
> **Responsável:** Analista (`business-rules-expert`)  
> **User Stories:** US-06, US-07, US-08

---

## 1. Contexto e Objetivo
- **User Story Relacionada:** US-06, US-07, US-08 (Fase 2 - Projeto 1).
- **Objetivo da Feature:** Otimizar hiperparâmetros de modelos de classificação diagnóstica clínica (Câncer de Mama e PCOS) utilizando Algoritmos Genéticos (AG), garantindo sensibilidade médica maximizada (Recall/F2-Score) e gerando laudos compreensíveis em linguagem natural via LLM.
- **Atores Envolvidos:** Médico, Administrador do Sistema, Motor de IA/AG.

---

## 2. Catálogo de Regras de Negócio (P-010 a P-019)

### `P-010`: Codificação Cromossômica Híbrida e Bounds Rígidos
- **Declaração Mandatória:** O sistema DEVE validar e garantir que cada gene pertença estritamente ao intervalo e tipo permitido do hiperparâmetro (ex: `n_estimators` deve ser inteiro no intervalo [20, 300]; `max_depth` inteiro no intervalo [3, 30] ou None; `min_samples_split` no intervalo [0.01, 0.5]; `C` e `gamma` do SVM reais positivos na escala logarítmica).
- **Condições de Ativação:** Inicialização da população e após mutação/crossover genético.
- **Resultado Esperado:** O cromossomo resultante deve ser imediatamente podado (*clipped*) aos limites permitidos caso a mutação exceda as bordas.

### `P-011`: Função Fitness Orientada à Sensibilidade Clínica ($F_2$-Score)
- **Declaração Mandatória:** O sistema DEVE avaliar a aptidão de cada indivíduo através de Validação Cruzada Estratificada ($5$-Fold Stratified CV) utilizando prioritariamente a métrica $F_2$-Score, que atribui peso 4 vezes maior ao Recall (Sensibilidade) do que à Precisão.
- **Condições de Ativação:** Avaliação de aptidão de cada geração do AG.
- **Resultado Esperado:** Modelos com menos falsos negativos recebem escore significativamente superior a modelos que apenas maximizam acurácia pura às custas de pacientes doentes não diagnosticados.

### `P-012`: Elitismo Mandatório
- **Declaração Mandatória:** O motor genético DEVE preservar intactos os $E=2$ melhores indivíduos de cada geração para a geração subsequente, impedindo qualquer regressão da aptidão global máxima ao longo das gerações.
- **Condições de Ativação:** Transição entre gerações no algoritmo genético.

### `P-013`: Execução de Três Experimentos Comparativos
- **Declaração Mandatória:** O sistema DEVE executar e registrar 3 configurações distintas de AG (Experimento 1: População 20 / 10 gerações; Experimento 2: População 50 / 25 gerações; Experimento 3: População 100 / 40 gerações), comparando métricas finais (Acurácia, F1-Score, Recall) contra a linha de base da Fase 1.
- **Resultado Esperado:** Registro estruturado das métricas em arquivo de pesos e documentação comparativa.

### `P-014`: Explicabilidade Clínica Estruturada (LLM)
- **Declaração Mandatória:** A explicação em linguagem natural gerada pela LLM DEVE basear-se estritamente nas características laboratoriais/clínicas fornecidas para a paciente e na probabilidade inferida pelo modelo, contendo obrigatoriamente: (1) Resumo clínico, (2) Top 3 fatores determinantes, (3) Justificativa médica, (4) Recomendações de exames complementares e (5) Disclaimer ético de apoio à decisão.
- **Exceção / Erro:** Caso a LLM esteja indisponível, o sistema DEVE acionar a cascata de fallbacks (`gemini-2.5-flash` -> `gemini-2.0-flash` -> `gpt-4o-mini` -> fallback heurístico determinístico) mantendo a estrutura do laudo sem quebrar a interface.

### `P-015`: Governança de LLMs: Prompts em Inglês, Segurança Anti-Injection Restrita e Cache de Similaridade
- **Declaração Mandatória:** Todos os módulos de LLM do sistema (`text.py`, `clinical_llm.py`, `logistics_llm.py` e `query_rag.py`) DEVEM:
  1. Utilizar `SYSTEM_PROMPT` em **inglês técnico conciso** (otimização de tokens SentencePiece/BPE) exigindo saída final em **Português do Brasil (`pt-BR`)**;
  2. Aplicar o `PromptSecurityGuard` para truncar tamanho máximo de input, neutralizar delimitadores, isolar dados do usuário em `<untrusted_user_input>` e bloquear determinísticamente tentativas de *Prompt Injection* / *Jailbreak* em PT e EN antes de invocar a API;
  3. Utilizar o `SimilarityLLMCache` em duas camadas (L1 Hash SHA-256 sobre texto normalizado + L2 Similaridade de Cosseno sobre 3-gramas de caracteres e palavras com threshold $\ge 0.85$) para reutilizar respostas em textos idênticos ou similares sem custo adicional de API.

---

## 3. Enquadramento LGPD & Privacidade (Art. 7º e 11)

| Dado / Atributo | Classificação LGPD | Base Legal Aplicada | Finalidade Específica e Proporcional |
| :--- | :--- | :--- | :--- |
| `Dados Clínicos (ex: raio, textura, hormônios)` | Dado Pessoal Sensível de Saúde (Art. 11, II, 'f') | Tutela da Saúde em procedimento realizado por profissionais ou entidades de saúde | Inferência preditiva de risco e geração de laudo complementar sem persistência desnecessária (Stateless). |

---

## 4. Critérios de Aceitação (DoD)
- [x] Cromossomo e operadores com testes unitários em `pytest`.
- [x] 3 experimentos executados e registrados.
- [x] Fallback de LLM implementado e testado.
