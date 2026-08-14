# 1. Visão Geral e Arquitetura

*Read this in other languages: [English](../docs_en/1-visao-geral-arquitetura.md) | [Português](1-visao-geral-arquitetura.md)*

Este documento explica as escolhas arquiteturais fundamentais que tomei para construir a plataforma **HealthAI**. Como desenvolvi este projeto sozinho com foco em estudos e eficiência de custos, optei por uma infraestrutura **Serverless** (Sem Servidor) no Google Cloud Platform (GCP).

O objetivo principal desta arquitetura é garantir **baixíssimo custo**, alta disponibilidade e uma separação clara de responsabilidades (Frontend vs Backend).

---

## 1.1. O Problema das Arquiteturas Tradicionais
Em sistemas tradicionais de Machine Learning (ML), empresas alugam máquinas robustas com GPUs e bancos de dados gerenciados (como PostgreSQL ou Kubernetes) que ficam ligados 24 horas por dia. 

Como este é um projeto acadêmico/pessoal, pagar centenas de dólares mensais apenas para manter os modelos de IA disponíveis não faz sentido. 

## 1.2. A Solução: Arquitetura Serverless "Low-Cost"
Para resolver o problema do custo, desenhei uma arquitetura **100% Serverless** baseada nos *Free Tiers* (Níveis Gratuitos) do Google Cloud.

Neste modelo, eu só "pago" (ou consumo cota gratuita) nos exatos milissegundos em que uma requisição está sendo processada. Se ninguém estiver acessando o sistema de madrugada, as instâncias são desligadas (Scale to Zero).

A divisão de responsabilidades ficou da seguinte forma:

1.  **Frontend (Angular)** hospedado no **Firebase Hosting**.
2.  **Backend e Motor de IA (FastAPI)** hospedado no **Google Cloud Run**.

---

## 1.3. Por que Angular no Frontend?
Escolhi o Angular por ser um framework extremamente estruturado e robusto.
Diferente de gerar as telas dentro do Python (como usando Jinja2 ou Django Templates), o Angular me permite criar uma **Single Page Application (SPA)**. 

Isso significa que o navegador baixa todo o código HTML/CSS/JS de uma vez. Quando o paciente navega entre as telas de Anamnese ou Dashboard, a transição é instantânea e assíncrona, sem recarregar a página.

**Hospedagem (Firebase Hosting):** 
Como o Angular gera apenas arquivos estáticos no final do processo de *build*, eu não preciso de um servidor rodando. Hospedo esses arquivos estáticos no Firebase Hosting, que tem um nível gratuito generoso, CDN global e certificado SSL configurado automaticamente.

---

## 1.4. Por que FastAPI no Backend?
O coração da plataforma é o motor de Inteligência Artificial. Eu precisava de um backend em Python (pois 99% das bibliotecas de ML como PyTorch, Scikit-Learn e Pandas são em Python).

Escolhi o **FastAPI** em vez de Flask ou Django pelos seguintes motivos:

1.  **Assíncrono por Padrão (ASGI):** O sistema se comunica pela internet com as APIs do Gemini e GPT. O FastAPI é excelente em não travar o servidor enquanto espera respostas lentas da rede.
2.  **Validação Estrita (Pydantic):** Em sistemas de saúde, dados errados geram diagnósticos perigosos. O FastAPI valida os tipos de dados automaticamente usando o Pydantic, rejeitando requisições malformadas instantaneamente.
3.  **Velocidade:** É um dos frameworks Python mais rápidos disponíveis, rivalizando com NodeJS e Go.

**Hospedagem (Cloud Run):**
Coloco esse servidor FastAPI dentro de um *Container Docker* e faço o deploy no **Google Cloud Run**. O Cloud Run cobra apenas pelos segundos em que a API está processando a inferência médica.

---

## 1.5. Arquitetura Stateless (Sem Estado)
Para manter tudo simples e barato, tomei uma decisão arquitetural crucial: **o sistema é Stateless**.

Isso significa que:
*   Eu **não** possuo um banco de dados SQL (como MySQL ou Postgres).
*   Eu **não** guardo histórico de diagnósticos dos pacientes a longo prazo.
*   Eu **não** salvo senhas nem faço gestão pesada de contas de usuários no banco.

A plataforma atua puramente como uma "Calculadora Avançada". O Angular envia os dados clínicos; o FastAPI recebe, carrega os pesos dos modelos na RAM, faz o cálculo, devolve a resposta final de diagnóstico, e imediatamente **esquece** quem fez a requisição.

Essa abordagem foca 100% no algoritmo de Inteligência Artificial, reduzindo enormemente a superfície de vulnerabilidade (vazamento de dados médicos) e o custo de infraestrutura.

---

**Próximo Passo:**
Para entender profundamente como a IA toma a decisão por trás dos panos, leia o documento [2-inteligencia-artificial.md](./2-inteligencia-artificial.md).
