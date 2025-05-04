
from flask import Flask, request, send_file
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Auto-Editor API!"

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    f = request.files['file']
    uid = uuid.uuid4().hex
    input_path = f"input_{uid}.mp4"
    output_path = f"output_{uid}.mp4"
    f.save(input_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return f"Processing error:\n{result.stderr}", 500
            "auto-editor", input_path,
            "--edit", "audio",
            "--silent-threshold", "0.03",
            "--video-speed", "1",
            "--frame-margin", "6",
            "--output", output_path
        ], check=True)

        return send_file(output_path, as_attachment=True)
    except subprocess.CalledProcessError as e:
        return f"Processing error: {e}", 500
    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
