"""
Módulo de Visualização Gráfica Dinâmica para Algoritmos Genéticos (P-013).
Plota e atualiza interativamente na tela as curvas de convergência de F2-Score,
Recall e Diversidade Genética a cada geração durante o treinamento.
"""

import os
import matplotlib
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

class LiveGeneticVisualizer:
    def __init__(
        self,
        model_name: str,
        dataset_name: str = "cancer",
        total_generations: int = 20,
        interactive: bool = True
    ):
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.total_generations = total_generations
        self.interactive = interactive
        
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        
        self._init_plot()

    def _init_plot(self):
        """
        Inicializa a figura do Matplotlib com duas subplots.
        Se interactive=True, habilita modo dinâmico na tela (GUI).
        """
        try:
            if self.interactive:
                plt.ion()
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(9, 7))
            if self.interactive:
                try:
                    self.fig.canvas.manager.set_window_title(f"HealthAI - AG Live Hyperopt [{self.model_name.upper()} - {self.dataset_name.upper()}]")
                except Exception:
                    pass
            
            self._setup_axes()
            plt.tight_layout()
            if self.interactive:
                plt.show(block=False)
                plt.pause(0.1)
        except Exception as e:
            print(f"[Visualizer] Aviso: Interface gráfica interativa indisponível ({e}). Modo headless ativo.")
            self.interactive = False

    def _setup_axes(self):
        # Subplot 1: Fitness Clínico (F2-Score)
        self.ax1.set_title(f"Convergência de Aptidão Clínica: {self.model_name.upper()} ({self.dataset_name.upper()})", fontsize=11, fontweight='bold', pad=10)
        self.ax1.set_xlabel("Geração", fontsize=9)
        self.ax1.set_ylabel("F2-Score Clínico", fontsize=9)
        self.ax1.set_xlim(1, max(2, self.total_generations))
        self.ax1.set_ylim(0.80, 1.01)
        self.ax1.grid(True, linestyle="--", alpha=0.5)

        # Subplot 2: Diversidade Genética e Recall
        self.ax2.set_title("Dinâmica da População (Diversidade Genética & Recall)", fontsize=11, fontweight='bold', pad=10)
        self.ax2.set_xlabel("Geração", fontsize=9)
        self.ax2.set_ylabel("Taxa / Proporção", fontsize=9)
        self.ax2.set_xlim(1, max(2, self.total_generations))
        self.ax2.set_ylim(0.0, 1.05)
        self.ax2.grid(True, linestyle="--", alpha=0.5)

    def update(self, history: Dict[str, Any], current_gen: int):
        """
        Atualiza as curvas na janela aberta a cada geração concluída.
        """
        if self.fig is None:
            return

        gens = history["generation"]
        best_f2 = history["best_fitness"]
        mean_f2 = history["mean_fitness"]
        divs = history["diversity_ratio"]
        recalls = [m.get("recall", 0.0) for m in history["best_metrics"]]

        self.ax1.cla()
        self.ax2.cla()
        self._setup_axes()

        # Plota Subplot 1
        self.ax1.plot(gens, best_f2, color="#10B981", marker="o", linewidth=2.2, label=f"Melhor F2 (Atual: {best_f2[-1]:.4f})")
        self.ax1.plot(gens, mean_f2, color="#3B82F6", linestyle="--", linewidth=1.8, label=f"Média da População ({mean_f2[-1]:.4f})")
        self.ax1.legend(loc="lower right", fontsize=8.5)
        
        last_rec = recalls[-1] if recalls else 0.0
        self.ax1.set_title(
            f"Gen {current_gen:02d}/{self.total_generations:02d} | Melhor F2: {best_f2[-1]:.4f} | Recall: {last_rec:.4f}",
            fontsize=11, fontweight='bold', color="#0f172a"
        )

        # Plota Subplot 2
        self.ax2.plot(gens, recalls, color="#EF4444", marker="s", linewidth=2.0, label=f"Recall do Campeão ({last_rec:.4f})")
        self.ax2.plot(gens, divs, color="#8B5CF6", linestyle="-.", linewidth=1.8, label=f"Diversidade Genética ({divs[-1]:.2f})")
        self.ax2.legend(loc="lower left", fontsize=8.5)

        if self.interactive:
            try:
                self.fig.canvas.draw()
                plt.pause(0.02)
            except Exception:
                pass

    def save(self, output_path: str):
        """
        Salva a figura estática final em alta resolução.
        """
        if self.fig is not None:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            self.fig.savefig(output_path, dpi=150, bbox_inches="tight")
            print(f"[Visualizer] Gráfico salvo com sucesso em: {output_path}")

    def close(self):
        """
        Finaliza a janela interativa.
        """
        if self.interactive and self.fig is not None:
            try:
                plt.ioff()
                plt.close(self.fig)
            except Exception:
                pass
