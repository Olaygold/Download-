from flask import Flask, request, send_file, jsonify
from pytube import YouTube
import os
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Get the request data
        data = request.json
        url = data.get('url')
        resource_type = data.get('type')

        if not url or not resource_type:
            return jsonify({"error": "Missing URL or resource type"}), 400

        # Fetch YouTube video
        yt = YouTube(url)
        if resource_type == 'mp4':
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        elif resource_type == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
        else:
            return jsonify({"error": "Invalid resource type"}), 400

        if not stream:
            return jsonify({"error": "No suitable stream found"}), 404

        # Create a temporary directory for downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the video/audio
            file_path = stream.download(output_path=temp_dir)

            # Convert audio to MP3 if needed
            if resource_type == 'mp3':
                base, ext = os.path.splitext(file_path)
                mp3_path = base + '.mp3'
                os.rename(file_path, mp3_path)
                file_path = mp3_path

            # Send the file
            response = send_file(file_path, as_attachment=True)

            return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Use environment variables for flexibility
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
