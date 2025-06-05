import os
import shutil

IMAGE_DIR = "static/images"

def clear_static_images():
    '''Очистка папки "static/images" при каждой инициализации приложения'''
    if os.path.exists(IMAGE_DIR):
        for filename in os.listdir(IMAGE_DIR):
            file_path = os.path.join(IMAGE_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Ошибка при удалении {file_path}: {e}")