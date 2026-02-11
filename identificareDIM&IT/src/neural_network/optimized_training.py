import os
import shutil
from ultralytics import YOLO

def main():
    print("--- START ANTRENARE STANDARD (640p + Model SMALL) ---")
    
    if not os.path.exists('models'):
        os.makedirs('models')
  
    # 1. SCHIMBARE MAJORĂ: Trecem la 'yolov8s-obb.yaml' (Small)
    # Are mai multe straturi și parametri, deci vede mai bine detaliile fine (Ø, ±).
    print("[INFO] Construire model YOLOv8s-OBB (Small)...")
    model = YOLO('yolov8s-obb.yaml')   

    # 2. Start Antrenare
    print("[INFO] Începe antrenarea la rezoluție standard...")
    
    results = model.train(
        data='data.yaml',   
        epochs=200,
        patience=15,
        
        # --- CONFIGURAȚIA PENTRU 640p ---
        imgsz=640,             # Rezoluția standard. Detaliile sunt clare.
        batch=16,              # Ajustat pentru 640p (dacă primești eroare de memorie, pune 8 sau 4)
        
        lr0=0.01,             # Rămâne 0.001 pentru AdamW
        
        project='results5',     
        name='antrenare_640_lr001_small', 
        exist_ok=True,         
        device='cpu',            # RECOMANDAT: Folosește GPU ('0') dacă ai. Pe CPU ('cpu') va dura mult!
        pretrained=False,      
        
        # --- OPTIMIZĂRI ---
        optimizer='AdamW',     # Stabil
        cos_lr=True,           
        
        # Ajustări fine
        cls=4.0,               # Păstrăm focusul pe clasificarea corectă (să nu confunde Ø cu 0)
        box=7.5,               # Revenim la default (7.5) pentru că 640p are destulă rezoluție spațială
        dfl=1.5,               # Default Distribution Focal Loss (ajută la aliniere fină)
        
        close_mosaic=10        # Oprim augmentarea cu mozaic la final pentru fine-tuning
    )

    # 3. Salvare
    path_yolo_best = os.path.join("results4", "antrenare_640_small", "weights", "best.pt")
    path_destinatie = os.path.join("models", "antrenare_640.pt") 
    path_ui = os.path.join("models", "antrenare_640_lr001_small_ui.pt")

    if os.path.exists(path_yolo_best):
        shutil.copy(path_yolo_best, path_destinatie)
        shutil.copy(path_yolo_best, path_ui)
        print(f"\n[SUCCES] Model SMALL (640p) salvat: {path_destinatie}")
    else:
        print("\n[EROARE] Nu găsesc fișierul best.pt")

if __name__ == '__main__':
    main()