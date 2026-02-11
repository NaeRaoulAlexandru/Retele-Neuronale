# 📘 README – Etapa 5: Configurarea și Antrenarea Modelului RN

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** NAE Raoul-Alexandru  
**Link Repository GitHub:** https://github.com/NaeRaoulAlexandru/Retele-Neuronale
**Data predării:** 11.01.2026 (actualizat)

---


## Scopul Etapei 5

Această etapă corespunde punctului **6. Configurarea și antrenarea modelului RN** din lista de 9 etape - slide 2 **RN Specificatii proiect.pdf**.

**Obiectiv principal:** Antrenarea efectivă a modelului RN definit în Etapa 4, evaluarea performanței și integrarea în aplicația completă.

**Pornire obligatorie:** Arhitectura completă și funcțională din Etapa 4:
- State Machine definit și justificat
- Cele 3 module funcționale (Data Logging, RN, UI)
- Minimum 40% date originale în dataset

---

## PREREQUISITE – Verificare Etapa 4 (OBLIGATORIU)

**Înainte de a începe Etapa 5, verificați că aveți din Etapa 4:**

- [X] **State Machine** definit și documentat în `docs/state_machine.*`
- [X] **Contribuție ≥40% date originale** în `data/generated/` (verificabil)
- [X] **Modul 1 (Data Logging)** funcțional - produce CSV-uri
- [X] **Modul 2 (RN)** cu arhitectură definită dar NEANTRENATĂ (`models/untrained_model.h5`)
- [X] **Modul 3 (UI/Web Service)** funcțional cu model dummy
- [X] **Tabelul "Nevoie → Soluție → Modul"** complet în README Etapa 4

** Dacă oricare din punctele de mai sus lipsește → reveniți la Etapa 4 înainte de a continua.**

---

## Pregătire Date pentru Antrenare 

### Dacă ați adăugat date noi în Etapa 4 (contribuția de 40%):

**TREBUIE să refaceți preprocesarea pe dataset-ul COMBINAT:**

Exemplu:
```bash
# 1. Combinare date vechi (Etapa 3) + noi (Etapa 4)
python src/preprocessing/combine_datasets.py

# 2. Refacere preprocesare COMPLETĂ
python src/preprocessing/data_cleaner.py
python src/preprocessing/feature_engineering.py
python src/preprocessing/data_splitter.py --stratify --random_state 42

# Verificare finală:
# data/train/ → trebuie să conțină date vechi + noi
# data/validation/ → trebuie să conțină date vechi + noi
# data/test/ → trebuie să conțină date vechi + noi
```

** ATENȚIE - Folosiți ACEIAȘI parametri de preprocesare:**
- Același `scaler` salvat în `config/preprocessing_params.pkl`
- Aceiași proporții split: 70% train / 15% validation / 15% test
- Același `random_state=42` pentru reproducibilitate

**Verificare rapidă:**
```python
import pandas as pd
train = pd.read_csv('data/train/X_train.csv')
print(f"Train samples: {len(train)}")  # Trebuie să includă date noi
```

---

##  Cerințe Structurate pe 3 Niveluri

### Nivel 1 – Obligatoriu pentru Toți (70% din punctaj)

Completați **TOATE** punctele următoare:

1. **Antrenare model** definit în Etapa 4 pe setul final de date (≥40% originale)
2. **Minimum 10 epoci**, batch size 8–32
3. **Împărțire stratificată** train/validation/test: 70% / 15% / 15%
4. **Tabel justificare hiperparametri** (vezi secțiunea de mai jos - OBLIGATORIU)
5. **Metrici calculate pe test set:**
   - **Acuratețe ≥ 65%** : mAP50 92.46%
   - **F1-score (macro) ≥ 0.60** 0.8748
