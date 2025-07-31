import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pcloud_utils import create_folder, upload_file, generate_share_link
# from keep_alive import keep_alive
# keep_alive()
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

PCLOUD_EMAIL = os.getenv("PCLOUD_EMAIL")
PCLOUD_PASSWORD = os.getenv("PCLOUD_PASSWORD")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = file.filename
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        folder_id = create_folder("WebUploads")
        file_id = upload_file(folder_id, file_path)
        link_data = generate_share_link(file_id)

        # Clean up the local file after upload
        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            'success': True,
            'short_link': link_data['shortlink']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/result')
def result():
    short_link = request.args.get('link')
    if not short_link:
        return redirect(url_for('index'))
    return render_template('result.html', short_link=short_link)


if __name__ == '__main__':
    app.run(debug=True)