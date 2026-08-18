# 6. Exemplos de Testes Inéditos (Triagem)

*Read this in other languages: [English](../docs_en/6-exemplos-testes.md) | [Português](6-exemplos-testes.md)*

Para testar a acurácia dos modelos e entender se tudo que expliquei nos documentos anteriores está de fato funcionando, criei alguns exemplos sintéticos de pacientes.

Você pode colar esses valores no Frontend do Angular e rodar o diagnóstico. Lembre-se: como esses dados não existem na base de treinamento original, estou forçando a IA a inferir algo que ela nunca viu.

---

## 6.1. Câncer de Mama

### Exemplo A: Alto Risco (Maligno)
*Dados sintéticos projetados com características acentuadas típicas de nódulos malignos (maior volume, textura irregular, alta concavidade).*
- **Raio Médio**: 21.35
- **Textura Média**: 24.12
- **Compacidade Média**: 0.2985
- **Concavidade Média**: 0.3210
- **Pontos Côncavos Médios**: 0.1652
- **Raio SE**: 1.250
- **Perímetro SE**: 9.150
- **Área SE**: 185.3
- **Concavidade SE**: 0.0621
- **Raio Pior**: 28.50
- **Textura Pior**: 31.05
- **Suavidade Pior**: 0.1785
- **Compacidade Pior**: 0.7231
- **Concavidade Pior**: 0.7854
- **Pontos Côncavos Pior**: 0.2891
- **Simetria Pior**: 0.5102

### Exemplo B: Baixo Risco (Benigno)
*Dados sintéticos projetados com características típicas de nódulos benignos (menor dimensão, bordas suaves, pouca concavidade).*
- **Raio Médio**: 11.45
- **Textura Média**: 13.10
- **Compacidade Média**: 0.0652
- **Concavidade Média**: 0.0315
- **Pontos Côncavos Médios**: 0.0215
- **Raio SE**: 0.1850
- **Perímetro SE**: 1.350
- **Área SE**: 15.20
- **Concavidade SE**: 0.0152
- **Raio Pior**: 12.85
- **Textura Pior**: 16.45
- **Suavidade Pior**: 0.1150
- **Compacidade Pior**: 0.1350
- **Concavidade Pior**: 0.1052
- **Pontos Côncavos Pior**: 0.0651
- **Simetria Pior**: 0.2510

---

## 6.2. Síndrome do Ovário Policístico (SOP)

### Exemplo C: Alto Risco (SOP = Sim)
*Dados sintéticos para uma paciente apresentando sintomas clássicos de hiperandrogenismo e desequilíbrio metabólico/hormonal (LH alto em relação ao FSH).*
- **Peso (Kg)**: 82.5
- **Altura (cm)**: 162.0
- **Ganho de Peso Recente?**: Sim
- **Crescimento de Pelos Incomum?**: Sim
- **Escurecimento da Pele?**: Sim
- **Consumo Frequente de Fast Food?**: Sim
- **Duração do Ciclo (Dias)**: 7
- **RBS (Glicemia)**: 110.5
- **FSH (mIU/mL)**: 4.10
- **LH (mIU/mL)**: 9.35
- **TSH (mIU/L)**: 3.20
- **Progesterona (PRG)**: 0.25
- **Nº de Folículos (Esq)**: 25
- **Nº de Folículos (Dir)**: 16

### Exemplo D: Baixo Risco (SOP = Não)
*Dados sintéticos para uma paciente saudável, com perfil hormonal equilibrado e sem os sintomas físicos da síndrome.*
- **Peso (Kg)**: 58.0
- **Altura (cm)**: 168.0
- **Ganho de Peso Recente?**: Não
- **Crescimento de Pelos Incomum?**: Não
- **Escurecimento da Pele?**: Não
- **Consumo Frequente de Fast Food?**: Não
- **Duração do Ciclo (Dias)**: 4
- **RBS (Glicemia)**: 85.0
- **FSH (mIU/mL)**: 6.80
- **LH (mIU/mL)**: 3.10
- **TSH (mIU/L)**: 1.80
- **Progesterona (PRG)**: 0.95
- **Nº de Folículos (Esq)**: 6
- **Nº de Folículos (Dir)**: 5