6. **Salvare model antrenat** în `models/trained_model.h5` (Keras/TensorFlow) sau `.pt` (PyTorch) sau `.lvmodel` (LabVIEW)
7. **Integrare în UI din Etapa 4:**
   - UI trebuie să încarce modelul ANTRENAT (nu dummy)
   - Inferență REALĂ demonstrată
   - Screenshot în `docs/screenshots/inference_real.png`

#### Tabel Hiperparametri și Justificări (OBLIGATORIU - Nivel 1)

Completați tabelul cu hiperparametrii folosiți și **justificați fiecare alegere**:

| **Hiperparametru** | **Valoare Aleasă** | **Justificare** |
|--------------------|-------------------|-----------------|
| Learning rate | Auto (AdamW) + cos_lr | Am activat Cosine Decay Scheduler (cos_lr=True). Rata de învățare scade lin spre final, permițând modelului să convergă fin în minimul global fără oscilații |
| Batch size | 8 | Am redus batch-ul (standard 16 -> 8) pentru a compensa consumul de memorie crescut cauzat de imaginile mari (1024px), prevenind erorile Out Of Memory. |
| Number of epochs | 150 | Antrenarea From Scratch necesită mai mult timp pentru a extrage trăsături complexe. Am setat un plafon ridicat. |
| Optimizer | AdamW | Specificat explicit (optimizer='AdamW'). Este standardul actual pentru transformeri și CNN-uri moderne, gestionând eficient regularizarea ("Weight Decay"). |
| Class Weight | cls=4.0 | Strategie Anti-Imbalance: Am mărit drastic penalizarea pentru erorile de clasificare (Default 0.5 → 4.0) pentru a forța modelul să nu ignore clasele rare (Toleranțe/Rugozități). |
| Mosaic | close_mosaic=15 | Am oprit augmentarea Mosaic în ultimele 15 epoci. Aceasta permite modelului să se "calibreze" pe imagini reale, nealterate, înainte de testul final. |
| Image Size | 1024 | Critic: Am crescut rezoluția de la 640 la 1024px. Deoarece simbolurile de Rugozitate sunt minuscule, la 640px deveneau ilizibile (3-4 pixeli). 1024px păstrează detaliile geometrice esențiale. |
| Activation / Loss | SiLU/Tal | Arhitectură standard YOLOv8: SiLU pentru neliniaritate și Task Aligned Loss (CIoU + BCE + DFL) pentru optimizare simultană a cutiei și clasei. |

---

### Nivel 2 – Recomandat (85-90% din punctaj)

Includeți **TOATE** cerințele Nivel 1 + următoarele:

1. **Early Stopping** - patience=25.Antrenarea s-a oprit automat când val_loss nu a mai scăzut, prevenind memorarea mecanică (overfitting) a datelor de antrenare. 
2. **Learning Rate Scheduler** - cos_lr pentru ajustarea dinamică a ratei de învățare.
3. **Augmentări relevante domeniu:** Mosaic: Folosită intens pentru a învăța detectarea obiectelor mici prin combinarea a 4 imagini într-un grid. 
4. **Grafic loss și val_loss** în funcție de epoci salvat în `docs/loss_curve.png`
5. **Analiză erori context industrial** (vezi secțiunea dedicată mai jos - OBLIGATORIU Nivel 2)

**Indicatori țintă Nivel 2:**
- **Acuratețe ≥ 75%** : mAP50 92.46%
- **F1-score (macro) ≥ 0.70** : 0.8748

---

### Nivel 3 – Bonus (până la 100%)

**Punctaj bonus per activitate:**

| **Activitate** |  **Livrabil** |
|----------------|--------------|
| Comparare 2+ arhitecturi diferite | Tabel comparativ + justificare alegere finală în README |
| Export ONNX/TFLite + benchmark latență | Fișier `models/final_model.onnx` + demonstrație <50ms |
| Confusion Matrix + analiză 5 exemple greșite | `docs/confusion_matrix.png` + analiză în README |

**Activitate: Selecția Modelului Final (Comparativ):**

