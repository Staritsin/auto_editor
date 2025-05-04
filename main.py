from flask import Flask, request, send_file
import os
import subprocess
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return '🚀 Flask API работает!'

@app.route('/process', methods=['POST'])
def process_video():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    uid = uuid.uuid4().hex

    input_path = f"input_{uid}.mp4"
    edited_path = f"edited_{uid}.mp4"
    compressed_path = f"compressed_{uid}.mp4"

    file.save(input_path)

    try:
        # Удаление тишины
        subprocess.run([
            'auto-editor', input_path,
            '--output', edited_path,
            '--edit', 'audio:threshold=0.03',
            '--video-speed', '1',
            '--frame-margin', '6'
        ], check=True, capture_output=True, text=True)

        # Сжатие
        subprocess.run([
            'ffmpeg', '-i', edited_path,
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'fast',
            '-vf', 'scale=720:-2',
            '-y', compressed_path
        ], check=True)

        return send_file(compressed_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return f"Auto-Editor Error:\n{e.stderr}", 500

    except Exception as e:
        return f"Unexpected Error: {str(e)}", 500

    finally:
        for path in [input_path, edited_path, compressed_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Railway использует эту переменную
    app.run(host='0.0.0.0', port=port)
