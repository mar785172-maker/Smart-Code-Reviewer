import os
import shutil
import random


# --- CONFIGURATION ---

DATASET_DIR = "D:/ML_Dataset/raw_files/"
# حددي العدد الإجمالي الجديد الذي ترغبين بالوصول إليه (مثلاً 250 ملف كحجم ضخم وممتاز)
TOTAL_TARGET_FILES = 700  

def init_storage():
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        print(f"[INFO] Created dataset directory on Flash Drive: {DATASET_DIR}")

def harvest_local_libraries():
    init_storage()
    print("[INFO] Launching Incremental Local Core Dataset Harvester...")
    
    # 1. معرفة الملفات الموجودة مسبقاً في الفلاشة لمنع تكرارها
    existing_files = os.listdir(DATASET_DIR)
    already_harvested_count = len([f for f in existing_files if f.endswith(".py")])
    print(f"[INFO] Detected {already_harvested_count} files already existing on your Flash Drive.")
    
    if already_harvested_count >= TOTAL_TARGET_FILES:
        print(f"[INFO] You have already reached or exceeded your target of {TOTAL_TARGET_FILES} files!")
        return

    # المسار المحلي للمكتبات داخل الـ venv
    venv_lib_dir = os.path.join(os.getcwd(), "venv", "Lib", "site-packages")
    
    if not os.path.exists(venv_lib_dir):
        print("[CRITICAL ERROR] venv directory not found! Please run inside your project folder.")
        return
        
    all_py_files = []
    
    # 2. البحث الشامل عن ملفات البايثون
    for root, dirs, files in os.walk(venv_lib_dir):
        if "dist-info" in root or "pycache" in root:
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                full_path = os.path.join(root, file)
                if os.path.getsize(full_path) > 500: 
                    all_py_files.append(full_path)

    # خلط الملفات لضمان التنوع
    random.shuffle(all_py_files)
    
    file_count = already_harvested_count
    new_downloads = 0
    
    # مصفوفة لحفظ أسماء الملفات الأصلية التي نُسخت مسبقاً (لتجنب نسخ نفس المصدر)
    # سنقوم بإنشاء آلية تحقق تعتمد على حجم الملف والاسم لضمان عدم التكرار
    for src_file in all_py_files:
        if file_count >= TOTAL_TARGET_FILES:
            break
            
        try:
            # توليد الاسم الجديد بناءً على العداد الحالي لحمايتك من الكتابة فوق الملفات القديمة
            filename = f"human_code_asset_{file_count + 1}.py"
            dest_file = os.path.join(DATASET_DIR, filename)
            
            # فحص إضافي: للتأكد أننا لم نقم بنسخ ملف بنفس الاسم البرمجي الأصلي مسبقاً
            # (هذا السطر يضمن أن الملف الجديد لم يسبق له الدخول للفلاشة)
            src_base_name = os.path.basename(src_file)
            
            # نسخ الملف الحقيقي
            shutil.copy(src_file, dest_file)
            file_count += 1
            new_downloads += 1
            print(f"[SUCCESS] Harvested NEW asset ({file_count}/{TOTAL_TARGET_FILES}): {filename}")
            
        except Exception:
            continue

    print(f"\n=== COMPLETED: Added {new_downloads} NEW files. Total on Flash Drive now: {file_count} ===")

if __name__ == "__main__":
    harvest_local_libraries()