| **Metrica** | **Model 1 (Baseline:640px)** | **Model 2 (Optimizat: 1024px)** | **Diferență** |
|-------------|--------------|-------------|------------------|
| mAP50 | 0.9122 | 0.9246 | +1.24% |
| Recall | 0.8578 | 0.8954 | +3.76% |
| Precision | 0.8667 | 0.8550 | -1.17% |

**Concluzie și Selecție:** Am selectat Modelul 2 pentru integrarea finală. Deși Modelul 1 are o precizie ușor mai mare (mai puține alarme false), Modelul 2 oferă un Recall superior (+3.76%) și o localizare geometrică mai bună (+3.43% la mAP50-95). În contextul desenului tehnic, capacitatea de a "vedea" detaliile fine (facilitată de rezoluția 1024px) este factorul decisiv.

---

## Verificare Consistență cu State Machine (Etapa 4)

Antrenarea și inferența trebuie să respecte fluxul din State Machine-ul vostru definit în Etapa 4.

**Exemplu pentru monitorizare vibrații lagăr:**

| **Stare din Etapa 4** | **Implementare în Etapa 5** |
|-----------------------|-----------------------------|
| `ACQUIRE_DATA` | Citire batch date din `data/train/` pentru antrenare |
| `PREPROCESS` | Aplicare scaler salvat din `config/preprocessing_params.pkl` |
| `RN_INFERENCE` | Forward pass cu model ANTRENAT (nu weights random) |
| `THRESHOLD_CHECK` | Clasificare Normal/Uzură pe baza output RN antrenat |
| `ALERT` | Trigger în UI bazat pe predicție modelului real |

**În `src/app/main.py` (UI actualizat):**

Verificați că **TOATE stările** din State Machine sunt implementate cu modelul antrenat:

```python
# ÎNAINTE (Etapa 4 - model dummy):
model = keras.models.load_model('models/untrained_model.h5')  # weights random
prediction = model.predict(input_scaled)  # output aproape aleator

# ACUM (Etapa 5 - model antrenat):
model = keras.models.load_model('models/trained_model.h5')  # weights antrenate
prediction = model.predict(input_scaled)  # predicție REALĂ și corectă
```

---

## Analiză Erori în Context Industrial (OBLIGATORIU Nivel 2)

**Nu e suficient să raportați doar acuratețea globală.** Analizați performanța în contextul aplicației voastre industriale:

### 1. Pe ce clase greșește cel mai mult modelul?

**Exemplu robotică (predicție traiectorii):**
```
Confusion Matrix arată că modelul confundă 'viraj stânga' cu 'viraj dreapta' în 18% din cazuri.
Cauză posibilă: Features-urile IMU (gyro_z) sunt simetrice pentru viraje în direcții opuse.
```

**Completați pentru proiectul vostru:**
```
Modelul întâmpină dificultăți ocazionale în a distinge Cotele foarte mici (cifre izolate) de textul auxiliar din cartuș sau note tehnice, din cauza similitudinii vizuale (caractere negre pe fundal alb).

```

### 2. Ce caracteristici ale datelor cauzează erori?

**Exemplu vibrații motor:**
```
Modelul eșuează când zgomotul de fond depășește 40% din amplitudinea semnalului util.
În mediul industrial, acest nivel de zgomot apare când mai multe motoare funcționează simultan.

```

**Completați pentru proiectul vostru:**
```
Limitare Metodologică (Rezoluție): Setul de date a fost preprocesat inițial la 640x640px. Deși antrenarea s-a efectuat cu imgsz=1024, detaliile fine pierdute la compresia inițială nu au putut fi recuperate total prin upscaling. Totuși, performanța ridicată (92%) arată că formele geometrice ale simbolurilor au rămas suficient de distincte.

Densitatea: Suprapunerea liniilor de cotă cu geometria piesei (feature specific desenului tehnic) complică regresia precisă a cutiei OBB.

```

### 3. Ce implicații are pentru aplicația industrială?

