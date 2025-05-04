from flask import Flask, request, send_file
import os
import subprocess
import uuid

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_video():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    uid = uuid.uuid4().hex

    input_path = f"input_{uid}.mp4"
    output_path = f"output_{uid}.mp4"

    file.save(input_path)

    try:
        result = subprocess.run([
            'auto-editor', input_path,
            '--output', output_path,
            '--edit', 'audio',
            '--video-speed', '1',
            '--frame-margin', '6'
        ], capture_output=True, text=True, timeout=180, check=True)

        return send_file(output_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return f"Auto-Editor Error:\n{e.stderr}", 500

    except Exception as e:
        return f"Unexpected Error: {str(e)}", 500

    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
