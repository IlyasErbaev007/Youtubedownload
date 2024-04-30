from flask import Flask, render_template, request, redirect, send_from_directory
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from moviepy.editor import AudioFileClip
import os
from flask import send_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloads'

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    format_type = request.form['format']

    try:
        yt = YouTube(video_url)
        title = sanitize_filename(yt.title)

        if format_type == 'mp4':
            stream = yt.streams.get_highest_resolution()
            filename = f"{title}.mp4"
            stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=filename)
            return redirect(f'/downloaded/{filename}')
        elif format_type == 'mp3':
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_filename = f"{title}.mp3"
            audio_stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=audio_filename)

            # Конвертация аудио в формат MP3
            clip = AudioFileClip(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))
            clip.write_audiofile(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))

            return redirect(f'/downloaded/{audio_filename}')

    except VideoUnavailable:
        return render_template('unavailable.html')

@app.route('/downloaded/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