**Exemplu detectare defecte sudură:**
```
FALSE NEGATIVES (defect nedetectat): CRITIC → risc rupere sudură în exploatare
FALSE POSITIVES (alarmă falsă): ACCEPTABIL → piesa este re-inspectată manual

Prioritate: Minimizare false negatives chiar dacă cresc false positives.
Soluție: Ajustare threshold clasificare de la 0.5 → 0.3 pentru clasa 'defect'.

```

**Completați pentru proiectul vostru:**
```
False Negatives (Critic): Dacă o Rugozitate este ratată (Recall mic), sistemul CAPP va genera un plan tehnologic greșit (ex: strunjire în loc de rectificare), ducând la piese rebutate fizic.

False Positives (Acceptabil): O detecție falsă (ex: o pată de ulei văzută ca o cotă) poate fi invalidată rapid de inginer în interfața UI ("Human-in-the-loop").

Decizie: Am prioritizat un model cu Recall mare (89.54%) chiar dacă am sacrificat puțin din Precizie.

```

### 4. Ce măsuri corective propuneți?

**Exemplu clasificare imagini piese:**
```
Măsuri corective:
1. Colectare 500+ imagini adiționale pentru clasa minoritară 'zgârietură ușoară'
2. Implementare filtrare Gaussian blur pentru reducere zgomot cameră industrială
3. Augmentare perspective pentru simulare unghiuri camera variabile (±15°)
4. Re-antrenare cu class weights: [1.0, 2.5, 1.2] pentru echilibrare

```

**Completați pentru proiectul vostru:**
```
Măsura luată: Modificarea arhitecturii de antrenare pentru a accepta imagini de 1024x1024 px. Chiar și cu date upscaled, această măsură a crescut Recall-ul semnificativ față de varianta standard 640px.

Măsură propusă: Reprocesarea completă a datelor raw direct la 1024px (sau păstrarea rezoluției native) și colectarea a 50 imagini suplimentare ("Oversampling") pentru clasa Toleranțe.

```

---

## Structura Repository-ului la Finalul Etapei 5

**Clarificare organizare:** Vom folosi **README-uri separate** pentru fiecare etapă în folderul `docs/`:

```
proiect-rn-[prenume-nume]/
├── README.md                           # Overview general proiect (actualizat)
├── etapa3_analiza_date.md         # Din Etapa 3
├── etapa4_arhitectura_sia.md      # Din Etapa 4
├── etapa5_antrenare_model.md      # ← ACEST FIȘIER (completat)
│
├── docs/
│   ├── state_machine.png              # Din Etapa 4
│   ├── loss_curve.png                 # NOU - Grafic antrenare
│   ├── confusion_matrix.png           # (opțional - Nivel 3)
│   └── screenshots/
│       ├── inference_real.png         # NOU - OBLIGATORIU
│       └── ui_demo.png                # Din Etapa 4
│
├── data/                               # Din Etapa 3-4 (NESCHIMBAT)
│   ├── raw/
│   ├── generated/                     # Contribuția voastră 40%
│   ├── processed/
│   ├── train/
│   ├── validation/
│   └── test/
│
├── src/
│   ├── data_acquisition/              # Din Etapa 4
│   ├── preprocessing/                 # Din Etapa 3
│   │   └── combine_datasets.py        # NOU (dacă ați adăugat date în Etapa 4)
│   ├── neural_network/
│   │   ├── model.py                   # Din Etapa 4
│   │   ├── train.py                   # NOU - Script antrenare
│   │   └── evaluate.py                # NOU - Script evaluare
│   └── app/
│       └── main.py                    # ACTUALIZAT - încarcă model antrenat
│
├── models/
│   ├── untrained_model.h5             # Din Etapa 4
│   ├── trained_model.h5               # NOU - OBLIGATORIU
│   └── final_model.onnx               # (opțional - Nivel 3 bonus)
│
├── results/                            # NOU - Folder rezultate antrenare
│   ├── training_history.csv           # OBLIGATORIU - toate epoch-urile
│   ├── test_metrics.json              # Metrici finale pe test set
│   └── hyperparameters.yaml           # Hiperparametri folosiți
│
├── config/
│   └── preprocessing_params.pkl       # Din Etapa 3 (NESCHIMBAT)
│
├── requirements.txt                    # Actualizat
└── .gitignore
```

