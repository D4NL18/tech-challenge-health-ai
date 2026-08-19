# 6. Unseen Test Examples (Triage)

*Read this in other languages: [English](6-exemplos-testes.md) | [Português](../docs/6-exemplos-testes.md)*

To test the accuracy of the models and understand if everything I explained in the previous documents is actually working, I created some synthetic patient examples.

You can paste these values into the Angular Frontend and run the diagnosis. Remember: since this data does not exist in the original training database, I am forcing the AI to infer something it has never seen.

---

## 6.1. Breast Cancer

### Example A: High Risk (Malignant)
*Synthetic data designed with accentuated characteristics typical of malignant nodules (larger volume, irregular texture, high concavity).*
- **Mean Radius**: 21.35
- **Mean Texture**: 24.12
- **Mean Compactness**: 0.2985
- **Mean Concavity**: 0.3210
- **Mean Concave Points**: 0.1652
- **Radius SE**: 1.250
- **Perimeter SE**: 9.150
- **Area SE**: 185.3
- **Concavity SE**: 0.0621
- **Worst Radius**: 28.50
- **Worst Texture**: 31.05
- **Worst Smoothness**: 0.1785
- **Worst Compactness**: 0.7231
- **Worst Concavity**: 0.7854
- **Worst Concave Points**: 0.2891
- **Worst Symmetry**: 0.5102

### Example B: Low Risk (Benign)
*Synthetic data designed with typical characteristics of benign nodules (smaller dimension, smooth edges, little concavity).*
- **Mean Radius**: 11.45
- **Mean Texture**: 13.10
- **Mean Compactness**: 0.0652
- **Mean Concavity**: 0.0315
- **Mean Concave Points**: 0.0215
- **Radius SE**: 0.1850
- **Perimeter SE**: 1.350
- **Area SE**: 15.20
- **Concavity SE**: 0.0152
- **Worst Radius**: 12.85
- **Worst Texture**: 16.45
- **Worst Smoothness**: 0.1150
- **Worst Compactness**: 0.1350
- **Worst Concavity**: 0.1052
- **Worst Concave Points**: 0.0651
- **Worst Symmetry**: 0.2510

---

## 6.2. Polycystic Ovary Syndrome (PCOS)

### Example C: High Risk (PCOS = Yes)
*Synthetic data for a patient presenting classic symptoms of hyperandrogenism and metabolic/hormonal imbalance (high LH in relation to FSH).*
- **Weight (Kg)**: 82.5
- **Height (cm)**: 162.0
- **Recent Weight Gain?**: Yes
- **Unusual Hair Growth?**: Yes
- **Skin Darkening?**: Yes
- **Frequent Fast Food Consumption?**: Yes
- **Cycle Length (Days)**: 7
- **RBS (Blood Sugar)**: 110.5
- **FSH (mIU/mL)**: 4.10
- **LH (mIU/mL)**: 9.35
- **TSH (mIU/L)**: 3.20
- **Progesterone (PRG)**: 0.25
- **Follicle No. (Left)**: 25
- **Follicle No. (Right)**: 16

### Example D: Low Risk (PCOS = No)
*Synthetic data for a healthy patient, with a balanced hormonal profile and without physical symptoms of the syndrome.*
- **Weight (Kg)**: 58.0
- **Height (cm)**: 168.0
- **Recent Weight Gain?**: No
- **Unusual Hair Growth?**: No
- **Skin Darkening?**: No
- **Frequent Fast Food Consumption?**: No
- **Cycle Length (Days)**: 4
- **RBS (Blood Sugar)**: 85.0
- **FSH (mIU/mL)**: 6.80
- **LH (mIU/mL)**: 3.10
- **TSH (mIU/L)**: 1.80
- **Progesterone (PRG)**: 0.95
- **Follicle No. (Left)**: 6
- **Follicle No. (Right)**: 5
