import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
import pandas as pd
import os
import math
import re
import pytesseract #
from PIL import Image

# --- CONFIGURARE TESSERACT (OBLIGATORIU PENTRU WINDOWS) ---
# Dacă ești pe Windows, decomentează linia de mai jos și pune calea corectă:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- 1. CONFIGURARE PAGINĂ ---
st.set_page_config(
    page_title="SIA - Procesare Desen Tehnic (Tesseract)",
    layout="wide",
    page_icon="🛠️"
)
st.title("🛠️ SIA - Analiză Desen Tehnic & Generare Tehnologie")
st.markdown("---")

# --- 2. RESURSE (DOAR MODELUL MACRO) ---
@st.cache_resource
def load_resources():
    # Păstrăm doar modelul care găsește cutiile (Cote, Rugozități)
    path_macro = "models/antrenare_1024.pt"
    if not os.path.exists(path_macro):
        st.error(f"❌ Lipsă model Macro! Nu găsesc: {path_macro}")
        st.stop()
    
    model_macro = YOLO(path_macro)
    return model_macro

try:
    model_macro = load_resources()
except Exception as e:
    st.error(f"Eroare critică la inițializare: {e}")
    st.stop()

# --- 3. FUNCȚII PROCESARE & TESSERACT OCR ---

def preprocess_for_tesseract(img_crop):
    """
    Tesseract are nevoie de imagini procesate agresiv:
    1. Rotire (dacă e vertical).
    2. Grayscale.
    3. Upscaling (Mărire) - CRITIC pentru cote mici.
    4. Thresholding (Alb-Negru).
    """
    if img_crop.size == 0: return img_crop
    
    h, w = img_crop.shape[:2]
    # 1. Rotire dacă e text vertical
    if h > w: 
        img_crop = cv2.rotate(img_crop, cv2.ROTATE_90_CLOCKWISE)
    
    # 2. Convertire la Grayscale
    gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
    
    # 3. Upscaling (Mărire rezoluție)
    # Textul mic din desene e greu de citit. Îl mărim de 2x sau 3x.
    scale_factor = 2
    upscaled = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    # 4. Thresholding (Binarizare)
    # Folosim Otsu pentru a separa textul negru de fundal
    thresh = cv2.threshold(upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Optional: Denoising dacă imaginea e foarte murdară
    # thresh = cv2.medianBlur(thresh, 3)
    
    return thresh

def run_tesseract_ocr(img_processed, whitelist='0123456789.,Ra+-'):
    """
    Rulează Tesseract pe imaginea preprocesată.
    whitelist: Caracterele permise (elimină zgomotul).
    """
    # Configurație Tesseract:
    # --psm 7: Tratează imaginea ca o singură linie de text.
    # -c tessedit_char_whitelist: Forțează recunoașterea doar a caracterelor specificate.
    custom_config = f'--oem 3 --psm 7 -c tessedit_char_whitelist={whitelist}'
    
    try:
        text = pytesseract.image_to_string(img_processed, config=custom_config)
        # Curățare caractere invizibile (newlines)
        return text.strip()
    except Exception as e:
        return ""

def calculate_distance(box1, box2):
    c1_x, c1_y = (box1[0] + box1[2]) / 2, (box1[1] + box1[3]) / 2
    c2_x, c2_y = (box2[0] + box2[2]) / 2, (box2[1] + box2[3]) / 2
    return math.sqrt((c1_x - c2_x)**2 + (c1_y - c2_y)**2)

# --- 4. LOGICĂ CAPP ---
def determine_process(rug_val, is_circular):
    try:
        # Caută numere float sau int în text
        vals = re.findall(r"[-+]?\d*\.\d+|\d+", rug_val.replace(',', '.'))
        ra = float(vals[0]) if vals else 12.5
    except:
        ra = 12.5 

    if ra <= 0.8: return "Rectificare (Grinding)"
    elif ra <= 1.6: return "Strunjire Finisare" if is_circular else "Frezare Finisare"
    elif ra <= 6.3: return "Strunjire Semifinisare" if is_circular else "Frezare Semifinisare"
    else: return "Degroșare (Roughing)"

# --- 5. INTERFAȚA UTILIZATOR ---

with st.sidebar:
    st.header("🎛️ Parametri Generali")
    
    st.subheader("1. Valori Implicite")
    gen_rug = st.text_input("Rugozitate Generală", value="Ra 3.2")
    gen_tol = st.text_input("Toleranță Generală", value="ISO 2768-m")
    
    st.divider()
    
    st.subheader("2. Setări AI")
    conf_macro = st.slider("Macro Confidence (Detectie)", 0.2, 1.0, 0.25, 0.05)
    
    st.info("ℹ️ OCR-ul este realizat acum cu **Tesseract**.")
    st.info("ℹ️ Proximitatea de asociere este fixată la **50px**.")

# B. Zona Principală
uploaded_file = st.file_uploader("1. Încarcă Desenul Tehnic (JPG/PNG)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_original = cv2.imdecode(file_bytes, 1)
    h, w, _ = img_original.shape

    st.image(img_original, caption="Imagine Originală", channels="BGR", use_container_width=True)

    if st.button("🚀 Analizează Desenul", type="primary"):
        with st.spinner("🔍 1. Detecție Obiecte (YOLO) ... 2. Citire Text (Tesseract) ... 3. Generare Tehnologie"):
            
            prox_thresh = 50  
            
            # 1. Inferență MACRO (Găsește cutiile mari)
            results = model_macro.predict(img_original, imgsz=1024, conf=conf_macro)[0]
            
            dims = []       
            dias = []       
            tols = []       
            rugs_spec = []  
            
            boxes = results.obb if results.obb is not None else results.boxes
            
            if boxes:
                for box in boxes:
                    cls_id = int(box.cls[0])
                    label = results.names[cls_id].lower()
                    coords = box.xyxy[0].cpu().numpy()
                    item = {'box': coords, 'label': label}
                    
                    if any(x in label for x in ['cota', 'dim']): dims.append(item)
                    elif any(x in label for x in ['dia', 'simbol']): dias.append(item)
                    elif any(x in label for x in ['tol']): tols.append(item)
                    elif any(x in label for x in ['rug', 'ra']): rugs_spec.append(item)
            
            # 2. Procesare Cote cu TESSERACT
            final_data = []
            img_result = img_original.copy()
            prog_bar = st.progress(0)
            
            for i, dim in enumerate(dims):
                prog_bar.progress((i + 1) / len(dims))
                
                dx1, dy1, dx2, dy2 = map(int, dim['box'])
                
                # --- A. OCR Cota ---
                # Adăugăm padding alb în jur pentru a ajuta Tesseract
                pad = 5
                crop_dim = img_original[max(0, dy1-pad):min(h, dy2+pad), max(0, dx1-pad):min(w, dx2+pad)]
                
                # Preprocesare specifică Tesseract (Alb-negru, Upscale)
                proc_dim = preprocess_for_tesseract(crop_dim)
                
                # Rulare Tesseract (Whitelist doar cifre și punct)
                val_cota = run_tesseract_ocr(proc_dim, whitelist='0123456789.,')
                if not val_cota: val_cota = "N/A"
                
                # --- B. Geometrie (Diametru?) ---
                is_circular = False
                for dia in dias:
                    if calculate_distance(dim['box'], dia['box']) < prox_thresh:
                        is_circular = True
                        cx, cy = int((dia['box'][0]+dia['box'][2])/2), int((dia['box'][1]+dia['box'][3])/2)
                        dcx, dcy = int((dx1+dx2)/2), int((dy1+dy2)/2)
                        cv2.line(img_result, (cx, cy), (dcx, dcy), (0, 165, 255), 2)
                        break
                
                # --- C. Toleranță ---
                toleranta_finala = gen_tol
                for tol in tols:
                    if calculate_distance(dim['box'], tol['box']) < prox_thresh:
                        tx1, ty1, tx2, ty2 = map(int, tol['box'])
                        crop_tol = img_original[max(0, ty1):min(h, ty2), max(0, tx1):min(w, tx2)]
                        
                        proc_tol = preprocess_for_tesseract(crop_tol)
                        res_tol = run_tesseract_ocr(proc_tol, whitelist='0123456789.+-kjsmfgH') # Whitelist extins pt toleranțe
                        
                        if res_tol:
                            toleranta_finala = res_tol
                            tcx, tcy = int((tx1+tx2)/2), int((ty1+ty2)/2)
                            dcx, dcy = int((dx1+dx2)/2), int((dy1+dy2)/2)
                            cv2.line(img_result, (tcx, tcy), (dcx, dcy), (255, 0, 0), 2)
                        break

                # --- D. Rugozitate ---
                rugozitate_finala = gen_rug
                for rug in rugs_spec:
                    if calculate_distance(dim['box'], rug['box']) < prox_thresh:
                        rx1, ry1, rx2, ry2 = map(int, rug['box'])
                        crop_rug = img_original[max(0, ry1):min(h, ry2), max(0, rx1):min(w, rx2)]
                        
                        proc_rug = preprocess_for_tesseract(crop_rug)
                        res_rug = run_tesseract_ocr(proc_rug, whitelist='0123456789.Ra')
                        
                        if res_rug:
                            rugozitate_finala = res_rug # Tesseract citește "Ra 3.2" direct dacă e clar
                            rcx, rcy = int((rx1+rx2)/2), int((ry1+ry2)/2)
                            dcx, dcy = int((dx1+dx2)/2), int((dy1+dy2)/2)
                            cv2.line(img_result, (rcx, rcy), (dcx, dcy), (0, 0, 255), 2)
                        break

                procedeu = determine_process(rugozitate_finala, is_circular)

                final_data.append({
                    "ID": i+1,
                    "Tip Geometrie": "Circulară (Ø)" if is_circular else "Liniară",
                    "Valoare Nominală": val_cota,
                    "Toleranță": toleranta_finala,
                    "Rugozitate": rugozitate_finala,
                    "Procedeu Sugerat": procedeu
                })
                
                cv2.rectangle(img_result, (dx1, dy1), (dx2, dy2), (0, 255, 0), 2)
                cv2.putText(img_result, str(i+1), (dx1, dy1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            prog_bar.empty()

            # 3. Afișare
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("🖼️ Detecții Vizuale")
                st.image(img_result, caption="Vizualizare Asocieri", channels="BGR", use_container_width=True)

            with col2:
                st.subheader("📝 Tabel Tehnologic (Tesseract OCR)")
                
                if final_data:
                    df = pd.DataFrame(final_data)
                    edited_df = st.data_editor(
                        df,
                        use_container_width=True,
                        num_rows="dynamic",
                        key="tech_table"
                    )
                    
                    st.divider()
                    st.subheader("💾 Export")
                    csv = edited_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Descarcă CSV", csv, "fisa_tehnologica.csv", "text/csv")
                else:
                    st.warning("⚠️ Nu s-au detectat cote.")