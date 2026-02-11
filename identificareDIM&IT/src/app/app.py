import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
import pandas as pd
import os
import re
import math
import easyocr
import procedee  # Modulul logic

# ------------------------------------------------------------------------------
# 1. CONFIGURARE & STATE
# ------------------------------------------------------------------------------
st.set_page_config(page_title="SIA - CAPP", layout="wide", page_icon="✅")
st.title("⚡ SIA - Computer Aided Process Planning")

if 'last_upload' not in st.session_state:
    st.session_state.last_upload = None
if 'df_cote' not in st.session_state:
    st.session_state.df_cote = pd.DataFrame()
if 'annotated_result' not in st.session_state:
    st.session_state.annotated_result = None

# Setări distanțe (în pixeli)
STRICT_LIMIT_TOL = 15   
LOOSE_LIMIT_RUG = 40    

# ------------------------------------------------------------------------------
# 2. CALLBACK DE RESETARE
# ------------------------------------------------------------------------------
def reset_inference():
    st.session_state.annotated_result = None
    st.session_state.df_cote = pd.DataFrame()

# ------------------------------------------------------------------------------
# 3. RESURSE
# ------------------------------------------------------------------------------
@st.cache_resource
def load_resources():
    path_model = "models/antrenare_640.pt" 
    if not os.path.exists(path_model):
        st.error(f"❌ Lipsă model: {path_model}")
        st.stop()
    model = YOLO(path_model)
    print("⏳ Loading OCR...")
    reader = easyocr.Reader(['en'], gpu=False) 
    return model, reader

try:
    model_ai, reader_ocr = load_resources()
except Exception as e:
    st.error(f"Eroare resurse: {e}")
    st.stop()

# ------------------------------------------------------------------------------
# 4. FUNCȚII GEOMETRICE
# ------------------------------------------------------------------------------
def crop_box(img, box):
    h, w = img.shape[:2]
    x1, y1, x2, y2 = map(int, box)
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    return img[y1:y2, x1:x2]

