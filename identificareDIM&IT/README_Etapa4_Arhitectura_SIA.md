# 📘 README – Etapa 4: Arhitectura Completă a Aplicației SIA bazată pe Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** NAE Raoul-Alexandru  
**Link Repository GitHub**: https://github.com/NaeRaoulAlexandru/Retele-Neuronale/tree/main
**Data:** 09.12.2025  
---

## Scopul Etapei 4

Această etapă corespunde punctului **5. Dezvoltarea arhitecturii aplicației software bazată pe RN** din lista de 9 etape - slide 2 **RN Specificatii proiect.pdf**.

**Trebuie să livrați un SCHELET COMPLET și FUNCȚIONAL al întregului Sistem cu Inteligență Artificială (SIA). In acest stadiu modelul RN este doar definit și compilat (fără antrenare serioasă).**

### IMPORTANT - Ce înseamnă "schelet funcțional":

 **CE TREBUIE SĂ FUNCȚIONEZE:**
- Toate modulele pornesc fără erori
- Pipeline-ul complet rulează end-to-end (de la date → până la output UI)
- Modelul RN este definit și compilat (arhitectura există)
- Web Service/UI primește input și returnează output

 **CE NU E NECESAR ÎN ETAPA 4:**
- Model RN antrenat cu performanță bună
- Hiperparametri optimizați
- Acuratețe mare pe test set
- Web Service/UI cu funcționalități avansate

**Scopul anti-plagiat:** Nu puteți copia un notebook + model pre-antrenat de pe internet, pentru că modelul vostru este NEANTRENAT în această etapă. Demonstrați că înțelegeți arhitectura și că ați construit sistemul de la zero.

---

##  Livrabile Obligatorii

### 1. Tabelul Nevoie Reală → Soluție SIA → Modul Software (max ½ pagină)
Completați in acest readme tabelul următor cu **minimum 2-3 rânduri** care leagă nevoia identificată în Etapa 1-2 cu modulele software pe care le construiți (metrici măsurabile obligatoriu):

| **Nevoie reală concretă** | **Cum o rezolvă SIA-ul vostru** | **Modul software responsabil** |
|---------------------------|--------------------------------|--------------------------------|
| Validarea rapidă a documentației: Verificarea manuală a prezenței tuturor cotelor și toleranțelor pe un desen A3 durează ~5-10 minute.| Detectare automată și inventariere: Identificarea instantanee (< 2 secunde) a tuturor simbolurilor (Cote, Ra, Toleranțe) și afișarea lor într-o listă de verificare. | RN + UI |
| Asistență decizională: Inginerii juniori pot alege greșit procedeul de prelucrare pentru o anumită rugozitate (ex: strunjire în loc de rectificare). | Logică de Recomandare: Algoritmul sugerează automat operația (ex: "Rectificare") bazat pe asocierea detectată {Cotă + Ra 0.8}. | UI |
| Crearea bazei de date (Data Loop) Lipsa dataset-urilor publice cu simboluri ISO/STAS pentru antrenarea algoritmilor. | Data Logging Automat: Salvarea desenelor validate de utilizator și generarea sintetică (augmentare) a noi date pentru re-antrenare. | Data Acquisition + UI |

---

#### Tipuri de contribuții acceptate

| **Tip contribuție** | **Exemple concrete din inginerie** | **Dovada minimă cerută** |
|---------------------|-------------------------------------|--------------------------|
| **Etichetare/adnotare manuală** | • Etichetat manual 950 de clase in RoboFLOW | Fișier Excel/JSON cu labels + capturi ecran tool etichetare + log timestamp-uri lucru |

### Contribuția originală la setul de date:

**Total observații finale:** 140 imagini
**Observații originale:** 41 imagini (100%)

**Tipul contribuției:**
[] Date generate prin simulare fizică  
[X] Date achiziționate cu senzori proprii 
[X] Etichetare/adnotare manuală (Roboflow) 
[ ] Date sintetice prin metode avansate  

**Descriere detaliată:**
Datele(desenele de executie) au fost luate dint-un document primit la un curs de procese industriale. Aici se regaseau ~140 de desene de executie. Am ales aleator 41 de poze. 

Datele au fost importate pe platforma Roboflow, unde le-am parcurs pe toate si am etichetat fiecare informatie(rugozitate,cota,simboluri,etc). Apoi le-am preprocesat (Stretch to 640x640 px) si am folosit metodele de augmentare(Rotation:Between -2° and +2°; Brightness: Between -15% and +15%; Noise: Up to 1.25% of pixels). Astfel au rezultat 140 de poze.

