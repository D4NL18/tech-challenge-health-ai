# 6. Exemplos de Testes Inéditos (Triagem)

*Read this in other languages: [English](../docs_en/6-exemplos-testes.md) | [Português](6-exemplos-testes.md)*

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

O projeto conta com uma suíte de testes automatizados com cobertura completa para os módulos da Fase 1 e Fase 2.

### Arquivos de Teste:
- `backend/tests/test_genetic_hyperopt.py`: Validação de mutação, crossover e convergência do Algoritmo Genético de Hiperparâmetros.
- `backend/tests/test_vrp_routing.py`: Validação de operadores VRP (Order Crossover OX, Swap/Inversion Mutation) e penalidades de prioridade/janela.
- `backend/tests/test_osrm_cache.py`: Validação do SQLite Geo Cache e resiliência com fallback Haversine.
- `backend/tests/test_routes_api.py`: Teste de integração assíncrono dos endpoints `/api/v1/routes/optimize`, `/assistant-chat` e `/generate-report`.

### Como Executar a Suíte:
```bash
cd backend
venv\Scripts\python -m pytest tests/ -v
```
**Resultado Homologado:** 11 testes aprovados (100% de sucesso).

