#!/bin/bash

set -e

echo "🚀 CKA 시뮬레이터 환경 설정 시작..."

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  이 스크립트는 Linux에서 실행하도록 설계되었습니다."
fi

# Check Docker
echo "📦 Docker 확인 중..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    echo "   설치 방법: https://docs.docker.com/engine/install/"
    exit 1
fi
echo "✅ Docker 설치 확인됨: $(docker --version)"

# Check kubectl
echo "🔧 kubectl 확인 중..."
if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl이 설치되어 있지 않습니다. 설치 중..."

    # Install kubectl
    KUBECTL_VERSION="v1.28.0"
    curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
    chmod +x kubectl
    sudo mv kubectl /usr/local/bin/
    echo "✅ kubectl 설치 완료"
else
    echo "✅ kubectl 설치 확인됨: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
fi

# Check kind
echo "🎯 kind 확인 중..."
if ! command -v kind &> /dev/null; then
    echo "⚠️  kind가 설치되어 있지 않습니다. 설치 중..."

    # Install kind
    curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    echo "✅ kind 설치 완료"
else
    echo "✅ kind 설치 확인됨: $(kind --version)"
fi

# Check Python
echo "🐍 Python 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3가 설치되어 있지 않습니다."
    exit 1
fi
echo "✅ Python 설치 확인됨: $(python3 --version)"

# Install Python dependencies
echo "📚 Python 패키지 설치 중..."
pip3 install -r requirements.txt

# Create directories
echo "📁 디렉토리 생성 중..."
mkdir -p results
mkdir -p logs

echo ""
echo "✅ 환경 설정 완료!"
echo ""
echo "다음 단계:"
echo "  1. 클러스터 생성: ./scripts/create-cluster.sh"
echo "  2. 시험 시작: python3 simulator/main.py"
