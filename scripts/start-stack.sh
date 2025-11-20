#!/bin/bash

echo "🚀 CKA 시뮬레이터 풀스택 시작..."

# Docker Compose로 전체 스택 시작
docker-compose up -d

echo ""
echo "✅ 서비스 시작 완료!"
echo ""
echo "📊 접속 정보:"
echo "  - 백엔드 API: http://localhost:8000"
echo "  - API 문서: http://localhost:8000/docs"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3001"
echo "    (기본 로그인: admin/admin)"
echo ""
echo "React 프론트엔드 시작:"
echo "  cd web/react-frontend"
echo "  npm install"
echo "  npm run dev"
echo ""
echo "종료: docker-compose down"
