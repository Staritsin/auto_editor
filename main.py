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
    edited_path = f"edited_{uid}.mp4"
    compressed_path = f"compressed_{uid}.mp4"

    file.save(input_path)

    try:
        # Проверим валидность файла
        check = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=format_name',
            '-of', 'default=noprint_wrappers=1:nokey=1', input_path
        ], capture_output=True, text=True)

        if check.returncode != 0:
            return f"Invalid video format:\n{check.stderr}", 400

        # Обработка авто-редактором
        print(f"Running Auto-Editor on {input_path}")
        subprocess.run([
            'auto-editor', input_path,
            '--edit', 'audio:threshold=0.08',
            '--silent-speed', '99999',
            '--video-speed', '1.0',
            '--frame-margin', '6',
            '--export', 'default',
            '--output', edited_path
        ], check=True, capture_output=True, text=True)

        # Сжатие ffmpeg
        print(f"Compressing {edited_path}")
        subprocess.run([
            'ffmpeg', '-i', edited_path,
            '-vcodec', 'libx264', '-crf', '30', '-preset', 'fast',
            '-vf', 'scale=720:-2',
            '-acodec', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',
            '-y', compressed_path
        ], check=True)

        return send_file(compressed_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        print("Processing error:", e.stderr)
        return f"Processing error:\n{e.stderr}", 500

    except Exception as e:
        print("General error:", str(e))
        return f"Unexpected error: {str(e)}", 500

    finally:
        for path in [input_path, edited_path, compressed_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
