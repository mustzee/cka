# Kubernetes CKA 학습 도구 & 실습 환경

CKA (Certified Kubernetes Administrator) 시험 준비를 위한 실전 중심 학습 도구입니다.

## ⚠️ 이 프로젝트는 무엇인가요?

✅ **Kubernetes 학습 도구** - CKA 개념과 명령어를 실습으로 배웁니다
✅ **CKA 개념 학습용** - 31개의 실전 문제로 핵심 개념 마스터 (고급 트러블슈팅 3개 포함)
✅ **멀티 클러스터 환경** - 실제 CKA처럼 6개 클러스터 전환 연습
✅ **💀 Ultra Mode** - Chaos Engineering으로 실전 장애 대응 연습 (NEW!)
❌ **CKA 시험 최종 준비 도구 아님** - Killer.sh 같은 실전 시뮬레이터 권장

### 💡 CKA 합격 로드맵

```
1단계 (1-2주) ► 이 시뮬레이터로 Kubernetes 개념 학습
                - 힌트 모드로 기초 다지기
                - Hard 모드로 실전 감각 익히기
                - 멀티 클러스터 환경에 익숙해지기

2단계 (2-3주) ► KodeKloud 또는 Linux Foundation 강의
                - 체계적인 커리큘럼
                - 상세한 실습 랩

2.5단계 (시험 2주 전) ► 💀 Ultra Mode 도전! (NEW!)
                        - Chaos Engineering으로 실전 대비
                        - 무작위 장애 대응 능력 향상
                        - 고급 트러블슈팅 마스터

3단계 (시험 1주일 전) ► Killer.sh 최종 점검 ($36)
                      - 실제 시험과 99% 동일한 환경
                      - 최종 실력 검증
```

## 🎯 주요 기능

### 핵심 기능
- ✅ **멀티 클러스터 지원** (NEW! 🔥): 실제 CKA처럼 6개 클러스터 전환 연습
- ✅ **힌트 모드**: 학습용 힌트 표시/숨김 선택 가능
- ✅ **Hard 모드**: 힌트 완전 제거, 실전 난이도
- ✅ **💀 Ultra 모드** (NEW! 🔥): Chaos Engineering + 무작위 장애 주입 + 실전 트러블슈팅
- ✅ **🔄 시험 환경 리셋** (NEW! 🔥): 빠른 환경 초기화 (5-10초)
- ✅ **31개 실전 문제**: CKA 도메인 비중에 맞춘 문제 구성 (고급 트러블슈팅 3개 포함)
- ✅ **2시간 타이머**: 실제 시험과 동일한 시간 제한
- ✅ **자동 채점 시스템**: 리소스 검증, 상태 확인, 필드 값 검증
- ✅ **Context 검증**: 올바른 클러스터에서 작업했는지 확인
- ✅ **오답노트 생성**: 상세 해설 및 참고 자료 포함

### 고급 기능
- ✅ **명령어 출력 검증**: 실행 결과 자동 확인
- ✅ **JQ 필터 지원**: JSON 데이터 정밀 검증
- ✅ **커스텀 스크립트**: 복잡한 시나리오 검증
- ✅ **웹 UI**: 브라우저 기반 시험 진행
- ✅ **FastAPI 백엔드**: RESTful API 제공
- ✅ **통계 및 분석**: 진행률 추적, 약점 분석, 도메인별 통계

## 💪 실전 CKA 대비 장점

| 기능 | 이 시뮬레이터 | Killer.sh | 차이점 |
|------|------------|-----------|-------|
| 멀티 클러스터 | ✅ 6개 | ✅ 6개 | 동일 |
| Context 전환 | ✅ 필수 | ✅ 필수 | 동일 |
| 힌트 제거 | ✅ Hard 모드 | ✅ 기본 | 학습/실전 선택 가능 |
| 문제 품질 | ⚠️ 학습용 | ✅ 실전급 | 이 도구는 개념 학습용 |
| 환경 유사도 | ⚠️ 60% | ✅ 99% | Kind/k3d vs 실제 클러스터 |
| 가격 | ✅ 무료 | $36 | - |

## 시스템 요구사항

- Docker 20.10+
- kubectl 1.28+
- k3d (권장) 또는 kind
- Python 3.9+
- (선택) Node.js 16+ (웹 UI 사용 시)

