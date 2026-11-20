# Contrato de API: Explicabilidade Clínica e Benchmarks de IA (Projeto 1)

> **Localização Mandatória:** `.agents/docs/api_contracts/clinical_explanation_contract.md`  
> **Responsável:** Arquiteto (`api-contract-expert`)  
> **Versão da API:** `v1`  
> **Base Path:** `/api/v1/models`

---

## 1. Endpoints

### 1.1 `POST /api/v1/models/explain-diagnosis`
Recebe as variáveis clínicas do paciente e as predições probabilísticas do modelo e gera um laudo médico estruturado em linguagem natural utilizando LLMs.

**Request Body Schema:**
```json
{
  "disease": "cancer",
  "patient_name": "Maria Silva",
  "patient_age": 48,
  "confidence_score": 0.84,
  "tabular_data": {
    "radius_mean": 17.99,
    "texture_mean": 10.38,
    "compactness_mean": 0.2776,
    "concavity_mean": 0.3001
  }
}
```

**Response 200 OK Schema:**
```json
{
  "success": true,
  "clinical_report": {
    "summary": "Paciente do sexo feminino, 48 anos, apresentando nódulo mamário com características morfológicas suspeitas.",
    "key_risk_factors": [
      "Concavidade média elevada (0.3001)",
      "Raio médio tumoral significativo (17.99 mm)",
      "Compacidade celular aumentada"
    ],
    "explanation": "O modelo identificou forte correlação estatística entre o padrão de concavidade acentuada e tecido maligno, resultando em risco estimado de 84%.",
    "recommendations": [
      "Encaminhamento urgente para biópsia por agulha grossa (Core Biopsy)",
      "Mamografia com magnificação e ultrassonografia complementar",
      "Consulta com mastologista em até 7 dias úteis"
    ],
    "ethical_disclaimer": "Este laudo é gerado por Inteligência Artificial para suporte à decisão clínica e não substitui a avaliação presencial do médico especialista."
  }
}
```

---

### 1.2 `GET /api/v1/models/ga-benchmarks`
Retorna a tabela dos 3 experimentos comparativos do Algoritmo Genético contra a linha de base clássica (GridSearchCV) para Câncer e PCOS.
