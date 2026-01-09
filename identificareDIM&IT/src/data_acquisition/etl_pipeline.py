import os
import cv2
import glob
import random
import csv
import shutil
import numpy as np
import albumentations as A
from tqdm import tqdm

# ================= CONFIGURATION =================
BASE_DIR = os.getcwd()
INPUT_DIR = os.path.join(BASE_DIR, "train") 
INPUT_IMGS_DIR = os.path.join(INPUT_DIR, "images")
INPUT_LBLS_DIR = os.path.join(INPUT_DIR, "labels")
OUTPUT_BASE = os.path.join(BASE_DIR, "dataset_final")

IMG_SIZE = 640
AUGMENTATIONS_PER_IMG = 4 
SPLIT_RATIOS = (0.70, 0.15, 0.15) 

# Augmentation Parameters
ROTATION_LIMIT = 2
BRIGHTNESS_LIMIT = 0.15
NOISE_VAR_LIMIT = (10.0, 50.0)

DIRS = ['train', 'validation', 'test']
SUBDIRS = ['images', 'labels']

def setup_directories():
    if os.path.exists(OUTPUT_BASE):
        try:
            shutil.rmtree(OUTPUT_BASE)
            print(f"[INFO] Removed old '{OUTPUT_BASE}' folder to start fresh.")
        except:
            pass
            
    for split in DIRS:
        for sub in SUBDIRS:
            path = os.path.join(OUTPUT_BASE, split, sub)
            os.makedirs(path, exist_ok=True)

def read_yolo_obb(txt_path, img_w, img_h):
    bboxes_points = []
    class_ids = []
    if not os.path.exists(txt_path): return [], []

    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        parts = list(map(float, line.strip().split()))
        class_id = int(parts[0])
        coords = parts[1:]
        points = []
        for i in range(0, len(coords), 2):
            points.append((coords[i] * img_w, coords[i+1] * img_h))
        bboxes_points.append(points)
        class_ids.append(class_id)
    return class_ids, bboxes_points

def write_yolo_obb(save_path, class_ids, transformed_keypoints, img_w, img_h):
    with open(save_path, 'w', encoding='utf-8') as f:
        for i, cls in enumerate(class_ids):
            poly_points = transformed_keypoints[i*4 : (i+1)*4]
            line_parts = [str(cls)]
            for (x, y) in poly_points:
                x = min(max(x, 0), img_w)
                y = min(max(y, 0), img_h)
                line_parts.extend([f"{x/img_w:.6f}", f"{y/img_h:.6f}"])
            f.write(" ".join(line_parts) + "\n")

def get_aug_pipeline(is_augmentation=False):
    transforms = [A.Resize(height=IMG_SIZE, width=IMG_SIZE, always_apply=True)]
    if is_augmentation:
        transforms.extend([
            A.Rotate(limit=ROTATION_LIMIT, p=0.8, border_mode=cv2.BORDER_CONSTANT, value=0),
            A.RandomBrightnessContrast(brightness_limit=BRIGHTNESS_LIMIT, contrast_limit=0, p=0.7),
            A.GaussNoise(var_limit=NOISE_VAR_LIMIT, p=0.5)
        ])
    return A.Compose(transforms, keypoint_params=A.KeypointParams(format='xy', remove_invisible=False))

def main():
    print(f"--- START SCRIPT ---")
    print(f"Looking for data in: {INPUT_IMGS_DIR}")

    if not os.path.exists(INPUT_IMGS_DIR):
        print(f"\n[FATAL ERROR] Cannot find folder: {INPUT_IMGS_DIR}")
        print("Please check structure! Script must be next to 'train' folder.")
        return

    # Find images regardless of extension case (jpg, JPG, png, PNG)
    all_files = os.listdir(INPUT_IMGS_DIR)
    valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    raw_files = [f for f in all_files if f.lower().endswith(valid_exts)]
    
    unique_names = list(set([os.path.splitext(f)[0] for f in raw_files]))
    
    if not unique_names:
        print(f"\n[ERROR] 'images' folder exists but is EMPTY or contains invalid files!")
        return

    print(f"[INFO] Found {len(unique_names)} images. Starting processing...")
    setup_directories()
    
    random.shuffle(unique_names)
    total = len(unique_names)
    n_train = int(total * SPLIT_RATIOS[0])
    n_val = int(total * SPLIT_RATIOS[1])
    
    splits = {
        'train': unique_names[:n_train],
        'validation': unique_names[n_train:n_train+n_val],
        'test': unique_names[n_train+n_val:]
    }

    csv_path = os.path.join(BASE_DIR, 'data_log.csv')
    csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['filename', 'type', 'augmentation_details', 'dataset_split'])
    
    stats = {'train': 0, 'validation': 0, 'test': 0}

    for split_name, files in splits.items():
        print(f"Processing set: {split_name}...")
        for name in tqdm(files):
            # Find correct extension
            img_filename = next((f for f in raw_files if f.startswith(name + ".")), None)
            if not img_filename: continue

            img_path = os.path.join(INPUT_IMGS_DIR, img_filename)
            txt_path = os.path.join(INPUT_LBLS_DIR, name + ".txt")
            
            image = cv2.imread(img_path)
            if image is None: 
                print(f"[WARNING] Could not read image: {img_path}")
                continue

            h, w, _ = image.shape
            class_ids, polies = read_yolo_obb(txt_path, w, h)
            all_keypoints = [pt for poly in polies for pt in poly]
            
            # 1. Original
            t = get_aug_pipeline(False)(image=image, keypoints=all_keypoints)
            
            # Create filenames
            out_img_name = f"{name}.jpg"
            out_txt_name = f"{name}.txt"
            
            cv2.imwrite(os.path.join(OUTPUT_BASE, split_name, 'images', out_img_name), t['image'])
            write_yolo_obb(os.path.join(OUTPUT_BASE, split_name, 'labels', out_txt_name), 
                           class_ids, t['keypoints'], IMG_SIZE, IMG_SIZE)
            
            csv_writer.writerow([out_img_name, 'original', 'Resize', split_name])
            stats[split_name] += 1
            
            # 2. Augmented
            for i in range(AUGMENTATIONS_PER_IMG):
                t_aug = get_aug_pipeline(True)(image=image, keypoints=all_keypoints)
                
                aug_name = f"{name}_aug_{i}"
                out_aug_img = f"{aug_name}.jpg"
                out_aug_txt = f"{aug_name}.txt"
                
                cv2.imwrite(os.path.join(OUTPUT_BASE, split_name, 'images', out_aug_img), t_aug['image'])
                write_yolo_obb(os.path.join(OUTPUT_BASE, split_name, 'labels', out_aug_txt), 
                               class_ids, t_aug['keypoints'], IMG_SIZE, IMG_SIZE)
                
                csv_writer.writerow([out_aug_img, 'augmented', 'Augmented', split_name])
                stats[split_name] += 1

    csv_file.close()
    print(f"\n[SUCCESS] Dataset generated in folder: dataset_final")
    print(f"Statistics: {stats}")

if __name__ == "__main__":
    main()