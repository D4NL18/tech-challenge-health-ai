# 6. Exemplos de Testes Inéditos (Triagem)

*Read this in other languages: [English](../docs_en/6-test-examples.md) | [Português](6-exemplos-testes.md)*

Para testar a acurácia dos modelos e entender se tudo que expliquei nos documentos anteriores está de fato funcionando, criei alguns exemplos sintéticos de pacientes.

Você pode colar esses valores no Frontend do Angular e rodar o diagnóstico. Lembre-se: como esses dados não existem na base de treinamento original, estou forçando a IA a inferir algo que ela nunca viu.

---

## 6.1. Câncer de Mama

### Exemplo A: Alto Risco (Maligno)
*Dados sintéticos projetados com características acentuadas típicas de nódulos malignos (maior volume, textura irregular, alta concavidade).*
- **Raio Médio**: 21.35
- **Textura Média**: 24.12
- **Compacidade Média**: 0.2985
- **Concavidade Média**: 0.3210
- **Pontos Côncavos Médios**: 0.1652
- **Raio SE**: 1.250
- **Perímetro SE**: 9.150
- **Área SE**: 185.3
- **Concavidade SE**: 0.0621
- **Raio Pior**: 28.50
- **Textura Pior**: 31.05
- **Suavidade Pior**: 0.1785
- **Compacidade Pior**: 0.7231
- **Concavidade Pior**: 0.7854
- **Pontos Côncavos Pior**: 0.2891
- **Simetria Pior**: 0.5102

### Exemplo B: Baixo Risco (Benigno)
*Dados sintéticos projetados com características típicas de nódulos benignos (menor dimensão, bordas suaves, pouca concavidade).*
- **Raio Médio**: 11.45
- **Textura Média**: 13.10
- **Compacidade Média**: 0.0652
- **Concavidade Média**: 0.0315
- **Pontos Côncavos Médios**: 0.0215
- **Raio SE**: 0.1850
- **Perímetro SE**: 1.350
- **Área SE**: 15.20
- **Concavidade SE**: 0.0152
- **Raio Pior**: 12.85
- **Textura Pior**: 16.45
- **Suavidade Pior**: 0.1150
- **Compacidade Pior**: 0.1350
- **Concavidade Pior**: 0.1052
- **Pontos Côncavos Pior**: 0.0651
- **Simetria Pior**: 0.2510

---

## 6.2. Síndrome do Ovário Policístico (SOP)

### Exemplo C: Alto Risco (SOP = Sim)
*Dados sintéticos para uma paciente apresentando sintomas clássicos de hiperandrogenismo e desequilíbrio metabólico/hormonal (LH alto em relação ao FSH).*
- **Peso (Kg)**: 82.5
- **Altura (cm)**: 162.0
- **Ganho de Peso Recente?**: Sim
- **Crescimento de Pelos Incomum?**: Sim
- **Escurecimento da Pele?**: Sim
- **Consumo Frequente de Fast Food?**: Sim
- **Duração do Ciclo (Dias)**: 7
- **RBS (Glicemia)**: 110.5
- **FSH (mIU/mL)**: 4.10
- **LH (mIU/mL)**: 9.35
- **TSH (mIU/L)**: 3.20
- **Progesterona (PRG)**: 0.25
- **Nº de Folículos (Esq)**: 25
- **Nº de Folículos (Dir)**: 16

### Exemplo D: Baixo Risco (SOP = Não)
*Dados sintéticos para uma paciente saudável, com perfil hormonal equilibrado e sem os sintomas físicos da síndrome.*
- **Peso (Kg)**: 58.0
- **Altura (cm)**: 168.0
- **Ganho de Peso Recente?**: Não
- **Crescimento de Pelos Incomum?**: Não
- **Escurecimento da Pele?**: Não
- **Consumo Frequente de Fast Food?**: Não
- **Duração do Ciclo (Dias)**: 4
- **RBS (Glicemia)**: 85.0
- **FSH (mIU/mL)**: 6.80
- **LH (mIU/mL)**: 3.10
- **TSH (mIU/L)**: 1.80
- **Progesterona (PRG)**: 0.95
---

## 6.3. Cenário de Teste: Roteamento Médico em São Paulo (Fase 2)

Para testar o módulo de Roteamento Médico (`/routes`), você pode usar o botão "Carregar Cenário Demo (São Paulo)" ou enviar os seguintes pontos via API:

### Depósito / Posto Central de Distribuição:
- **Nome**: UBS Vila Mariana (Base Central)
- **Coordenadas**: `[-23.5895, -46.6348]`

### Pacientes para Visita Domiciliar:
1. **Dona Lurdes (Oncologia / Curativo Pós-Op)**:
   - Coordenadas: `[-23.6498, -46.7032]` (Santo Amaro)
   - Prioridade: Alta (Peso 10) | Janela: 08:00 - 10:30
