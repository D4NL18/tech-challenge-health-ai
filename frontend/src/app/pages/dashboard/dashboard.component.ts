import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CardComponent } from '../../components/card/card.component';
import { ButtonComponent } from '../../components/button/button.component';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, CardComponent, ButtonComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
  private http = inject(HttpClient);
  private router = inject(Router);

  isGeneratingLLM = signal<boolean>(false);
  clinicalReport = signal<any | null>(null);

  mockResults = {
    patientName: 'Maria Silva',
    imageAnalysis: {
      risk: 'Alto',
      probability: '87%',
      description: 'Padrão suspeito identificado no quadrante superior externo (BI-RADS 4C sugerido).'
    },
    textAnalysis: {
      risk: 'Moderado',
      probability: '65%',
      description: 'Relato indica dores recorrentes e possíveis sinais secundários de risco.'
    }
  };

  newTriage() {
    this.router.navigate(['/']);
  }

  generateClinicalReport() {
    this.isGeneratingLLM.set(true);
    const payload = {
      disease: 'cancer',
      patient_name: this.mockResults.patientName,
      patient_age: 48,
      confidence_score: 0.87,
      tabular_data: {
        radius_mean: 17.99,
        texture_mean: 10.38,
        compactness_mean: 0.2776,
        concavity_mean: 0.3001
      }
    };

    this.http.post<any>(`${environment.apiUrl}/api/v1/anamnesis/explain-diagnosis`, payload).subscribe({
      next: (res) => {
        if (res.success && res.clinical_report) {
          this.clinicalReport.set(res.clinical_report);
        }
        this.isGeneratingLLM.set(false);
      },
      error: (err) => {
        console.error('Erro ao gerar laudo LLM:', err);
        this.isGeneratingLLM.set(false);
      }
    });
  }
}
