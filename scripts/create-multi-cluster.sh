#!/bin/bash
set -e

echo "🎯 CKA 멀티 클러스터 환경 생성 중..."
echo "실제 CKA 시험처럼 6개의 클러스터를 생성합니다."
echo ""

# 사용할 도구 확인
TOOL=""
if command -v k3d &> /dev/null; then
    TOOL="k3d"
    echo "✅ k3d 감지됨 - k3d 사용"
elif command -v kind &> /dev/null; then
    TOOL="kind"
    echo "✅ kind 감지됨 - kind 사용"
else
    echo "❌ k3d 또는 kind가 설치되어 있지 않습니다."
    echo ""
    echo "설치 방법:"
    echo "  macOS: brew install k3d"
    echo "  Linux: curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash"
    echo ""
    echo "또는 kind:"
    echo "  macOS: brew install kind"
    echo "  Linux: curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64 && chmod +x ./kind && sudo mv ./kind /usr/local/bin/"
    exit 1
fi

echo ""

# 클러스터 정의
# 실제 CKA처럼 다양한 구성
declare -A CLUSTERS=(
    ["cluster1"]="control-plane:1,worker:2"  # 일반 클러스터
    ["cluster2"]="control-plane:1,worker:1"  # 작은 클러스터
    ["cluster3"]="control-plane:1,worker:2"  # 일반 클러스터
    ["cluster4"]="control-plane:1,worker:1"  # 작은 클러스터
    ["cluster5"]="control-plane:1,worker:3"  # 큰 클러스터
    ["cluster6"]="control-plane:1,worker:1"  # 작은 클러스터
)

CLUSTER_NAMES=("cluster1" "cluster2" "cluster3" "cluster4" "cluster5" "cluster6")

create_k3d_cluster() {
    local name=$1
    local workers=$2

    echo "📦 k3d 클러스터 생성: $name (workers: $workers)"

    # 포트 범위 할당 (클러스터별로 다른 포트)
    local base_port=$((30000 + $(echo $name | grep -o '[0-9]*') * 100))
    local port_range="${base_port}-$((base_port + 99))"

    k3d cluster create $name \
        --agents $workers \
        --port "${port_range}:${port_range}@loadbalancer" \
        --wait \
        --timeout 120s \
        2>&1 | grep -v "INFO\|WARN" || true

    echo "  ✅ $name 생성 완료"
}

create_kind_cluster() {
    local name=$1
    local workers=$2

    echo "📦 kind 클러스터 생성: $name (workers: $workers)"

    # kind 설정 파일 생성
    cat > /tmp/kind-config-$name.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
EOF

    for ((i=1; i<=workers; i++)); do
        cat >> /tmp/kind-config-$name.yaml <<EOF
- role: worker
EOF
    done

    kind create cluster --name $name --config /tmp/kind-config-$name.yaml --wait 120s
    rm -f /tmp/kind-config-$name.yaml

    echo "  ✅ $name 생성 완료"
}

# 기존 CKA 클러스터 삭제 확인
echo "기존 CKA 클러스터 확인 중..."
EXISTING_CLUSTERS=""
if [ "$TOOL" = "k3d" ]; then
    EXISTING_CLUSTERS=$(k3d cluster list | grep -E "cluster[1-6]" | awk '{print $1}' || true)
else
    EXISTING_CLUSTERS=$(kind get clusters | grep -E "cluster[1-6]" || true)
fi

if [ -n "$EXISTING_CLUSTERS" ]; then
    echo ""
    echo "⚠️  기존 CKA 클러스터가 발견되었습니다:"
    echo "$EXISTING_CLUSTERS"
    echo ""
    read -p "기존 클러스터를 삭제하고 새로 생성하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  기존 클러스터 삭제 중..."
        if [ "$TOOL" = "k3d" ]; then
            echo "$EXISTING_CLUSTERS" | xargs -I {} k3d cluster delete {} 2>/dev/null || true
        else
            echo "$EXISTING_CLUSTERS" | xargs -I {} kind delete cluster --name {} 2>/dev/null || true
        fi
        echo "  ✅ 삭제 완료"
    else
        echo "❌ 취소되었습니다."
        exit 0
    fi
fi

echo ""
echo "🚀 6개 클러스터 생성 시작..."
echo "예상 소요 시간: 3-5분"
echo ""

START_TIME=$(date +%s)

# 클러스터 생성
for cluster_name in "${CLUSTER_NAMES[@]}"; do
    config="${CLUSTERS[$cluster_name]}"
    workers=$(echo $config | grep -o 'worker:[0-9]*' | cut -d: -f2)

    if [ "$TOOL" = "k3d" ]; then
        create_k3d_cluster "$cluster_name" "$workers"
    else
        create_kind_cluster "$cluster_name" "$workers"
    fi

    echo ""
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "✅ 모든 클러스터 생성 완료! (소요 시간: ${DURATION}초)"
echo ""

# Context 이름 변경 (CKA 스타일로)
echo "🔧 Context 이름 변경 중..."
for cluster_name in "${CLUSTER_NAMES[@]}"; do
    if [ "$TOOL" = "k3d" ]; then
        # k3d는 k3d-cluster1 형식으로 생성됨
        kubectl config rename-context "k3d-$cluster_name" "$cluster_name" 2>/dev/null || true
    else
        # kind는 kind-cluster1 형식으로 생성됨
        kubectl config rename-context "kind-$cluster_name" "$cluster_name" 2>/dev/null || true
    fi
done

echo "  ✅ Context 이름 변경 완료"
echo ""

# 모든 클러스터 상태 확인
echo "📊 클러스터 상태 확인..."
echo ""

for cluster_name in "${CLUSTER_NAMES[@]}"; do
    echo "=== $cluster_name ==="
    kubectl config use-context $cluster_name >/dev/null 2>&1

    # 노드 대기
    kubectl wait --for=condition=Ready nodes --all --timeout=60s >/dev/null 2>&1 || true

    kubectl get nodes -o wide 2>/dev/null || echo "  ❌ 노드 확인 실패"
    echo ""
done

# 기본 context 설정
kubectl config use-context cluster1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ CKA 멀티 클러스터 환경 준비 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 사용 가능한 Context:"
kubectl config get-contexts | grep -E "cluster[1-6]|CURRENT"
echo ""
echo "💡 사용 방법:"
echo "  # Context 전환"
echo "  kubectl config use-context cluster1"
echo "  kubectl config use-context cluster2"
echo ""
echo "  # 현재 Context 확인"
echo "  kubectl config current-context"
echo ""
echo "  # 시뮬레이터 실행"
echo "  python3 simulator/main.py --type A"
echo ""
echo "⚠️  주의사항:"
echo "  - 실제 CKA 시험처럼 문제마다 올바른 context로 전환해야 합니다!"
echo "  - context 전환을 잊으면 0점 처리됩니다."
echo "  - kubectl config use-context <cluster-name> 명령어를 반드시 확인하세요."
echo ""
echo "🗑️  클러스터 삭제 방법:"
if [ "$TOOL" = "k3d" ]; then
    echo "  k3d cluster delete cluster1 cluster2 cluster3 cluster4 cluster5 cluster6"
    echo "  또는: k3d cluster delete --all"
else
    echo "  kind delete cluster --name cluster1"
    echo "  kind delete cluster --name cluster2"
    echo "  # ... (cluster3-6도 동일)"
fi
echo ""
