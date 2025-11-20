# 🚀 Kubernetes CKA 시험 시뮬레이터 v2.0

**프로덕션급 CKA (Certified Kubernetes Administrator) 시험 완벽 대비 플랫폼**

## ⭐ 주요 특징

### 핵심 기능
- ✅ **실제 CKA 시험 환경**: kind 기반 Kubernetes 1.28 클러스터
- ✅ **22개 이상의 실전 문제**: A/B/C 타입별 5개 세트 (총 110+ 문제)
- ✅ **React 프론트엔드**: 현대적이고 반응형 UI/UX
- ✅ **자동 채점 시스템**: 리소스 검증, 상태 확인, 고급 검증
- ✅ **오답노트 및 해설**: 상세한 문제 해설 및 참고 자료

### 🆕 v2.0 신규 기능
- 🌐 **React + Tailwind CSS**: 아름다운 glassmorphism 디자인
- ⚡ **WebSocket 실시간 업데이트**: 시험 진행 상황 실시간 동기화
- 📜 **PDF 리포트 자동 생성**: ReportLab 기반 전문적인 리포트
- 🏆 **자동 인증서 발급**: QR 코드 포함 합격 인증서
- 📊 **Prometheus + Grafana**: 실시간 모니터링 및 메트릭
- 🔄 **문제 세트 시스템**: 타입당 5개 세트 (반복 학습 가능)
- 🎯 **고급 채점 기능**: JQ 필터, 커스텀 스크립트, 명령어 출력 검증

## 🎨 스크린샷

```
┌─────────────────────────────────────────┐
│  홈: 타입 선택 & 세트 선택              │
│  ↓                                       │
│  시험 진행: 실시간 타이머 & 문제 표시   │
│  ↓                                       │
│  결과: 점수, 통계, PDF 다운로드          │
│  ↓                                       │
│  인증서: 합격 시 자동 발급              │
└─────────────────────────────────────────┘
```

## 📦 시스템 요구사항

### 필수
- **Docker** 20.10+
- **kubectl** 1.28+
- **kind** (Kubernetes in Docker)
- **Python** 3.9+
- **Node.js** 18+ (React 프론트엔드용)

### 선택 (모니터링)
- **Docker Compose** 2.0+
- **Prometheus** (포함)
- **Grafana** (포함)

## 🚀 빠른 시작

### 방법 1: Docker Compose (권장)

```bash
# 전체 스택 시작 (백엔드 + Prometheus + Grafana)
./scripts/start-stack.sh

# React 프론트엔드 시작 (별도 터미널)
cd web/react-frontend
npm install
npm run dev
```

**접속:**
- React UI: http://localhost:3000
- API 문서: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

### 방법 2: 수동 설치

```bash
# 1. 환경 설정
./scripts/setup.sh

# 2. Kubernetes 클러스터 생성
./scripts/create-cluster.sh

# 3. 백엔드 시작
pip3 install -r requirements.txt
cd web/backend
python3 -m uvicorn app_enhanced:app --reload

# 4. React 프론트엔드 시작
cd web/react-frontend
npm install
npm run dev
```

### 방법 3: CLI 모드 (기존)

```bash
python3 simulator/main.py --type A --practice
```

## 📚 사용 방법

### 웹 UI (React)

1. **타입 선택**: A (기본), B (고급), C (실전)
2. **세트 선택**: 1-5 중 선택 (각 세트마다 다른 문제)
3. **옵션 설정**: 연습 모드 or 실전 모드 (2시간)
4. **시험 시작**: 문제 확인 및 kubectl로 작업
5. **시험 종료**: 자동 채점 및 결과 확인
6. **리포트 다운로드**: PDF 리포트 & 인증서 (합격 시)

### API 사용

```bash
# 시험 시작
curl -X POST http://localhost:8000/api/exam/start \
  -H "Content-Type: application/json" \
  -d '{"exam_type": "A", "practice_mode": false, "set_number": 1}'

# 채점
curl -X POST http://localhost:8000/api/exam/grade \
  -H "Content-Type: application/json" \
  -d '{"session_id": "...", "questions": [...]}'

# PDF 다운로드
curl http://localhost:8000/api/exam/report/pdf/{session_id} -o report.pdf

# 인증서 다운로드
curl http://localhost:8000/api/exam/certificate/{session_id} -o cert.pdf
```

## 📁 프로젝트 구조