Acestea au fost exportate in format YoloV8 unde fiecare fisier (train/valid/test) au cate 2 fisiere: image si label. Fisierul image cuprinde toate pozele cu desene in format .jpg, iar cel label cuprinde file in format .txt ce au informatii despre fiecare "dreptunghi" plasat in acea imagine si ce clasa reprezinta acesta. 

**Locația codului:** `src/data_acquisition/[numele_scriptului]`
**Locația datelor:** `data/generated/` sau `data/raw/original/`

**Dovezi:**
- Grafic comparativ: `docs/generated_vs_real.png`
- Setup experimental: `docs/acquisition_setup.jpg` (dacă aplicabil)
- Tabel statistici: `docs/data_statistics.csv`
---

### 3. Legenda State Machine

Am ales o arhitectura de tip "Human-in-the-loop CAPP" (Computer-Aided Process Planning asistat), pentru ca automatizarea totala a desenelor tehnice prezinta riscuri de eroare contextuala. Desi Reteaua Neuronala poate detecta cu precizie prezenta simbolurilor, ea nu poate deduce automat relatiile tehnologice dintre acestea (ex: ce rugozitate se aplica acestei cote?).

### Stările principale sunt:

1. **[IDLE]:** Sistemul este în repaus, interfața web (Modul 3) așteaptă încărcarea unui fișier de tip imagine (JPG/PNG).
2. **[PREPROCESS]:** Imaginea încărcată este redimensionată la **640x640 px** (standard YOLO) pentru a optimiza viteza de inferență.
3. **[AI_INFERENCE]:** Modelul YOLOv8 (Modul 2) rulează predicția pe imaginea procesată, generând o listă de obiecte cu coordonate și clase (Cote, Ra, Filete), cu o latență vizată de **< 2 secunde**.
4. **[USER_GROUPING]:** Etapă interactivă (Human-in-the-loop) în care utilizatorul selectează vizual elementele asociate tehnologic (ex: grupează o "Cotă" cu o "Rugozitate" detectată), deoarece AI-ul nu poate deduce automat relațiile spațiale complexe.
5. **[GENERATE_PLAN]:** Un algoritm bazat pe reguli (Rule-Based System) analizează grupul validat de utilizator și determină operația (ex: "Dacă Ra < 0.8 → Rectificare").
6. **[LOG_AND_EXPORT]:** Generarea fișierului CSV final și salvarea automată a datelor validate în **Modulul 1** pentru re-antrenare viitoare.

### Tranzițiile critice sunt:

- **[IDLE] → [PREPROCESS]:** Se declanșează când utilizatorul încarcă un fișier valid, iar buffer-ul de upload confirmă recepția completă a datelor.
- **[AI_INFERENCE] → [USER_GROUPING]:** Se întâmplă automat după finalizarea predicției, doar dacă **numărul de obiecte detectate > 0**.
- **[AI_INFERENCE] → [ERROR/WARNING]:** Se întâmplă când modelul returnează 0 detecții (Confidence < Pragul stabilit), semnalând utilizatorului că imaginea poate fi neclară sau lipsită de simboluri cunoscute.
- **[USER_GROUPING] → [GENERATE_PLAN]:** Se declanșează la apăsarea butonului "Generează Operație", validând că selecția conține cel puțin o entitate geometrică și o condiție tehnică.

---

### 4. Scheletul Complet al celor 3 Module Cerute la Curs (slide 7)

Toate cele 3 module trebuie să **pornească și să ruleze fără erori** la predare. Nu trebuie să fie perfecte, dar trebuie să demonstreze că înțelegeți arhitectura.

| **Modul** | **Python (exemple tehnologii)** | **LabVIEW** | **Cerință minimă funcțională (la predare)** |
|-----------|----------------------------------|-------------|----------------------------------------------|
| **1. Data Logging / Acquisition** | `src/data_acquisition/` | LLB cu VI-uri de generare/achiziție | **MUST:** Produce CSV cu datele voastre (inclusiv cele 40% originale). Cod rulează fără erori și generează minimum 100 samples demonstrative. |
| **2. Neural Network Module** | `src/neural_network/model.py` sau folder dedicat | LLB cu VI-uri RN | **MUST:** Modelul RN definit, compilat, poate fi încărcat. **NOT required:** Model antrenat cu performanță bună (poate avea weights random/inițializați). |
| **3. Web Service / UI** | Streamlit, Gradio, FastAPI, Flask, Dash | WebVI sau Web Publishing Tool | **MUST:** Primește input de la user și afișează un output. **NOT required:** UI frumos, funcționalități avansate. |

#### Detalii per modul:

#### **Modul 1: Data Logging / Acquisition**

**Funcționalități obligatorii:**
- [ ] Cod rulează fără erori: `python src/data_acquisition/generate.py` sau echivalent LabVIEW
- [ ] Generează CSV în format compatibil cu preprocesarea din Etapa 3
- [ ] Include minimum 40% date originale în dataset-ul final
- [ ] Documentație în cod: ce date generează, cu ce parametri

