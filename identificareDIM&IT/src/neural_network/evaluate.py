import os
import json
import shutil
from ultralytics import YOLO

def main():
    print("--- START EVALUARE MODEL PE TEST SET ---")

    # 1. Căi fișiere
    # Căutăm modelul antrenat. Dacă nu există cel de 150 epoci, căutăm fallback.
    path_model = os.path.join("models", "antrenare_1024.pt")
    if not os.path.exists(path_model):
        path_model = os.path.join("models", "antrenare_1024.pt")
        
    if not os.path.exists(path_model):
        print(f"❌ EROARE: Nu găsesc modelul în {path_model}")
        return

    # Folderul unde YOLO va salva graficele temporar
    project_dir = "results"
    run_name = "evaluare_finala"
    
    # 2. Încărcare Model
    print(f"[INFO] Încărcare model: {path_model}")
    model = YOLO(path_model)

    # 3. Rulare Validare pe setul de TEST
    # split='test' este CRITIC pentru corectitudinea evaluării!
    print("[INFO] Rulare inferență pe test set...")
    metrics = model.val(
        data='data.yaml',
        split='test',          # Specificăm explicit setul de test
        project=project_dir,
        name=run_name,
        exist_ok=True,
        plots=True             # Generăm matricea de confuzie
    )

    # 4. Extragere și Calcul Metrici
    # YOLO returnează obiectul metrics.box
    map50 = metrics.box.map50      # mAP la IoU 0.5 (Acuratețea standard)
    map50_95 = metrics.box.map     # mAP la IoU 0.5-0.95 (Precizie riguroasă)
    precision = metrics.box.mp     # Mean Precision
    recall = metrics.box.mr        # Mean Recall
    
    # Calculăm F1-Score (Media Armonică)
    # Evităm împărțirea la zero
    if (precision + recall) > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0

    print("\n--- REZULTATE FINALE ---")
    print(f"mAP50 (Acuratețe): {map50:.4f}")
    print(f"F1-Score:          {f1_score:.4f}")
    print(f"Precision:         {precision:.4f}")
    print(f"Recall:            {recall:.4f}")

    # 5. Salvare JSON (Cerință Nivel 1)
    results_json = {
        "test_accuracy_map50": round(map50, 4),
        "test_map50_95": round(map50_95, 4),
        "test_f1_score": round(f1_score, 4),
        "test_precision": round(precision, 4),
        "test_recall": round(recall, 4)
    }
    
    json_path = os.path.join("results", "test_metrics.json")
    with open(json_path, "w") as f:
        json.dump(results_json, f, indent=4)
    print(f"[INFO] Metrici salvate în: {json_path}")

    # 6. Salvare Matrice de Confuzie (Cerință Nivel 3)
    # YOLO o salvează ca confusion_matrix.png sau confusion_matrix_normalized.png
    source_cm = os.path.join(project_dir, run_name, "confusion_matrix_normalized.png")
    if not os.path.exists(source_cm):
        # Încercăm varianta nenormalizată dacă cea normalizată nu există
        source_cm = os.path.join(project_dir, run_name, "confusion_matrix.png")
        
    dest_cm = os.path.join("docs", "confusion_matrix.png")
    
    if os.path.exists(source_cm):
        if not os.path.exists("docs"):
            os.makedirs("docs")
        shutil.copy(source_cm, dest_cm)
        print(f"[INFO] Matricea de confuzie salvată în: {dest_cm}")
    else:
        print("[WARN] Nu am găsit imaginea matricei de confuzie generată de YOLO.")

if __name__ == "__main__":
    main()