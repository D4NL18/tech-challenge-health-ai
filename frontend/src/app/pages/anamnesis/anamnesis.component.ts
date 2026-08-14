import { Component, ChangeDetectorRef, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AnamnesisService, AnamnesisPredictionResult } from '../../services/anamnesis.service';
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
  currentStep = 1;
  isAnimating = false;
  animationClass = 'dust-in';
  selectedDisease: 'cancer' | 'pcos' | '' = '';

  patientData = {
    name: '',
    age: '',
    openTextSymptoms: '',
    // Campos legados para compatibilidade e texto
    breast_symptoms: '',
    breast_history: '',
    pcos_symptoms: '',
    pcos_history: '',
    // Novos campos tabulares PCOS
    pcos: {
      weight: '',
      height: '',
      cycle_length: '',
      fsh: '',
      lh: '',
      tsh: '',
      prg: '',
      rbs: '',
      weight_gain: false,
      hair_growth: false,
      skin_darkening: false,
      fast_food: false
    },
    // Novos campos tabulares Câncer
    cancer: {
      radius_mean: '',
      texture_mean: '',
      compactness_mean: '',
      concavity_mean: '',
      concave_points_mean: '',
      radius_se: '',
      perimeter_se: '',
      area_se: '',
      concavity_se: '',
      radius_worst: '',
      texture_worst: '',
      smoothness_worst: '',
      compactness_worst: '',
      concavity_worst: '',
      concave_points_worst: '',
      symmetry_worst: ''
    }
  };

  selectedFile: File | null = null;
  isLoading = false;
  predictionResult: AnamnesisPredictionResult | null = null;

  constructor(private router: Router, private anamnesisService: AnamnesisService, private cdr: ChangeDetectorRef, private el: ElementRef) {}

  selectDisease(disease: 'cancer' | 'pcos') {
    this.selectedDisease = disease;
    this.nextStep();
  }

  onFileSelected(event: any) {
    if (event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];
    }
  }

  handleFormSubmit() {
    if (this.currentStep < 4) {
      this.nextStep();
    } else if (this.currentStep === 4) {
      this.onSubmit();
    }
  }

  nextStep() {
    if (this.currentStep < 4 && !this.isAnimating) {
      this.transitionToStep(this.currentStep + 1);
    }
  }

  prevStep() {
    if (this.currentStep > 1 && !this.isAnimating) {
      if (this.currentStep === 2) {
        this.selectedDisease = '';
      }
      this.transitionToStep(this.currentStep - 1);
    }
  }

  transitionToStep(newStep: number) {
    if (this.isAnimating) return;
    this.isAnimating = true;

    this.animationClass = 'dust-out';
    this.cdr.detectChanges(); // force view update immediately

    setTimeout(() => {
      this.currentStep = newStep;
      this.animationClass = 'dust-in';
      this.cdr.detectChanges(); // force rendering of new step

      setTimeout(() => {
        this.isAnimating = false;
        this.animationClass = ''; // reset to default state to avoid any CSS stickiness
        this.cdr.detectChanges();
      }, 800); // 800ms is materialize duration
    }, 2500); // 2500ms is dissolve-rtl duration
  }

  onSubmit() {
    if (this.isAnimating) return;
    this.isAnimating = true;

    this.animationClass = 'dust-out';
    this.cdr.detectChanges();

    setTimeout(() => {
      this.currentStep = 5; // Loading Step
      this.animationClass = 'dust-in';
      this.isLoading = true;
      this.cdr.detectChanges();

      const parseFloatSafe = (val: any): number => {
        if (!val) return 0;
        if (typeof val === 'number') return val;
        return parseFloat(val.toString().replace(',', '.')) || 0;
      };

      let finalSymptoms = '';
      let finalHistory = '';
      let tabularData: any = {};

      if (this.selectedDisease === 'cancer') {
        finalSymptoms = 'Câncer de Mama: ' + this.patientData.breast_symptoms;
        finalHistory = `Mamografia/Nódulo: ${this.patientData.breast_history}`;
        tabularData = {
          'radius_mean': parseFloatSafe(this.patientData.cancer.radius_mean),
          'texture_mean': parseFloatSafe(this.patientData.cancer.texture_mean),
          'compactness_mean': parseFloatSafe(this.patientData.cancer.compactness_mean),
          'concavity_mean': parseFloatSafe(this.patientData.cancer.concavity_mean),
          'concave points_mean': parseFloatSafe(this.patientData.cancer.concave_points_mean),
          'radius_se': parseFloatSafe(this.patientData.cancer.radius_se),
          'perimeter_se': parseFloatSafe(this.patientData.cancer.perimeter_se),
          'area_se': parseFloatSafe(this.patientData.cancer.area_se),
          'concavity_se': parseFloatSafe(this.patientData.cancer.concavity_se),
          'radius_worst': parseFloatSafe(this.patientData.cancer.radius_worst),
          'texture_worst': parseFloatSafe(this.patientData.cancer.texture_worst),
          'smoothness_worst': parseFloatSafe(this.patientData.cancer.smoothness_worst),
          'compactness_worst': parseFloatSafe(this.patientData.cancer.compactness_worst),
          'concavity_worst': parseFloatSafe(this.patientData.cancer.concavity_worst),
          'concave points_worst': parseFloatSafe(this.patientData.cancer.concave_points_worst),
          'symmetry_worst': parseFloatSafe(this.patientData.cancer.symmetry_worst)
        };
      } else {
        finalSymptoms = `SOP | Ganho Peso: ${this.patientData.pcos.weight_gain ? 'Sim' : 'Não'}, ` +
                        `Pelos: ${this.patientData.pcos.hair_growth ? 'Sim' : 'Não'}, ` +
                        `Pele: ${this.patientData.pcos.skin_darkening ? 'Sim' : 'Não'}, ` +
                        `Fast Food: ${this.patientData.pcos.fast_food ? 'Sim' : 'Não'}`;
        finalHistory = `Avaliação Hormonal.`;
        tabularData = {
          'Weight (Kg)': parseFloatSafe(this.patientData.pcos.weight),
          'Height(Cm) ': parseFloatSafe(this.patientData.pcos.height),
          'Weight gain(Y/N)': this.patientData.pcos.weight_gain ? 1 : 0,
          'hair growth(Y/N)': this.patientData.pcos.hair_growth ? 1 : 0,
          'Skin darkening (Y/N)': this.patientData.pcos.skin_darkening ? 1 : 0,
          'Fast food (Y/N)': this.patientData.pcos.fast_food ? 1 : 0,
          'Cycle length(days)': parseFloatSafe(this.patientData.pcos.cycle_length),
          'RBS(mg/dl)': parseFloatSafe(this.patientData.pcos.rbs),
          'FSH(mIU/mL)': parseFloatSafe(this.patientData.pcos.fsh),
          'LH(mIU/mL)': parseFloatSafe(this.patientData.pcos.lh),
          'TSH (mIU/L)': parseFloatSafe(this.patientData.pcos.tsh),
          'PRG(ng/mL)': parseFloatSafe(this.patientData.pcos.prg)
        };
      }

      const formData = new FormData();
      const payload = {
        patient_name: this.patientData.name,
        age: parseInt(this.patientData.age) || 0,
        symptoms: finalSymptoms,
        open_text: this.patientData.openTextSymptoms,
        medical_history: finalHistory,
        disease: this.selectedDisease,
        tabular_data: tabularData
      };

      formData.append('anamnesis_data', JSON.stringify(payload));
      if (this.selectedFile) {
        formData.append('image', this.selectedFile);
      }

      this.anamnesisService.analyze(formData).subscribe({
        next: (res: AnamnesisPredictionResult) => {
          setTimeout(() => {
            this.isLoading = false;
            this.animationClass = 'dust-out';
            setTimeout(() => {
              this.currentStep = 6; // Result Step
              this.predictionResult = res;
              this.animationClass = 'dust-in';
              this.cdr.detectChanges();

              setTimeout(() => {
                this.isAnimating = false;
                this.animationClass = ''; // reset to avoid CSS sticky state
                this.cdr.detectChanges();
              }, 800);
            }, 2500);
          }, 1500); // Artificial delay to simulate processing
        },
        error: (err) => {
          console.error(err);
          this.isLoading = false;
          alert('Erro ao realizar a predição. Tente novamente.');
          this.currentStep = 4;
          this.isAnimating = false;
          this.cdr.detectChanges();
        }
      });
    }, 2500);
  }

  restart() {
    this.transitionToStep(1);
    this.selectedDisease = '';
    this.patientData = { 
      name: '', age: '', openTextSymptoms: '',
      breast_symptoms: '', breast_history: '', pcos_symptoms: '', pcos_history: '',
      pcos: { weight: '', height: '', cycle_length: '', fsh: '', lh: '', tsh: '', prg: '', rbs: '', weight_gain: false, hair_growth: false, skin_darkening: false, fast_food: false },
      cancer: { radius_mean: '', texture_mean: '', compactness_mean: '', concavity_mean: '', concave_points_mean: '', radius_se: '', perimeter_se: '', area_se: '', concavity_se: '', radius_worst: '', texture_worst: '', smoothness_worst: '', compactness_worst: '', concavity_worst: '', concave_points_worst: '', symmetry_worst: '' }
    };
    this.selectedFile = null;
    this.predictionResult = null;
  }
}
