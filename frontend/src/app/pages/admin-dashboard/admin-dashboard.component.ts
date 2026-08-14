import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { Router } from '@angular/router';
import { AdminService } from '../../services/admin.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit {
  pcosModels: any[] = [];
  cancerModels: any[] = [];
  visionModels: any[] = [];
  imageUrls: { [key: string]: SafeUrl } = {};
  isLoading = true;
  activeModels: { pcos: string, cancer: string, vision_cancer: string, llm: string } = { pcos: '', cancer: '', vision_cancer: '', llm: '' };
  
  selectedModel: any = null;
  showInfoModal = false;

  constructor(
    private adminService: AdminService, 
    private authService: AuthService,
    private http: HttpClient,
    private sanitizer: DomSanitizer,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Busca métricas
    this.adminService.getMetrics().subscribe({
      next: (response) => {
        if (response && response.data) {
          this.pcosModels = response.data.filter((m: any) => m.disease === 'pcos');
          this.cancerModels = response.data.filter((m: any) => m.disease === 'cancer');
          this.visionModels = response.data.filter((m: any) => m.disease === 'vision_cancer');
          
          this.loadImages([...this.pcosModels, ...this.cancerModels, ...this.visionModels]);
        }
        
        // Busca modelos ativos
        this.adminService.getActiveModels().subscribe({
          next: (activeRes) => {
            this.activeModels = activeRes;
            if (!this.activeModels.llm) this.activeModels.llm = 'gemini';
            this.isLoading = false;
            this.cdr.detectChanges();
          },
          error: () => {
            this.isLoading = false;
            this.cdr.detectChanges();
          }
        });
      },
      error: () => {
        this.isLoading = false;
        this.cdr.detectChanges();
        // Se der erro 401, o token expirou
        this.logout();
      }
    });
  }

  loadImages(models: any[]): void {
    models.forEach(model => {
      const fileDisease = model.disease === 'vision_cancer' ? 'cancer' : model.disease;
      const filename = `matriz_${model.model_name}_${fileDisease}.png`;
      const url = this.adminService.getMatrixUrl(filename);
      // Fetch the image as blob with HttpClient to inject Auth Token via Interceptor
      this.http.get(url, { responseType: 'blob' }).subscribe({
        next: (blob) => {
          const objectUrl = URL.createObjectURL(blob);
          this.imageUrls[`${model.model_name}_${model.disease}`] = this.sanitizer.bypassSecurityTrustUrl(objectUrl);
          this.cdr.detectChanges();
        },
        error: () => {
          // Fallback if not found
        }
      });
    });
  }

  getMatrixSrc(model: any): SafeUrl | null {
    return this.imageUrls[`${model.model_name}_${model.disease}`] || null;
  }

  openModelDetails(model: any): void {
    this.selectedModel = model;
  }

  closeModelDetails(): void {
    this.selectedModel = null;
  }

  openInfoModal(): void {
    this.showInfoModal = true;
  }

  closeInfoModal(): void {
    this.showInfoModal = false;
  }

  getModelSummary(model: any): string {
    if (!model) return '';
    const diseaseName = model.disease === 'pcos' ? 'Síndrome do Ovário Policístico (PCOS)' : model.disease === 'cancer' ? 'Câncer de Mama' : model.disease === 'llm' ? 'Sintomas via IA Generativa' : 'Câncer (Visão Computacional)';
    const modelName = model.model_name;
    const formattedName = modelName.replace(/_/g, ' ').toUpperCase();
    
    let modelDescription = '';
    
    switch (modelName) {
      case 'knn':
        modelDescription = 'O KNN (K-Nearest Neighbors) é um algoritmo simples e baseado em instâncias que classifica um novo paciente analisando os pacientes com histórico clínico mais semelhante (seus "vizinhos mais próximos").';
        break;
      case 'svm':
        modelDescription = 'O SVM (Support Vector Machine) busca encontrar a linha (ou hiperplano) que melhor separa as classes. É muito eficaz em encontrar limites de decisão complexos e lidar com dados onde as diferenças entre doentes e saudáveis são sutis.';
        break;
      case 'logistic_regression':
        modelDescription = 'A Regressão Logística é um modelo estatístico tradicional que calcula diretamente a probabilidade do paciente ter a condição médica. É muito valorizada na área da saúde pela sua alta interpretabilidade.';
        break;
      case 'random_forest':
        modelDescription = 'O Random Forest (Floresta Aleatória) cria dezenas ou centenas de "Árvores de Decisão" diferentes e junta a resposta de todas elas para tomar a decisão final. Isso o torna extremamente robusto e reduz muito o risco de viés (overfitting).';
        break;
      case 'gradient_boosting':
        modelDescription = 'O Gradient Boosting é um modelo avançado que também usa múltiplas árvores de decisão, mas de forma sequencial: cada nova árvore foca especificamente em corrigir os erros das árvores anteriores, oferecendo alta precisão.';
        break;
      case 'mlp':
        modelDescription = 'O MLP (Multi-Layer Perceptron) é uma arquitetura clássica de Redes Neurais Artificiais. Ele aprende através de múltiplas camadas de neurônios, sendo capaz de identificar padrões ocultos e relações não-lineares muito complexas nos exames.';
        break;
      case 'naive_bayes':
        modelDescription = 'O Naive Bayes é um classificador probabilístico baseado no Teorema de Bayes. Ele assume de forma "ingênua" que todos os sintomas e exames são independentes entre si, sendo um modelo extremamente rápido e eficiente.';
        break;
      case 'resnet50':
        modelDescription = 'A ResNet-50 é uma Rede Neural Convolucional profunda com Conexões Residuais, especializada em extrair padrões visuais complexos diretamente de imagens de mamografia para detecção de anomalias.';
        break;
      case 'densenet121':
        modelDescription = 'A DenseNet-121 conecta cada camada a todas as outras camadas da rede. Isso garante máxima preservação de informações (microcalcificações, bordas) extraídas da imagem radiológica original.';
        break;
      case 'efficientnet_b2':
        modelDescription = 'A EfficientNet-B2 é uma CNN de última geração que balanceia de maneira ótima a resolução, a profundidade e a largura da rede neural, conseguindo altíssima acurácia no processamento da imagem.';
        break;
      case 'gemini':
        modelDescription = 'O Gemini é a IA de fronteira do Google, capaz de ler relatos médicos complexos, entender nuances e contexto em descrições de sintomas e formatar hipóteses médicas em frações de segundo.';
        break;
      case 'gpt':
        modelDescription = 'O GPT é a IA de ponta da OpenAI (conhecida pelo ChatGPT), destacando-se pela fluidez no entendimento da linguagem natural e capacidade de raciocínio clínico textual avançado.';
        break;
      default:
        modelDescription = 'Este modelo utiliza aprendizado de máquina para prever as probabilidades e classificar novos casos com base no padrão aprendido com os dados históricos.';
    }

    if (model.disease === 'llm') {
      return `O ${formattedName} está sendo utilizado para interpretar o relato aberto do paciente. ${modelDescription}`;
    }

    return `O modelo ${formattedName} está focado no diagnóstico de ${diseaseName}. ${modelDescription} A matriz abaixo detalha a performance separando os acertos (diagonal principal) e os erros nas previsões.`;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/admin/login']);
  }

  setAsActive(disease: string, modelName: string): void {
    // Optimistic update
    if (disease === 'pcos') this.activeModels.pcos = modelName;
    if (disease === 'cancer') this.activeModels.cancer = modelName;
    if (disease === 'vision_cancer') this.activeModels.vision_cancer = modelName;
    if (disease === 'llm') this.activeModels.llm = modelName;
    
    this.adminService.setActiveModel(disease, modelName).subscribe({
      next: (res) => {
        if (res && res.active_models) {
          this.activeModels = res.active_models;
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        console.error('Failed to set active model', err);
        // Re-fetch to revert optimistic update on error
        this.adminService.getActiveModels().subscribe(activeRes => {
          this.activeModels = activeRes;
          this.cdr.detectChanges();
        });
      }
    });
  }
}
