#!/bin/bash

set -e

echo "🔄 CKA 시험 환경 리셋 중..."

# 시험 관련 네임스페이스들 정리
EXAM_NAMESPACES=(
    "production"
    "staging" 
    "development"
    "dev-team"
    "monitoring"
    "testing"
)

echo "🧹 시험 네임스페이스 정리..."
for ns in "${EXAM_NAMESPACES[@]}"; do
    if kubectl get namespace "$ns" &>/dev/null; then
        echo "  - 삭제 중: $ns"
        kubectl delete namespace "$ns" --ignore-not-found=true --wait=false
    fi
done

# 기본 네임스페이스의 시험 관련 리소스 정리
echo "🧹 기본 네임스페이스 리소스 정리..."
kubectl delete pods,deployments,services,configmaps,secrets,persistentvolumeclaims,cronjobs,daemonsets --all -n default --ignore-not-found=true --wait=false

# 클러스터 레벨 리소스 정리 (PV, ClusterRole, ClusterRoleBinding 등)
echo "🧹 클러스터 레벨 리소스 정리..."
kubectl delete persistentvolumes --all --ignore-not-found=true --wait=false
kubectl delete clusterroles --ignore-not-found=true -l "created-by=cka-exam" --wait=false
kubectl delete clusterrolebindings --ignore-not-found=true -l "created-by=cka-exam" --wait=false

# Node taints 정리
echo "🧹 Node taints 정리..."
kubectl get nodes -o jsonpath='{.items[*].metadata.name}' | xargs -I {} kubectl taint node {} dedicated- --ignore-not-found=true || true

# 시험 결과 파일 정리
echo "📁 결과 파일 정리..."
rm -f results/*.json results/*.md results/*.log 2>/dev/null || true

echo "⏳ 네임스페이스 삭제 완료 대기..."
sleep 5

# 네임스페이스들이 완전히 삭제될 때까지 대기
for ns in "${EXAM_NAMESPACES[@]}"; do
    while kubectl get namespace "$ns" &>/dev/null; do
        echo "  - 대기 중: $ns 삭제"
        sleep 2
    done
done

echo "✅ CKA 시험 환경 리셋 완료!"
echo "🚀 새로운 시험을 시작할 준비가 되었습니다."