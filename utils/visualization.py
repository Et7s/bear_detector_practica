import cv2
import numpy as np

def draw_colored_box(image, detection):
    img = image.copy()
    bbox = detection['bbox']
    confidence = detection['confidence']
    
    x1, y1, x2, y2 = map(int, bbox)
    
    # Определяем цвет в зависимости от уверенности
    if confidence > 0.8:
        color = (0, 255, 0)  # Зеленый - высокая уверенность (>80%)
    elif confidence > 0.65:
        color = (0, 200, 255)  # Оранжевый - средняя уверенность (65-80%)
    elif confidence > 0.5:
        color = (0, 100, 255)  # Оранжево-красный - низкая уверенность (50-65%)
    else:
        color = (0, 0, 255)  # Красный - очень низкая уверенность (<50%)
    
    height, width = img.shape[:2]
    thickness = max(2, int(min(width, height) / 300))
    
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
    
    label = f"Bear: {confidence:.1%}"
    
    font_scale = max(0.5, min(width, height) / 1200)
    font_thickness = max(1, int(font_scale * 2))
    
    (text_width, text_height), baseline = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
    )
    
    cv2.rectangle(
        img,
        (x1, max(0, y1 - text_height - baseline - 5)),
        (x1 + text_width, y1),
        color,
        -1
    )
    
    cv2.putText(
        img,
        label,
        (x1, max(0, y1 - baseline - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (255, 255, 255),
        font_thickness,
        cv2.LINE_AA
    )
    
    if 'area' in detection:
        area_text = f"Area: {detection['area']:.0f}px²"
        area_font_scale = font_scale * 0.8
        
        (area_width, area_height), _ = cv2.getTextSize(
            area_text, cv2.FONT_HERSHEY_SIMPLEX, area_font_scale, 1
        )
        
        cv2.rectangle(
            img,
            (x1, y2),
            (x1 + area_width + 5, y2 + area_height + 5),
            color,
            -1
        )
        
        cv2.putText(
            img,
            area_text,
            (x1 + 3, y2 + area_height),
            cv2.FONT_HERSHEY_SIMPLEX,
            area_font_scale,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )
    
    return img

def add_info_panel(image, detections, processing_time=None):
    img = image.copy()
    height, width = img.shape[:2]
    
    overlay = img.copy()
    panel_height = 120
    
    cv2.rectangle(overlay, (0, 0), (width, panel_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2
    color = (255, 255, 255)
    
    cv2.putText(img, "Bear Detection Results", (20, 35), 
                font, 1.2, color, thickness, cv2.LINE_AA)
    
    if detections:
        total_bears = len(detections)
        avg_confidence = sum([d['confidence'] for d in detections]) / total_bears if total_bears > 0 else 0
        
        stats_text = f"Bears detected: {total_bears} | Avg confidence: {avg_confidence:.1%}"
        cv2.putText(img, stats_text, (20, 70), 
                    font, font_scale, color, thickness-1, cv2.LINE_AA)
        
        legend_y = 95
        legend_items = [
            ("High (>80%)", (0, 255, 0)),
            ("Medium (65-80%)", (0, 200, 255)),
            ("Low (50-65%)", (0, 100, 255)),
            ("Very Low (<50%)", (0, 0, 255))
        ]
        
        x_offset = 20
        for text, color_rgb in legend_items:
            cv2.rectangle(img, (x_offset, legend_y-10), 
                         (x_offset + 20, legend_y + 10), 
                         color_rgb, -1)
            cv2.rectangle(img, (x_offset, legend_y-10), 
                         (x_offset + 20, legend_y + 10), 
                         (255, 255, 255), 1)
            
            cv2.putText(img, text, (x_offset + 30, legend_y + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
            x_offset += 150
    
    if processing_time:
        time_text = f"Processing time: {processing_time:.2f}s"
        cv2.putText(img, time_text, (width - 300, 35), 
                   font, 0.7, color, 1, cv2.LINE_AA)
    
    return img