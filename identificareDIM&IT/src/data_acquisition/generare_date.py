import os
from PIL import Image, ImageOps # Am importat si ImageOps
from tqdm import tqdm

# === CONFIGURARE ===
# Folosim r'...' pentru a evita problemele cu backslash-urile din Windows
INPUT_FOLDER = r'C:\Users\Nae\Desktop\date_brute\tesituri - Copy'
OUTPUT_FOLDER = r'C:\Users\Nae\Desktop\date_brute\tesituri'

EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp')
ANGLES = [13, 26 , 7, 9, 17, 25, 33, 41, 90, 180, 270]
# ===================

def rotate_and_save_images():
    if not os.path.exists(INPUT_FOLDER):
        print(f"Eroare: Folderul sursa '{INPUT_FOLDER}' nu exista!")
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    image_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(EXTENSIONS)]
    print(f"Am gasit {len(image_files)} imagini. Incep procesarea...")

    for filename in tqdm(image_files):
        file_path = os.path.join(INPUT_FOLDER, filename)
        filename_base, file_ext = os.path.splitext(filename)

        try:
            with Image.open(file_path) as img:
                # PAS CRUCIAL: Corectăm orientarea EXIF (dacă poza e făcută cu telefonul)
                # Astfel, "sus" e chiar "sus" înainte să începem rotirea.
                img = ImageOps.exif_transpose(img)

                # Opțional: Salvăm și imaginea originală (0 grade) în noul folder?
                # Dacă vrei și originalul, decomentează linia de mai jos:
                # img.save(os.path.join(OUTPUT_FOLDER, f"{filename_base}_original{file_ext}"), quality=95)

                for angle in ANGLES:
                    # Rotim imaginea
                    rotated_img = img.rotate(angle, expand=True)

                    new_filename = f"{filename_base}_rot{angle}{file_ext}"
                    output_path = os.path.join(OUTPUT_FOLDER, new_filename)

                    rotated_img.save(output_path, quality=95)

        except Exception as e:
            print(f"\nEroare la procesarea fisierului {filename}: {e}")

    print(f"\nProces finalizat! Imaginile sunt în: '{OUTPUT_FOLDER}'")

if __name__ == "__main__":
    # Asigură-te că ai instalate bibliotecile:
    # pip install pillow tqdm
    rotate_and_save_images()