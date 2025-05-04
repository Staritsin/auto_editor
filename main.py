from flask import Flask, request, send_file, jsonify
import os
import uuid
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return "Auto-Editor API is running."

@app.route("/process", methods=["POST"])
def process_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    input_filename = f"{uuid.uuid4()}.mp4"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    output_filename = f"output_{input_filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    try:
        result = subprocess.run([
            "auto-editor", input_path,
            "--edit", "audio",
            "--output", output_path
        ], capture_output=True, text=True, check=True)

        return send_file(output_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Processing failed",
            "details": e.stderr
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
