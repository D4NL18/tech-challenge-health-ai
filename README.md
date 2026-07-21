# Plataforma de Anamnese e Diagnóstico Virtual - Fase 1

Este projeto é uma plataforma de triagem e diagnóstico médico com suporte de Inteligência Artificial, focado na saúde e segurança da mulher.
O sistema é estruturado como um monorepo para acomodar:

*   **Frontend (Angular)**: Interface do usuário para a anamnese e dashboard de resultados.
*   **Backend (Spring Boot)**: API Core de gerenciamento. *(Em breve)*
*   **AI Engine (FastAPI)**: Microsserviço de inteligência artificial com modelos de Machine Learning para processamento de dados médicos. *(Em breve)*

## Documentação da Arquitetura
Veja os detalhes em [docs/arq-IA.md](docs/arq-IA.md).

## Como Executar o Frontend
1. Acesse o diretório: `cd frontend`
2. Instale as dependências: `npm install`
3. Execute a aplicação: `npm run start` ou `ng serve`
4. Acesse em `http://localhost:4200`
