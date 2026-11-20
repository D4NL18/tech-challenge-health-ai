# F1 — Coleta e Geração do Corpus (R1.1–R1.3, E4)

> [Índice](INDEX.md) · Anterior: [← F0](F00-fundacao.md) · Próxima: [F2 →](F02-anonimizacao-curadoria.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Montar o corpus bruto do fine-tuning: PubMedQA, MedQuAD filtrado e um corpus interno sintético em pt-BR (protocolos, FAQ de médicos, laudos, receitas e procedimentos).

## Ponto de partida
- **Projeto:** 5 PDFs em `knowledge_base/docs/`; o padrão `PyPDFLoader` + `RecursiveCharacterTextSplitter` de `ingest_docs.py`; a coleção Chroma existente em `knowledge_base/vector_db/` (ancora as respostas da FAQ nos protocolos, com fonte e página); `google-genai` (mesmo padrão de chamada de `clinical_llm._call_gemini`).
- **F0:** `requirements-training.txt` (`datasets`), ADR-005 (fontes, volumes, licenças), `tests/finetuning/`.

## Etapas e agentes
- **Etapas ativas:** 2 (especificação de coleta e geração), 3, 4. Sem checkpoint (segue o ADR-005 aprovado).
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `ai-specialist` | Dono: schema do corpus, filtros, prompts de geração, templates clínicos, revisão qualitativa, execução da geração |
| `tester` | Testes de schema, idempotência, filtros e regra P-040 nas receitas |
| `developer` (×2) | Coletores públicos / geradores sintéticos |
| `reviewer` | Quality Gate |

- **Não acionados:** `privacy-officer` (dados públicos + sintéticos com PII **fictícia** plantada de propósito; a auditoria de privacidade é na F2, onde a anonimização acontece), `security`, `dba`, `architect` (estrutura já definida no ADR-005), `designer`/`ux-reviewer`, `devops` (nada publicado).

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `ai-specialist` | `CorpusRecord` (1.1), `FOCUS_KEYWORDS`, prompts de geração, templates de laudo/receita/procedimento, metas de volume | `finetuning/schemas.py`, `finetuning/synthetic/prompts/*.md`, `finetuning/synthetic/templates/*.yaml` |
| **R2** (Etapa 3 — TDD) | `tester#1` | Testes de `io`, `pubmedqa`, `medquad` (download mockado) + fixture `corpus_sample.jsonl` (20 registros com PII fictícia) | `tests/finetuning/test_io.py`, `test_collectors.py`, `fixtures/` |
| | `tester#2` | Testes dos geradores sintéticos (determinismo por seed, P-040 nas receitas, referências presentes) | `tests/finetuning/test_synthetic.py` |
| **R3** (Etapa 3 — código) | `developer#1` | 1.2, 1.3, 1.4 | `finetuning/io.py`, `finetuning/collectors/*` |
| | `developer#2` | 1.5, 1.6, 1.7 | `finetuning/synthetic/*.py` |
| **R4** (execução) | `ai-specialist` ∥ `developer#1` | Rodar a geração com LLM (1.5, 1.6) e revisar 30 amostras ∥ 1.8 (`build_corpus.py`) | `data/finetuning/synthetic/*.jsonl` ∥ `finetuning/build_corpus.py` |
| **R5** (Etapa 4) | `reviewer` ∥ `tester` | Revisão ∥ suíte + Auto-Healer | — |
| **R6** (Fechamento) | `ai-specialist` ∥ Orquestrador | Seção "Dados – coleta" ∥ merge + `STATE.md` | `docs/fase3/secoes/01-dados.md` |

## Código passo a passo
- [ ] **1.1 — `finetuning/schemas.py`:** `CorpusRecord{id, source, task_type, instruction, input, output, references: list[SourceRef], language, license}`; `TaskType` enum (`qa_biomedical`, `qa_health`, `protocol_qa`, `faq_medico`, `laudo`, `receita_sugestao`, `procedimento`).
- [ ] **1.2 — `finetuning/io.py` + `collectors/base.py`:** `read_jsonl`, `write_jsonl` (ordenado por `id`, idempotente), `sha256_file`, `write_manifest`; `CorpusCollector(Protocol)` com `name`, `download(raw_dir)` e `to_records(raw_path)`.
- [ ] **1.3 — `collectors/pubmedqa.py`:** `PubMedQACollector` → `datasets.load_dataset("qiaojin/PubMedQA", "pqa_labeled")` → `instruction = question`, `input = contexts`, `output = final_decision + long_answer`.
- [ ] **1.4 — `collectors/medquad.py`:** download do repositório (zip) → parse de `QAPair` com `xml.etree.ElementTree` → filtro `FOCUS_KEYWORDS` → **descarta QAs sem resposta** (coleções com respostas removidas por direitos autorais).
- [ ] **1.5 — `synthetic/protocol_qa_generator.py`:** `ProtocolQAGenerator(seed)` → fatia os PDFs → amostra chunks → Gemini gera 2–3 pares pergunta/resposta em pt-BR, estritamente do trecho → `references=[{source_file, page}]`. **Saída versionada** (LLM não é determinístico). Gerado no **free tier do Gemini** (D14), com cache por chunk, backoff e geração espalhada em dias se bater o limite diário.
- [ ] **1.6 — `synthetic/physician_faq_generator.py`:** tópicos × perfis (`templates/faq_topics.yaml`) → perguntas → resposta com contexto buscado direto no Chroma existente (`similarity_search` devolve `source` e `page` nos metadados; o `get_rag_context()` legado descarta as fontes e não serve aqui) → `faq_medico` com referências.
- [ ] **1.7 — `synthetic/document_templates_generator.py`** (determinístico, sem LLM): `MammographyReportTemplate` (BI-RADS 0–6), `PelvicUltrasoundReportTemplate` (SOP), `PrescriptionSuggestionTemplate` (sempre com o bloco `[SUGESTÃO — VALIDAÇÃO MÉDICA OBRIGATÓRIA]`, P-040), `ProcedureTemplate`. PII fictícia plantada em ~10%. Também exporta os templates em markdown para `knowledge_base/internal_protocols/` (**usado na F6**).
- [ ] **1.8 — `build_corpus.py`:** `python -m finetuning.build_corpus --sources … --out data/finetuning/corpus_raw.jsonl` + `reports/corpus_stats.json`.

> **Termos de uso:** as saídas do Gemini viram dado de treino. O ADR-005 e o dataset card registram a conferência dos termos da Gemini API sobre uso de saídas para treinar modelos (uso acadêmico, sem fins comerciais). Alternativa sem essa dependência e sem limite diário: gerar com um modelo aberto maior rodando localmente (ex.: 7–8B em Q4 no `llama.cpp`, com parte das camadas na GPU), mais lento.

## Critérios de aceite

Coletores idempotentes; 100% dos registros validam no schema; licença e versão no manifest; zero receitas sem a marca de validação; `internal_protocols/` gerado.

## Audit

(1) rodar 2× → mesmo hash do corpus; (2) validação de schema; (3) regex P-040 = 0 violações; (4) download real só com o marker `slow`.

## Commits

`feat(finetuning): adiciona schema do corpus e io idempotente` · `feat(finetuning): coleta pubmedqa e medquad filtrado` · `feat(finetuning): gera qa sintetico de protocolos e faq medica` · `feat(finetuning): gera templates de laudos, receitas e procedimentos (P-040)`

## Entrega para a F2

`corpus_raw.jsonl`, `corpus_stats.json`, fixture com PII fictícia.
