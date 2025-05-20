from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import re
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form
        video_url = data['video_url'].strip()
        mode = data['mode']
        playlist_mode = data['playlist_mode']
        resolution = data.get('resolution', 'best[ext=mp4]')

        # 清理播放清單參數
        if playlist_mode == '2':
            video_url = re.sub(r"&list=[^&]*", "", video_url)
            video_url = re.sub(r"&start_radio=[^&]*", "", video_url)
            video_url = re.sub(r"&index=[^&]*", "", video_url)

        # 建立下載命令
        file_template = "%(playlist_index)s - %(title)s.%(ext)s" if playlist_mode == '1' else "%(title)s.%(ext)s"
        output_template = os.path.join(app.config['UPLOAD_FOLDER'], file_template)

        try:
            if mode == '1':
                cmd = [
                    'yt-dlp',
                    '-f', resolution,
                    '-o', output_template,
                    video_url
                ]
            else:
                cmd = [
                    'yt-dlp',
                    '-x',
                    '--audio-format', 'mp3',
                    '-o', output_template,
                    video_url
                ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("Download completed:", result.stdout)
            return redirect(url_for('downloads'))
            
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
            
    return render_template('index.html')

@app.route('/downloads')
def downloads():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('downloads.html', files=files)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)