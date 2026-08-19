# HealthAI - Plataforma de Diagnóstico Multimodal

*Read this in other languages: [English](README_en.md) | [Português](README.md)*

Bem-vindo ao repositório do **HealthAI**. Desenvolvi este projeto como um objeto de estudo intensivo para explorar a convergência entre Engenharia de Software Moderna e Inteligência Artificial Multimodal.

O objetivo da plataforma é atuar como um assistente de triagem médica. Diferente de projetos tradicionais de Ciência de Dados que rodam apenas em planilhas ou blocos de notas, este é um **produto de software de ponta a ponta**, com um Frontend limpo e um Backend estruturado pronto para a internet.

## 📚 Guia de Estudos (Documentação)

Como este repositório é o meu guia de estudos, documentei absolutamente todas as decisões de arquitetura e código. Sugiro ler os documentos abaixo na ordem, pois eles contam a "história" de como o projeto foi construído:

1. [Visão Geral e Arquitetura Serverless](docs/1-visao-geral-arquitetura.md)
2. [Deep Dive: Motor de Inteligência Artificial](docs/2-inteligencia-artificial.md)
3. [Backend e FastAPI](docs/3-backend-fastapi.md)
4. [Frontend e Angular](docs/4-frontend-angular.md)
5. [MLOps e Ciclo de Vida do Treinamento](docs/5-mlops-treinamento.md)
6. [Dados de Teste Sintéticos](docs/6-exemplos-testes.md)
7. [Relatório Técnico](docs/relatorio-tecnico.md)

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

# 5. Gere o banco de dados vetorial local (RAG / ChromaDB) a partir dos PDFs médicos
python knowledge_base/ingest_docs.py

# 6. Inicie o servidor FastAPI na porta 8000
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
A interface gráfica abrirá automaticamente no seu navegador em `http://localhost:4200`.

---

## 🛠 Tecnologias Utilizadas
*   **Inteligência Artificial**: PyTorch (Visão), Scikit-Learn (Tabular), APIs do Google Gemini / OpenAI GPT (NLP).
*   **Backend**: Python, FastAPI, Pydantic, Uvicorn.
*   **Frontend**: Angular 18 (Standalone Components), RxJS, SCSS (Metodologia BEM).
