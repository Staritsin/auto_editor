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
        # Удаление тишины (с логами)
        auto_editor_cmd = [
            'auto-editor', input_path,
            '--output', edited_path,
            '--edit', 'audio:threshold=0.03',
            '--video-speed', '1',
            '--frame-margin', '6'
        ]
        result = subprocess.run(auto_editor_cmd, check=True, capture_output=True, text=True, timeout=180)
        print("Auto-Editor Output:", result.stdout)
        print("Auto-Editor Errors:", result.stderr)

        # Сжатие
        ffmpeg_cmd = [
            'ffmpeg', '-i', edited_path,
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'fast',
            '-vf', 'scale=720:-2',
            '-y', compressed_path
        ]
        ffmpeg_result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True, timeout=180)
        print("FFmpeg Output:", ffmpeg_result.stdout)
        print("FFmpeg Errors:", ffmpeg_result.stderr)

        return send_file(compressed_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        print("Subprocess Error:", e.stderr)
        return f"Process Error:\n{e.stderr}", 500

    except FileNotFoundError as e:
        return f"Command not found. Make sure auto-editor and ffmpeg are installed.\n{str(e)}", 500

    except subprocess.TimeoutExpired:
        return "Processing timeout. Try using smaller video files or increase server timeout.", 500

    except Exception as e:
        return f"Unexpected error: {str(e)}", 500

    finally:
        for path in [input_path, edited_path, compressed_path]:
            if os.path.exists(path):
                os.remove(path)
