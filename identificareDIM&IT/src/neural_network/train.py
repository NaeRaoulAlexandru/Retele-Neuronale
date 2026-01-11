import os
import shutil
from ultralytics import YOLO

def main():
    print("--- START ANTRENARE INTENSIVĂ (150 EPOCI) ---")
    
    # Asigurăm folderul de modele
    if not os.path.exists('models'):
        os.makedirs('models')
  
    # 1. Construim arhitectura goală (From Scratch)
    print("[INFO] Construire model YOLOv8n-OBB (Weights Random)...")
    model = YOLO('yolov8n-obb.yaml')  

    # 2. Start Antrenare
    print("[INFO] Începe antrenarea... Ia-ți o cafea, va dura!")
    
    results = model.train(
        data='data.yaml',   
        epochs=150,            # CERINȚA TA: 150 Epoci
        patience=25,           # Așteptăm mai mult înainte de Early Stopping
        batch=8,              
        imgsz=1024,             
        project='results',     
        name='antrenare_1024', # Nume nou pentru experiment
        exist_ok=True,         
        device='cpu',          # Schimbă în '0' dacă ai GPU NVIDIA
        pretrained=False,      # De la zero
        
        # --- OPTIMIZĂRI PENTRU CLASELE MICI (Rugozitate/Toleranta) ---
        optimizer='AdamW',     # AdamW este cel mai stabil pentru antrenare lungă
        cos_lr=True,           # Scade learning rate-ul lin spre final (ajută precizia)
        
        # TRUCUL MAGIC PENTRU CLASELE TALE:
        cls=4.0,               # Default=0.5. Am pus 4.0 ca să pedepsim aspru greșelile de clasă!
        box=7.5,               # Păstrăm localizarea importantă
        
        # Oprim augmentarea (mosaic) în ultimele 15 epoci pentru a vedea imagini curate
        close_mosaic=15        
    )

    # 3. Salvarea modelului final
    # Atenție: folderul sursă este acum 'antrenare_150_epoci'
    path_yolo_best = os.path.join("results", "antrenare_1024", "weights", "best.pt")
    
    # Îl salvăm cu nume distinct ca să știi că e cel bun
    path_destinatie = os.path.join("models", "antrenare_1024.pt")
    
    # Facem și o copie peste 'trained_model.pt' ca să meargă direct în UI
    path_ui = os.path.join("models", "trained_model.pt")

    if os.path.exists(path_yolo_best):
        shutil.copy(path_yolo_best, path_destinatie)
        shutil.copy(path_yolo_best, path_ui)
        
        print(f"\n[SUCCES] Modelul a fost salvat în două locuri:")
        print(f"   1. Backup: {path_destinatie}")
        print(f"   2. Pentru UI: {path_ui}")
        print("Acum poți reporni 'streamlit run src/app/app.py'!")
    else:
        print("\n[EROARE] Nu găsesc fișierul best.pt")

if __name__ == '__main__':
    main()
