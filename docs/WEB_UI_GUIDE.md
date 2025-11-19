# 웹 UI 사용 가이드

## 개요

CKA 시뮬레이터는 이제 웹 브라우저에서도 사용할 수 있습니다!

## 시작하기

### 1. 웹 서버 시작

```bash
# 프로젝트 루트에서 실행
./scripts/start-web.sh
```

서버가 시작되면:
- **FastAPI 백엔드**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs (Swagger UI)
- **웹 UI**: `web/frontend/index.html` 파일을 브라우저로 열기

### 2. 웹 UI 열기

브라우저에서 `file:///path/to/cka/web/frontend/index.html` 열기

또는 간단한 HTTP 서버 사용:

```bash
cd web/frontend
python3 -m http.server 3000
# http://localhost:3000 접속
```

## 기능

### 시험 타입 선택
- Type A (기본): 표준 CKA 문제
- Type B (고급): 고급 시나리오
- Type C (실전): 프로덕션 시나리오

### 시험 옵션
- **일반 모드**: 2시간 타이머
- **연습 모드**: 타이머 없음

### 시험 진행
1. 타입 선택 및 옵션 설정
2. "시험 시작" 클릭
3. 문제 목록 확인
4. 별도 터미널에서 kubectl로 작업 수행
5. "시험 종료 및 채점" 클릭

### 결과 확인
- 합격/불합격 판정
- 총점 및 획득 점수
- 문제별 상세 결과
- 오답 상세 정보

### 통계
- 총 시험 횟수
- 합격률
- 타입별 통계
- 평균 점수

## API 엔드포인트

### 문제 관련
- `GET /api/questions/types` - 사용 가능한 타입 조회
- `GET /api/questions/{type}` - 특정 타입 문제 조회

### 시험 관련
- `POST /api/exam/start` - 시험 시작
- `POST /api/exam/grade` - 시험 채점
- `GET /api/exam/sessions` - 시험 기록 조회

### 통계
- `GET /api/statistics` - 전체 통계
- `GET /api/statistics/domain` - 도메인별 통계

### 헬스 체크
- `GET /health` - 서버 상태 확인

## 상세 API 문서

http://localhost:8000/docs 에서 Swagger UI로 모든 API를 테스트할 수 있습니다.

## 데이터베이스

SQLite 데이터베이스에 다음 정보가 저장됩니다:
- 시험 세션 정보
- 점수 및 결과
- 시간 기록

위치: `results/cka_simulator.db`

## 문제 해결

### 서버가 시작되지 않음
```bash
# 의존성 재설치
pip3 install -r requirements.txt

# 포트 사용 중 확인
lsof -i :8000
```

### CORS 오류
현재 CORS는 모든 출처에서 허용됩니다. 프로덕션에서는 제한하세요.

### 데이터베이스 오류
```bash
# DB 재생성
rm results/cka_simulator.db
python3 -c "from web.backend.database import init_db; init_db()"
```

## 향후 개선 사항

- [ ] 사용자 인증
- [ ] 다중 사용자 지원
- [ ] 실시간 진행률 업데이트
- [ ] 채팅 기능 (질문/답변)
- [ ] PDF 리포트 생성
- [ ] 이메일 알림

---

**Enjoy!** 🚀
