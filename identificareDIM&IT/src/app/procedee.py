# ==============================================================================
# FISIER: procedee.py
# ==============================================================================
import re
import math

def extrage_it_din_iso(simbol_toleranta):
    """
    Extrage cifra calității (IT) dintr-un simbol ISO (ex: 'H7' -> 7, 'js14' -> 14).
    Returnează None dacă nu găsește un format valid.
    """
    if not simbol_toleranta:
        return None
    s = str(simbol_toleranta).strip()
    # Caută o secvență de cifre la finalul stringului sau după o literă
    match = re.search(r'[A-Za-z]+(\d+)', s)
    if match:
        return int(match.group(1))
    # Fallback: caută doar cifre dacă stringul e doar numeric (ex: "7")
    match_simple = re.search(r'^\d+$', s)
    if match_simple:
        return int(match_simple.group())
    return None

def get_toleranta_generala_iso2768(dimensiune, clasa_toleranta):
    """
    Returnează toleranța în mm conform ISO 2768-1 (f, m, c, v).
    """
    # Tabel 1 din ISO 2768-1: Abateri limită pentru dimensiuni liniare
    # Format: (limita_superioara_exclusiva, f, m, c, v)
    tabel_4_2 = [
        (3,    0.05, 0.1,  0.2,  0.5),  # 0.5 - 3
        (6,    0.05, 0.1,  0.3,  0.5),  # 3 - 6
        (30,   0.1,  0.2,  0.5,  1.0),  # 6 - 30
        (120,  0.15, 0.3,  0.8,  1.5),  # 30 - 120
        (400,  0.2,  0.5,  1.2,  2.5),  # 120 - 400
        (1000, 0.3,  0.8,  2.0,  4.0),  # 400 - 1000
        (2000, 0.5,  1.2,  3.0,  6.0),  # 1000 - 2000
        (4000, 0.5,  2.0,  4.0,  8.0)   # 2000 - 4000
    ]
    
    # Mapare coloane: f=1, m=2, c=3, v=4
    mapare = {'f': 1, 'm': 2, 'c': 3, 'v': 4}
    try:
        col = mapare.get(str(clasa_toleranta).lower(), 2) # Default 'm'
    except:
        col = 2

    dim = float(dimensiune)
    for rand in tabel_4_2:
        # ISO definește intervalele ca: peste X până la Y inclusiv
        if dim <= rand[0]:
            return rand[col]
            
    # Pentru dimensiuni > 4000mm, returnăm o valoare fallback rezonabilă pt 'm'
    return 3.0

def determina_it_din_valoare(dimensiune, toleranta_mm):
    """
    Deduce gradul IT (5..16) pe baza dimensiunii și a toleranței în mm.
    Folosește valorile standard ISO 286-1.
    """
    if toleranta_mm is None: 
        return 12 # Default general

    tol_microni = abs(toleranta_mm * 1000)
    dim = float(dimensiune)

    # Tabel complet ISO 286 pentru IT5 - IT11 (cele mai uzuale in prelucrari)
    # Structura: (min_exclusive, max_inclusive): {IT_grade: microns}
    tabel_it = {
        (0, 3):     {5:4, 6:6, 7:10, 8:14, 9:25, 10:40, 11:60, 12:100, 13:140, 14:250},
        (3, 6):     {5:5, 6:8, 7:12, 8:18, 9:30, 10:48, 11:75, 12:120, 13:180, 14:300},
        (6, 10):    {5:6, 6:9, 7:15, 8:22, 9:36, 10:58, 11:90, 12:150, 13:220, 14:360},
        (10, 18):   {5:8, 6:11, 7:18, 8:27, 9:43, 10:70, 11:110, 12:180, 13:270, 14:430},
        (18, 30):   {5:9, 6:13, 7:21, 8:33, 9:52, 10:84, 11:130, 12:210, 13:330, 14:520},
        (30, 50):   {5:11, 6:16, 7:25, 8:39, 9:62, 10:100, 11:160, 12:250, 13:390, 14:620},
        (50, 80):   {5:13, 6:19, 7:30, 8:46, 9:74, 10:120, 11:190, 12:300, 13:460, 14:740},
        (80, 120):  {5:15, 6:22, 7:35, 8:54, 9:87, 10:140, 11:220, 12:350, 13:540, 14:870},
        (120, 180): {5:18, 6:25, 7:40, 8:63, 9:100, 10:160, 11:250, 12:400, 13:630, 14:1000},
        (180, 250): {5:20, 6:29, 7:46, 8:72, 9:115, 10:185, 11:290, 12:460, 13:720, 14:1150},
        (250, 315): {5:23, 6:32, 7:52, 8:81, 9:130, 10:210, 11:320, 12:520, 13:810, 14:1300},
        (315, 400): {5:25, 6:36, 7:57, 8:89, 9:140, 10:230, 11:360, 12:570, 13:890, 14:1400},
        (400, 500): {5:27, 6:40, 7:63, 8:97, 9:155, 10:250, 11:400, 12:630, 13:970, 14:1550}
    }
    
    sel = None
    # Găsire interval dimensiune
    for interval in tabel_it:
        if interval[0] < dim <= interval[1]:
            sel = tabel_it[interval]
            break
            
    # Dacă dimensiunea e > 500 sau nu e găsită, folosim valori aproximative pt interval mare
    if not sel:
        sel = {5:30, 6:45, 7:70, 8:110, 9:170, 10:280, 11:450, 12:700, 13:1000}

    # Găsire IT: Căutăm primul IT care are toleranța >= toleranța cerută
    # Dacă toleranța cerută e mai mică decât IT5, considerăm IT5 sau IT4 (superfinisare)
    for it_grade in sorted(sel.keys()):
        if tol_microni <= sel[it_grade]:
            return it_grade
            
    return 14 # Pentru toleranțe foarte largi

