# Kubernetes CKA 시험 시뮬레이터

실제 CKA (Certified Kubernetes Administrator) 시험과 동일한 환경을 제공하는 완전한 시뮬레이터입니다.

## 🎯 주요 기능

### 핵심 기능
- ✅ **실제 CKA 시험 환경**: kind 기반 Kubernetes 1.28 클러스터
- ✅ **다양한 문제 타입**: A/B/C 타입별 15개 이상의 실전 문제
- ✅ **2시간 타이머**: 실제 시험과 동일한 시간 제한
- ✅ **자동 채점 시스템**: 리소스 검증, 상태 확인, 필드 값 검증
- ✅ **오답노트 생성**: 상세 해설 및 참고 자료 포함

### 고급 기능 (NEW! 🚀)
- ✅ **명령어 출력 검증**: 실행 결과 자동 확인
- ✅ **JQ 필터 지원**: JSON 데이터 정밀 검증
- ✅ **커스텀 스크립트**: 복잡한 시나리오 검증
- ✅ **웹 UI**: 브라우저 기반 시험 진행
- ✅ **FastAPI 백엔드**: RESTful API 제공
- ✅ **통계 및 분석**: 진행률 추적, 약점 분석, 도메인별 통계

## 시스템 요구사항

- Docker 20.10+
- kubectl 1.28+
- kind (Kubernetes in Docker)
- Python 3.9+

## 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
./scripts/setup.sh

# Kubernetes 클러스터 생성
./scripts/create-cluster.sh
```

### 2. 시뮬레이터 시작

#### CLI 모드 (터미널)

```bash
# 시험 시작 (기본: A 타입)
python3 simulator/main.py --type A

# 특정 타입 선택
python3 simulator/main.py --type B
python3 simulator/main.py --type C

# 연습 모드 (타이머 없음)
python3 simulator/main.py --practice
```

#### 웹 UI 모드 (NEW! 🌐)

```bash
# 웹 서버 시작
./scripts/start-web.sh

# 브라우저로 접속:
# - API: http://localhost:8000
# - API 문서: http://localhost:8000/docs
# - 웹 UI: web/frontend/index.html 파일을 브라우저로 열기
```

### 3. 시험 진행

- 시험 시간: 2시간
- 문제 수: 15-20개
- 합격 점수: 66%
- kubectl 명령어를 사용하여 실제 클러스터에서 작업 수행

### 4. 결과 확인

시험 완료 후 자동으로 생성되는 리포트:
- `results/score_report.json` - 점수 리포트
- `results/wrong_answers.md` - 오답노트 (해설 포함)

## 📁 프로젝트 구조

```
cka/
├── simulator/              # CLI 시뮬레이터
│   ├── main.py            # 메인 실행 파일
│   ├── question_loader.py # 문제 로더
│   ├── grader.py          # 기본 채점
│   ├── grader_advanced.py # 고급 채점 (NEW!)
│   ├── timer.py           # 타이머
│   └── report_generator.py# 리포트 생성
├── web/                   # 웹 인터페이스 (NEW!)
│   ├── backend/
│   │   ├── app.py        # FastAPI 서버
│   │   └── database.py   # SQLite DB
│   └── frontend/
│       ├── index.html    # 웹 UI
│       └── app.js        # JavaScript
├── questions/            # 시험 문제 데이터베이스
│   ├── type_a/          # A 타입 (15개)
│   ├── type_b/          # B 타입 (5개)
│   └── type_c/          # C 타입 (2개)
├── cluster/             # Kubernetes 클러스터 설정
│   └── kind-config.yaml
├── scripts/             # 유틸리티 스크립트
│   ├── setup.sh
│   ├── create-cluster.sh
│   ├── cleanup.sh
│   └── start-web.sh     # 웹 서버 시작 (NEW!)
├── docs/                # 문서
│   ├── USAGE_GUIDE.md
│   └── CONTRIBUTING.md
└── results/             # 시험 결과 저장
    ├── *.json           # 점수 리포트
    ├── *.md             # 오답노트
    └── cka_simulator.db # 통계 DB (NEW!)
```

## 문제 타입

### A 타입 (기본)
- 표준 CKA 시험 문제
- 모든 도메인 균등 분포

### B 타입 (고급)
- Troubleshooting 및 복잡한 시나리오 중점
- 난이도 상승

### C 타입 (실전)
- 실제 프로덕션 시나리오 기반
- 복합적인 문제 해결

## CKA 시험 도메인

1. **Cluster Architecture, Installation & Configuration** (25%)
2. **Workloads & Scheduling** (15%)
3. **Services & Networking** (20%)
4. **Storage** (10%)
5. **Troubleshooting** (30%)

## 라이센스

MIT License
