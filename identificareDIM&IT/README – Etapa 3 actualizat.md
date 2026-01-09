# 📘 README – Etapa 3: Analiza și Pregătirea Setului de Date pentru Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** NAE RAOUL-ALEXANDRU 
**Data:** 09.01.2026 (Actualizat)

---

## Introducere

Acest document descrie activitățile realizate în **Etapa 3**, în care se analizează și se preprocesează setul de date necesar proiectului „Rețele Neuronale". Scopul etapei este pregătirea corectă a datelor pentru instruirea modelului RN, respectând bunele practici privind calitatea, consistența și reproductibilitatea datelor.

---

##  1. Structura Repository-ului Github (versiunea Etapei 3)

```
project-name/
├── README.md
├── docs/
│   └── datasets/          # descriere seturi de date, surse, diagrame
├── data/
│   ├── raw/               # Imaginile originale (41 buc) + XML/TXT Roboflow
│   ├── processed/         # date curățate și transformate
│   ├── train/            # 140 imagini (70%)
│   │   ├── images/
│   │   └── labels/
│   ├── validation/       # 30 imagini (15%)
│   │   ├── images/
│   │   └── labels/
│   └── test/             # 35 imagini (15%) (fiind 41 de poze, python a calculat % si a rotunjit)
│       ├── images/
│       └── labels/  
├── src/
│   ├── preprocessing/     # funcții pentru preprocesare
       └── etl_pipeline.py       # Scriptul de Data Engineering (Augmentare, Split + DATA LOGGING care creeaza fisier csv)
│   ├── data_acquisition/  # generare / achiziție date (dacă există)
│   └── neural_network/    # implementarea RN (în etapa următoare)
├── config/                # fișiere de configurare
└── requirements.txt       # dependențe Python (dacă aplicabil)
```

---

##  2. Descrierea Setului de Date

### 2.1 Sursa datelor

* **Origine:** Documentație tehnică (desene de execuție) provenită din suportul de curs "Procese Industriale".
* **Modul de achiziție:**  ☐ Fișier extern (1.Selecție manuală a 41 de desene relevante din suportul de curs. 2. Etichetare manuală (Manual Annotation) utilizând platforma Roboflow. 3. Augmentare sintetică prin script Python propriu.)
* **Perioada / condițiile colectării:** Decembrie 2025

### 2.2 Caracteristicile dataset-ului

* **Număr total de observații:** 205 imagini (41 originale + 164 augmentate).
* **Număr de caracteristici (features):** [4] (Cote, Rugozități, Toleranțe, Diametru).
* **Tipuri de date:**  ☐ Imagini
* **Format fișiere:** ☐ JPG / ☐ TXT (format YOLO OBB - Oriented Bounding Box)

### 2.3 Descrierea fiecărei caracteristici

| **Caracteristică** | **Tip** | **Unitate** | **Descriere** | **Domeniu valori** |
|-------------------|---------|-------------|---------------|--------------------|
| Cota | categorial OBB (Poligon) | - | Dimensiuni liniare ale piesei | (~10-20 per desen) |
| Rugozitate (Ra) | categorial OBB (Poligon) | – | Simboluri de calitate a suprafeței (ex: Ra 3.2) | (~2-5 per desen) |
| Toleranta | categorial OBB (Poligon) | - | Abateri dimensionale | (~1-3 per desen) |
| Diametru | categorial OBB (Poligon) | - | Simbol diametru | (~7-12 per desen) |
| ... | ... | ... | ... | ... |

**Fișier recomandat:**  `data/README.md`

---

##  3. Analiza Exploratorie a Datelor (EDA) – Sintetic

### 3.1 Statistici descriptive aplicate

* **Medie, mediană, deviație standard**
* **Min–max și quartile**
* **Distribuții pe caracteristici** (histograme)
* **Identificarea outlierilor** (IQR / percentile)

### 3.2 Analiza calității datelor

* **Detectarea valorilor lipsă** (% pe coloană)
* **Detectarea valorilor inconsistente sau eronate**
* **Identificarea caracteristicilor redundante sau puternic corelate**

### 3.3 Probleme identificate

* [exemplu] Variabilitate ridicată în clase (class imbalance)

---

##  4. Preprocesarea Datelor

### 4.1 Curățarea datelor

* **Eliminare duplicatelor**
* **Tratarea valorilor lipsă:**
  * Feature A: imputare cu mediană
  * Feature B: eliminare (30% valori lipsă)
* **Tratarea outlierilor:** IQR / limitare percentile

### 4.2 Transformarea caracteristicilor

* **Resize (Redimensionare):**

* Toate imaginile au fost aduse la rezoluția 640x640 px (metoda Stretch) pentru a fi compatibile cu input-ul standard YOLOv8.

* **Augmentare Geometrică (Critică pentru OBB):**

*Rotație: Random între -2° și +2°.

*Important: Coordonatele poligoanelor din fișierele .txt au fost recalculate matematic pentru a se potrivi cu noua orientare a imaginii.

* **Augmentare Fotometrică (Simulare condiții reale):**

*Luminozitate: Variații aleatoare între -15% și +15%.

*Zgomot (Noise): Adăugare zgomot Gaussian pe max 1.25% din pixeli (simulare cameră slabă/praf).

### 4.3 Structurarea seturilor de date

**Împărțire recomandată:**
* 80% – train
* 15% – validation
* 15% – test

**Principii respectate:**
* Stratificare pentru clasificare
* Fără scurgere de informație (data leakage)
* Statistici calculate DOAR pe train și aplicate pe celelalte seturi

### 4.4 Salvarea rezultatelor preprocesării

* Date preprocesate în `data/processed/`
* Seturi train/val/test în foldere dedicate
* Parametrii de preprocesare în `config/preprocessing_config.*` (opțional)

---

##  5. Fișiere Generate în Această Etapă

* `data/raw/` – date brute
* `data/processed/` – date curățate & transformate
* `data/train/`, `data/validation/`, `data/test/` – seturi finale
* `src/preprocessing/` – codul de preprocesare
* `data/README.md` – descrierea dataset-ului

---

##  6. Stare Etapă (de completat de student)

- [X] Structură repository configurată
- [X] Dataset analizat (EDA realizată)
- [X] Date preprocesate
- [X] Seturi train/val/test generate
- [X] Documentație actualizată în README + `data/README.md`

---
