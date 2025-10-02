from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloads'

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Video İndirici</title>
        <style>
            body { font-family: Arial; background: #f0f0f0; padding: 40px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            input, button { width: 100%; padding: 15px; margin: 10px 0; font-size: 16px; }
            button { background: #ff4444; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Video İndirici</h1>
            <input type="text" id="url" placeholder="YouTube/Instagram/Facebook/X linki">
            <button onclick="download()">📥 İndir</button>
            <div id="result"></div>
        </div>
        <script>
            async function download() {
                const url = document.getElementById('url').value;
                const result = document.getElementById('result');
                
                try {
                    const response = await fetch('/download', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url: url})
                    });
                    const data = await response.json();
                    
                    if(data.success) {
                        result.innerHTML = '<a href="' + data.download_url + '" download>✅ Videoyu İndir</a>';
                    } else {
                        result.innerHTML = '❌ Hata: ' + data.error;
                    }
                } catch(error) {
                    result.innerHTML = '❌ Bağlantı hatası';
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data['url']
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
        }
        
        os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        return jsonify({
            'success': True,
            'download_url': f'/file/{os.path.basename(filename)}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/file/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
