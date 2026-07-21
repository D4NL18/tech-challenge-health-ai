# Plataforma de Anamnese e Diagnóstico Virtual - Fase 1

Este projeto é uma plataforma de triagem e diagnóstico médico com suporte de Inteligência Artificial, focado na saúde e segurança da mulher.
O sistema é estruturado como um monorepo para acomodar:

*   **Frontend (Angular)**: Interface do usuário para a anamnese e dashboard de resultados.
*   **Backend (FastAPI)**: Serviço único de processamento e inteligência artificial rodando de forma stateless.

## Documentação da Arquitetura
Veja os detalhes em [docs/arq-IA.md](docs/arq-IA.md).

## Como Executar o Backend (API)
1. Acesse o diretório: `cd backend`
2. Crie e ative um ambiente virtual e instale as dependências: `pip install -r requirements.txt`
3. Inicie o servidor: `uvicorn app.main:app --reload`
4. Acesse a documentação Swagger em `http://localhost:8000/docs`
