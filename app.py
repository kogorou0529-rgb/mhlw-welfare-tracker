"""
厚生労働省 障害者福祉情報トラッカー — Flask アプリ
"""
import os
from flask import Flask, render_template, jsonify
from scraper import collect_data
import threading
from datetime import datetime

app = Flask(__name__)

_cache = {"data": None, "fetched_at": None}
_lock = threading.Lock()


def refresh_cache(days: int = 30):
    with _lock:
        _cache["data"] = collect_data(days=days)
        _cache["fetched_at"] = datetime.now().isoformat()


@app.route("/")
def index():
    if _cache["data"] is None:
        refresh_cache()
    return render_template("index.html", data=_cache["data"])


@app.route("/api/refresh")
def api_refresh():
    refresh_cache()
    return jsonify({"status": "ok", "fetched_at": _cache["fetched_at"], "total": _cache["data"]["total"]})


@app.route("/api/data")
def api_data():
    if _cache["data"] is None:
        refresh_cache()
    return jsonify(_cache["data"])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print("=" * 60)
    print("厚生労働省 障害者福祉情報トラッカー")
    print(f"http://127.0.0.1:{port} でアクセスできます")
    print("=" * 60)
    app.run(debug=False, host="0.0.0.0", port=port)
