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
            '--edit', 'audio'
        ], check=True, capture_output=True, text=True)

        return send_file(output_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        print("🔴 Auto-Editor STDERR:\n", e.stderr)
        return f"Auto-Editor Error:\n{e.stderr}", 500

    except Exception as e:
        print("🔴 Unexpected Error:", str(e))
        return f"Unexpected Error: {str(e)}", 500

    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
