# Regras do Agente (Workspace Customizations)

## Tecnologias e Padrões
- **Frontend**: O frontend DEVE ser desenvolvido em Angular (versão standalone, sem ngModules), utilizando SCSS para a estilização. Ferramentas de estilização (como TailwindCSS ou Bootstrap) não devem ser adicionadas, devendo-se utilizar SCSS puro (BEM e variáveis CSS).
- **Backend / Microserviço de AI**: O backend que provê a inteligência artificial DEVE ser desenvolvido em Python utilizando FastAPI.
- **Armazenamento**: O armazenamento de imagens para processamento (se necessário) deve utilizar as abstrações para o Google Cloud Storage (GCS). O sistema é 100% stateless e não utilizará bancos de dados relacionais ou não relacionais.
- **Estrutura de Repositório**: Monorepo. Mantenha os serviços em pastas separadas: `frontend` e `backend`.
## Arquitetura de Baixo Custo (GCP)
Sempre considere que a aplicação será hospedada seguindo uma arquitetura de baixíssimo custo (Free Tier):
1. **Frontend**: Firebase Hosting (CDN rápida).
2. **Backend (FastAPI)**: Google Cloud Run (modelos quantizados e compactos, via ONNX/Int8, utilizando CPU, escala a zero).

*Sempre verifique o arquivo `docs/arq-IA.md` para mais contexto arquitetural.*