```
cka/
├── web/
│   ├── react-frontend/        # React + Vite + Tailwind
│   │   ├── src/
│   │   │   ├── pages/         # 페이지 컴포넌트
│   │   │   ├── context/       # React Context
│   │   │   └── App.jsx
│   │   └── package.json
│   └── backend/
│       ├── app_enhanced.py    # FastAPI + WebSocket
│       ├── database.py        # SQLAlchemy ORM
│       └── pdf_generator.py   # PDF/인증서 생성
├── simulator/
│   ├── main.py                # CLI 버전
│   ├── grader.py              # 기본 채점
│   └── grader_advanced.py     # 고급 채점
├── questions/
│   ├── type_a/
│   │   ├── set1/              # 세트 1 문제
│   │   ├── set2/              # 세트 2 문제
│   │   └── ...
│   ├── type_b/
│   └── type_c/
├── prometheus.yml             # Prometheus 설정
├── docker-compose.yml         # 풀스택 배포
├── Dockerfile.backend         # 백엔드 Docker 이미지
└── grafana/                   # Grafana 대시보드
    ├── dashboards/
    └── datasources/
```

## 🔥 주요 기능 상세

### 1. React 프론트엔드

- **Vite** 기반 빠른 개발 서버
- **Tailwind CSS** 유틸리티 우선 스타일링
- **React Router** SPA 라우팅
- **Recharts** 통계 시각화
- **Lucide React** 아이콘
- **Glassmorphism** 디자인

### 2. WebSocket 실시간 통신

```javascript
// 클라이언트
const ws = new WebSocket(`ws://localhost:8000/ws/${session_id}`)
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // 실시간 업데이트 처리
}
```

### 3. PDF 리포트 생성

- **ReportLab** 사용
- 시험 결과 요약
- 문제별 상세 결과
- 점수 및 합격 여부

### 4. 인증서 발급

- 합격 시 자동 발급
- QR 코드 포함 (검증용)
- PDF 형식
- 고유 인증서 ID

### 5. Prometheus 메트릭

```python
# 수집되는 메트릭
- cka_exam_started_total: 시험 시작 횟수
- cka_exam_completed_total: 시험 완료 횟수
- cka_exam_duration_seconds: 시험 소요 시간
- cka_active_exams: 현재 진행 중인 시험
- cka_exam_score: 점수 분포
```

### 6. 문제 세트 시스템

```
Type A: 5개 세트 × 15문제 = 75문제
Type B: 5개 세트 × 5문제 = 25문제
Type C: 5개 세트 × 2문제 = 10문제
───────────────────────────────────
총 110개 문제 (반복 학습 가능)
```

## 📊 통계 대시보드

- 총 시험 횟수
- 합격/불합격 비율
- 타입별 평균 점수
- 도메인별 성적
- 시간대별 진행률

## 🛠️ 개발

### 프론트엔드 개발

```bash
cd web/react-frontend
npm run dev    # 개발 서버
npm run build  # 프로덕션 빌드
```

### 백엔드 개발

```bash
cd web/backend
uvicorn app_enhanced:app --reload
```

### Docker 빌드

```bash
docker build -f Dockerfile.backend -t cka-simulator:latest .
docker-compose up -d
```

## 🧪 테스트

```bash
# 클러스터 생성
./scripts/create-cluster.sh

# 시험 실행 (연습 모드)
python3 simulator/main.py --type A --practice

# API 테스트
curl http://localhost:8000/health
```

## 📈 모니터링

### Prometheus Queries

```promql
# 시간당 시험 완료 수
rate(cka_exam_completed_total[1h])

# 평균 점수
histogram_quantile(0.5, cka_exam_score)

# 활성 세션
cka_active_exams
```

### Grafana 대시보드

- 실시간 메트릭 시각화
- 알림 설정
- 커스텀 대시보드

## 🎯 CKA 시험 도메인

1. **Cluster Architecture (25%)**: ETCD, RBAC, ServiceAccount
2. **Workloads & Scheduling (15%)**: Deployment, StatefulSet, DaemonSet
3. **Services & Networking (20%)**: Service, Ingress, NetworkPolicy
4. **Storage (10%)**: PV, PVC, StorageClass
5. **Troubleshooting (30%)**: Pod 트러블슈팅, 로그 분석

## 🤝 기여

`docs/CONTRIBUTING.md` 참고

## 📄 라이선스

MIT License

## 🙏 감사

- Kubernetes 커뮤니티
- CKA 시험 준비생 여러분

---

**v2.0 업데이트 하이라이트:**
- ✨ React 프론트엔드
- ⚡ WebSocket 실시간 통신
- 📜 PDF 리포트 & 인증서
- 📊 Prometheus + Grafana
- 🔄 110+ 문제 (5개 세트)

**화이팅!** 🚀 CKA 합격까지 함께합니다!
