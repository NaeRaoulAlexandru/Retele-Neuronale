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
|   |    ├── filete/
|   |    ├── racordari/
|   |    ├── tesituri/
│   ├── processed/         # date curățate și transformate
│   ├── train/             # set de instruire
│   ├── validation/        # set de validare
│   └── test/              # set de testare
├── src/
│   ├── preprocessing/     # funcții pentru preprocesare
│   ├── data_acquisition/  # generare / achiziție date (dacă există)
│   └── neural_network/    # implementarea RN (în etapa următoare)
├── config/                # fișiere de configurare
└── requirements.txt       # dependențe Python (dacă aplicabil)
```

---

##  2. Descrierea Setului de Date

### 2.1 Sursa datelor

* **Origine:** [Dataset public de desene tehnice pentru diferite piese mecanice]
* **Modul de achiziție:** Fisiere externe si generare programabila pentru inclinarea capturilor la anumite grade
* **Perioada / condițiile colectării:** [Noiembrie 2025 - Decembrie 2025]

### 2.2 Caracteristicile dataset-ului

* **Număr total de observații:** 
* **Număr de caracteristici (features):** 
* **Tipuri de date:** Categoriale / Imagini
* **Format fișiere:** PNG

### 2.3 Descrierea fiecărei caracteristici

| **Caracteristică** | **Tip** | **Unitate** | **Descriere** | **Domeniu valori** |
|-------------------|---------|-------------|---------------|--------------------|
| pixeli | numeric | intensitate | valorile pixelilor | 0-255 |
| cota | categorial | – | cotele sunt de diferite tipuri (1-gauri, 2-filete, 3-racordari, 4-tesituri, 5-lungimi, 6-diametre) | 1-6 |
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

* [exemplu] Feature X are 8% valori lipsă
* [exemplu] Distribuția feature Y este puternic neuniformă
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
