import { Component, ChangeDetectorRef, ElementRef, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
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
      follicle_l: '',
      follicle_r: '',
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
  lastTabularPayload: any = {};
  isGeneratingLLM = signal(false);
  clinicalReport = signal<any | null>(null);

  constructor(
    private router: Router,
    private anamnesisService: AnamnesisService,
    private http: HttpClient,
    private cdr: ChangeDetectorRef,
    private el: ElementRef
  ) {}

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

      const parseFloatSafe = (val: any): number | null => {
        if (val === '' || val === null || val === undefined) return null;
        if (typeof val === 'number') return val;
        const parsed = parseFloat(val.toString().replace(',', '.'));
        return isNaN(parsed) ? null : parsed;
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
          ' Age (yrs)': parseInt(this.patientData.age) || null,
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
          'PRG(ng/mL)': parseFloatSafe(this.patientData.pcos.prg),
          'Follicle No. (L)': parseFloatSafe(this.patientData.pcos.follicle_l),
          'Follicle No. (R)': parseFloatSafe(this.patientData.pcos.follicle_r)
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

      this.lastTabularPayload = tabularData;
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
              // Dispara automaticamente a explicabilidade clinica por LLM para esta triagem
              this.generateClinicalReport();

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
      pcos: { weight: '', height: '', cycle_length: '', fsh: '', lh: '', tsh: '', prg: '', rbs: '', follicle_l: '', follicle_r: '', weight_gain: false, hair_growth: false, skin_darkening: false, fast_food: false },
      cancer: { radius_mean: '', texture_mean: '', compactness_mean: '', concavity_mean: '', concave_points_mean: '', radius_se: '', perimeter_se: '', area_se: '', concavity_se: '', radius_worst: '', texture_worst: '', smoothness_worst: '', compactness_worst: '', concavity_worst: '', concave_points_worst: '', symmetry_worst: '' }
    };
    this.selectedFile = null;
    this.predictionResult = null;
    this.clinicalReport.set(null);
    this.isGeneratingLLM.set(false);
  }

  fillTestData(disease: 'cancer' | 'pcos', autoSubmit: boolean = false) {
    if (this.isAnimating) return;
    this.selectedDisease = disease;

    if (disease === 'cancer') {
      this.patientData.name = 'Mariana Silva Santos';
      this.patientData.age = '48';
      this.patientData.breast_symptoms = 'Nódulo palpável indolor no quadrante superior externo da mama direita há 3 meses com aumento progressivo.';
      this.patientData.breast_history = 'Histórico familiar de neoplasia mamária em parente de primeiro grau (mãe aos 50 anos).';
      this.patientData.openTextSymptoms = 'Paciente relata nódulo endurecido em mama direita com ligeira retração de pele há 3 meses. Refere cansaço e histórico materno de neoplasia de mama aos 50 anos. Nega secreção papilar.';
      this.patientData.cancer = {
        radius_mean: '17.99',
        texture_mean: '10.38',
        compactness_mean: '0.2776',
        concavity_mean: '0.3001',
        concave_points_mean: '0.1471',
        radius_se: '1.095',
        perimeter_se: '8.589',
        area_se: '153.4',
        concavity_se: '0.05373',
        radius_worst: '25.38',
        texture_worst: '17.33',
        smoothness_worst: '0.1622',
        compactness_worst: '0.6656',
        concavity_worst: '0.7119',
        concave_points_worst: '0.2654',
        symmetry_worst: '0.4601'
      };
    } else {
      this.patientData.name = 'Camila Fernandes Oliveira';
      this.patientData.age = '26';
      this.patientData.pcos_symptoms = 'Ciclos menstruais irregulares com intervalos de 42 a 48 dias, ganho de peso e acne persistente.';
      this.patientData.pcos_history = 'Tentativa de gestação há 1 ano sem sucesso prévio.';
      this.patientData.openTextSymptoms = 'Paciente jovem apresentando amenorreia secundária com ciclos irregulares de 40 a 45 dias, aumento de oleosidade e acne facial persistente, dificuldade de perda de peso e hirsutismo progressivo.';
      this.patientData.pcos = {
        weight: '74.5',
        height: '162',
        cycle_length: '42',
        fsh: '5.2',
        lh: '12.8',
        tsh: '2.4',
        prg: '0.6',
        rbs: '108',
        follicle_l: '16',
        follicle_r: '18',
        weight_gain: true,
        hair_growth: true,
        skin_darkening: true,
        fast_food: true
      };
    }

    if (autoSubmit) {
      this.onSubmit();
    } else {
      this.currentStep = 4;
      this.cdr.detectChanges();
    }
  }

  generateClinicalReport() {
    if (!this.predictionResult) return;
    this.isGeneratingLLM.set(true);

    const payload = {
      disease: this.selectedDisease || 'cancer',
      patient_name: this.patientData.name || 'Paciente',
      patient_age: parseInt(this.patientData.age) || null,
      confidence_score: this.predictionResult.confidence || 0.85,
      tabular_data: this.lastTabularPayload || {}
    };

    this.http.post<any>(`${environment.apiUrl}/api/v1/anamnesis/explain-diagnosis`, payload).subscribe({
      next: (res) => {
        if (res.success && res.clinical_report) {
          this.clinicalReport.set(res.clinical_report);
        }
        this.isGeneratingLLM.set(false);
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Erro ao gerar laudo LLM:', err);
        this.isGeneratingLLM.set(false);
        this.cdr.detectChanges();
      }
    });
  }

  getCircularDasharray(score: number | null | undefined): string {
    if (score === null || score === undefined) return '0, 100';
    const val = Math.round(Math.min(1.0, Math.max(0.0, score)) * 100);
    return `${val}, 100`;
  }

  getScorePercentage(score: number | null | undefined): string {
    if (score === null || score === undefined) return '-';
    return `${Math.round(Math.min(1.0, Math.max(0.0, score)) * 100)}%`;
  }

  getScoreRiskText(score: number | null | undefined): string {
    if (score === null || score === undefined) return 'Não Fornecido';
    if (score > 0.7) return 'Alto';
    if (score > 0.4) return 'Moderado';
    return 'Baixo';
  }

  getScoreRiskClass(score: number | null | undefined): string {
    if (score === null || score === undefined) return 'risk-neutral';
    if (score > 0.7) return 'risk-high pulse-danger';
    if (score > 0.4) return 'risk-moderate';
    return 'risk-low';
  }
}