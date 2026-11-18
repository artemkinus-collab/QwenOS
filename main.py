from flask import Flask, request, jsonify, send_from_directory
import os, subprocess, json

app = Flask(__name__, static_folder='static', static_url_path='')
NOTES_FILE = "notes.json"

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/files')
def get_files():
    path = request.args.get('path', '')
    # В облаке мы работаем внутри папки static
    full_path = os.path.join(os.getcwd(), 'static', path) if path else os.path.join(os.getcwd(), 'static')
    
    items = []
    if os.path.isdir(full_path):
        for name in sorted(os.listdir(full_path)):
            p = os.path.join(full_path, name)
            items.append({
                "name": name,
                "is_dir": os.path.isdir(p),
                "size": os.path.getsize(p) if not os.path.isdir(p) else 0
            })
    return jsonify(items)

@app.route('/api/exec', methods=['POST'])
def exec_cmd():
    cmd = request.json.get('cmd', '')
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return jsonify({"output": result.stdout + result.stderr})
    except Exception as e:
        return jsonify({"output": str(e)}), 500

@app.route('/api/notes', methods=['GET', 'POST'])
def notes():
    if request.method == 'POST':
        with open(NOTES_FILE, 'w') as f:
            json.dump(request.json, f)
        return jsonify({"status": "ok"})
    else:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({})

if __name__ == '__main__':
    # Render требует слушать порт из переменной окружения
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
