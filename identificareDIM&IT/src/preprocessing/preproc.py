import os
import cv2
import numpy as np
import pandas as pd
import hashlib
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# ================= CONFIGURARE =================
INPUT_DIR = r'C:\Users\Nae\Desktop\date_brute'          # Folderul cu cele 5 clase (Strunjire, Frezare etc.)
OUTPUT_DIR = r'C:\Users\Nae\Desktop\data_preproc'         # Folderul unde salvăm pozele procesate
CSV_DIR = r'C:\Users\Nae\Desktop\data_splits'              # Folderul pentru CSV-uri
IMG_SIZE = 128                       # Dimensiunea 128x128 (bună pentru simboluri)
PAD_COLOR = (255, 255, 255)          # Alb (pentru fundal)
SEED = 42                            # Pentru rezultate reproductibile
VALID_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif'}
# ===============================================

def calculate_md5(filepath):
    """Hash pentru detectarea duplicatelor."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def resize_and_pad(image, target_size, pad_color):
    """Redimensionare cu pastrarea proportiilor si adaugare padding alb."""
    old_size = image.shape[:2]
    ratio = float(target_size) / max(old_size)
    new_size = tuple([int(x * ratio) for x in old_size])
    
    # Folosim INTER_LANCZOS4 pentru a menține textul clar
    img_resized = cv2.resize(image, (new_size[1], new_size[0]), interpolation=cv2.INTER_LANCZOS4)
    
    new_img = np.full((target_size, target_size, 3), pad_color, dtype=np.uint8)
    
    # Centrare
    y_off = (target_size - new_size[0]) // 2
    x_off = (target_size - new_size[1]) // 2
    
    new_img[y_off:y_off+new_size[0], x_off:x_off+new_size[1]] = img_resized
    return new_img

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(CSV_DIR): os.makedirs(CSV_DIR)

    data_records = []
    seen_hashes = set()
    
    print("--- 1. Preprocesare Imagini ---")
    
    classes = sorted([d for d in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))])
    
    for label_name in classes:
        class_in_path = os.path.join(INPUT_DIR, label_name)
        class_out_path = os.path.join(OUTPUT_DIR, label_name)
        if not os.path.exists(class_out_path): os.makedirs(class_out_path)
            
        print(f"Procesare clasa: {label_name}")
        
        files = os.listdir(class_in_path)
        for filename in tqdm(files):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in VALID_EXTS: continue
                
            src_path = os.path.join(class_in_path, filename)
            
            # Eliminare duplicate exacte
            file_hash = calculate_md5(src_path)
            if file_hash in seen_hashes: continue
            seen_hashes.add(file_hash)
            
            img = cv2.imread(src_path)
            if img is None: continue
            
            # NOTĂ: Nu rotim automat imaginea, deoarece ai deja date rotite (Augmentation).
            
            # Resize + Padding
            final_img = resize_and_pad(img, IMG_SIZE, PAD_COLOR)
            
            dst_filename = f"{os.path.splitext(filename)[0]}_proc.jpg"
            dst_path = os.path.join(class_out_path, dst_filename)
            cv2.imwrite(dst_path, final_img)
            
            data_records.append({
                'filepath': dst_path,
                'label': label_name,
                'filename': dst_filename
            })

    # Creare DataFrame
    df = pd.DataFrame(data_records)
    label_map = {name: i for i, name in enumerate(classes)}
    df['label_idx'] = df['label'].map(label_map)
    
    print(f"\nTotal imagini: {len(df)}")
    print(f"Clase identificate: {label_map}")

    print("\n--- 2. Impartire Seturi (Split) ---")
    
    X = df
    y = df['label_idx']

    # === LOGICA DE SPLIT (80% Train, 10% Val, 10% Test) ===
    # Pas 1: Păstrăm 80% pentru Train, restul de 20% merge în Temp
    # Dacă vrei 70% Train, schimbă test_size=0.2 în test_size=0.3
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED
    )

    # Pas 2: Împărțim Temp (20%) în două jumătăți egale => 10% Val, 10% Test
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=SEED
    )

    print(f"Train: {len(X_train)} (80%)")
    print(f"Val:   {len(X_val)} (10%)")
    print(f"Test:  {len(X_test)} (10%)")

    print("\n--- 3. Calcul Statistici Normalizare (Mean/Std pe Train) ---")
    
    pixel_means = []
    pixel_stds = []
    
    # Calculăm pe un eșantion din Train pentru viteză (max 1000 imagini)
    sample_train = X_train.sample(min(1000, len(X_train)), random_state=SEED)
    
    for _, row in sample_train.iterrows():
        img = cv2.imread(row['filepath'])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) / 255.0
        pixel_means.append(np.mean(img, axis=(0,1)))
        pixel_stds.append(np.std(img, axis=(0,1)))
        
    final_mean = np.mean(pixel_means, axis=0)
    final_std = np.mean(pixel_stds, axis=0)
    
    print(f"Mean (RGB): {final_mean}")
    print(f"Std  (RGB): {final_std}")

    # Salvare
    with open(os.path.join(CSV_DIR, 'stats.txt'), 'w') as f:
        f.write(f"MEAN: {list(final_mean)}\nSTD: {list(final_std)}")

    X_train.to_csv(os.path.join(CSV_DIR, 'train.csv'), index=False)
    X_val.to_csv(os.path.join(CSV_DIR, 'val.csv'), index=False)
    X_test.to_csv(os.path.join(CSV_DIR, 'test.csv'), index=False)
    
    print(f"\nGata! CSV-urile sunt în '{CSV_DIR}'.")

if __name__ == "__main__":
    main()