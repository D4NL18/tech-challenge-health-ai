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

**Próximo Passo:**
Para entender como estruturei o Frontend que consome essa API, acesse [4-frontend-angular.md](./4-frontend-angular.md).
