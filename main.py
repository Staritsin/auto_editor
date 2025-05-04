from flask import Flask, request, send_file
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process_video():
    if 'file' not in request.files:
        return "No file provided", 400

    file = request.files["file"]
    uid = uuid.uuid4().hex

    input_path = f"input_{uid}.mp4"
    output_path = f"edited_{uid}.mp4"
    final_path = f"compressed_{uid}.mp4"

    file.save(input_path)

    try:
        # Удаление тишины
        subprocess.run([
            "auto-editor", input_path,
            "--output", output_path,
            "--edit", "audio:threshold=0.08",
            "--silent-speed", "99999",
            "--video-speed", "1.0",
            "--frame-margin", "6",
            "--export", "default"
        ], check=True)

        # Сжатие
        subprocess.run([
            "ffmpeg", "-i", output_path,
            "-vcodec", "libx264", "-crf", "30", "-preset", "fast",
            "-vf", "scale=720:-2",
            "-acodec", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            final_path
        ], check=True)

        return send_file(final_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return f"Ошибка обработки:\n{e}", 500

    finally:
        for path in [input_path, output_path, final_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
