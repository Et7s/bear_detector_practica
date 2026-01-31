import cv2
import numpy as np
from PIL import Image

from config import CONFIDENCE_THRESHOLD, IOU_THRESHOLD
from models.model_loader import model


def detect_bears(image_path,confidence_threshold=CONFIDENCE_THRESHOLD,iou_threshold=IOU_THRESHOLD):

    # Загружаем изображение
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")

    image_np = np.array(image)

    # Запускаем модель
    results = model(
        image_np,
        conf=confidence_threshold,
        iou=iou_threshold,
        verbose=False
    )

    detections = []
    result_image = image_np.copy()

    # YOLO может вернуть несколько результатов (обычно один)
    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            class_id = int(box.cls[0])

            # В COCO class_id = 21 соответствует медведю
            if class_id != 21:
                continue

            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            bbox = [float(x1), float(y1), float(x2), float(y2)]
            area = (x2 - x1) * (y2 - y1)

            detections.append({
                "bbox": bbox,
                "confidence": confidence,
                "class": "bear",
                "class_id": class_id,
                "area": float(area),
                "center_x": float((x1 + x2) / 2),
                "center_y": float((y1 + y2) / 2)
            })

        # Если медведей нет — используем стандартный вывод YOLO
        if not detections:
            plotted = result.plot()
            result_image = cv2.cvtColor(plotted, cv2.COLOR_BGR2RGB)

    return detections, result_image