## 빠른 시작

### 1. 멀티 클러스터 환경 생성 (실제 CKA처럼!)

```bash
# k3d 설치 (M2 Mac에서 더 안정적)
brew install k3d  # macOS
# 또는: curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# 6개 클러스터 생성 (cluster1~6)
./scripts/create-multi-cluster.sh

# 클러스터 확인
kubectl config get-contexts
# cluster1, cluster2, cluster3, cluster4, cluster5, cluster6 확인
```

### 2. 시뮬레이터 시작

#### 기본 모드 (힌트 숨김)
```bash
python3 simulator/main.py --type A

# 실전처럼 힌트 없이 연습
# Context 전환 필수!
```

#### 학습 모드 (힌트 표시)
```bash
python3 simulator/main.py --type A --hints

# 힌트를 보면서 개념 학습
```

#### 🔥 Hard 모드 (실전 난이도)
```bash
python3 simulator/main.py --type A --hard

# 힌트 완전 제거
# Context 검증 강화
# 실제 CKA처럼 연습
```

#### 💀 Ultra 모드 (최고 난이도 - Chaos Engineering)
```bash
python3 simulator/main.py --type A --ultra

# 🔥 Chaos Engineering 활성화
# 시험 중 무작위 장애 발생 (2-4회)
#   - 노드 리소스 압박 (메모리 부족)
#   - 무작위 Pod 삭제
#   - DNS 장애 (CoreDNS 재시작)
#   - 네트워크 지연
# 힌트 완전 제거
# 실전 트러블슈팅 능력 극한 테스트
# Killer.sh 수준의 난이도
```

#### 연습 모드 (타이머 없음)
```bash
python3 simulator/main.py --practice

# 시간 제한 없이 충분히 연습
```

### 3. 시험 진행

실제 CKA처럼 문제마다 Context 전환 필수!

```bash
# 문제에서 요구하는 클러스터로 전환
kubectl config use-context cluster1  # 또는 cluster2, cluster3...

# 현재 context 확인
kubectl config current-context

# ⚠️ Context 전환을 잊으면 0점 처리!
```

### 4. 시험 환경 리셋 (NEW! 🔄)

시험을 다시 시작하고 싶을 때:

```bash
# 대화형 리셋 (확인 질문 있음)
python3 simulator/main.py --reset

# 자동 리셋 (확인 질문 생략)  
python3 simulator/main.py --reset --yes

# 또는 스크립트 직접 실행
./scripts/reset-exam.sh
```

**리셋 대상:**
- ✅ 모든 시험 관련 네임스페이스 (production, staging, dev-team 등)
- ✅ 기본 네임스페이스의 시험 리소스
- ✅ 클러스터 레벨 리소스 (PV, ClusterRole 등)
- ✅ Node taints 제거  
- ✅ 시험 결과 파일 정리

**장점:**
- ⚡ 빠른 정리 (5-10초)
- 🛡️ 안전한 삭제 (시스템 리소스 보존)
- 🚫 클러스터 재생성 불필요

### 5. 결과 확인

시험 완료 후 자동으로 생성되는 리포트:
- `results/score_report.json` - 점수 리포트 (Context 오류 횟수 포함)
- `results/wrong_answers.md` - 오답노트 (해설 포함)

## 📁 프로젝트 구조

```
cka/
├── simulator/              # CLI 시뮬레이터
│   ├── main.py            # 메인 실행 파일 (힌트 모드, Hard 모드 지원)
│   ├── question_loader.py # 문제 로더
│   ├── grader.py          # 기본 채점
│   ├── grader_advanced.py # 고급 채점
│   ├── timer.py           # 타이머
│   └── report_generator.py# 리포트 생성
├── web/                   # 웹 인터페이스
│   ├── backend/
│   │   ├── app.py        # FastAPI 서버
│   │   └── database.py   # SQLite DB
│   └── frontend/
│       ├── index.html    # 웹 UI
│       └── app.js        # JavaScript
├── questions/            # 시험 문제 데이터베이스
│   └── type_a/          # A 타입 (28개) - 각 문제에 context 필드 포함
├── cluster/             # Kubernetes 클러스터 설정
│   └── kind-config.yaml
├── scripts/             # 유틸리티 스크립트
│   ├── setup.sh
│   ├── create-cluster.sh        # 단일 클러스터 (구버전)
│   ├── create-multi-cluster.sh  # 멀티 클러스터 (NEW!)
│   ├── create-cluster-k3d.sh   # k3d 단일 클러스터
│   ├── reset-exam.sh           # 시험 환경 리셋 (NEW!)
│   └── cleanup.sh              # 전체 클러스터 삭제
├── docs/                # 문서
│   ├── USAGE_GUIDE.md
│   ├── TROUBLESHOOTING_M2.md   # M2 Mac 호환성 가이드
│   └── CONTRIBUTING.md
└── results/             # 시험 결과 저장
```

