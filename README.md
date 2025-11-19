# Kubernetes CKA 시험 시뮬레이터

실제 CKA (Certified Kubernetes Administrator) 시험과 동일한 환경을 제공하는 시뮬레이터입니다.

## 주요 기능

- ✅ 실제 CKA 시험과 유사한 Kubernetes 클러스터 환경
- ✅ 시험 문제 유형 A/B/C 타입 변조
- ✅ 2시간 타이머 및 실시간 진행 상황 추적
- ✅ 자동 채점 시스템
- ✅ 시험 완료 후 오답노트 및 해설 제공

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

```bash
# 시험 시작 (기본: A 타입)
python3 simulator/main.py --type A

# 특정 타입 선택
python3 simulator/main.py --type B
python3 simulator/main.py --type C

# 연습 모드 (타이머 없음)
python3 simulator/main.py --practice
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

## 프로젝트 구조

```
cka/
├── simulator/          # 시뮬레이터 메인 애플리케이션
│   ├── main.py        # 메인 실행 파일
│   ├── exam.py        # 시험 관리
│   ├── grader.py      # 자동 채점
│   └── timer.py       # 타이머 관리
├── questions/         # 시험 문제 데이터베이스
│   ├── type_a/       # A 타입 문제
│   ├── type_b/       # B 타입 문제
│   └── type_c/       # C 타입 문제
├── cluster/          # Kubernetes 클러스터 설정
│   └── kind-config.yaml
├── scripts/          # 유틸리티 스크립트
│   ├── setup.sh
│   ├── create-cluster.sh
│   └── cleanup.sh
└── results/          # 시험 결과 저장
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
