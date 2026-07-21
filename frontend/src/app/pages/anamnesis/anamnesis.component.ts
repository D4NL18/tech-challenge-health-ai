import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CardComponent } from '../../components/card/card.component';
import { InputComponent } from '../../components/input/input.component';
import { ButtonComponent } from '../../components/button/button.component';

@Component({
  selector: 'app-anamnesis',
  standalone: true,
  imports: [CommonModule, FormsModule, CardComponent, InputComponent, ButtonComponent],
  templateUrl: './anamnesis.component.html',
  styleUrls: ['./anamnesis.component.scss']
})
export class AnamnesisComponent {
  patientData = {
    name: '',
    age: '',
    symptoms: '',
  };

  constructor(private router: Router) {}

  onSubmit() {
    console.log('Dados enviados:', this.patientData);
    setTimeout(() => {
      this.router.navigate(['/dashboard']);
    }, 1000);
  }
}
