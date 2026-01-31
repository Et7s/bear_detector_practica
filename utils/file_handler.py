import os
import uuid
from PIL import Image
from config import UPLOAD_FOLDER, RESULT_FOLDER

def save_uploaded_file(file):
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)
    return filename, upload_path

def save_result_image(image_array, filename):
    result_filename = f"result_{filename}"
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    
    result_pil = Image.fromarray(image_array)
    result_pil.save(result_path)
    
    return result_filename, result_path