#### **Modul 2: Neural Network Module**

**Funcționalități obligatorii:**
- [X] Arhitectură RN definită și compilată fără erori
- [X] Model poate fi salvat și reîncărcat
- [X] Include justificare pentru arhitectura aleasă (în docstring sau README)
- [X] **NU trebuie antrenat** cu performanță bună (weights pot fi random)


#### **Modul 3: Web Service / UI**

**Funcționalități MINIME obligatorii:**
- [X] Propunere Interfață ce primește input de la user (formular, file upload, sau API endpoint)
- [X] Includeți un screenshot demonstrativ în `docs/screenshots/`

**Ce NU e necesar în Etapa 4:**
- UI frumos/profesionist cu grafică avansată
- Funcționalități multiple (istorice, comparații, statistici)
- Predicții corecte (modelul e neantrenat, e normal să fie incorect)
- Deployment în cloud sau server de producție

**Scop:** Prima demonstrație că pipeline-ul end-to-end funcționează: input user → preprocess → model → output.


## Structura Repository-ului la Finalul Etapei 4 (OBLIGATORIE)

**Verificare consistență cu Etapa 3:**

```
proiect-rn-[nume-prenume]/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── generated/  # Date originale
│   ├── train/
│   ├── validation/
│   └── test/
├── src/
│   ├── data_acquisition/
│   ├── preprocessing/  # Din Etapa 3
│   ├── neural_network/
│   └── app/  # UI schelet
├── docs/
│   ├── state_machine.*           #(state_machine.png sau state_machine.pptx sau state_machine.drawio)
│   └── [alte dovezi]
├── models/  # Untrained model
├── config/
├── README.md
├── README_Etapa3.md              # (deja existent)
├── README_Etapa4_Arhitectura_SIA.md              # ← acest fișier completat (în rădăcină)
└── requirements.txt  # Sau .lvproj
```

**Diferențe față de Etapa 3:**
- Adăugat `data/generated/` pentru contribuția dvs originală
- Adăugat `src/data_acquisition/` - MODUL 1
- Adăugat `src/neural_network/` - MODUL 2
- Adăugat `src/app/` - MODUL 3
- Adăugat `models/` pentru model neantrenat
- Adăugat `docs/state_machine.png` - OBLIGATORIU
- Adăugat `docs/screenshots/` pentru demonstrație UI

---

## Checklist Final – Bifați Totul Înainte de Predare

### Documentație și Structură
- [X] Tabelul Nevoie → Soluție → Modul complet (minimum 2 rânduri cu exemple concrete completate in README_Etapa4_Arhitectura_SIA.md)
- [X] Declarație contribuție 40% date originale completată în README_Etapa4_Arhitectura_SIA.md
- [ ] Cod generare/achiziție date funcțional și documentat
- [X] Dovezi contribuție originală: grafice + log + statistici în `docs/`
- [X] Diagrama State Machine creată și salvată în `docs/state_machine.*`
- [X] Legendă State Machine scrisă în README_Etapa4_Arhitectura_SIA.md (minimum 1-2 paragrafe cu justificare)
- [X] Repository structurat conform modelului de mai sus (verificat consistență cu Etapa 3)

### Modul 1: Data Logging / Acquisition
- [ ] Cod rulează fără erori (`python src/data_acquisition/...` sau echivalent LabVIEW)
- [ ] Produce minimum 40% date originale din dataset-ul final
- [ ] CSV generat în format compatibil cu preprocesarea din Etapa 3
- [ ] Documentație în `src/data_acquisition/README.md` cu:
  - [ ] Metodă de generare/achiziție explicată
  - [ ] Parametri folosiți (frecvență, durată, zgomot, etc.)
  - [ ] Justificare relevanță date pentru problema voastră
- [ ] Fișiere în `data/generated/` conform structurii

### Modul 2: Neural Network
- [X] Arhitectură RN definită și documentată în cod (docstring detaliat) - versiunea inițială 
- [X] README în `src/neural_network/` cu detalii arhitectură curentă

### Modul 3: Web Service / UI
- [X] Propunere Interfață ce pornește fără erori (comanda de lansare testată)
- [X] Screenshot demonstrativ în `docs/screenshots/ui_demo.png`
- [X] README în `src/app/` cu instrucțiuni lansare (comenzi exacte)

---

**Predarea se face prin commit pe GitHub cu mesajul:**  
`"Etapa 4 completă - Arhitectură SIA funcțională"`

**Tag obligatoriu:**  
`git tag -a v0.4-architecture -m "Etapa 4 - Skeleton complet SIA"`


