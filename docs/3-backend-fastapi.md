# 3. Backend e FastAPI (Engenharia de Software)

*Read this in other languages: [English](../docs_en/3-backend-fastapi.md) | [Português](3-backend-fastapi.md)*

Neste documento, vou focar puramente em Engenharia de Software. Explico como estruturei o Backend em Python para lidar com as chamadas de rede, gerenciar memória de forma inteligente e validar dados.

A estrutura do projeto segue o padrão **MVC (Model-View-Controller) adaptado para Serviços**, promovendo a separação de responsabilidades.

---

## 3.1. Estrutura de Diretórios e Responsabilidades

```text
backend/app/
├── main.py                    # Entrypoint: Liga o servidor, gerencia CORS e o ciclo de vida.
├── api/routers/anamnesis.py   # Controllers: Expõe os endpoints HTTP (as URLs da API).
├── models/schemas.py          # DTOs: Define os "moldes" estritos de entrada e saída (Pydantic).
├── services/inference.py      # Camada de Serviço (Facade): Orquestra os modelos de IA.
└── ml/                        # Motores de IA isolados.
    ├── tabular.py             
    ├── text.py              
    ├── vision.py              
    └── ensemble.py            
```

### O Fluxo de uma Requisição:
1. O Angular envia os dados.
2. O **Router** (`anamnesis.py`) recebe a chamada HTTP.
3. O **Schema** (`schemas.py`) valida se os dados estão corretos (ex: se "Idade" é um número inteiro).
4. Se válido, o Router joga o problema para o **Service** (`inference.py`).
5. O Service funciona como um gerente. Ele não sabe calcular nada, mas ele sabe chamar os **Especialistas de ML** (`ml/`).
6. Os modelos calculam as notas, o Service recebe de volta, e empacota num objeto JSON padronizado para o Frontend.

---

## 3.2. Gerenciamento de Memória (Lifespan / Cold Start)
**Arquivo de Referência:** `backend/app/main.py`

Esse é o conceito mais importante de performance da aplicação.
Modelos de Machine Learning (como uma rede neural PyTorch) são pesados. Eles dependem de matrizes matemáticas gigantes (pesos) salvas em arquivos `.pth` ou `.pkl` no HD.

Carregar gigabytes do HD para a Memória RAM é uma operação de I/O que demora *segundos*.
Se eu fizesse esse carregamento a cada vez que um paciente clicasse em "Diagnosticar", a API seria insuportavelmente lenta.

**A Solução:** Uso o recurso `@asynccontextmanager` do FastAPI chamado **Lifespan**.
Quando eu digito `npm start` (ou o Cloud Run liga o container), o `main.py` intercepta o evento de inicialização. Ele abre os arquivos `.pkl` e `.pth`, carrega as matrizes na RAM (Warm-up) e deixa lá. 
Quando as requisições chegam, a IA já está "acordada" e responde em milissegundos.

---

## 3.3. Validação Estrita de Dados (Pydantic)
**Arquivo de Referência:** `backend/app/models/schemas.py`

A principal vantagem do FastAPI sobre o Flask é a sua integração profunda com o **Pydantic**.
No `schemas.py`, eu crio Classes de Dados (DTOs - Data Transfer Objects). Eu defino exatamente quais campos o Frontend é obrigado a mandar, e qual o tipo deles (`str`, `int`, `float`, `Optional`).

Se o Frontend tentar enviar "vinte anos" num campo que espera o número `20`, o Pydantic intercepta o erro antes mesmo de chegar na Inteligência Artificial e já devolve um Erro 422 (Unprocessable Entity) avisando exatamente qual campo estava errado.

Isso previne que a plataforma quebre ou gere um diagnóstico bizarro por "sujeira" nos dados.

---

## 3.4. Multipart Form-Data vs JSON
**Arquivo de Referência:** `backend/app/api/routers/anamnesis.py`

Geralmente APIs REST usam o formato `application/json` para trafegar dados. Mas eu tenho um problema: **eu preciso enviar a foto do Raio-X**. 
JSON não foi feito para transmitir arquivos binários pesados de forma eficiente.