def determina_etapa_maxima(it, ra):
    """
    Determină numărul de etape necesare bazat pe cel mai restrictiv criteriu.
    Etape: 1=Degroșare, 2=Semifinisare, 3=Finisare, 4=Superfinisare/Rectificare
    """
    # Analiză după Precizie (IT)
    if it >= 12: 
        max_it = 1       # Degroșare (IT12-IT14)
    elif 10 <= it <= 11: 
        max_it = 2       # Semifinisare (IT10-IT11)
    elif 8 <= it <= 9:   
        max_it = 3       # Finisare (IT8-IT9)
    else:                
        max_it = 4       # Rectificare/Finisare Fină (IT5-IT7)

    # Analiză după Rugozitate (Ra în microni)
    if ra > 12.5:
        max_ra = 1
    elif 3.2 < ra <= 12.5:
        max_ra = 2
    elif 1.6 < ra <= 3.2:
        max_ra = 3
    else: # Ra <= 1.6
        max_ra = 4
        
    # Procesul este dictat de cerința cea mai strictă
    return max(max_it, max_ra)

def generate_technological_plan(tip_suprafata, cota, rugozitate_tinta, tol_input, tol_default_class='m'):
    """
    Generează fluxul tehnologic pe baza parametrilor piesei.
    Nu schimba semnătura funcției.
    """
    
    tol_str = str(tol_input).strip()
    it_tinta = 12 # Default start
    
    # 1. Verificare input gol sau clase generale ISO 2768
    iso_classes = ['f', 'm', 'c', 'v']
    is_general = tol_str.lower() in iso_classes
    is_empty = tol_str in ["None", "nan", "", "?", "ISO 2768-m", "general"]
    
    if is_empty or is_general:
        clasa = tol_str.lower() if is_general else tol_default_class
        val = get_toleranta_generala_iso2768(cota, clasa)
        it_tinta = determina_it_din_valoare(cota, val)

    # 2. Verificare simbol ISO ajustaj (ex: H7, k6)
    elif extrage_it_din_iso(tol_str) is not None:
        it_tinta = extrage_it_din_iso(tol_str)

    # 3. Verificare valoare numerică directă (ex: +/-0.05, 0.02)
    else:
        try:
            # Curățare caractere non-numerice pentru a obține valoarea absolută
            clean = tol_str.replace('±', '').replace('+', '').replace('h', '').replace('k', '')
            # Dacă sunt două valori (ex: -0.01/-0.03), luăm plaja (diferența)
            if '/' in clean:
                parts = clean.split('/')
                val = abs(float(parts[0]) - float(parts[1])) / 2.0 # Aproximăm semi-câmpul
            else:
                val = float(clean.replace('-', ''))
                
            it_tinta = determina_it_din_valoare(cota, val)
        except:
            # Fallback absolut
            val = get_toleranta_generala_iso2768(cota, tol_default_class)
            it_tinta = determina_it_din_valoare(cota, val)

    # --- Generare Succesiune Operații ---
    operatii = []
    is_cil = "cilind" in str(tip_suprafata).lower() or "alezaj" in str(tip_suprafata).lower() or "arbore" in str(tip_suprafata).lower()
    
    # Nomenclator
    nume = "Strunjire" if is_cil else "Frezare"
    
    # Determinare număr pași
    etapa = determina_etapa_maxima(it_tinta, rugozitate_tinta)
    
    # Construire flux
    operatii.append(f"{nume} Degrosare (D)")         # Etapa 1
    
    if etapa >= 2:
        operatii.append(f"{nume} Semifinisare (F/2)") # Etapa 2
        
    if etapa >= 3:
        operatii.append(f"{nume} Finisare (F)")       # Etapa 3
        
    if etapa >= 4:
        # La etapa 4 (IT < 7 sau Ra < 1.6), diferențiem după formă și duritate implicită
        if is_cil:
            # Arborii/Alezajele precise se rectifică
            operatii.append("Rectificare (R)")
        else:
            # Suprafețele plane precise se rectifică plan sau se frezează fin
            operatii.append(f"Rectificare Plana sau {nume} Fina (SF)")

    return len(operatii), " + ".join(operatii), it_tinta