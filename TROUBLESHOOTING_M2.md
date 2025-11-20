# M2 Mac 트러블슈팅 가이드

## 문제 1: Kind 클러스터 생성 실패 (kubelet 시작 실패)

### 증상
```
[kubelet-check] It seems like the kubelet isn't running or healthy.
ERROR: failed to create cluster: failed to init node with kubeadm
```

### 원인
- Apple Silicon (ARM64) 아키텍처에서 cgroup 설정 문제
- systemd cgroup 드라이버 미설정

### 해결 방법

#### ⭐ 방법 1: k3d 사용 (가장 권장!)
```bash
# k3d 설치 (Homebrew 사용)
brew install k3d

# 클러스터 생성 (30초 내 완료!)
./scripts/create-cluster-k3d.sh
```

**k3d 장점:**
- ⚡ **매우 빠름**: Kind 2-3분 → k3d 30초
- 💻 **가벼움**: 메모리 사용량 50% 감소
- 🍎 **M2 Mac 최적화**: kubelet 문제 없음
- ✅ **안정적**: cgroup 충돌 없음

**k3d 단점:**
- ⚠️ 일부 CKA 기능 제한 (etcd snapshot 등)

#### 방법 2: 클러스터 없이 문제 학습
```bash
# 문제 목록만 보기 (클러스터 불필요!)
python3 simulator/main.py --type A --list-only

# 모든 문제 상세 내용 출력
python3 simulator/main.py --type A -l > questions_typeA.txt
```

#### 방법 3: 업데이트된 Kind 설정 사용
```bash
# 기존 클러스터 삭제 (있다면)
kind delete cluster --name cka-simulator

# 업데이트된 설정으로 재생성
./scripts/create-cluster.sh
```

업데이트된 `cluster/kind-config.yaml`에는 다음 사항이 포함되어 있습니다:
- ✅ systemd cgroup 드라이버 설정
- ✅ containerd systemd cgroup 활성화
- ✅ ARM64 호환 이미지 SHA 명시

#### 방법 4: 간소화된 Kind 클러스터
```bash
# 단일 노드 클러스터 (control-plane만)
./scripts/create-cluster-simple.sh
```

장점:
- ⚡ 빠른 시작 (약 1분)
- 💻 낮은 리소스 사용
- ✅ 대부분의 CKA 문제 연습 가능

단점:
- ❌ 멀티 노드 관련 문제 연습 제한 (Node Affinity, Taints 등)
- ⚠️ M2 Mac에서 여전히 kubelet 문제 발생 가능

## 문제 2: Docker Desktop 미실행

### 증상
```
Cannot connect to the Docker daemon at unix:///Users/.../.docker/run/docker.sock
```

### 해결 방법
1. Docker Desktop 실행
2. Docker가 완전히 시작될 때까지 대기 (상단 바 아이콘 확인)
3. 터미널에서 확인:
```bash
docker ps
```

## 문제 3: YAML 파싱 오류

### 증상
```
문제 로드 실패: while parsing a block collection
expected <block end>, but found '<scalar>'
```

### 해결 방법
이미 수정되었습니다! 최신 코드를 사용하세요:
```bash
git pull origin claude/kubernetes-cka-simulator-013GwqESTvKa7XKSicghN6J3
```

## 문제 4: 리소스 부족 (메모리/CPU)

### 증상
- 클러스터 생성이 매우 느림
- 노드가 NotReady 상태

### 해결 방법

#### Docker Desktop 리소스 증가
1. Docker Desktop 설정 열기
2. Resources → Advanced
3. 권장 설정:
   - **CPU**: 4 cores 이상
   - **Memory**: 8 GB 이상
   - **Swap**: 2 GB
   - **Disk**: 60 GB

#### 간소화된 클러스터 사용
```bash
./scripts/create-cluster-simple.sh
```

## 문제 5: Kind 설치 확인

### Kind 버전 확인
```bash
kind version
```

### Kind 재설치 (필요시)
```bash
# Homebrew 사용
brew install kind

# 또는 직접 다운로드
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-darwin-arm64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### kubectl 설치 확인
```bash
kubectl version --client
```

### kubectl 설치 (필요시)
```bash
brew install kubectl
```

## 유용한 명령어

### 클러스터 상태 확인
```bash
# 클러스터 목록
kind get clusters

# 노드 상태
kubectl get nodes -o wide

# 시스템 Pod 확인
kubectl get pods -n kube-system

# 클러스터 정보
kubectl cluster-info
```

### 클러스터 초기화
```bash
# 완전 삭제 후 재생성
kind delete cluster --name cka-simulator
./scripts/create-cluster.sh
```

### 로그 확인
```bash
# Docker 컨테이너 확인
docker ps -a | grep cka-simulator

# Control plane 로그
docker logs cka-simulator-control-plane

# Kubelet 로그 (컨테이너 내부)
docker exec cka-simulator-control-plane journalctl -u kubelet
```

## 권장 워크플로우

### M2 Mac 사용자 추천 순서 (업데이트)

#### 최고의 방법 ⭐ (k3d 사용)

1. **Docker Desktop 실행 확인**
```bash
docker ps
```

2. **k3d 설치 (한 번만)**
```bash
brew install k3d
```

3. **k3d 클러스터 생성 (30초!)**
```bash
./scripts/create-cluster-k3d.sh
```

4. **시뮬레이터 테스트**
```bash
# 문제 목록만 먼저 보기
python3 simulator/main.py --type A --list-only

# 실제 시험 모드 (자동 진행)
python3 simulator/main.py --type A --yes
```

#### 대안: 클러스터 없이 학습

클러스터 생성이 계속 실패한다면:

1. **문제만 학습**
```bash
# Type A 문제 모두 보기
python3 simulator/main.py --type A --list-only

# 파일로 저장하여 나중에 읽기
python3 simulator/main.py --type A -l > cka_questions_A.txt
python3 simulator/main.py --type B -l > cka_questions_B.txt
python3 simulator/main.py --type C -l > cka_questions_C.txt
```

2. **웹 UI 사용**
```bash
# React 프론트엔드 실행
cd web/react-frontend
npm install
npm run dev

# 브라우저에서 http://localhost:3000 접속
```

#### 마지막 수단: Kind 재시도

1. **Docker 완전 정리**
```bash
docker system prune -a -f
docker volume prune -f
```

2. **간소화된 클러스터로 시작**
```bash
./scripts/create-cluster-simple.sh
```

3. **실패 시 전체 시스템 재부팅 후 재시도**

## 추가 도움

문제가 지속되면:
1. Docker Desktop 재시작
2. 시스템 재부팅
3. Kind 버전 업데이트
4. GitHub Issues에 보고

---

## 새로운 기능 (2024년 11월)

### Python 시뮬레이터 개선

**문제 목록만 보기 (클러스터 불필요!)**
```bash
python3 simulator/main.py --type A --list-only
python3 simulator/main.py -t B -l
```

**비대화형 모드 (자동 진행)**
```bash
python3 simulator/main.py --type A --yes
python3 simulator/main.py -t B -y --practice
```

**옵션 조합**
```bash
# 문제 목록을 파일로 저장
python3 simulator/main.py -t A -l > typeA.txt

# 연습 모드 + 자동 진행
python3 simulator/main.py -t B -p -y
```

---

**참고**: M2 Mac에서 **가장 안정적인 방법**은 **k3d**를 사용하는 것입니다!
