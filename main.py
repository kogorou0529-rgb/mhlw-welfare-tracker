"""
モーリス 福祉情報トラッカー — デスクトップ起動エントリーポイント
ダブルクリックで Flask サーバーを起動し、ブラウザを自動で開く
"""
import sys
import os
import threading
import webbrowser
import time
import socket

# ── PyInstaller バンドル時のパス解決 ──
if getattr(sys, 'frozen', False):
    # exe として実行中
    BASE_DIR = sys._MEIPASS
    WORK_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    WORK_DIR = BASE_DIR

os.chdir(WORK_DIR)
sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, jsonify
from scraper import collect_data
import threading as _threading
from datetime import datetime

# ── Flask アプリ初期化（テンプレートパスを明示） ──
template_dir = os.path.join(BASE_DIR, 'templates')
flask_app = Flask(__name__, template_folder=template_dir)

_cache = {"data": None, "fetched_at": None}
_lock = _threading.Lock()

def refresh_cache(hours=120):
    with _lock:
        _cache["data"] = collect_data(hours)
        _cache["fetched_at"] = datetime.now().isoformat()

@flask_app.route("/")
def index():
    if _cache["data"] is None:
        refresh_cache()
    return render_template("index.html", data=_cache["data"])

@flask_app.route("/api/refresh")
def api_refresh():
    refresh_cache()
    return jsonify({"status": "ok", "fetched_at": _cache["fetched_at"], "total": _cache["data"]["total"]})

@flask_app.route("/api/data")
def api_data():
    if _cache["data"] is None:
        refresh_cache()
    return jsonify(_cache["data"])

# ── ポート確認 ──
def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) != 0

def find_free_port(start=5001):
    for port in range(start, start + 20):
        if is_port_free(port):
            return port
    return start

# ── メイン ──
def main():
    port = find_free_port(5001)

    def run_server():
        flask_app.run(
            host='127.0.0.1',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )

    server = threading.Thread(target=run_server, daemon=True)
    server.start()

    # サーバー起動待ち
    for _ in range(20):
        time.sleep(0.3)
        if not is_port_free(port):
            break

    # ブラウザを自動で開く
    webbrowser.open(f'http://127.0.0.1:{port}')

    print(f"モーリス 福祉情報トラッカー 起動中 → http://127.0.0.1:{port}")
    print("このウィンドウを閉じるとアプリが終了します。")

    # アプリが終了するまで待機
    server.join()

if __name__ == '__main__':
    main()
