"""
Daily Notes - 간소화된 주식 일지 Flask 서버
"""
import sys
from pathlib import Path

# 상위 디렉토리의 supabase_client 사용
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
from supabase_client import SupabaseClient
import os

app = Flask(__name__)

# Supabase 클라이언트 초기화
def get_supabase_client():
    """환경변수 또는 .env 파일에서 설정을 로드하여 클라이언트 생성"""
    env_path = Path(__file__).parent.parent / ".env"
    env_vars = {}

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

    url = env_vars.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = env_vars.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise Exception("SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")

    return SupabaseClient(url, key)

# 전역 클라이언트 (lazy initialization)
_client = None

def get_client():
    global _client
    if _client is None:
        _client = get_supabase_client()
    return _client


@app.route("/")
def index():
    """메인 페이지"""
    today = date.today().isoformat()
    return render_template("index.html", today=today)


@app.route("/api/note/<note_date>", methods=["GET"])
def get_note(note_date):
    """특정 날짜의 노트 조회"""
    try:
        client = get_client()
        note = client.get_daily_note_by_date(note_date)

        if note:
            return jsonify({"success": True, "note": note})
        else:
            return jsonify({"success": True, "note": None})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/note", methods=["POST"])
def save_note():
    """노트 저장 (생성 또는 업데이트)"""
    try:
        data = request.json
        client = get_client()

        note_date = data.get("note_date")
        content = data.get("content", "")
        tags = data.get("tags", [])
        image_urls = data.get("image_urls", [])

        # 기존 노트가 있는지 확인
        existing = client.get_daily_note_by_date(note_date)

        if existing:
            # 업데이트
            result = client.update_daily_note(existing["id"], {
                "content": content,
                "tags": tags,
                "image_urls": image_urls
            })
        else:
            # 새로 생성
            result = client.create_daily_note({
                "note_date": note_date,
                "content": content,
                "tags": tags,
                "image_urls": image_urls
            })

        return jsonify({"success": True, "note": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload_image():
    """이미지 업로드"""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "파일이 없습니다."}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "파일명이 없습니다."}), 400

        client = get_client()

        file_data = file.read()
        file_name = file.filename
        content_type = file.content_type or "image/png"

        url = client.upload_image(file_data, file_name, content_type)

        return jsonify({"success": True, "url": url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/notes", methods=["GET"])
def list_notes():
    """노트 목록 조회"""
    try:
        client = get_client()
        tag = request.args.get("tag")
        limit = int(request.args.get("limit", 30))

        notes = client.query_daily_notes(search_tag=tag, limit=limit)

        return jsonify({"success": True, "notes": notes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("Daily Notes Server Starting...")
    print("URL: http://localhost:5000")
    print("=" * 50)
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, port=5000)
