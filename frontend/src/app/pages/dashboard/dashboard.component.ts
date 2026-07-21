import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { CardComponent } from '../../components/card/card.component';
import { ButtonComponent } from '../../components/button/button.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, CardComponent, ButtonComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
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

  constructor(private router: Router) {}

  newTriage() {
    this.router.navigate(['/']);
  }
}
