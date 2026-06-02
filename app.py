"""
厚生労働省 障害者福祉情報トラッカー — Flask アプリ
"""
import os
from flask import Flask, render_template, jsonify, request
from scraper import collect_data
import threading
from datetime import datetime, timedelta

app = Flask(__name__)

_cache = {"data": None, "fetched_at": None}
_lock = threading.Lock()


def refresh_cache(from_date: str = None, to_date: str = None, days: int = 30):
    """
    from_date, to_date: YYYY-MM-DD 形式の文字列（省略時は days で計算）
    days: 遡る日数（最大30）
    """
    today = datetime.now().date()

    # to_date の決定
    if to_date:
        try:
            td = datetime.strptime(to_date, "%Y-%m-%d").date()
            td = min(td, today)  # 未来日付は今日に丸める
        except ValueError:
            td = today
    else:
        td = today

    # from_date の決定
    if from_date:
        try:
            fd = datetime.strptime(from_date, "%Y-%m-%d").date()
        except ValueError:
            fd = td - timedelta(days=days)
    else:
        fd = td - timedelta(days=days)

    # 最大1ヶ月（31日）制限
    if (td - fd).days > 31:
        fd = td - timedelta(days=31)

    # from > to の場合は修正
    if fd > td:
        fd = td - timedelta(days=1)

    actual_days = (td - fd).days

    with _lock:
        _cache["data"] = collect_data(
            days=actual_days,
            from_date_str=fd.strftime("%Y-%m-%d"),
            to_date_str=td.strftime("%Y-%m-%d"),
        )
        _cache["fetched_at"] = datetime.now().isoformat()


@app.route("/")
def index():
    if _cache["data"] is None:
        refresh_cache()
    return render_template("index.html", data=_cache["data"])


@app.route("/api/refresh")
def api_refresh():
    from_date = request.args.get("from_date")
    to_date   = request.args.get("to_date")
    days      = int(request.args.get("days", 30))
    days      = max(1, min(31, days))
    refresh_cache(from_date=from_date, to_date=to_date, days=days)
    return jsonify({
        "status": "ok",
        "fetched_at": _cache["fetched_at"],
        "total": _cache["data"]["total"],
        "date_range": _cache["data"]["date_range"],
    })


@app.route("/api/data")
def api_data():
    if _cache["data"] is None:
        refresh_cache()
    return jsonify(_cache["data"])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    print("=" * 60)
    print("厚生労働省 障害者福祉情報トラッカー")
    print(f"http://127.0.0.1:{port} でアクセスできます")
    print("=" * 60)
    app.run(debug=False, host="0.0.0.0", port=port)
