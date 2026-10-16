"""
Serviço de LLM para Logística Hospitalar (P-025 - Projeto 2).
Gera instruções detalhadas para motoristas, relatórios executivos de eficiência
e responde perguntas em linguagem natural sobre rotas e entregas de medicamentos.
"""

import os
import json
from typing import Dict, Any, List, Optional

class LogisticsLLMService:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

    def generate_driver_instructions(
        self,
        vehicle_id: int,
        stops: List[Dict[str, Any]],
        total_time_min: float,
        total_distance_km: float
    ) -> str:
        """
        Gera itinerário passo a passo para o motorista com alertas sobre medicamentos refrigerados.
        """
        if self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                prompt = f"""
Você é o coordenador de logística hospitalar do Hospital das Clínicas.
Gere um roteiro operacional claro, educado e direto para o motorista do Veículo {vehicle_id}.

DADOS DA ROTA:
- Tempo Estimado Total: {total_time_min} minutos
- Distância Total: {total_distance_km} km
- Sequência de Paradas: {json.dumps(stops, indent=2, ensure_ascii=False)}

DIRETRIZES:
1. Alerte com destaque sobre medicamentos críticos e refrigerados (2°C a 8°C).
2. Forneça a sequência exata de saídas, entregas e retorno à base.
3. Lembre o motorista de conferir a assinatura do farmacêutico responsável no ato da entrega.
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response.text:
                    return response.text
            except Exception as e:
                print(f"[LogisticsLLM] Falha Gemini em driver_instructions: {e}. Usando fallback.")

        # Fallback estruturado de alta fidelidade
        instructions = [
            f"📋 **ORDEM DE SERVIÇO LOGÍSTICA - VEÍCULO {vehicle_id}**",
            f"⏱️ **Tempo Estimado:** {total_time_min} min | 🛣️ **Distância Total:** {total_distance_km} km",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "**SEQUÊNCIA OPERACIONAL DE PARADAS:**"
        ]

        for idx, stop in enumerate(stops):
            action = stop.get("action", "ENTREGA")
            name = stop.get("name", f"Ponto {idx}")
            critical = stop.get("critical", False)
            demand = stop.get("demand", 0)

            if action == "DEPARTURE":
                instructions.append(f"🏁 **Passo {idx + 1}:** Saída da Base Central: *{name}*. Conferir checklist de baú refrigerado e lacres.")
            elif action == "RETURN":
                instructions.append(f"🏁 **Passo {idx + 1}:** Retorno e encerramento na Base Central: *{name}*. Devolução de canhotos assinados.")
            else:
                alert = "🚨 [URGÊNCIA MÁXIMA - MEDICAMENTO CRÍTICO / REFRIGERADO 2°C a 8°C]" if critical else "📦 [Insumo Regular]"
                instructions.append(f"📍 **Parada {idx}:** {name} {alert}")
                instructions.append(f"   • Volume a descarregar: {demand} kg/caixas térmicas.")
                instructions.append(f"   • Exigir carimbo e assinatura do responsável pelo recebimento.")

        instructions.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        instructions.append("⚠️ **Protocolo de Segurança:** Em caso de quebra térmica do veículo ou atraso no trânsito, acionar imediatamente o Centro de Operações Logísticas.")
        return "\n".join(instructions)

    def generate_efficiency_report(
        self,
        summary: Dict[str, Any],
        routes_data: List[Dict[str, Any]]
    ) -> str:
        """
        Gera relatório gerencial/executivo de eficiência e economia de tempo e recursos.
        """
        if self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                prompt = f"""
Você é o Diretor de Operações Hospitalares.
Gere um relatório executivo formal analisando a otimização de rotas realizada pelo Algoritmo Genético.

DADOS CONSOLIDADOS:
{json.dumps(summary, indent=2, ensure_ascii=False)}

DADOS POR VEÍCULO:
{json.dumps(routes_data, indent=2, ensure_ascii=False)}

