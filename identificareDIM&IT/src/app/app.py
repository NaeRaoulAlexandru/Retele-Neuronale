import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
import pandas as pd
import os
import datetime
import csv

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
if 'detected_objects' not in st.session_state:
    st.session_state['detected_objects'] = []
if 'image_name' not in st.session_state:
    st.session_state['image_name'] = ""
if 'run_inference' not in st.session_state:
    st.session_state['run_inference'] = False

# --- 3. ÎNCĂRCARE MODEL ---
@st.cache_resource
def get_model():
    # Cale către modelul antrenat în Etapa 5
    custom_model_path = os.path.join("models", "antrenare_1024.pt")
    
    # Verificare existență
    if os.path.exists(custom_model_path):
        return YOLO(custom_model_path), "Custom (Antrenat Local)"
    
    # Fallback pentru testare (dacă nu ai antrenat încă)
    return YOLO("yolov8n.pt"), "Standard YOLOv8n (Dummy)"

try:
    model, model_type = get_model()
except Exception as e:
    st.error(f"Eroare la încărcarea modelului: {e}")
    st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Panou Control")
    st.success(f"Model Activ: **{model_type}**")
    conf_threshold = st.slider("Prag de Încredere (Confidence)", 0.0, 1.0, 0.25, 0.05)
    st.info("Reglează pragul dacă modelul ratează obiecte.")

# --- 5. INTERFAȚA PRINCIPALĂ ---
col_left, col_right = st.columns([1, 1])

# === COLOANA STÂNGA: VIZUALIZARE ===
with col_left:
    st.subheader("1. Încărcare și Detecție")
    uploaded_file = st.file_uploader("Încarcă un desen de execuție", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        # Conversie imagine
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        st.session_state['image_name'] = uploaded_file.name
        
        # Afișare imagine originală
        st.image(image, caption="Desen Original", channels="BGR", use_container_width=True)

        # Buton Inferență
        if st.button("🔍 Analizează (Modul 2 - RN)", type="primary"):
            with st.spinner("Rulare inferență YOLOv8..."):
                # PREDICȚIA
                results = model.predict(image, conf=conf_threshold)
                result = results[0]
                
                # Plotare rezultate pe imagine
                res_plotted = result.plot(line_width=1, font_size=1)
                st.image(res_plotted, caption="Rezultat Detecție", channels="BGR", use_container_width=True)
                
                # Extragere date pentru tabel (Modul Logic)
                found_objects = []
                
                # Tratare universală (OBB vs Standard Boxes)
                boxes = result.obb if result.obb is not None else result.boxes
                
                if boxes is not None:
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        class_name = result.names[cls_id]
                        conf = float(box.conf[0])
                        
                        found_objects.append({
                            "Clasă": class_name,
                            "Încredere": f"{conf:.2f}"
                        })
                
                # Salvare în sesiune pentru coloana dreaptă
                st.session_state['detected_objects'] = found_objects
                st.session_state['run_inference'] = True

# === COLOANA DREAPTA: DECISIE ȘI LOGGING ===
with col_right:
    st.subheader("2. Inventar și Proces Tehnologic")
    
    if st.session_state.get('run_inference'):
        # A. Tabelul de inventar
        data = st.session_state['detected_objects']
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Statistici rapide
            nr_cote = sum(1 for x in data if "Cota" in x['Clasă'])
            nr_rug = sum(1 for x in data if "Rugozitate" in x['Clasă'])
            nr_tol = sum(1 for x in data if "Toleranta" in x['Clasă'])
            
            st.markdown(f"**Rezumat:** `{nr_cote}` Cote | `{nr_rug}` Rugozități | `{nr_tol}` Toleranțe")
            
            # B. CAPP Logic (Rule-Based System)
            st.divider()
            st.subheader("3. Generare Plan (Reguli)")
            
            recommendations = []
            
            # Regula 1: Rugozitate Fină -> Rectificare
            if nr_rug > 0:
                recommendations.append("✅ **Rectificare necesară:** S-au detectat simboluri de rugozitate. Verificați valorile Ra < 0.8.")
            else:
                recommendations.append("ℹ️ **Strunjire suficientă:** Nu s-au detectat condiții speciale de suprafață.")
                
            # Regula 2: Toleranțe -> Control Calitate
            if nr_tol > 0:
                recommendations.append("⚠️ **Atenție Control:** S-au detectat toleranțe geometrice. Necesită verificare pe CMM.")
            
            # Afișare recomandări
            for rec in recommendations:
                st.write(rec)

            # C. Data Logging (Modul 1 Loop)
            st.divider()
            st.subheader("4. Data Loop (Feedback)")
            st.caption("Validezi acest rezultat? Dacă da, salvăm datele pentru re-antrenare.")
            
            if st.button("💾 Validează și Salvează Log"):
                try:
                    # Nume fișier log
                    log_file = 'data_log.csv'
                    file_exists = os.path.isfile(log_file)
                    
                    with open(log_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(['Timestamp', 'File', 'Detected_Count', 'Validation'])
                        
                        writer.writerow([
                            datetime.datetime.now(),
                            st.session_state['image_name'],
                            len(data),
                            'Validated_by_User'
                        ])
                    st.toast("✅ Date salvate cu succes în data_log.csv!")
                    st.success("Datele au fost trimise către Modulul 1 pentru ciclul următor de antrenare.")
                except Exception as e:
                    st.error(f"Eroare la salvare: {e}")

        else:
            st.warning("Nu s-au detectat obiecte. Încearcă să scazi pragul de încredere.")
    else:
        st.info("👈 Încarcă o imagine și apasă 'Analizează' pentru a vedea rezultatele.")

# Footer
st.markdown("---")
st.caption("Sistem Inteligent de Asistență (SIA) - Proiect Rețele Neuronale 2025")