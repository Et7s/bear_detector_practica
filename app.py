import numpy as np
import json
import time
from datetime import datetime
import uuid

from flask import Flask, render_template, request, jsonify, send_file

from config import UPLOAD_FOLDER, RESULT_FOLDER, MAX_CONTENT_LENGTH

from models.detector import detect_bears
from utils.visualization import draw_colored_box, add_info_panel
from utils.history_manager import load_history, save_history, calculate_summary_statistics
from utils.excel_reporter import generate_excel_report, generate_json_report, generate_pdf_report
from utils.file_handler import save_uploaded_file, save_result_image


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.json_encoder = NumpyEncoder


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    start_time = time.time()

    filename, upload_path = save_uploaded_file(file)

    detections, result_img = detect_bears(upload_path, confidence_threshold=0.25)

    for detection in detections:
        result_img = draw_colored_box(result_img, detection)

    processing_time = time.time() - start_time

    result_img = add_info_panel(result_img, detections, processing_time)

    result_filename, result_path = save_result_image(result_img, filename)

    detailed_detections = []
    for det in detections:
        detailed_detections.append({
            'bbox': [float(x) for x in det['bbox']],
            'confidence': float(det['confidence']),
            'class': det['class'],
            'class_id': int(det['class_id']),
            'area': float(det.get('area', 0)),
            'center_x': float(det.get('center_x', 0)),
            'center_y': float(det.get('center_y', 0))
        })

    history_entry = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'original_image': f'static/uploads/{filename}',
        'result_image': f'static/results/{result_filename}',
        'detections': detailed_detections,
        'bear_count': int(len(detections)),
        'processing_time': float(processing_time)
    }

    history = load_history()
    history.append(history_entry)
    save_history(history)

    response_detections = []
    for det in detections:
        response_detections.append({
            'bbox': [float(x) for x in det['bbox']],
            'confidence': float(det['confidence']),
            'class': det['class'],
            'class_id': int(det['class_id'])
        })

    return jsonify({
        'success': True,
        'bear_count': int(len(detections)),
        'detections': response_detections,
        'result_image': f'static/results/{result_filename}',
        'history_id': history_entry['id'],
        'processing_time': float(processing_time)
    })


@app.route('/history')
def get_history():
    history = load_history()
    return jsonify(history)


@app.route('/generate-report')
def generate_report():
    history = load_history()
    if not history:
        return jsonify({'error': 'History is empty'}), 400

    report_format = request.args.get('format', 'excel').lower()

    try:
        if report_format == 'excel':
            path = generate_excel_report(history)
            return send_file(
                path,
                as_attachment=True,
                download_name='bear_report.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        elif report_format == 'pdf':
            path = generate_pdf_report(history)
            return send_file(
                path,
                as_attachment=True,
                download_name='bear_report.pdf',
                mimetype='application/pdf'
            )

        elif report_format == 'json':
            path = generate_json_report(history)
            return send_file(
                path,
                as_attachment=True,
                download_name='bear_report.json',
                mimetype='application/json'
            )

        else:
            return jsonify({'error': 'Unsupported format'}), 400

    except Exception as e:
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500



@app.route('/stats')
def get_statistics():
    history = load_history()

    if not history:
        return jsonify({
            'total_requests': 0,
            'total_bears': 0,
            'avg_confidence': 0,
            'daily_stats': []
        })

    summary = calculate_summary_statistics(history)

    return jsonify({
        'total_requests': summary['total_requests'],
        'total_bears': summary['total_bears'],
        'avg_confidence': summary['avg_confidence'],
        'max_confidence': summary['max_confidence'],
        'min_confidence': summary['min_confidence'],
        'bears_per_request': summary['bears_per_request'],
        'daily_stats': summary['daily_stats']
    })


@app.route('/quick-stats')
def get_quick_stats():
    history = load_history()

    if not history:
        return jsonify({
            'total': 0,
            'bears_total': 0,
            'today': 0,
            'avg_confidence': 0
        })

    today = datetime.now().strftime("%Y-%m-%d")
    today_requests = 0
    today_bears = 0

    for item in history:
        if item['timestamp'].startswith(today):
            today_requests += 1
            today_bears += item['bear_count']

    total_requests = len(history)
    total_bears = sum(item['bear_count'] for item in history)

    all_confidences = []
    for item in history:
        for det in item['detections']:
            all_confidences.append(det['confidence'])

    avg_confidence = np.mean(all_confidences) if all_confidences else 0

    return jsonify({
        'total': total_requests,
        'bears_total': total_bears,
        'today': today_requests,
        'today_bears': today_bears,
        'avg_confidence': avg_confidence
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
