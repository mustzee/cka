# 사용 가이드

## 📋 목차

1. [시작하기](#시작하기)
2. [시험 준비](#시험-준비)
3. [시험 진행](#시험-진행)
4. [채점 및 결과](#채점-및-결과)
5. [문제 타입 설명](#문제-타입-설명)
6. [팁과 트릭](#팁과-트릭)
7. [문제 해결](#문제-해결)

## 시작하기

### 1단계: 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd cka

# 의존성 설치 및 환경 설정
./scripts/setup.sh
```

이 스크립트는 자동으로:
- Docker, kubectl, kind 설치 확인
- Python 패키지 설치
- 필요한 디렉토리 생성

### 2단계: 클러스터 생성

```bash
# Kubernetes 클러스터 생성 (약 2-3분 소요)
./scripts/create-cluster.sh
```

클러스터 구성:
- Control Plane 노드 1개
- Worker 노드 2개
- Kubernetes 버전: 1.28

### 3단계: 클러스터 확인

```bash
# 노드 확인
kubectl get nodes

# 출력 예시:
# NAME                          STATUS   ROLES           AGE   VERSION
# cka-simulator-control-plane   Ready    control-plane   2m    v1.28.0
# cka-simulator-worker          Ready    <none>          2m    v1.28.0
# cka-simulator-worker2         Ready    <none>          2m    v1.28.0
```

## 시험 준비

### kubectl 자동 완성 설정 (선택사항)

```bash
# Bash
source <(kubectl completion bash)
echo "source <(kubectl completion bash)" >> ~/.bashrc
alias k=kubectl
complete -o default -F __start_kubectl k

# Zsh
source <(kubectl completion zsh)
echo "source <(kubectl completion zsh)" >> ~/.zshrc
```

### 유용한 kubectl 별칭

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgn='kubectl get nodes'
alias kdp='kubectl describe pod'
alias kds='kubectl describe svc'
```

### 문서 북마크

CKA 시험에서 공식 문서 참조가 허용됩니다. 다음 페이지를 숙지하세요:

- https://kubernetes.io/docs/
- https://kubernetes.io/docs/reference/kubectl/cheatsheet/

## 시험 진행

### 시험 시작

```bash
# 기본 타입 A로 시작 (실전 모드, 2시간)
python3 simulator/main.py --type A

# 연습 모드 (타이머 없음)
python3 simulator/main.py --type A --practice

# 고급 타입 B
python3 simulator/main.py --type B

# 실전 타입 C
python3 simulator/main.py --type C
```

### 시험 화면 안내

시험 시작 후:
1. 문제 목록이 표시됩니다
2. 각 문제의 제목, 도메인, 난이도, 배점을 확인할 수 있습니다
3. 현재 문제가 화면에 표시됩니다

### 문제 해결 방법

1. **문제 읽기**: 요구사항을 정확히 파악하세요
2. **별도 터미널**: 다른 터미널을 열어 kubectl 명령어를 실행하세요
3. **Context 확인**: 각 문제는 특정 context를 사용합니다
4. **작업 수행**: kubectl을 사용하여 요구사항을 구현하세요
5. **검증**: 생성한 리소스가 정상 작동하는지 확인하세요

### 시험 중 명령어

시뮬레이터에서 사용 가능한 명령어:

- `next`: 다음 문제로 이동
- `prev`: 이전 문제로 이동
- `list`: 전체 문제 목록 보기
- `skip`: 현재 문제 건너뛰기
- `finish`: 시험 종료 및 채점
- `quit`: 시험 중단 (채점 안 됨)

### 터미널 분할 권장

```
┌─────────────────────────────────────────┐
│  터미널 1: 시뮬레이터                   │
│  - 문제 확인                            │
│  - 진행 상황 관리                       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  터미널 2: kubectl 작업                 │
│  - 리소스 생성/수정/삭제                │
│  - 문제 해결                            │
└─────────────────────────────────────────┘
```

## 채점 및 결과

### 자동 채점

시험 종료 시 자동으로 채점이 진행됩니다:

1. **리소스 존재 확인**: 요구된 리소스가 생성되었는지
2. **설정 검증**: 리소스의 설정이 정확한지
3. **상태 확인**: Pod가 Running 상태인지 등

### 결과 파일

채점 완료 후 다음 파일이 생성됩니다:

#### 1. 점수 리포트 (JSON)
`results/score_report_YYYYMMDD_HHMMSS.json`

```json
{
  "exam_info": {
    "type": "A",
    "start_time": "2025-01-15T10:00:00",
    "elapsed_time": "01:45:23"
  },
  "grade": {
    "total_score": 75.5,
    "total_weight": 100,
    "percentage": 75.5,
    "passed": true
  }
}
```

#### 2. 오답노트 (Markdown)
`results/wrong_answers_YYYYMMDD_HHMMSS.md`

포함 내용:
- 오답 문제 상세
- 정답 및 해설
- 참고 자료 링크
- 학습 제안

### 합격 기준

- **합격 점수**: 66% 이상
- **실제 CKA 시험**: 66% 이상 (동일)

## 문제 타입 설명

### Type A - 기본 (난이도: ⭐⭐)

**특징:**
- 표준 CKA 시험 문제
- 모든 도메인 균등 분포
- 기본적인 Kubernetes 개념

**적합한 대상:**
- CKA 시험 준비 초보자
- Kubernetes 기본 개념 학습자

**주요 도메인:**
- Deployment, Service 생성
- ConfigMap, Secret 관리
- 기본 RBAC 구성
- Pod 트러블슈팅

### Type B - 고급 (난이도: ⭐⭐⭐)

**특징:**
- Troubleshooting 및 복잡한 시나리오 중점
- 실무 경험 필요
- 난이도 상승

**적합한 대상:**
- 중급 이상 Kubernetes 사용자
- 실무 경험이 있는 엔지니어

**주요 도메인:**
- ETCD 백업/복구
- Network Policy 구성
- 노드 유지보수
- Ingress 설정

### Type C - 실전 (난이도: ⭐⭐⭐⭐)

**특징:**
- 실제 프로덕션 시나리오 기반
- 복합적인 문제 해결
- 종합적인 지식 필요

**적합한 대상:**
- CKA 시험 직전 최종 점검
- 실무 능력 검증

**주요 도메인:**
- 프로덕션 애플리케이션 배포
- StatefulSet 구성
- 고가용성 설정
- 종합 시나리오

## 팁과 트릭

### kubectl 효율적 사용

```bash
# 1. 선언적 vs 명령적
# 명령적 (빠름)
kubectl create deployment nginx --image=nginx --replicas=3

# 선언적 (정확함)
kubectl apply -f deployment.yaml

# 2. 드라이런으로 YAML 생성
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deploy.yaml

# 3. explain으로 필드 확인
kubectl explain pod.spec.containers

# 4. jsonpath로 특정 값 추출
kubectl get pods -o jsonpath='{.items[*].metadata.name}'
```

### 시간 관리

- **쉬운 문제 먼저**: 높은 점수를 빨리 확보
- **시간 제한**: 문제당 예상 시간 참고
- **건너뛰기**: 막히면 일단 넘어가기
- **검증 시간**: 마지막 10-15분은 검증용

### 실수 방지

1. **네임스페이스 확인**: `-n` 옵션 빼먹지 않기
2. **레이블 정확히**: 오타 주의
3. **YAML 들여쓰기**: 공백 2칸 사용
4. **검증 필수**: 생성 후 반드시 확인

### 유용한 명령어 모음

```bash
# Pod 로그 확인
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> --previous  # 이전 컨테이너

# 리소스 상세 정보
kubectl describe pod <pod-name>

# 실행 중인 Pod에 명령 실행
kubectl exec -it <pod-name> -- /bin/bash

# 리소스 편집
kubectl edit deployment <name>

# 리소스 삭제
kubectl delete pod <pod-name> --force --grace-period=0

# 이벤트 확인
kubectl get events --sort-by=.metadata.creationTimestamp

# 리소스 사용량
kubectl top nodes
kubectl top pods
```

## 문제 해결

### 클러스터가 생성되지 않음

```bash
# Docker 상태 확인
sudo systemctl status docker

# kind 재설치
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# 클러스터 삭제 후 재생성
kind delete cluster --name cka-simulator
./scripts/create-cluster.sh
```

### kubectl 명령어가 작동하지 않음

```bash
# kubeconfig 확인
kubectl config view
kubectl config current-context

# context 설정
kubectl config use-context kind-cka-simulator
```

### Pod가 Pending 상태

```bash
# 이벤트 확인
kubectl describe pod <pod-name>

# 노드 리소스 확인
kubectl top nodes
kubectl describe node <node-name>
```

### 시뮬레이터 오류

```bash
# Python 패키지 재설치
pip3 install -r requirements.txt --force-reinstall

# 권한 확인
chmod +x simulator/main.py
chmod +x scripts/*.sh
```

### 클러스터 초기화

```bash
# 클러스터 삭제
./scripts/cleanup.sh

# 새로 생성
./scripts/create-cluster.sh
```

## 추가 학습 자료

### 공식 문서
- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [CKA 시험 가이드](https://www.cncf.io/certification/cka/)

### 실습 환경
- [Kubernetes Playground](https://labs.play-with-k8s.com/)
- [Katacoda Kubernetes](https://www.katacoda.com/courses/kubernetes)

### 커뮤니티
- [Kubernetes Slack](https://kubernetes.slack.com/)
- [Reddit r/kubernetes](https://www.reddit.com/r/kubernetes/)

---

**행운을 빕니다! 🚀**

문제가 있거나 피드백이 있으시면 이슈를 등록해주세요.
