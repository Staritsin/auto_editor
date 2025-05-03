from flask import Flask, request, send_file, after_this_request
import os
import subprocess
import uuid

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_video():
    file = request.files['file']
    uid = uuid.uuid4().hex

    input_path = f"input_{uid}.mp4"
    edited_path = f"edited_{uid}.mp4"
    compressed_path = f"compressed_{uid}.mp4"

    file.save(input_path)

    # Auto-Editor
    subprocess.run([
        'auto-editor', input_path,
        '--output', edited_path,
        '--edit', 'audio',
        '--silent-threshold', '0.03',
        '--video-speed', '1',
        '--frame-margin', '6'
    ], check=True)

    # Сжатие ffmpeg
    subprocess.run([
        'ffmpeg', '-i', edited_path,
        '-vcodec', 'libx264',
        '-crf', '28',
        '-preset', 'fast',
        '-vf', 'scale=720:-2',
        '-y', compressed_path
    ], check=True)

    # Очистка временных файлов после отправки
    @after_this_request
    def cleanup(response):
        for path in [input_path, edited_path, compressed_path]:
            try:
                os.remove(path)
            except:
                pass
        return response

    return send_file(compressed_path, as_attachment=True)