Para resolver isso, utilizo no Controller o padrão **Multipart/Form-Data**.
*   Eu recebo o arquivo de imagem puro no campo `image`.
*   Eu recebo todos os dados clínicos de texto no campo `anamnesis_data` na forma de uma grande String.
*   No Python, eu uso `json.loads` para converter essa String de volta pra um Dicionário, e passo pro Pydantic validar.

Assim, numa única requisição de rede, eu envio tanto os dados tabulares quanto a Imagem.

---

## 3.5. Evolução Fase 2: Roteador de Rotas Médicas (`routes_router.py`)
**Arquivo de Referência:** `backend/app/api/routers/routes_router.py`

Na Fase 2, adicionamos uma esteira completa de otimização logística médica através de endpoints assíncronos:
1. `POST /api/v1/routes/optimize`: Recebe lista de pontos de atendimento (depósito/posto de saúde e pacientes com prioridade clínica e janelas de atendimento), executa o algoritmo genético VRP sobre matriz OSRM real e devolve trajeto ótimo sequenciado com telemetria detalhada (distância em km, tempo em min, polyline codificada e waypoints ordenados).
2. `POST /api/v1/routes/assistant-chat`: Chat assistente especializado em logística de saúde para orientar a equipe médica em campo.
3. `POST /api/v1/routes/generate-report`: Gera relatório executivo para o comitê hospitalar com análise de custos, mitigação de riscos e impacto em vidas.

Adicionalmente, expandimos `anamnesis.py` com:
- `POST /api/v1/anamnesis/explain-diagnosis`: Geração de laudo médico explicativo detalhado via LLM (Gemini / OpenAI com fallback heurístico robusto).
- `GET /api/v1/anamnesis/admin/genetic-experiments`: Histórico comparativo dos 3 experimentos de calibração hiperparamétrica por Algoritmo Genético.

---

## 3.6. Camada Geo & Provedor OSRM com Cache SQLite Local
**Arquivos de Referência:** `backend/app/services/geo/osrm_provider.py` e `backend/app/services/geo/geo_cache.py`

Para evitar riscos de estouro de cota e custos com APIs pagas de mapas (como Google Maps), adotamos o **OSRM (Open Source Routing Machine) sobre OpenStreetMap**:
- **Consumo Zero de Cotas Pagas:** API pública aberta e gratuita com fallback automático para Geometria Haversine caso haja indisponibilidade de rede.
- **Cache Local SQLite (`backend/data/geo_cache.db`):** Armazena matrizes $N \times N$ de tempo/distância por chave hash das coordenadas geográficas. Quando a mesma região ou rota é recalculada, a consulta à internet é 0, respondendo em menos de 1ms.
- **Arquitetura em Duas Etapas:** O Algoritmo Genético roda centenas de milhares de iterações em memória RAM consumindo a matriz cached em microssegundos. Apenas a rota vencedora final faz 1 chamada de `/route/v1/driving` para obter a polyline de visualização.

---

## 3.7. LLM Clínico e de Logística com Resiliência Heurística
**Arquivos de Referência:** `backend/app/services/clinical_llm.py` e `backend/app/services/logistics_llm.py`

Integração de Modelos de Linguagem para auxílio à decisão médica e operacional:
- Suporte dinâmico a provedores modernos (Google Gemini `gemini-1.5-flash` / OpenAI `gpt-4o-mini`).
- **Resiliência Total:** Caso nenhuma API Key esteja configurada no ambiente, o sistema não quebra: ele aciona automaticamente geradores heurísticos especialistas que analisam regras clínicas (fatores de risco, exames laboratoriais, prioridades SUS) e diretrizes de rota, entregando laudos e respostas estruturadas de alta fidelidade técnica.

---

**Próximo Passo:**
Para entender como estruturei o Frontend que consome essa API, acesse [4-frontend-angular.md](./4-frontend-angular.md).
