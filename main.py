from flask import Flask, request, jsonify
import os
import uuid
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return 'Auto-Editor API is working!'

@app.route('/process', methods=['POST'])
def process_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename = f"{uuid.uuid4()}.mp4"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"output_{filename}")

    file.save(input_path)

    try:
        result = subprocess.run([
            'auto-editor',
            input_path,
            '--edit', 'audio',
            '--silent-threshold', '0.03',
            '--video-speed', '1',
            '--frame-margin', '6',
            '--output', output_path
        ], check=True, capture_output=True, text=True)

        return jsonify({'message': 'Processing complete', 'output_file': output_path}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Processing failed', 'details': e.stderr}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
