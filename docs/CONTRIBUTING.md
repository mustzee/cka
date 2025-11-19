# 기여 가이드

CKA 시뮬레이터 프로젝트에 기여해주셔서 감사합니다!

## 새로운 문제 추가하기

### 1. 문제 파일 생성

`questions/question_template.yaml` 템플릿을 사용하여 새 문제를 작성하세요.

```bash
# 적절한 타입 디렉토리에 생성
cp questions/question_template.yaml questions/type_a/q008_your_question.yaml
```

### 2. 문제 작성 가이드라인

#### 필수 필드
- `id`: 고유 ID (예: A008, B005, C003)
- `title`: 간결한 제목
- `domain`: CKA 도메인 중 하나
- `difficulty`: easy, medium, hard
- `weight`: 1-10 (난이도에 따라)
- `description`: 문제 설명
- `task`: 수행할 작업
- `validation`: 채점 규칙
- `solution`: 정답 코드
- `explanation`: 상세 해설

#### 도메인 분류
1. Cluster Architecture, Installation & Configuration
2. Workloads & Scheduling
3. Services & Networking
4. Storage
5. Troubleshooting

#### 난이도 기준
- **easy**: 기본 명령어, 단일 리소스
- **medium**: 복수 리소스, 설정 구성
- **hard**: 복잡한 시나리오, 트러블슈팅

### 3. 검증 규칙 작성

자동 채점을 위한 검증 규칙:

```yaml
validation:
  checks:
    - resource: "pod"
      name: "my-pod"
      namespace: "default"
      conditions:
        - type: "Ready"
          status: "True"
        - field: "spec.containers[0].image"
          value: "nginx:latest"
```

### 4. 테스트

```bash
# 클러스터 생성
./scripts/create-cluster.sh

# 문제 수동 테스트
# 1. 문제 요구사항대로 리소스 생성
# 2. 검증 규칙이 정상 작동하는지 확인

# 시뮬레이터 실행하여 테스트
python3 simulator/main.py --type A --practice
```

## 코드 기여

### 개발 환경 설정

```bash
# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 코드 스타일

- PEP 8 준수
- 함수와 클래스에 docstring 작성
- 타입 힌트 사용 권장

### Pull Request

1. Fork 저장소
2. Feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 버그 리포트

이슈를 생성할 때 다음 정보를 포함해주세요:

- 운영체제 및 버전
- Kubernetes 버전
- 재현 단계
- 예상 동작 vs 실제 동작
- 로그 또는 스크린샷

## 문의

질문이나 제안사항이 있으시면 이슈를 생성해주세요.