**Diferențe față de Etapa 4:**
- Adăugat `docs/etapa5_antrenare_model.md` (acest fișier)
- Adăugat `docs/loss_curve.png` (Nivel 2)
- Adăugat `models/trained_model.h5` - OBLIGATORIU
- Adăugat `results/` cu history și metrici
- Adăugat `src/neural_network/train.py` și `evaluate.py`
- Actualizat `src/app/main.py` să încarce model antrenat

---

## Instrucțiuni de Rulare (Actualizate față de Etapa 4)

### 1. Setup mediu (dacă nu ați făcut deja)

```bash
pip install -r requirements.txt
```

### 2. Pregătire date (DACĂ ați adăugat date noi în Etapa 4)

```bash
# Combinare + reprocesare dataset complet
python src/preprocessing/combine_datasets.py
python src/preprocessing/data_cleaner.py
python src/preprocessing/feature_engineering.py
python src/preprocessing/data_splitter.py --stratify --random_state 42
```

### 3. Antrenare model

```bash
python src/neural_network/train.py 

# Output așteptat:
# Epoch 1/50 - loss: 0.8234 - accuracy: 0.6521 - val_loss: 0.7891 - val_accuracy: 0.6823
# ...
# Epoch 23/50 - loss: 0.3456 - accuracy: 0.8234 - val_loss: 0.4123 - val_accuracy: 0.7956
# Early stopping triggered at epoch 23
# ✓ Model saved to models/trained_model.h5
```

### 4. Evaluare pe test set

```bash
python src/neural_network/evaluate.py 

# Output așteptat:
# Test Accuracy: 0.7823
# Test F1-score (macro): 0.7456
# ✓ Metrics saved to results/test_metrics.json
# ✓ Confusion matrix saved to docs/confusion_matrix.png
```

### 5. Lansare UI cu model antrenat

```bash
streamlit run src/app/app.py

# SAU pentru LabVIEW:
# Deschideți WebVI și rulați main.vi
```

**Testare în UI:**
1. Introduceți date de test (manual sau upload fișier)
2. Verificați că predicția este DIFERITĂ de Etapa 4 (când era random)
3. Verificați că confidence scores au sens (ex: 85% pentru clasa corectă)
4. Faceți screenshot → salvați în `docs/screenshots/inference_real.png`

---

## Checklist Final – Bifați Totul Înainte de Predare

### Prerequisite Etapa 4 (verificare)
- [X] State Machine există și e documentat în `docs/state_machine.*`
- [X] Contribuție ≥40% date originale verificabilă în `data/generated/`
- [X] Cele 3 module din Etapa 4 funcționale

### Preprocesare și Date
- [X] Dataset combinat (vechi + nou) preprocesat (dacă ați adăugat date)
- [X] Split train/val/test: 70/15/15% (verificat dimensiuni fișiere)
- [X] Scaler din Etapa 3 folosit consistent (`config/preprocessing_params.pkl`)

### Antrenare Model - Nivel 1 (OBLIGATORIU)
- [X] Model antrenat de la ZERO (nu fine-tuning pe model pre-antrenat)
- [X] Minimum 10 epoci rulate (verificabil în `results/training_history.csv`)
- [X] Tabel hiperparametri + justificări completat în acest README
- [X] Metrici calculate pe test set: **Accuracy ≥65%**, **F1 ≥0.60**
- [X] Model salvat în `models/trained_model.h5` (sau .pt, .lvmodel)
- [X] `results/training_history.csv` există cu toate epoch-urile

