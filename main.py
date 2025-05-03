from flask import Flask, request, send_file
import os
import subprocess
import uuid

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_video():
    file = request.files['file']
    filename = f"input_{uuid.uuid4()}.mp4"
    output = f"output_{uuid.uuid4()}.mp4"
    file.save(filename)

    # Запуск auto-editor
    subprocess.run([
        'auto-editor', filename,
        '--output', output,
        '--edit', 'audio',
        '--silent-threshold', '0.03',
        '--video-speed', '1',
        '--frame-margin', '6'
    ])

from flask import after_this_request

@after_this_request
def cleanup(response):
    try:
        os.remove(filename)
        os.remove(output)
    except:
        pass
    return response


    return send_file(output, as_attachment=True)
