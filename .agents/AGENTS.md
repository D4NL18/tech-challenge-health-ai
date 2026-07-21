# Regras do Agente (Workspace Customizations)

## Tecnologias e Padrões
- **Frontend**: O frontend DEVE ser desenvolvido em Angular (versão standalone, sem ngModules), utilizando SCSS para a estilização. Ferramentas de estilização (como TailwindCSS ou Bootstrap) não devem ser adicionadas, devendo-se utilizar SCSS puro (BEM e variáveis CSS).
- **Backend Core**: O backend DEVE ser desenvolvido em Java Spring Boot.
- **Microserviço de AI**: O microserviço de inteligência artificial DEVE ser desenvolvido em Python utilizando FastAPI.
- **Banco de Dados**: PostgreSQL (que será hospedado em instâncias e2-micro do GCP para baixo custo).
- **Armazenamento**: O armazenamento de imagens deve utilizar as abstrações para o Google Cloud Storage (GCS).
- **Estrutura de Repositório**: Monorepo. Mantenha os serviços em pastas separadas, preferencialmente `frontend`, `backend` e `ai-service`.

## Arquitetura de Baixo Custo (GCP)
Sempre considere que a aplicação será hospedada seguindo uma arquitetura de baixíssimo custo (Free Tier):
1. **Frontend**: Firebase Hosting (CDN rápida).
2. **Backend**: Google Cloud Run (escala a zero).
3. **Microserviço IA**: Google Cloud Run (modelos quantizados e compactos, via ONNX/Int8, utilizando CPU).
4. **Banco de Dados**: Instância manual em Compute Engine (e2-micro).

*Sempre verifique o arquivo `docs/arq-IA.md` para mais contexto arquitetural.*
