from ultralytics import YOLO
from config import MODEL_NAME

def load_model():
    try:
        model = YOLO(MODEL_NAME)
        print(f"✅ Модель {MODEL_NAME} успешно загружена")
        return model
    except Exception as e:
        print(f"⚠️ Не удалось загрузить {MODEL_NAME}: {e}")
        print("🔄 Пробую загрузить yolo26n...")
        model = YOLO("yolo26s")
        return model

model = load_model()