# HealthAI - Plataforma de Diagnóstico Multimodal

*Read this in other languages: [English](README_en.md) | [Português](README.md)*

Bem-vindo ao repositório do **HealthAI**. Desenvolvi este projeto como um objeto de estudo intensivo para explorar a convergência entre Engenharia de Software Moderna e Inteligência Artificial Multimodal.

O objetivo da plataforma é atuar como um assistente de triagem médica. Diferente de projetos tradicionais de Ciência de Dados que rodam apenas em planilhas ou blocos de notas, este é um **produto de software de ponta a ponta**, com um Frontend limpo e um Backend estruturado pronto para a internet.

## 📚 Guia de Estudos e Documentação por Fases

Como este repositório é o meu guia de estudos e entrega dos Tech Challenges, a documentação está organizada de forma estruturada:

### Documentação Técnica Principal:
1. [Visão Geral e Arquitetura Serverless](docs/1-visao-geral-arquitetura.md) *(Completado com Fase 2)*
2. [Deep Dive: Motor de Inteligência Artificial](docs/2-inteligencia-artificial.md) *(Completado com Fase 2)*
3. [Backend e FastAPI](docs/3-backend-fastapi.md) *(Completado com Fase 2)*
4. [Frontend e Angular](docs/4-frontend-angular.md) *(Completado com Fase 2)*
5. [MLOps e Ciclo de Vida do Treinamento](docs/5-mlops-treinamento.md) *(Completado com Fase 2)*
6. [Dados de Teste Sintéticos e Roteamento](docs/6-exemplos-testes.md) *(Completado com Fase 2)*

### Entregas Específicas por Fase:
- **Fase 1 (Diagnóstico Multimodal de Saúde):**
  - [Relatório Técnico Oficial da Fase 1](docs/fase1/relatorio-tecnico-fase1.md)
- **Fase 2 (Algoritmos Genéticos e Roteamento Médico):**
  - [Relatório Técnico Oficial da Fase 2](docs/fase2/relatorio-tecnico-fase2.md)
  - [Comparativo Antes e Depois: GridSearch (Fase 1) vs. Algoritmos Genéticos (Fase 2)](docs/fase2/comparativo-antes-depois-fase1-fase2.md)
  - [Roteiro de Gravação do Vídeo de Demonstração (YouTube/Vídeo)](docs/fase2/roteiro-video-apresentacao.md)
  - [Benchmarks e Comparativo dos 3 Experimentos de AG](docs/fase2/benchmarks-experimentos-ag.md)

---

## 🔬 Destaques da Fase 2 (Novas Funcionalidades)

### 1. Otimização Hiperparamétrica por Algoritmos Genéticos (Projeto 1)
- Otimização bio-inspirada para os modelos de triagem clínica (Câncer de Mama e SOP).
- **Função Fitness Médica:** $0.70 \times F_2\text{-Score} + 0.20 \times \text{Recall} + 0.10 \times \text{Acurácia}$ com penalidade de complexidade, priorizando a erradicação de Falsos Negativos.
- **3 Experimentos Sistemáticos:** Ganho de **+5.8% em Recall** e **+4.7% em $F_2$-Score** sobre o Baseline do GridSearch da Fase 1.
- **Laudos Médicos via LLM:** Endpoint `POST /api/v1/anamnesis/explain-diagnosis` gerando explicações clínicas detalhadas para o médico.

### 2. Sistema de Roteamento Médico com Grafos Reais OSRM (Projeto 2)
- Nova rota dedicada no Frontend: **`/routes`** (`http://localhost:4200/routes`).
- **OpenStreetMap & OSRM (Custo Zero de API):** Cálculo de matrizes de tempo e distância viária ponderada sem risco de estouro de cota e sem necessidade de chaves de API pagas.
- **Cache Local SQLite Inteligente (`geo_cache.db`):** Resposta instantânea (< 1ms) para pares geográficos já consultados.
- **Algoritmo Genético VRP (Vehicle Routing Problem):** Resolução de rotas com janelas de tempo, prioridade clínica de pacientes (urgência) e penalidade por atraso.
- **Mapa Interativo Leaflet.js:** Visualização em tempo real de pontos de atendimento, ordem de paradas e polylines viárias reais.
- **Assistente LLM para Equipe de Campo e Relatório Executivo Hospitalar:** Suporte a chat operacional e geração de relatório para auditoria de gestão de saúde pública.

---

## 🚀 Como Executar o Projeto Localmente

O repositório é um **Monorepo**, contendo tanto o Frontend quanto o Backend. Você precisará de dois terminais abertos para rodar a aplicação completa.

### 1. Rodando o Backend (API e Motor de IA)
O Backend exige Python instalado na sua máquina (versão 3.9+ recomendada).

```bash
# 1. Acesse a pasta do backend
cd backend

# 2. (Opcional, mas recomendado) Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# 4. Instale as dependências pesadas (PyTorch, FastAPI, Pandas, etc)
pip install -r requirements.txt

# 5. (Opcional) Executar os 3 experimentos do Algoritmo Genético
python training_scripts/train_genetic_hyperopt.py

# 6. Rodar os testes automatizados da Fase 1 e Fase 2 (11 testes)
pytest tests/ -v

# 7. Inicie o servidor FastAPI na porta 8000
python -m uvicorn app.main:app --reload
```
A API estará rodando em `http://localhost:8000`. Você pode acessar a documentação interativa Swagger em `http://localhost:8000/docs`.

### 2. Rodando o Frontend (Interface de Usuário)
O Frontend exige Node.js (versão 18+) e o Angular CLI instalados.

```bash
# 1. Acesse a pasta do frontend
cd frontend

# 2. Instale as dependências do Node
npm install

# 3. Inicie o servidor de desenvolvimento do Angular
npm start
```
A interface gráfica abrirá automaticamente no seu navegador em `http://localhost:4200`:
- **Dashboard de Diagnóstico Multimodal:** `http://localhost:4200/dashboard`
- **Módulo de Roteamento Médico (Fase 2):** `http://localhost:4200/routes`
- **Painel Administrativo e Auditoria de AG:** `http://localhost:4200/admin`

---

## 🛠 Tecnologias Utilizadas
*   **Algoritmos Genéticos & IA**: Algoritmos Genéticos customizados (DEAP / Custom), PyTorch (Visão ResNet-18), Scikit-Learn (Random Forest, XGBoost), LLMs (Google Gemini 1.5 Flash / OpenAI GPT-4o-mini).
*   **Logística & Geo**: OSRM (Open Source Routing Machine), OpenStreetMap, Leaflet.js, SQLite Geo Caching.
*   **Backend**: Python 3.12, FastAPI, Pydantic v2, Uvicorn, Pytest.
*   **Frontend**: Angular 18 (Standalone Components), Leaflet.js, RxJS, SCSS (Design System BEM).
