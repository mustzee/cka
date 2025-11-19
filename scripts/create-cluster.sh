#!/bin/bash

set -e

CLUSTER_NAME="cka-simulator"

echo "🎯 CKA 시험 클러스터 생성 중..."

# Check if cluster already exists
if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "⚠️  클러스터가 이미 존재합니다. 삭제하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🗑️  기존 클러스터 삭제 중..."
        kind delete cluster --name ${CLUSTER_NAME}
    else
        echo "✅ 기존 클러스터 사용"
        exit 0
    fi
fi

# Create cluster
echo "🔨 클러스터 생성 중 (약 2-3분 소요)..."
kind create cluster --config cluster/kind-config.yaml --wait 300s

# Wait for cluster to be ready
echo "⏳ 클러스터 준비 대기 중..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Display cluster info
echo ""
echo "✅ 클러스터 생성 완료!"
echo ""
echo "클러스터 정보:"
kubectl cluster-info --context kind-${CLUSTER_NAME}

echo ""
echo "노드 목록:"
kubectl get nodes -o wide

echo ""
echo "🎉 CKA 시뮬레이터 클러스터가 준비되었습니다!"
echo ""
echo "시험 시작: python3 simulator/main.py"
