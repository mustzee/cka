#!/bin/bash

set -e

CLUSTER_NAME="cka-simulator"

echo "🎯 CKA 시뮬레이터 클러스터 생성 중 (k3d 사용)..."
echo "💡 k3d는 M2 Mac에서 Kind보다 안정적으로 작동합니다."
echo ""

# Check if k3d is installed
if ! command -v k3d &> /dev/null; then
    echo "❌ k3d가 설치되어 있지 않습니다."
    echo ""
    echo "설치 방법:"
    echo "  brew install k3d"
    echo ""
    echo "또는:"
    echo "  curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash"
    exit 1
fi

# Check if cluster already exists
if k3d cluster list | grep -q "^${CLUSTER_NAME}"; then
    echo "⚠️  클러스터가 이미 존재합니다. 삭제하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🗑️  기존 클러스터 삭제 중..."
        k3d cluster delete ${CLUSTER_NAME}
    else
        echo "✅ 기존 클러스터 사용"
        kubectl cluster-info --context k3d-${CLUSTER_NAME}
        exit 0
    fi
fi

# Create cluster with k3d
echo "🔨 클러스터 생성 중 (약 30초 소요)..."
k3d cluster create ${CLUSTER_NAME} \
  --agents 2 \
  --port 30000-30100:30000-30100@loadbalancer \
  --wait

# Wait for cluster to be ready
echo "⏳ 노드 준비 대기 중..."
kubectl wait --for=condition=Ready nodes --all --timeout=120s

# Display cluster info
echo ""
echo "✅ 클러스터 생성 완료!"
echo ""
echo "클러스터 정보:"
kubectl cluster-info --context k3d-${CLUSTER_NAME}

echo ""
echo "노드 목록:"
kubectl get nodes -o wide

echo ""
echo "🎉 CKA 시뮬레이터 클러스터가 준비되었습니다!"
echo ""
echo "💡 k3d 장점:"
echo "  - ⚡ Kind보다 빠른 시작 (30초 vs 2-3분)"
echo "  - 💻 낮은 리소스 사용"
echo "  - 🍎 M2 Mac에서 안정적"
echo ""
echo "클러스터 삭제: k3d cluster delete ${CLUSTER_NAME}"
echo "시험 시작: python3 simulator/main.py --type A --list-only"