2. **Sr. João (Monitoramento Cardíaco)**:
   - Coordenadas: `[-23.6821, -46.6743]` (Cidade Dutra)
   - Prioridade: Média (Peso 5) | Janela: 09:00 - 12:00
3. **Dona Maria (Exames Coleta Sangue)**:
   - Coordenadas: `[-23.5431, -46.5312]` (Tatuapé)
   - Prioridade: Baixa (Peso 2) | Janela: 10:00 - 14:00
4. **Criança Enzo (Antibioticoterapia EV)**:
   - Coordenadas: `[-23.5182, -46.6021]` (Vila Maria)
   - Prioridade: Alta (Peso 9) | Janela: 08:30 - 11:00
5. **Sr. Benedito (Sutura Diabética)**:
   - Coordenadas: `[-23.5612, -46.6558]` (Bela Vista)
   - Prioridade: Urgência Máxima (Peso 12) | Janela: 07:30 - 09:30
6. **Dona Francisca (Fisioterapia Respiratória)**:
   - Coordenadas: `[-23.6015, -46.6912]` (Brooklin)
   - Prioridade: Média (Peso 4) | Janela: 13:00 - 16:00

O Algoritmo Genético prioriza o atendimento a Dona Lurdes, Criança Enzo e Sr. Benedito nas primeiras horas e minimiza a distância viária real consumindo o grafo do OSRM.

---

## 6.4. Bateria de Testes Automatizados (Pytest)

O projeto conta com uma suíte abrangente de testes automatizados com cobertura rigorosa para os módulos da Fase 1 e Fase 2, totalizando **27 testes unitários e de integração**.

### Módulos de Teste Homologados:
1. `backend/tests/test_genetic_hyperopt.py` (5 testes):
   - Validação de limites de genes (`int`, `float`, `float_log`, `cat`) e conversão para estimadores válidos do Scikit-Learn.
   - Operadores de mutação Gaussiana, crossover aritmético/uniforme e seleção por torneio.
   - Avaliação da função fitness clínica com $F_2$-score em folds estratificados sem data leakage.
   - Espaços de busca multimodelo (Random Forest, SVM, Gradient Boosting, MLP, KNN, Regressão Logística).
   - Inicialização e atualização de telemetria do visualizador gráfico.
2. `backend/tests/test_vrp_routing.py` (7 testes):
   - Cromossomo de permutação VRP, Order Crossover (OX) e mutação por inversão 2-opt.
   - Solver genético com respeito a capacidades de carga térmica e janelas de atendimento.
   - Distribuição de urgência clínica e minimização de tempo máximo de rota (*makespan*).
   - Atribuição estrita de veículos e balanceamento de prioridades em 3 níveis (Urgência Máxima, Alta, Regular).
   - Consideração de tempos de permanência (*dwell time*) e fatores de tráfego.
3. `backend/tests/test_traffic_model.py` (4 testes):
   - Modelagem de multiplicadores de tráfego dinâmico por portes de cidade (Metrópoles, Capitais, Cidades Médias).
   - Diferenciação precisa de horários de pico (07:00-09:30 e 17:30-19:30) vs. horários de entrepico.
   - Atenuação de congestionamento em corredores expressos e anéis rodoviários.
   - Parsing e formatação de relógios de trânsito (HH:MM).
4. `backend/tests/test_osrm_cache.py` (2 testes):
   - Persistência e integridade do banco SQLite local de coordenadas (`geo_cache.db`).
   - Validação dimensional e consistência das matrizes $N \times N$ retornadas pelo provedor OSRM com tolerância a falhas.
5. `backend/tests/test_routes_api.py` (4 testes):
   - Endpoint de cenário demonstrativo (`GET /api/v1/routes/demo-scenario`).
   - Otimização assíncrona de rotas (`POST /api/v1/routes/optimize`).
   - Geração de instruções ao motorista (`POST /api/v1/routes/instructions`) e relatório executivo (`POST /api/v1/routes/report`).
   - Geração de laudo explicativo de diagnóstico (`POST /api/v1/anamnesis/explain-diagnosis`).
6. `backend/tests/test_llm_governance.py` (5 testes):
   - Bloqueio de injeção de prompt (Prompt Security Guard) em português e inglês.
   - Cache semântico de similaridade para chamadas de LLM.
   - Imposição de System Prompts estritamente em inglês para maior determinismo e economia de tokens.
   - Cadeias de fallback com degradação graciosa para geradores heurísticos especialistas.
   - Validação de segurança e formatação dos laudos clínicos e instruções logísticas.

### Como Executar a Suíte Completa:
```bash
cd backend
python -m pytest tests/ -v
```
**Resultado Oficial:** 27 testes aprovados (100% de sucesso em ~50s).

