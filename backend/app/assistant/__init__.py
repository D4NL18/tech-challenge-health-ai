"""
Pacote `app.assistant`: núcleo do Assistente Médico da Fase 3 (portas e adaptadores).

O núcleo depende de ports; implementações concretas são ligadas em `bootstrap.py`, o ponto único
de ligação com o `app/main.py`. Subpacotes criados pelas fases seguintes (ARCHITECTURE.md 4.2):
`schemas/` e `ports.py` (F4–F8), `audit/` e `guardrails/` (F5), `retrieval/` (F6), `llm/` (F3/F7)
e `graph/` (F8). A F0 entrega só `errors.py` e `bootstrap.py`.
"""
