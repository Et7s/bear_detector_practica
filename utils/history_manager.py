import json
import os
import numpy as np
from datetime import datetime
from config import HISTORY_FILE

def load_history():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    try:
        if os.path.getsize(HISTORY_FILE) == 0:
            return []
        
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
            
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"⚠️ Ошибка чтения history.json: {e}")
        print("🔄 Создаю новый файл истории...")
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return []

def save_history(history):
    try:
        temp_file = str(HISTORY_FILE) + '.tmp'
        
        def numpy_serializer(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2, default=numpy_serializer)
        
        if os.path.exists(HISTORY_FILE):
            os.replace(temp_file, HISTORY_FILE)
        else:
            os.rename(temp_file, HISTORY_FILE)
            
    except Exception as e:
        print(f"❌ Ошибка сохранения истории: {e}")
        import traceback
        traceback.print_exc()
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)

def calculate_summary_statistics(history_data):
    if not history_data:
        return {
            'total_requests': 0,
            'total_bears': 0,
            'avg_confidence': 0,
            'max_confidence': 0,
            'min_confidence': 0,
            'bears_per_request': 0,
            'daily_stats': []
        }
    
    total_requests = len(history_data)
    total_bears = sum(item['bear_count'] for item in history_data)
    
    all_confidences = []
    for item in history_data:
        for det in item['detections']:
            all_confidences.append(det['confidence'])
    
    avg_confidence = np.mean(all_confidences) if all_confidences else 0
    max_confidence = max(all_confidences) if all_confidences else 0
    min_confidence = min(all_confidences) if all_confidences else 0
    
    daily_stats = {}
    for item in history_data:
        date = item['timestamp'][:10]  # YYYY-MM-DD
        if date not in daily_stats:
            daily_stats[date] = {
                'count': 0, 
                'bears': 0,
                'confidences': []
            }
        
        daily_stats[date]['count'] += 1
        daily_stats[date]['bears'] += item['bear_count']
        for det in item['detections']:
            daily_stats[date]['confidences'].append(det['confidence'])
    
    formatted_daily_stats = []
    for date, stats in sorted(daily_stats.items(), reverse=True):
        avg_conf = np.mean(stats['confidences']) if stats['confidences'] else 0
        max_conf = max(stats['confidences']) if stats['confidences'] else 0
        
        formatted_daily_stats.append({
            'date': date,
            'count': stats['count'],
            'bears': stats['bears'],
            'avg_confidence': avg_conf,
            'max_confidence': max_conf
        })
    
    return {
        'total_requests': total_requests,
        'total_bears': total_bears,
        'avg_confidence': avg_confidence,
        'max_confidence': max_confidence,
        'min_confidence': min_confidence,
        'bears_per_request': total_bears / total_requests if total_requests > 0 else 0,
        'daily_stats': formatted_daily_stats[:10]
    }