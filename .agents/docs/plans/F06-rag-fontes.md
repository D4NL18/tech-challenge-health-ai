# F6 — RAG de Protocolos: Vetorização, Busca Híbrida e Rastreabilidade de Fonte (R3.3, E2)

> [Índice](INDEX.md) · Anterior: [← F5](F05-seguranca-auditoria.md) · Próxima: [F7 →](F07-assistente-langchain.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md) · [Estratégia de vetorização](00-vetorizacao-rag.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Migrar a base de conhecimento do Chroma local para **pgvector no Supabase**, aplicando a [estratégia de vetorização](00-vetorizacao-rag.md): extração limpa, chunking por seção com cabeçalho contextual, modelo de embeddings escolhido por ablação no gold set, busca híbrida (vetor + texto em português) e fonte exata em cada trecho, sem quebrar a triagem da Fase 1.

## Ponto de partida
- **Projeto:** `ingest_docs.py` (`PyPDFLoader`, trechos de 1000/200 caracteres, `all-MiniLM-L6-v2`, Chroma na coleção `langchain`, com o binário `vector_db/` no git e na imagem); `query_rag.get_rag_context()` (**usado por `ml/text.py`**, assinatura e saída preservadas) e `query_rag()` (CLI); o modelo de embeddings é recriado a cada chamada e baixado do Hugging Face a cada cold start; `PromptSecurityGuard.sanitize_delimiters()`.
- **Fases anteriores:** `knowledge_base/internal_protocols/*.md` (F1); Supabase com Alembic e as extensões `vector` e `unaccent` (F0/F4); `pii_masker`, `Citation` e auditoria (F5); `settings.embedding_model`, `corpus_version` e `rag_min_score` (F0).

## Etapas e agentes
- **Etapas ativas:** 2 (estratégia de vetorização, gold set, regra de escolha e ADR-013), 3, 4 (injeção indireta e acesso ao banco). Sem checkpoint: a regra de escolha é pré-registrada e a decisão sai da medição.
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `ai-specialist` | Dono: estratégia de vetorização, gold set, grade de ablação, regra de escolha, execução da ablação |
| `dba` | Tabela `protocol_chunks`, índices, função SQL híbrida `match_protocol_chunks`, papéis e RLS |
| `tester` (×2) | Extração, chunking e ingestão / retriever híbrido em Postgres local, compatibilidade e falhas |
| `developer` (×2) | Extração, chunking, embeddings e ingestão / retriever, reescrita de consulta, formatter e compatibilidade |
| `security` | Injeção indireta pelo contexto recuperado; papéis do banco (backend só leitura) |
| `reviewer` | Quality Gate |

- **Não acionados:** `privacy-officer` (corpus de diretrizes públicas + protocolos sintéticos; a consulta passa pelo `pii_masker` antes de virar vetor), `architect` (o ADR-013 é do `ai-specialist`), `designer`/`ux-reviewer`, `devops` (a ingestão é uma CLI offline).

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `ai-specialist` | ADR-013, gold set (80–100 perguntas, desenvolvimento 70% / teste 30%), grade de ablação e regra de escolha | `.agents/docs/adr/ADR-013-vetorizacao.md`, `backend/evaluation/datasets/rag_gold.jsonl`, `knowledge_base/config/vectorization.yaml` |
| | `dba` | Migração da tabela `protocol_chunks`, índices, função `match_protocol_chunks` (vetor top-20 + texto top-20 + RRF), papéis e RLS | `backend/migrations/versions/0002_protocol_chunks.py`, `.agents/docs/db/knowledge_base.md` |
| **R2** (TDD) | `tester#1` | Extração (cabeçalho/rodapé repetido, hifenização), chunking (limite de tokens, sem cortar frase, cabeçalho contextual), ids estáveis e ingestão idempotente, com 5 documentos de fixture | `tests/knowledge_base/*` |
| | `tester#2` | Retriever híbrido contra Postgres local com pgvector (marker `integration`), filtros, limiar, formatter, compatibilidade da Fase 1, banco indisponível → lista vazia | `tests/assistant/retrieval/*` |
| **R3** (código) | `developer#1` | 6.1–6.4 | `knowledge_base/{extract,chunking,ingest_docs}.py`, `app/assistant/retrieval/embeddings.py` |
| | `developer#2` | 6.5–6.7 | `app/assistant/retrieval/{protocol_retriever,query_rewriter,context_formatter}.py` |
| **R4** (execução) | `ai-specialist` ∥ `developer#2` | 6.8: ablação no computador local e escolha pela regra, depois ingestão da configuração vencedora no Supabase ∥ 6.9 compatibilidade e remoção do Chroma + 6.10 bootstrap | `knowledge_base/evaluate_retrieval.py`, `evaluation/results/rag_ablation.*` ∥ `knowledge_base/query_rag.py`, `bootstrap.py`, `requirements.txt`, `Dockerfile` |
| **R5** (Etapa 4) | `security` ∥ `reviewer` ∥ `tester` | Injeção indireta e papéis do banco ∥ revisão ∥ suíte + Auto-Healer | — |
| **R6** (Fechamento) | `ai-specialist` ∥ Orquestrador | Seção "Base de conhecimento e vetorização" ∥ merge + `STATE.md` | `docs/fase3/secoes/03-rag.md` |

## Código passo a passo
- [ ] **6.1 — `knowledge_base/extract.py`:** PDF → texto por página (`pypdf`; `pdfplumber` para tamanho de fonte quando ajudar a achar títulos); remoção de linhas repetidas em mais de 50% das páginas (cabeçalho/rodapé); junção de hifenização; normalização unicode; tabelas mantidas como bloco; markdown dos protocolos internos com os cabeçalhos como caminho de seção. Saída: `Section{doc_id, title, section_path, page_start, page_end, text, source_type, doc_version}`.
- [ ] **6.2 — `knowledge_base/chunking.py`:** divisão por seção e depois por **tokens do tokenizer do modelo de embeddings** (tamanho e sobreposição vindos do `vectorization.yaml`; ponto de partida 350/50), sem cortar frases; **cabeçalho contextual** `"Documento: … | Seção: …"` só no texto vetorizado; `chunk_id = sha1(source_file|section_path|texto)[:16]`.
- [ ] **6.3 — `app/assistant/retrieval/embeddings.py`:** `EmbeddingModel` (sentence-transformers) com os prefixos de cada modelo (`query:`/`passage:` no E5), vetores normalizados, lote na ingestão e cache LRU de consultas no backend. O modelo escolhido é baixado na build da imagem (`HF_HUB_OFFLINE=1` em produção).
- [ ] **6.4 — `knowledge_base/ingest_docs.py` (CLI offline):** extrai → divide → vetoriza → `upsert` em `protocol_chunks` por `chunk_id` numa `corpus_version` nova → smoke de recuperação com o gold set → ativa a versão → apaga a anterior. O backend nunca vetoriza documentos.
- [ ] **6.5 — `protocol_retriever.py`:** `ProtocolRetriever(ProtocolRetrieverPort).retrieve(query, k=3, source_types=None)` → reescrita da consulta → embedding → chamada parametrizada a `match_protocol_chunks` (híbrida ou só vetor, conforme a ablação) → limiar `rag_min_score` → rerank opcional atrás de flag → `list[RetrievedChunk]`; evento `RETRIEVAL`. Banco indisponível → `[]` + `RETRIEVAL_FAILED`, sem erro 500.
- [ ] **6.6 — `query_rewriter.py`:** `pii_masker` na pergunta; expansão de siglas pelo glossário (BI-RADS, SOP/PCOS…); com paciente, acrescenta termos clínicos do snapshot (diagnósticos, exames pendentes, BI-RADS), **nunca identificadores**.
- [ ] **6.7 — `context_formatter.py`:** `format_protocol_context(chunks)` → `<medical_context><doc id="…" source="…" section="…" page="…">texto</doc>…</medical_context>`, com `sanitize_delimiters` em cada trecho (defesa contra injeção indireta).
- [ ] **6.8 — `knowledge_base/evaluate_retrieval.py`:** roda a grade do `vectorization.yaml` (tamanho × sobreposição × modelo × híbrida × rerank) no conjunto de desenvolvimento; mede recall@3, MRR, nDCG@5, latência e memória; aplica a regra pré-registrada; confirma a configuração vencedora no conjunto de teste; exporta `evaluation/results/rag_ablation.{json,md,png}`.
- [ ] **6.9 — Compatibilidade e remoção do Chroma:** `get_rag_context(query)` reimplementado sobre o `ProtocolRetriever` (mesma assinatura e saída em string; só `source_type=guideline`, só vetor, k=3, sem limiar); `query_rag()` imprime as fontes; saem `chromadb`, `langchain-chroma`, o `knowledge_base/vector_db/` e a cópia dele no `Dockerfile`.
- [ ] **6.10 — Bootstrap:** `init_assistant_resources()` passa a chamar `init_retriever()`, que carrega o modelo de embeddings uma única vez.

## Critérios de aceite

Todo trecho com `source_file`, `section_path`, página e `chunk_id`; configuração de vetorização escolhida pela regra pré-registrada, com a ablação documentada; recall@3 no conjunto de teste registrado; recuperação ≤ 300 ms; modelo de embeddings carregado uma vez e embutido na imagem; `test_llm_governance.py` (Fase 1) verde; conteúdo malicioso neutralizado; banco indisponível não derruba o assistente nem a triagem; Chroma removido do repositório e da imagem.

## Audit

(1) o mesmo PDF ingerido 2× gera os mesmos `chunk_id`; (2) cabeçalho/rodapé repetido não aparece em nenhum trecho; (3) nenhum trecho passa do limite de tokens nem corta frase; (4) "rastreamento para BI-RADS 3" traz trecho com fonte, seção e página; (5) pergunta com "SOP" acha trechos que só dizem "síndrome dos ovários policísticos"; (6) pergunta fora do corpus → lista vazia; (7) trecho com `</medical_context>` → neutralizado; (8) banco fora do ar → `[]` + `RETRIEVAL_FAILED`, sem 500; (9) regressão de `get_rag_context`; (10) uma `corpus_version` nova só é ativada depois do smoke; (11) pergunta com CPF → mascarado antes do embedding; (12) o papel do backend não consegue escrever em `protocol_chunks`.

## Commits

`docs(adr): registra estrategia de vetorizacao e regra de escolha` · `feat(db): cria tabela de trechos com pgvector e busca hibrida` · `feat(rag): adiciona extracao limpa e chunking por secao com cabecalho contextual` · `feat(rag): adiciona ingestao versionada no supabase` · `feat(rag): adiciona retriever hibrido com reescrita de consulta` · `test(rag): adiciona ablacao de vetorizacao no gold set` · `refactor(rag): reimplementa get_rag_context e remove o chroma`

## Entrega para a F7/F8

`ProtocolRetriever`, `format_protocol_context` e a configuração de vetorização vencedora; gold set (parte de teste) e resultados da ablação para a F10.