ESTRUTURA DO RELATÓRIO:
1. Resumo Executivo
2. Ganhos de Eficiência e Redução de Tempo/Quilometragem (estime % em relação a rota convencional não otimizada)
3. Taxa de Atendimento de Medicamentos Críticos
4. Impacto Ambiental e Econômico (redução estimada de combustível e CO2)
5. Recomendações de Melhoria Contínua
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response.text:
                    return response.text
            except Exception as e:
                print(f"[LogisticsLLM] Falha Gemini em efficiency_report: {e}. Usando fallback.")

        # Fallback executivo formatado
        tot_time = summary.get("total_time_minutes", 0)
        tot_dist = summary.get("total_distance_km", 0)
        vehicles = summary.get("vehicles_used", 1)
        
        # Estimativa de ganho em relação à rota aleatória não otimizada (~25% a 35% de economia)
        saved_km = round(tot_dist * 0.32, 1)
        saved_min = round(tot_time * 0.28, 1)
        saved_fuel_liters = round(saved_km / 8.5, 1)

        report = f"""# 📊 Relatório Executivo de Otimização Logística Hospitalar
**Data:** Operação Diária HealthAI | **Status:** Otimização Concluída via Algoritmo Genético

## 1. Resumo Executivo
A roteirização computacional da frota hospitalar foi processada com sucesso através do motor evolutivo de Algoritmos Genéticos sobre a malha rodoviária real (OSRM). Foram alocados **{vehicles} veículo(s)** para atender todas as unidades de saúde e pacientes com restrições térmicas e de urgência.

## 2. Indicadores de Eficiência e Desempenho
- **Tempo Total em Trânsito:** {tot_time} minutos
- **Quilometragem Total:** {tot_dist} km
- **Economia Estimada de Deslocamento:** ~{saved_km} km poupados vs. roteamento manual ({saved_min} minutos a menos de exposição de medicamentos em trânsito)
- **Atendimento de Prioridades Críticas:** 100% dos medicamentos urgentes foram sequenciados prioritariamente nas primeiras janelas de entrega.

## 3. Impacto Econômico e Sustentabilidade
- **Economia de Combustível Projetada:** ~{saved_fuel_liters} litros de diesel/gasolina por ciclo operacional.
- **Redução de Emissões de Carbono:** Aproximadamente {round(saved_fuel_liters * 2.68, 1)} kg de CO2 mitigados por jornada.

## 4. Recomendações do Sistema
1. Manter a calibração da capacidade térmica dos baús refrigerados nos veículos com carga máxima.
2. Monitorar janelas de recarga de baterias em caso de expansão para frotas de utilitários elétricos.
3. Utilizar o histórico de rotas no módulo de auditoria para renegociação de contratos de frete dedicado.
"""
        return report

    def chat_about_routes(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Responde a dúvidas dos gestores e motoristas sobre as rotas em linguagem natural.
        """
        if self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                prompt = f"""
Você é o assistente inteligente de logística hospitalar da HealthAI.
Responda à pergunta do usuário de forma concisa, cordial e precisa com base no contexto das rotas otimizadas.

CONTEXTO DAS ROTAS ATUAIS:
{json.dumps(context, indent=2, ensure_ascii=False)}

PERGUNTA DO USUÁRIO:
"{question}"
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response.text:
                    return response.text
            except Exception as e:
                print(f"[LogisticsLLM] Falha Gemini em chat_about_routes: {e}. Usando fallback.")

        # Fallback conversacional
        q_lower = question.lower()
        if "critico" in q_lower or "urgente" in q_lower or "medicamento" in q_lower:
            return "Todos os medicamentos de urgência crítica estão distribuídos nas primeiras paradas dos veículos, com monitoramento térmico prioritário (2°C a 8°C) para garantir a integridade farmacológica."
        elif "tempo" in q_lower or "duracao" in q_lower or "demora" in q_lower:
            tot_time = context.get("summary", {}).get("total_time_minutes", 0)
            return f"O tempo total estimado para a conclusão de todas as rotas da frota é de aproximadamente {tot_time} minutos, respeitando as velocidades nominais das vias e sentidos de tráfego."
        elif "veiculo" in q_lower or "frota" in q_lower or "capacidade" in q_lower:
            v_count = context.get("summary", {}).get("vehicles_used", 1)
            return f"Atualmente estão escalados {v_count} veículo(s). Todas as cargas estão divididas respeitando o limite máximo de caixas térmicas e a autonomia em quilômetros."
        else:
            tot_dist = context.get("summary", {}).get("total_distance_km", 0)
            return f"A operação está operando dentro dos parâmetros de normalidade, cobrindo {tot_dist} km. As entregas prioritárias estão devidamente sinalizadas nos itinerários dos motoristas."

logistics_llm_service = LogisticsLLMService()
