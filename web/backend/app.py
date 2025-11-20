"""
CKA 시뮬레이터 Web API (FastAPI)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os

# 부모 디렉토리를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from simulator.question_loader import QuestionLoader
from simulator.grader import AutoGrader
from web.backend.database import (
    init_db,
    save_exam_session,
    get_exam_sessions,
    get_exam_statistics,
)

app = FastAPI(
    title="CKA Simulator API",
    description="쿠버네티스 CKA 시험 시뮬레이터 Web API",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
init_db()

# 전역 객체
question_loader = QuestionLoader()
grader = AutoGrader()


# Pydantic 모델
class ExamStartRequest(BaseModel):
    exam_type: str = "A"
    practice_mode: bool = False
    show_hints: bool = False
    hard_mode: bool = False
    ultra_mode: bool = False


class ExamSession(BaseModel):
    session_id: str
    exam_type: str
    practice_mode: bool
    show_hints: bool = False
    hard_mode: bool = False
    ultra_mode: bool = False
    questions: List[Dict[str, Any]]
    start_time: datetime
    end_time: Optional[datetime] = None


class GradeRequest(BaseModel):
    session_id: str
    questions: List[Dict[str, Any]]


class GradeResponse(BaseModel):
    total_score: float
    total_weight: float
    percentage: float
    passed: bool
    results: List[Dict[str, Any]]


# 활성 세션 저장 (메모리)
active_sessions: Dict[str, ExamSession] = {}


@app.get("/")
async def root():
    """API 루트"""
    return {
        "message": "CKA Simulator API",
        "version": "1.0.0",
        "endpoints": {
            "questions": "/api/questions",
            "exam_start": "/api/exam/start",
            "exam_grade": "/api/exam/grade",
            "statistics": "/api/statistics",
        },
    }


@app.get("/api/questions/types")
async def get_question_types():
    """사용 가능한 시험 타입 조회"""
    types = []
    for exam_type in ["A", "B", "C"]:
        try:
            questions = question_loader.load_questions(exam_type)
            stats = question_loader.get_exam_stats(exam_type)
            types.append(
                {
                    "type": exam_type,
                    "name": f"Type {exam_type}",
                    "description": _get_type_description(exam_type),
                    "question_count": len(questions),
                    "total_weight": stats["total_weight"],
                    "domains": stats["by_domain"],
                }
            )
        except Exception:
            pass

    return types


def _get_type_description(exam_type: str) -> str:
    """타입별 설명"""
    descriptions = {
        "A": "기본 - 표준 CKA 문제, 기본 개념",
        "B": "고급 - Troubleshooting 및 복잡한 시나리오",
        "C": "실전 - 프로덕션 시나리오 기반",
    }
    return descriptions.get(exam_type, "")


@app.get("/api/questions/{exam_type}")
async def get_questions(exam_type: str):
    """특정 타입의 문제 조회"""
    try:
        questions = question_loader.load_questions(exam_type.upper())
        return {"exam_type": exam_type.upper(), "questions": questions}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다")


@app.post("/api/exam/start")
async def start_exam(request: ExamStartRequest):
    """시험 시작"""
    try:
        # 세션 ID 생성
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 문제 로드
        questions = question_loader.load_questions(request.exam_type.upper())

        # 모드 충돌 검사
        if request.ultra_mode and request.show_hints:
            raise HTTPException(
                status_code=400,
                detail="Ultra Mode와 힌트 모드는 동시에 사용할 수 없습니다"
            )
        if request.ultra_mode and request.hard_mode:
            raise HTTPException(
                status_code=400,
                detail="Ultra Mode와 Hard Mode는 동시에 사용할 수 없습니다"
            )
        if request.hard_mode and request.show_hints:
            raise HTTPException(
                status_code=400,
                detail="Hard Mode와 힌트 모드는 동시에 사용할 수 없습니다"
            )

        # 세션 생성
        session = ExamSession(
            session_id=session_id,
            exam_type=request.exam_type.upper(),
            practice_mode=request.practice_mode,
            show_hints=request.show_hints,
            hard_mode=request.hard_mode,
            ultra_mode=request.ultra_mode,
            questions=questions,
            start_time=datetime.now(),
        )

        # 메모리에 저장
        active_sessions[session_id] = session

        return {
            "session_id": session_id,
            "exam_type": session.exam_type,
            "practice_mode": session.practice_mode,
            "show_hints": session.show_hints,
            "hard_mode": session.hard_mode,
            "ultra_mode": session.ultra_mode,
            "question_count": len(questions),
            "questions": questions,
            "start_time": session.start_time.isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/exam/grade")
async def grade_exam(request: GradeRequest, background_tasks: BackgroundTasks):
    """시험 채점"""
    try:
        # 세션 확인
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

        session = active_sessions[request.session_id]
        session.end_time = datetime.now()

        # 채점
        grade_result = grader.grade_exam(request.questions)

        # 백그라운드에서 데이터베이스에 저장
        background_tasks.add_task(
            save_exam_session,
            {
                "session_id": request.session_id,
                "exam_type": session.exam_type,
                "practice_mode": session.practice_mode,
                "show_hints": session.show_hints,
                "hard_mode": session.hard_mode,
                "ultra_mode": session.ultra_mode,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "total_score": grade_result["total_score"],
                "total_weight": grade_result["total_weight"],
                "percentage": grade_result["percentage"],
                "passed": grade_result["passed"],
                "results": grade_result["results"],
            },
        )

        return GradeResponse(**grade_result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/exam/sessions")
async def get_sessions(limit: int = 10):
    """최근 시험 세션 조회"""
    try:
        sessions = get_exam_sessions(limit=limit)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    """통계 조회"""
    try:
        stats = get_exam_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics/domain")
async def get_domain_statistics():
    """도메인별 통계"""
    try:
        sessions = get_exam_sessions(limit=100)

        domain_stats = {}
        for session in sessions:
            for result in session.get("results", []):
                question = result.get("question", {})
                domain = question.get("domain", "Unknown")

                if domain not in domain_stats:
                    domain_stats[domain] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "avg_score": 0,
                    }

                domain_stats[domain]["total"] += 1
                if result.get("passed"):
                    domain_stats[domain]["passed"] += 1
                else:
                    domain_stats[domain]["failed"] += 1

        return {"domain_statistics": domain_stats}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