### Integrare UI și Demonstrație - Nivel 1 (OBLIGATORIU)
- [X] Model ANTRENAT încărcat în UI din Etapa 4 (nu model dummy)
- [X] UI face inferență REALĂ cu predicții corecte
- [X] Screenshot inferență reală în `docs/screenshots/inference_real.png`
- [X] Verificat: predicțiile sunt diferite față de Etapa 4 (când erau random)

### Documentație Nivel 2 (dacă aplicabil)
- [X] Early stopping implementat și documentat în cod
- [X] Learning rate scheduler folosit (ReduceLROnPlateau / StepLR)
- [X] Augmentări relevante domeniu aplicate (NU rotații simple!)
- [X] Grafic loss/val_loss salvat în `docs/loss_curve.png`
- [X] Analiză erori în context industrial completată (4 întrebări răspunse)
- [X] Metrici Nivel 2: **Accuracy ≥75%**, **F1 ≥0.70**

### Documentație Nivel 3 Bonus (dacă aplicabil)
- [X] Comparație 2+ arhitecturi (tabel comparativ + justificare)
- [ ] Export ONNX/TFLite + benchmark latență (<50ms demonstrat)
- [X] Confusion matrix + analiză 5 exemple greșite cu implicații

### Verificări Tehnice
- [x] `requirements.txt` actualizat cu toate bibliotecile noi
- [X] Toate path-urile RELATIVE (nu absolute: `/Users/...` )
- [X] Cod nou comentat în limba română sau engleză (minimum 15%)
- [X] `git log` arată commit-uri incrementale (NU 1 commit gigantic)
- [X] Verificare anti-plagiat: toate punctele 1-5 respectate

### Verificare State Machine (Etapa 4)
- [X] Fluxul de inferență respectă stările din State Machine
- [X] Toate stările critice (PREPROCESS, INFERENCE, ALERT) folosesc model antrenat
- [X] UI reflectă State Machine-ul pentru utilizatorul final

### Pre-Predare
- [X] `docs/etapa5_antrenare_model.md` completat cu TOATE secțiunile
- [X] Structură repository conformă: `docs/`, `results/`, `models/` actualizate
- [X] Commit: `"Etapa 5 completă – Accuracy=X.XX, F1=X.XX"`
- [X] Tag: `git tag -a v0.5-model-trained -m "Etapa 5 - Model antrenat"`
- [X] Push: `git push origin main --tags`
- [X] Repository accesibil (public sau privat cu acces profesori)

---

## Livrabile Obligatorii (Nivel 1)

Asigurați-vă că următoarele fișiere există și sunt completate:

1. **`docs/etapa5_antrenare_model.md`** (acest fișier) cu:
   - Tabel hiperparametri + justificări (complet)
   - Metrici test set raportate (accuracy, F1)
   - (Nivel 2) Analiză erori context industrial (4 paragrafe)

2. **`models/trained_model.h5`** (sau `.pt`, `.lvmodel`) - model antrenat funcțional

3. **`results/training_history.csv`** - toate epoch-urile salvate

4. **`results/test_metrics.json`** - metrici finale:

Exemplu:
```json
{
  "test_accuracy": 0.7823,
  "test_f1_macro": 0.7456,
  "test_precision_macro": 0.7612,
  "test_recall_macro": 0.7321
}
```

5. **`docs/screenshots/inference_real.png`** - demonstrație UI cu model antrenat

6. **(Nivel 2)** `docs/loss_curve.png` - grafic loss vs val_loss

7. **(Nivel 3)** `docs/confusion_matrix.png` + analiză în README

---

## Predare și Contact

**Predarea se face prin:**
1. Commit pe GitHub: `"Etapa 5 completă – Accuracy=X.XX, F1=X.XX"`
2. Tag: `git tag -a v0.5-model-trained -m "Etapa 5 - Model antrenat"`
3. Push: `git push origin main --tags`

---


**Mult succes! Această etapă demonstrează că Sistemul vostru cu Inteligență Artificială (SIA) funcționează în condiții reale!**

