import torch
import torch.nn as nn
import torch.optim as optim

from training_scripts.utils.vision_metrics_eval import evaluate_and_save_vision_model

class FocalLoss(nn.Module):
    """
    Focal Loss ajuda a tratar dados desbalanceados ao diminuir o peso de exemplos fáceis
    (bem classificados) e focar nos casos mais difíceis (onde o modelo tem menor confiança).
    """
    def __init__(self, alpha=1, gamma=2, logits=True, reduce=True):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.logits = logits
        self.reduce = reduce
        self.bce = nn.BCEWithLogitsLoss(reduction='none') if logits else nn.BCELoss(reduction='none')

    def forward(self, inputs, targets):
        BCE_loss = self.bce(inputs, targets)
        pt = torch.exp(-BCE_loss)
        F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss

        if self.reduce:
            return torch.mean(F_loss)
        else:
            return F_loss


def build_and_evaluate_vision_model(model_config, train_loader, test_loader, y_test, epochs=3):
    model_name = model_config['model_name']
    model = model_config['model']
    lr = model_config.get('lr', 1e-4)
    weight_decay = model_config.get('weight_decay', 1e-4)

    print(f"\n==========================================")
    print(f" TREINAMENTO DO MODELO DE VISÃO: {model_name.upper()}")
    print(f"==========================================")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"-> Usando dispositivo de processamento: {device}")
    
    model = model.to(device)
    
    # Utilizando BCE normal pois o dataloader já lida com o desbalanceamento através do WeightedRandomSampler
    criterion = nn.BCEWithLogitsLoss()
    # Com o Batch Size reduzido para 4, um Learning Rate de 1e-4 é muito agressivo e causa instabilidade.
    # O ideal é usar um LR menor (ex: 2e-5) desde o começo.
    optimizer = optim.AdamW(model.parameters(), lr=2e-5, weight_decay=weight_decay)
    
    # Scheduler: Corta o LR se a loss não melhorar após 1 época
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=1)
    
    best_val_loss = float('inf')
    epochs_no_improve = 0
    early_stop_patience = 4
    best_model_state = None
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        # Gradient Accumulation: acumula gradientes por múltiplos passos antes de atualizar os pesos, simulando um batch size maior.
        accumulation_steps = 4 
        optimizer.zero_grad()
        
        for i, (inputs, labels) in enumerate(train_loader):
            inputs = inputs.to(device)
            labels = labels.to(device).unsqueeze(1) 
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # A divisão da loss é necessária para normalizar os gradientes proporcionalmente ao tamanho efetivo do batch
            loss = loss / accumulation_steps
            loss.backward()
            
            # Atualização dos pesos apenas após o acúmulo de 'accumulation_steps' gradientes ou no fim do dataloader
            if (i + 1) % accumulation_steps == 0 or (i + 1) == len(train_loader):
                optimizer.step()
                optimizer.zero_grad()
            
            # A contagem total da epoch_loss reverte a divisão do step atual para exibir o valor real da perda
            running_loss += (loss.item() * accumulation_steps) * inputs.size(0)
            
        epoch_loss = running_loss / len(train_loader.dataset)
        
        # Validation Loop
        model.eval()
        val_running_loss = 0.0
        with torch.no_grad():
            for val_inputs, val_labels in test_loader:
                val_inputs = val_inputs.to(device)
                val_labels = val_labels.to(device).unsqueeze(1)
                
                val_outputs = model(val_inputs)
                v_loss = criterion(val_outputs, val_labels)
                val_running_loss += v_loss.item() * val_inputs.size(0)
                
        val_loss = val_running_loss / len(test_loader.dataset)
        
        print(f"Época {epoch+1}/{epochs} - Train Loss: {epoch_loss:.4f} | Val Loss: {val_loss:.4f}")
        
        # Otimizar LR usando a Val Loss (Não mais a Train Loss)
        scheduler.step(val_loss)
        
        # Early Stopping e Model Checkpointing
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            # Salvar em memória os pesos do melhor modelo
            # Isso é extremamente importante para não perdermos o ponto ótimo
            import copy
            best_model_state = copy.deepcopy(model.state_dict())
            epochs_no_improve = 0
            print(f"   -> Novo melhor modelo! (Val Loss: {best_val_loss:.4f})")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= early_stop_patience:
                print(f"   -> Early Stopping ativado! Treinamento interrompido na época {epoch+1}.")
                break
                
    # Antes da avaliação final, carregamos o melhor modelo encontrado durante as épocas
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        print("-> Melhor modelo restaurado da memória para a avaliação final.")
        
    evaluate_and_save_vision_model(model, model_name, test_loader, y_test, device)
