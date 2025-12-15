# 📘 README – Etapa 3: Analiza și Pregătirea Setului de Date pentru Rețele Neuronale

Proiectul are ca scop recomandarea proceselor de prelucrare in functie de dimensiunile desenului si standardele impuse.

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** NAE RAOUL-ALEXANDRU 
**Data:** 25.11.2025  

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
│   ├── raw/               # am adaugat poze din diferite desene de executie cu informatii de pe desen
│   ├── processed/         # date curățate și transformate
│   ├── train/             # set de instruire
│   │   ├── images/
│   │   └── labels/
│   ├── validation/        # set de validare
│   │   ├── images/
│   │   └── labels/
│   └── test/         # set de testare
│       ├── images/
│       └── labels/
├── src/
│   ├── preprocessing/     # funcții pentru preprocesare
│   ├── data_acquisition/  # generare / achiziție date (dacă există)
│   └── neural_network/    # implementarea RN (în etapa următoare)
├── config/                # fișiere de configurare
│   └── data.yaml          # fișier de configurare clase și căi
└── requirements.txt       # ultralytics, shutil, os, glob
```

---

##  2. Descrierea Setului de Date

### 2.1 Sursa datelor

* **Origine:** [Dataset propriu constituit din fotografii și scanări ale desenelor tehnice industriale.]
* **Modul de achiziție:**  Fisier extern (Roboflow) 
* **Perioada / condițiile colectării:** [Noiembrie 2025 - Decembrie 2025]

### 2.2 Caracteristicile dataset-ului

* **Număr total de observații: 140 (dupa augmentare), 41** 
* **Număr de caracteristici (features):** 8 clase distincte (Ra, cota, filet, gauri, racordare, simbol_diam, tesitura, toleranta)
* **Tipuri de date:** Imagini 
* **Format fișiere:** JPG/PNG (Imagini) / ☑ TXT (Adnotări format YOLO)

### 2.3 Descrierea fiecărei caracteristici

| **Caracteristică** | **Tip** | **Unitate** | **Descriere** | **Domeniu valori** |
|-------------------|---------|-------------|---------------|--------------------|
| Imagine | matrice pixeli | px | Imagine bruta redimensionata | 0-255 |
| Rezolutie | dimensiune | px | Rezolutia de intrare in retea | 640 x 640 |
| Bounding Box | numeric | coordonate | Pozitia obiectului | 0-1 |
| Clasa | cateforial | intreg | indicele clasei detectate | 0-7 |

**Fișier recomandat:**  `data/dataset_rebalansat/data.yaml`

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
* Dezechilibru de clasă: Clasa filet are un număr critic de mic de exemple (< 5% din total instanțe), rezultând inițial într-un Recall de 0%.
* Rezoluție insuficientă: La rezoluția standard de $640 \times 640$, detaliile fine ale hașurilor de filet se pierdeau, fiind confundate cu fundalul.
* Split incorect inițial: Roboflow a generat un split disproporționat (133 Train vs 4 Valid), ceea ce a dus la instabilitate în antrenament.

---

##  4. Preprocesarea Datelor

### 4.1 Curățarea datelor

* **Eliminare duplicatelor**
* **Tratarea valorilor lipsă:**
  * Feature A: imputare cu mediană
  * Feature B: eliminare (30% valori lipsă)
* **Tratarea outlierilor:** IQR / limitare percentile

### 4.2 Transformarea caracteristicilor

* **Normalizare:** Min–Max / Standardizare
* **Encoding pentru variabile categoriale**
* **Ajustarea dezechilibrului de clasă** (dacă este cazul)

### 4.3 Structurarea seturilor de date

**Împărțire recomandată:**
* 80% – train
* 10% – validation
* 10% – test

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
