#!/bin/bash

set -e

CLUSTER_NAME="cka-simulator"

echo "🧹 CKA 시뮬레이터 정리 중..."

# Delete cluster
if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "🗑️  클러스터 삭제 중..."
    kind delete cluster --name ${CLUSTER_NAME}
    echo "✅ 클러스터 삭제 완료"
else
    echo "ℹ️  클러스터가 존재하지 않습니다."
fi

# Clean results
echo "📁 결과 파일 정리 중..."
rm -f results/*.json results/*.md results/*.log
echo "✅ 정리 완료"
