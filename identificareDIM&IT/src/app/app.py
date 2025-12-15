import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
import pandas as pd
import os
import datetime

# --- 1. CONFIGURARE PAGINĂ ---
st.set_page_config(
    page_title="SIA - CAPP Assistant",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ SIA - Arhitectură Integrată de Analiză Desen Tehnic")
st.markdown("### Modul 3: Interfață Web & Asistență Tehnologică")
st.markdown("---")

# --- 2. INIȚIALIZARE MEMORIE (SESSION STATE) ---
# Avem nevoie de asta pentru a păstra datele când dai click pe butoane
if 'detected_objects' not in st.session_state:
    st.session_state['detected_objects'] = []
if 'process_plan' not in st.session_state:
    st.session_state['process_plan'] = []
if 'image_name' not in st.session_state:
    st.session_state['image_name'] = ""

# --- 3. ÎNCĂRCARE MODEL (DIRECTĂ) ---
@st.cache_resource
def get_model():
    """
    Încarcă modelul YOLOv8.
    Caută întâi modelul tău antrenat (models/yolo_v1.pt).
    Dacă nu îl găsește, folosește unul standard sau afișează eroare.
    """
    # Cale relativă către modelul tău
    custom_model_path = os.path.join("models", "yolo_v1.pt")
    
    # Verificăm dacă există fișierul tău
    if os.path.exists(custom_model_path):
        model = YOLO(custom_model_path)
        return model, "Custom (Antrenat de tine - 58% mAP)"
    
    # Fallback: Dacă ai uitat să copiezi fișierul, încearcă să ia din runs
    fallback_path = os.path.join("runs", "detect", "primul_meu_model", "weights", "yolo_v1.pt")
    if os.path.exists(fallback_path):
        model = YOLO(fallback_path)
        return model, "Custom (Din folderul Runs)"

    # Ultimul resort: Modelul standard COCO (ca să meargă aplicația orice ar fi)
    return YOLO("yolov8n.pt"), "Standard YOLOv8n (Warning: Nu e antrenat pe filete)"

# Încărcăm modelul
try:
    model, model_type = get_model()
except Exception as e:
    st.error(f"Eroare critică la încărcarea modelului: {e}")
    st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Panou Control")
    st.success(f"Model Activ: **{model_type}**")
    
    conf_threshold = st.slider("Prag de Încredere (Confidence)", 0.0, 1.0, 0.25, 0.05)
    st.info("Reglează pragul dacă modelul ratează obiecte sau vede prea multe.")

# --- 5. INTERFAȚA PRINCIPALĂ (DOUĂ COLOANE) ---
col_left, col_right = st.columns([1, 1])

# === COLOANA STÂNGA: VIZUALIZARE ===
with col_left:
    st.subheader("1. Încărcare și Detecție")
    uploaded_file = st.file_uploader("Încarcă un desen de execuție", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        # Conversie imagine pentru OpenCV
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        st.session_state['image_name'] = uploaded_file.name
        
        st.image(image, caption="Desen Original", channels="BGR", use_container_width=True)

        if st.button("🔍 Analizează (Modul 2 - Neural Network)", type="primary"):
            with st.spinner("Rulare inferență YOLOv8..."):
                # --- AICI SE FACE PREDICȚIA ---
                results = model.predict(image, conf=conf_threshold)
                result = results[0] # Luăm primul rezultat
                
                # Desenăm cutiile
                res_plotted = result.plot()
                st.image(res_plotted, caption="Rezultat Detecție", channels="BGR", use_container_width=True)
                
                # Salvăm ce am găsit pentru coloana din dreapta
                found_objects = []
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    label = result