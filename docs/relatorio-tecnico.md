# Relatório Técnico - Tech Challenge: Fase 1

## Introdução e Definição do Problema
Este projeto tem como objetivo realizar uma previsão de diagnóstico inicial de doenças relacionadas à saúde da mulher, mais especificamente ao câncer de mama e à síndrome dos ovários policísticos (SOP).
O intuito principal do projeto é ser disponibilizado como ferramenta para profissionais da área da saúde ou realização de triagens iniciais em clínicas, hospitais ou por pacientes antecedendo a consulta médica. Tendo isso em vista, o projeto não tem como proposta substituir uma análise de um profissional da saúde, servindo apenas como material complementar de apoio.

O código fonte do projeto está disponibilizado em um repositório do GitHub, que pode ser encontrado seguindo o link [Github: Health AI](https://github.com/D4NL18/tech-challenge-health-ai). O projeto encontra-se em produção, com deploy na nuvem pela plataforma GCP para facilitar a avaliação e utilização em testes, e pode ser visitado no link [Health AI - Prod](https://healthai-diagnostics.web.app/).

## Datasets
Para o projeto, foram utilizados os datasets sugeridos pela proposta da atividade, sendo eles [Polycystic ovary syndrome (PCOS)](https://www.kaggle.com/datasets/prasoonkottarathil/polycystic-ovary-syndrome-pcos) para dados tabulares de SOP, [Breast Cancer Wisconsin (Diagnostic) Data Set](https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data/data) para dados tabulares de câncer de mama e [CBIS-DDSM: Breast Cancer Image Dataset](https://www.kaggle.com/datasets/awsaf49/cbis-ddsm-breast-cancer-image-dataset) para dados de imagens também de câncer de mama.

## Relatório Técnico

### Discussões da Análise Exploratória
A análise exploratória guiou as decisões sobre quais dados seriam relevantes para o treinamento do modelo, a importância de cada um e quais seriam mantidos, com o objetivo de diminuir o dimensionamento dos dados e tornar o treinamento mais fácil e eficiente. Ademais, também foi realizada a detecção de anomalias nos datasets, como campos nulos ou com valores inválidos (como #NOME?) para um futuro tratamento dos dados.

### Estratégias de Pré Processamento
Para melhorar o treinamento dos modelos de IA, foi realizado o tratamento e pré-processamento dos dados, embasando-se na análise exploratória realizada anteriormente. A partir disso, foram criados scripts para o tratamento dos dados tabulares, tanto de SOP quanto do câncer de mama, além de scripts de tratamento para os dados em formato de imagem também para o câncer de mama. Os tratamentos dos dados tabulares podem ser visualizados em [backend/training_scripts/utils/data_treatment.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/training_scripts/utils/data_treatment.py), e o tratamento dos dados de imagens em [backend/training_scripts/utils/vision_data_treatment.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/training_scripts/utils/vision_data_treatment.py).

Para os dados relacionados ao SOP, foi realizado o tratamento dos erros da planilha, como valores “#NOME?” que foram transformados em NaN e valores de BMI recalculados e eliminação de colunas vazias ou de baixa importância.

Para os dados tabulares de câncer de mama, foi realizado um processo semelhante, contendo a remoção de colunas vazias ou de baixa importância, com a adição de um tratamento de colinearidade, isto é, colunas que se correlacionam entre si, como perímetro e área.

Ainda em `data_treatment.py`, foi criada a pipeline de tratamento dos dados, que utilizou o `KNNImputer` para imputação de nulos, `OutlierCapping` para remover outliers e `StandardScaling` para escalonamento dos dados. Em [backend/training_scripts/utils/model_builder.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/training_scripts/utils/model_builder.py) foi adicionada à pipeline o balanceamento SMOTE para equilibrar o número de positivos e negativos. Ainda em `model_builder.py`, foi criada uma função para separar a database em treino e teste, executar pipeline de pré-processamento e realizar o GridSearch para identificar melhores hiperparâmetros para serem utilizados, seguidos pelo salvamento do modelo.

Já em [backend/training_scripts/train_all.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/training_scripts/train_all.py), foi iniciada a lista de modelos que foram utilizados e iniciou o loop de execução, que utilizava as funções de tratamentos de dados e executava a Pipeline, repetindo o processo para cada modelo da lista, para cada uma das duas doenças abordadas no projeto.

Para os dados de imagens de câncer de mama, o processo de pré-processamento seguiu uma lógica semelhante em [backend/training_scripts/utils/vision_data_treatment.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/training_scripts/utils/vision_data_treatment.py). As imagens brutas passam primeiramente por um Auto Crop para remover o espaço preto ao redor da mama, evitando processamento inútil. Em seguida, aplicou-se o algoritmo CLAHE em grades de 8x8 pixels. Por fim, as imagens sofrem um redimensionamento fixo para 512x512 pixels e foram convertidas em tensores com as cores normalizadas nos padrões da ImageNet.

### Modelos usados
O projeto foi desenvolvido de forma a permitir o usuário administrador a escolher quais modelos serão utilizados para cada objetivo (SOP, Câncer de Mama com dados tabulares e Imagem). Sendo assim, foi criado um painel de administrador com todas as opções e as métricas disponibilizadas de cada modelo entre os escolhidos.

Os modelos escolhidos para os dados tabulares foram Logistic Regression, Random Forest, Gradient Boosting, SVM, KNN, Naive Bayes e MLP, devido à ampla utilização e familiarização do mercado com estes modelos, que são mais popularmente utilizados. Já para os modelos de visão computacional, foram utilizados diferentes modelos de CNN, sendo eles Densenet121, EfficientNet-B2 e ResNet50.

O objetivo desta abordagem leva em consideração a continuidade do treinamento e da melhoria de cada modelo de forma contínua. Sendo assim, se em determinado momento um modelo se torna melhor que os demais, devido à atualizações no treinamento e nos dados utilizados, ele pode passar a ser escolhido como principal para a aplicação. O desenvolvimento foi feito de forma padronizada para todos, implicando em poucas mudanças no treinamento entre os modelos, o que viabilizou esta abordagem sem adicionar muita complexidade e demanda de tempo para o código. Sendo assim, foram desenvolvidas funções com configurações específicas e hiperparâmetros escolhidos para cada modelo em [backend/training_scripts/models](https://github.com/D4NL18/tech-challenge-health-ai/tree/master/backend/training_scripts/models), sendo um arquivo deste diretório para cada modelo. Já em [backend/training_scripts/train_all](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/training_scripts/train_all.py) e [backend/training_scripts/train_vision](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/training_scripts/train_vision.py), é criado um array de modelos utilizando as configurações para cada um que foram desenvolvidas anteriormente para realizar o treinamento de todos de forma simultânea para cada doença abordada. A partir disso, os modelos são carregados em [backend/app/ml/tabular.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/app/ml/tabular.py) e [backend/app/ml/vision.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/app/ml/vision.py) para serem utilizados pela aplicação.

Além disso, foi implementada a análise textual utilizando os modelos do Gemini Flash 3.6, Gemini Flash 3.5 e GPT 5.6 Luna para auxiliar no diagnóstico, além de um modelo all-MiniLM-L6-v2 de código aberto utilizado internamente no sistema. A escolha dos modelos é feita da mesma forma citada anteriormente, onde o administrador escolhe priorizar Gemini ou GPT. Caso o usuário escolha o Gemini, o sistema tentará utilizar o Flash 3.6, tendo o Flash 3.5 e por fim o GPT 5.6 de fallback. Caso o usuário escolha o GPT, o inverso acontece. Isso pode ser visualizado no código presente em [backend/app/ml/text.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/app/ml/text.py). Os modelos utilizam documentos em PDF sobre diagnóstico de câncer de mama e SOP para embasar suas respostas e o diagnóstico gerados. Em [backend/knowledge_base/ingest_docs.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/knowledge_base/ingest_docs.py) e [backend/knowledge_base/query_rag](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/knowledge_base/query_rag.py), estes PDFs são quebrados em blocos e sumarizados, e o modelo all-MiniLM-L6-v2 irá auxiliar a encontrar as partes específicas de cada PDF que poderá ser utilizada para o diagnóstico dependendo do input do usuário, auxiliando na economia de tokens, ao evitar que todos os PDFs sejam lidos por completo em cada input do usuário.

Para permitir a união de diferentes metodologias de análise, sendo elas a visão computacional com CNN, dados tabulares com Machine Learning e dados textuais com LLMs, foi criado o arquivo [backend/app/ml/ensemble.py](https://github.com/D4NL18/tech-challenge-health-ai/blob/master/backend/app/ml/ensemble.py), que define a porcentagem que cada método vai ter de influência na resposta ao usuário. Caso sejam fornecidas informações tabulares, textuais e de imagem, elas representarão 50%, 25% e 25% respectivamente, e caso alguma destas informações estejam faltando, sua porcentagem será distribuída proporcionalmente entre as demais. A soma da confiabilidade de todas elas em conjunto com a porcentagem de influência de cada uma no resultado irá resultar na confiabilidade da resposta ao usuário.

### Front-end, API e Deploy
Para o Front-end, foi utilizado o Angular 21 no padrão SPA, com Typescript e SCSS. Já o backend foi estruturado como um orquestrador dos diferentes modelos e métodos, onde ele recebe as requisições HTTP e utiliza os modelos corretos conforme definido pelo usuário administrador. O deploy foi feito em nuvem na plataforma do GCP utilizando Cloud Run e Firebase. Não foi utilizado banco de dados neste projeto pois não houve a necessidade de persistência de dados, já que o login foi feito pela definição de um usuário padrão no sistema com o usuário “admin” e senha “admin” para facilitar o desenvolvimento.

## Resultados Obtidos

### Funcionamento do Produto
O projeto pode ser dividido em duas funcionalidades principais, sendo elas a anamnese e diagnóstico das doenças utilizando os modelos de IA pré treinados, unidos com a integração com as LLMs terceiras via API e o painel de administrador, acessado por meio de login, que permite que o usuário altere qual modelo vai ser utilizado para cada avaliação, tanto para os dados tabulares quanto para imagens, tendo como base as métricas obtidas nos testes.

#### Anamnese
A página inicial da anamnese tem o intuito de identificar o usuário, fornecendo nome e idade, conforme figura 1 abaixo:

![Figura 1 - Tela de identificação](images/figura-1.png)

No segundo passo, o sistema pergunta qual doença o usuário deseja diagnosticar, tendo como duas opções o câncer de mama e o SOP. A partir disso, o fluxo do usuário se dividirá, tento inputs diferentes para cada uma das doenças

![Figura 2 - Foco da Triagem](images/figura-2.png)

Para o câncer de mama, o sistema permitirá que o usuário envie informações numéricas sobre os exames realizados anteriormente para diagnóstico, exames de imagens de mamografias e um campo aberto de texto, protegido contra prompt injection, e utiliza os três métodos diferentes em conjunto para a identificação. Caso um ou mais métodos não sejam preenchidos, o sistema utilizará os demais para realizar o diagnóstico.

Já para a SOP, o sistema disponibiliza inputs numéricos e booleanos para a previsão com modelos tabulares, e o campo aberto para as LLMs, mas não conta com identificação por imagem.

Após a triagem, o sistema dá o diagnóstico, informando o nível de confiança da IA, isto é, o quanto a IA tem de “certeza” de um resultado positivo. Uma porcentagem alta irá retornar um risco estimado alto, enquanto uma certeza baixa retornará um risco estimado baixo. Ademais, o sistema complementa informando quanto cada “tipo” de previsão (tabular, texto e imagem) representa, em porcentagem, na previsão final, e alerta sobre a necessidade de uma consulta médica para validar seus resultados

![Figura 3 - Resultado](images/figura-3.png)

#### Admin
Para acessar o painel de administrador, o usuário deverá acessar a rota `/admin` e, caso não esteja autenticado, deverá fazer login na plataforma. Defini o usuário genérico “admin” com senha “admin” para facilitar os testes na plataforma.

![Figura 4 - Login](images/figura-4.png)

Ao realizar login, o usuário será redirecionado ao painel, que exibe todos os modelos, separados por objetivo (doença e tabular ou imagem) com as métricas de cada um (Acurácia e ROC-AUC), além da matriz confusão gerada na análise de resultados dos testes. Ao clicar em um modelo, abrirá um modal, que exibe, além das informações anteriores, informações básicas sobre o modelo e o botão para torná-lo ativo.

![Figura 5 - Painel de Administrador](images/figura-5.png)

![Figura 6 - Painel de Administrador](images/figura-6.png)

![Figura 7 - Painel de Administrador](images/figura-7.png)

![Figura 8 - Modal do Modelo](images/figura-8.png)