def run_ocr(img_crop, mode='numeric'):
    if img_crop.size == 0: return ""
    gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY) if len(img_crop.shape)==3 else img_crop
    scale = 3 
    big = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    clean = cv2.copyMakeBorder(binary, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
    
    try:
        res = reader_ocr.readtext(clean, detail=0)
        text = " ".join(res)
        
        if mode == 'numeric':
            text = text.replace(',', '.')
            matches = re.findall(r"[-+]?\d*\.\d+|\d+", text)
            if matches: return matches[0]
            return ""
        else:
            return text.strip()
    except: return ""

def get_edge_distance(box1, box2):
    """Calculează distanța minimă dintre margini."""
    x1a, y1a, x2a, y2a = box1
    x1b, y1b, x2b, y2b = box2

    left = x2a < x1b
    right = x1a > x2b
    bottom = y2a < y1b
    top = y1a > y2b
    
    if top and left:     return math.hypot(x1b-x2a, y2b-y1a)
    elif left and bottom: return math.hypot(x1b-x2a, y1b-y2a)
    elif bottom and right: return math.hypot(x2b-x1a, y1b-y2a)
    elif right and top:    return math.hypot(x2b-x1a, y2b-y1a)
    elif left:   return x1b - x2a
    elif right:  return x1a - x2b
    elif bottom: return y1b - y2a
    elif top:    return y1a - y2b
    else:        return 0 

def check_alignment(box1, box2):
    """Verifică dacă există suprapunere pe axe."""
    x1a, y1a, x2a, y2a = box1
    x1b, y1b, x2b, y2b = box2
    overlap_x = max(0, min(x2a, x2b) - max(x1a, x1b))
    overlap_y = max(0, min(y2a, y2b) - max(y1a, y1b))
    return (overlap_x > 0) or (overlap_y > 0)

def recalculate_row(row, tol_class):
    try:
        if pd.isna(row["Cota (mm)"]) or str(row["Cota (mm)"]).strip() == "": return None, None, None
        tip = str(row["Suprafață"])
        c = float(row["Cota (mm)"])
        r = float(row["Ra (µm)"]) if not pd.isna(row["Ra (µm)"]) else 3.2
        t_raw = str(row["Toleranță"])
        t = None if "Gen." in t_raw or t_raw == "nan" else t_raw.replace(f"Gen. {tol_class}", "")
        return procedee.generate_technological_plan(tip, c, r, t, tol_class)
    except: return 0, "Err", "N/A"

# ------------------------------------------------------------------------------
# 5. SIDEBAR
# ------------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Parametri")
    gen_rug = st.text_input("Ra General", value="3.2")
    gen_tol_class = st.selectbox("Clasă ISO 2768", ['f', 'm', 'c', 'v'], index=1)
    
    with st.expander("Calibrare Robot"):
        conf_thresh = st.slider("Sensibilitate AI", 0.2, 1.0, 0.25, 0.05, on_change=reset_inference)
        st.info(f"Dist. Toleranță: {STRICT_LIMIT_TOL}px\nDist. Rugozitate: {LOOSE_LIMIT_RUG}px")

    if st.button("🔄 Resetare Totală", on_click=lambda: st.session_state.clear()):
        st.rerun()

# ------------------------------------------------------------------------------
# 6. MAIN FLOW
# ------------------------------------------------------------------------------
uploaded_file = st.file_uploader("Încarcă Desenul", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    curr_img = cv2.imdecode(file_bytes, 1)
    
    is_new = (st.session_state.last_upload != uploaded_file.file_id)
    needs_run = (st.session_state.annotated_result is None)
    
    if is_new or needs_run:
        st.session_state.last_upload = uploaded_file.file_id
        
        with st.spinner("⚡ Analizez desenul..."):
            
            # 1. Inferență YOLO
            res = model_ai.predict(curr_img, imgsz=1024, conf=conf_thresh)[0]
            boxes = []
            if res.obb:
                for box in res.obb:
                    boxes.append({
                        'box': [int(c) for c in box.xyxy[0].cpu().numpy()],
                        'label': model_ai.names[int(box.cls[0])].lower()
                    })
            
            final_img = curr_img.copy()
            
            # 2. SEPARARE CLASE (FIX BUG: 'ra' vs 'toleranta')
            # Folosim egalitate strictă pentru 'ra' ca să nu prindă 'toleRAnta'
            
            dims = [b for b in boxes if 'cota' in b['label']]
            dias = [b for b in boxes if 'simbol' in b['label']]
            tols = [b for b in boxes if 'tol' in b['label']]
            
            # AICI ESTE FIX-UL: "==" în loc de "in" pentru Ra
            rugs = [b for b in boxes if b['label'] == 'ra']     
            
            dims.sort(key=lambda x: x['box'][1]) 
            list_cote = []

            # --- 3. DESENARE ELEMENTE DETECTATE (VISUAL DEBUG) ---
            # Toleranțe -> ALBASTRU (BGR: 255,0,0)
            for t in tols:
                x1, y1, x2, y2 = t['box']
                cv2.rectangle(final_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            # Rugozități -> ROȘU (BGR: 0,0,255)
            for r in rugs:
                x1, y1, x2, y2 = r['box']
                cv2.rectangle(final_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # Simboluri Diametru -> PORTOCALIU
            for d in dias:
                x1, y1, x2, y2 = d['box']
                cv2.rectangle(final_img, (x1, y1), (x2, y2), (0, 140, 255), 2)

            # --- 4. LOGICĂ DE ASOCIERE ---
            for i, d in enumerate(dims):
                dx1, dy1, dx2, dy2 = d['box']
                w, h = abs(dx2-dx1), abs(dy2-dy1)
                
                # Auto-rotire OCR
                crop_cota = crop_box(curr_img, d['box'])
                is_vertical = h > w
                if is_vertical:
                    crop_cota = cv2.rotate(crop_cota, cv2.ROTATE_90_CLOCKWISE)
                
                val_str = run_ocr(crop_cota, 'numeric')
                try: val_cota = float(val_str)
                except: val_cota = 0.0
                
                cx, cy = (dx1+dx2)//2, (dy1+dy2)//2
                tip = "Plană"
                
                # A. DIAMETRU
                for dia in dias:
                    dist = get_edge_distance(d['box'], dia['box'])
                    aligned = check_alignment(d['box'], dia['box'])
                    if dist < 100 and aligned:
                        tip = "Cilindrica"
                        ox1, oy1, ox2, oy2 = dia['box']
                        cv2.line(final_img, (cx, cy), ((ox1+ox2)//2, (oy1+oy2)//2), (0,140,255), 2)
                        break
                
                # B. TOLERANȚĂ
                tol_txt = None
                for t in tols:
                    dist = get_edge_distance(d['box'], t['box'])
                    aligned = check_alignment(d['box'], t['box'])
                    
                    if dist <= STRICT_LIMIT_TOL and aligned:
                        tx1, ty1, tx2, ty2 = t['box']
                        th_tol, tw_tol = abs(ty2-ty1), abs(tx2-tx1)
                        c_tol = crop_box(curr_img, t['box'])
                        
                        if is_vertical or th_tol > tw_tol:
                            c_tol = cv2.rotate(c_tol, cv2.ROTATE_90_CLOCKWISE)
                        
                        tol_txt = run_ocr(c_tol, 'tolerance')
                        cv2.line(final_img, (cx, cy), ((tx1+tx2)//2, (ty1+ty2)//2), (255,0,0), 2)
                        break
                
                # C. RUGOZITATE
                rug_specific = None
                for r in rugs:
                    dist = get_edge_distance(d['box'], r['box'])
                    
                    if dist <= LOOSE_LIMIT_RUG:
                        rx1, ry1, rx2, ry2 = r['box']
                        c_rug = crop_box(curr_img, r['box'])
                        if is_vertical:
                             c_rug = cv2.rotate(c_rug, cv2.ROTATE_90_CLOCKWISE)
                             
                        val_rug_str = run_ocr(c_rug, 'numeric')
                        if val_rug_str:
                            try: rug_specific = float(val_rug_str)
                            except: pass
                        
                        cv2.line(final_img, (cx, cy), ((rx1+rx2)//2, (ry1+ry2)//2), (0,0,255), 2)
                        break

                # Calcul Final
                ra_final = rug_specific if rug_specific is not None else float(gen_rug)
                tol_final = tol_txt if tol_txt else gen_tol_class
                
                nr, op, it = procedee.generate_technological_plan(tip, val_cota, ra_final, tol_final, gen_tol_class)
                
                list_cote.append({
                    "ID": i+1,
                    "Suprafață": tip,
                    "Cota (mm)": val_cota,
                    "Ra (µm)": ra_final,
                    "Toleranță": tol_final,
                    "IT Țintă": f"IT {it}",
                    "Nr. Op.": nr,
                    "Tehnologie": op
                })
                
                # Desenare Cota
                cv2.rectangle(final_img, (dx1, dy1), (dx2, dy2), (0,200,0), 2)
                lid = str(i+1)
                (tw, th), _ = cv2.getTextSize(lid, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                cv2.rectangle(final_img, (dx1, dy1-th-4), (dx1+tw+4, dy1), (0,200,0), -1)
                cv2.putText(final_img, lid, (dx1+2, dy1-2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

            st.session_state.annotated_result = final_img
            st.session_state.df_cote = pd.DataFrame(list_cote)

    # --- 5. AFIȘARE ---
    if st.session_state.annotated_result is not None:
        c1, c2 = st.columns([1, 1.5])
        
        with c1:
            st.image(st.session_state.annotated_result, channels="BGR", use_container_width=True)
            st.caption("Verde: Cote | Roșu: Ra | Albastru: Tol. | Portocaliu: Ø")
        
        with c2:
            col_cfg = {
                "ID": st.column_config.NumberColumn("ID", width="small", format="%d"),
                "Suprafață": st.column_config.TextColumn("Supraf.", width="small"),
                "Cota (mm)": st.column_config.NumberColumn("Cota", width="small", format="%d"),
                "Ra (µm)": st.column_config.NumberColumn("Ra", width="small", format="%.1f"),
                "Toleranță": st.column_config.TextColumn("Tol.", width="small"),
                "IT Țintă": st.column_config.TextColumn("IT", width="small"),
                "Nr. Op.": st.column_config.NumberColumn("#Op", width="small"),
                "Tehnologie": st.column_config.TextColumn("Tehnologie", width="large"),
            }

            if not st.session_state.df_cote.empty:
                edited = st.data_editor(
                    st.session_state.df_cote,
                    hide_index=True,
                    use_container_width=True,
                    height=600,
                    num_rows="dynamic",
                    key="editor",
                    column_config=col_cfg
                )
                
                old = st.session_state.df_cote.reset_index(drop=True)
                new = edited.reset_index(drop=True)
                
                has_changes = False
                if len(old) != len(new):
                    has_changes = True
                else:
                    cols = ["Suprafață", "Cota (mm)", "Ra (µm)", "Toleranță"]
                    try:
                        if not new[cols].equals(old[cols]): has_changes = True
                    except: has_changes = True

                if has_changes:
                    for idx, row in edited.iterrows():
                        res = recalculate_row(row, gen_tol_class)
                        if res[0] is not None:
                            nr, op, it = res
                            edited.at[idx, 'Nr. Op.'] = nr
                            edited.at[idx, 'Tehnologie'] = op
                            edited.at[idx, 'IT Țintă'] = f"IT {it}"
                    st.session_state.df_cote = edited
                    st.rerun()

                csv = st.session_state.df_cote.to_csv(index=False)
                st.download_button("💾 Export CSV", csv, "fisa.csv", type="primary")
            else:
                st.warning("Imagine procesată, dar nu s-au găsit cote.")