## 📚 문제 구성 (Type A - 31문제)

### 도메인별 비중

| 도메인 | 현재 비중 | CKA 목표 | 상태 |
|--------|----------|---------|------|
| **Troubleshooting** | 36.4% | 30% | ✅ 달성 |
| **Storage** | 9.7% | 10% | ✅ 달성 |
| **Cluster Architecture** | 20.0% | 25% | ⚠️ 약간 부족 |
| **Workloads & Scheduling** | 22.4% | 15% | ⚠️ 약간 높음 |
| **Services & Networking** | 11.5% | 20% | ⚠️ 약간 부족 |

### 문제 난이도 분포
- Easy: 7문제 (23%)
- Medium: 14문제 (45%)
- Hard: 10문제 (32%) - **3개 고급 트러블슈팅 문제 추가!**

### 멀티 클러스터 분포
- cluster1: 5문제
- cluster2: 5문제
- cluster3: 6문제 - **Node 장애 복구 추가**
- cluster4: 7문제 - **CNI 네트워크 트러블슈팅 추가**
- cluster5: 5문제 - **Control Plane 장애 복구 추가**
- cluster6: 3문제

### 🔥 신규 고급 트러블슈팅 문제 (Ultra Mode용)
1. **A029**: Node NotReady 상태 복구 (Hard, 10점)
2. **A030**: CNI 네트워크 플러그인 장애 (Hard, 10점)
3. **A031**: Control Plane 장애 복구 (Hard, 12점)

## 🎓 학습 모드 설명

### 1. 힌트 표시 모드 (`--hints`)
```bash
python3 simulator/main.py --type A --hints
```
- 💡 각 문제에 힌트 표시
- 개념을 처음 배울 때 사용
- kubectl 명령어 패턴 힌트 제공

### 2. 기본 모드 (힌트 숨김)
```bash
python3 simulator/main.py --type A
```
- 힌트 숨김 (힌트가 있다는 것만 알림)
- 스스로 생각하며 풀기
- 실전 준비 1단계

### 3. 🔥 Hard 모드 (`--hard`)
```bash
python3 simulator/main.py --type A --hard
```
- 힌트 완전 제거
- Context 검증 강화
- 실제 CKA 시험과 가장 유사
- 실전 준비 최종 단계

### 4. 💀 Ultra 모드 (`--ultra`) - NEW!
```bash
python3 simulator/main.py --type A --ultra
```
- **Chaos Engineering 활성화**: 시험 중 무작위 장애 발생 (2-4회)
- **실전 트러블슈팅**: 실제 장애 상황 대응 능력 평가
- **장애 유형**:
  - 노드 리소스 압박 (메모리 부족)
  - 무작위 Pod 강제 삭제
  - DNS 서비스 장애 (CoreDNS 재시작)
  - 네트워크 지연 주입
- **힌트 완전 제거**
- **고난도 문제 포함**: Node 장애, CNI 문제, Control Plane 복구
- **Killer.sh 수준**: 가장 실전에 가까운 연습
- **권장 시점**: CKA 시험 1-2주 전, 기본기 완성 후

## 🚀 CKA 시험 준비 팁

### 이 시뮬레이터로 할 것:
1. ✅ kubectl 명령어 숙련도 향상
2. ✅ Kubernetes 핵심 개념 이해
3. ✅ 멀티 클러스터 전환에 익숙해지기
4. ✅ 시간 관리 연습 (2시간 안에 모든 문제 풀기)
5. ✅ 자주 쓰는 명령어 패턴 암기
6. ✅ **Ultra Mode로 실전 트러블슈팅 연습** (시험 1-2주 전)

