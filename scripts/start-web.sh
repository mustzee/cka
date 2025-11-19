#!/bin/bash

echo "🚀 CKA 시뮬레이터 웹 서버 시작..."

# 백엔드 서버 시작
cd "$(dirname "$0")/.."

echo "📦 Python 의존성 설치 중..."
pip3 install -r requirements.txt

echo "🔧 데이터베이스 초기화 중..."
python3 -c "from web.backend.database import init_db; init_db()"

echo "🌐 FastAPI 서버 시작 중..."
echo ""
echo "서버 주소:"
echo "  - API: http://localhost:8000"
echo "  - 문서: http://localhost:8000/docs"
echo "  - 웹 UI: web/frontend/index.html 파일을 브라우저로 열기"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

cd web/backend
python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