### 실제 시험 전 반드시 할 것:
1. 🔥 **Killer.sh 구매** ($36) - 시험 1주일 전
2. 🔥 **실제 kubeadm 클러스터 구축** - Kind/k3d와 다름
3. 🔥 **실제 네트워킹 환경** - AWS/GKE 등 클라우드 환경
4. 🔥 **kubectl 문서 검색 연습** - 시험 중 공식 문서 참조 가능

## ⚠️ 제한 사항 (정직하게 말하자면...)

### 이 시뮬레이터의 한계:
- ❌ Kind/k3d는 실제 클러스터와 다름 (컨테이너 기반)
- ❌ kubeadm 구축/업그레이드는 제한적
- ❌ kubelet 디버깅은 실제 환경과 차이
- ❌ 네트워킹이 단순함 (Docker bridge vs 실제 CNI)
- ❌ 자동 채점은 일부 답안만 검증 (완벽하지 않음)

### 실전 CKA 시험과 다른 점:
- 실제 시험: Killer.sh와 거의 동일한 PSI 브라우저 환경
- 실제 시험: kubeadm으로 구축된 멀티 노드 클러스터
- 실제 시험: 복잡한 네트워킹 시나리오
- 실제 시험: systemd, journalctl 등 실제 Linux 환경

## 💰 비용 효율적인 CKA 합격 전략

```
1. 이 시뮬레이터 (무료)
   └─> Kubernetes 기초 학습 (1-2주)

2. KodeKloud CKA 강의 ($20-30)
   └─> 체계적 학습 (2-3주)

3. Killer.sh ($36, CKA 시험 등록 시 포함)
   └─> 최종 검증 (시험 1주일 전)

4. CKA 시험 ($395)
   └─> 합격! 🎉

총 비용: ~$450 (재시험 없이 합격 시)
재시험 비용: $395 (피하려면 Killer.sh 필수!)
```

## 🔧 고급 사용법

### 문제 목록만 보기
```bash
python3 simulator/main.py --list-only

# 클러스터 없이도 문제 확인 가능
```

### 시험 환경 리셋
```bash
# 대화형 리셋
python3 simulator/main.py --reset

# 자동 리셋 (확인 생략)
python3 simulator/main.py --reset --yes

# 리셋 + 새로운 시험 시작을 한 번에
python3 simulator/main.py --reset --yes && python3 simulator/main.py --type A --ultra
```

### 비대화형 모드
```bash
python3 simulator/main.py --yes

# CI/CD 파이프라인에서 사용 가능
```

### 웹 UI 모드
```bash
./scripts/start-web.sh

# 브라우저에서 http://localhost:8000/docs 접속
```

## 🐛 트러블슈팅

### M2 Mac 사용자
- [TROUBLESHOOTING_M2.md](docs/TROUBLESHOOTING_M2.md) 참조
- k3d 사용 권장 (Kind보다 안정적)

### 시험 환경 문제
```bash
# 시험 리소스만 정리 (권장)
python3 simulator/main.py --reset --yes

# 전체 클러스터 재생성 (문제 지속 시)
k3d cluster delete cluster1 cluster2 cluster3 cluster4 cluster5 cluster6
./scripts/create-multi-cluster.sh
```

### Python 의존성 문제
```bash
pip3 install -r requirements.txt
```

## 📖 추가 리소스

- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [CKA 시험 가이드](https://www.cncf.io/certification/cka/)
- [Killer.sh](https://killer.sh/) - 최종 검증 필수!
- [KodeKloud CKA 강의](https://kodekloud.com/courses/certified-kubernetes-administrator-cka/)

## 🤝 기여하기

이슈 제보, 문제 추가, 개선 제안 환영합니다!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이센스

MIT License

## 🙏 감사의 말

이 프로젝트는 CKA 준비생들의 학습을 돕기 위해 만들어졌습니다.
**완벽한 시험 시뮬레이터가 아니라 학습 도구**로 사용해주세요.

실제 시험 준비는 반드시 **Killer.sh**로 마무리하시기 바랍니다!

Good luck on your CKA journey! 🚀
