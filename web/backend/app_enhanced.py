"""
CKA 시뮬레이터 Web API (Enhanced - WebSocket, PDF, Prometheus)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os
import asyncio
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from simulator.question_loader import QuestionLoader
from simulator.grader import AutoGrader
from simulator.ai_recommender import WeaknessAnalyzer, QuestionRecommender
from web.backend.database import (
    init_db,
    save_exam_session,
    get_exam_sessions,
    get_exam_statistics,
)
from web.backend.pdf_generator import PDFReportGenerator, CertificateGenerator

app = FastAPI(
    title="CKA Simulator API Enhanced",
    description="쿠버네티스 CKA 시험 시뮬레이터 Web API (WebSocket, PDF, Prometheus)",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics
exam_start_counter = Counter('cka_exam_started_total', 'Total number of exams started', ['exam_type'])
exam_complete_counter = Counter('cka_exam_completed_total', 'Total number of exams completed', ['exam_type', 'result'])
exam_duration_histogram = Histogram('cka_exam_duration_seconds', 'Exam duration in seconds')
active_exams_gauge = Gauge('cka_active_exams', 'Number of currently active exams')
exam_score_histogram = Histogram('cka_exam_score', 'Exam scores', buckets=[0, 40, 50, 60, 66, 70, 80, 90, 100])

# Database Init
init_db()

# Global Objects
question_loader = QuestionLoader()
grader = AutoGrader()
pdf_generator = PDFReportGenerator()
cert_generator = CertificateGenerator()
weakness_analyzer = WeaknessAnalyzer()
question_recommender = QuestionRecommender(question_loader)

# Active WebSocket Connections
active_connections: Dict[str, WebSocket] = {}

# Active Sessions
active_sessions: Dict[str, Dict[str, Any]] = {}


# Pydantic Models
class ExamStartRequest(BaseModel):
    exam_type: str = "A"
    practice_mode: bool = False
    set_number: int = 1


class GradeRequest(BaseModel):
    session_id: str
    questions: List[Dict[str, Any]]


# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def root():
    """API 루트"""
    return {
        "message": "CKA Simulator API Enhanced",
        "version": "2.0.0",
        "features": [
            "WebSocket Real-time Updates",
            "PDF Reports",
            "Certificate Generation",
            "Prometheus Metrics",
            "Question Sets System",
            "AI-Powered Recommendations"
        ],
        "endpoints": {
            "questions": "/api/questions",
            "exam_start": "/api/exam/start",
            "exam_grade": "/api/exam/grade",
            "pdf_report": "/api/exam/report/pdf/{session_id}",
            "certificate": "/api/exam/certificate/{session_id}",
            "statistics": "/api/statistics",
            "recommendations": "/api/recommendations",
            "weakness_analysis": "/api/analysis/weakness",
            "metrics": "/metrics",
            "websocket": "/ws/{session_id}"
        },
    }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 엔드포인트 - 실시간 업데이트"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            # 클라이언트로부터 메시지 처리
            if data.get("type") == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    session_id
                )
            elif data.get("type") == "status_update":
                # 진행 상황 브로드캐스트
                await manager.broadcast({
                    "type": "exam_progress",
                    "session_id": session_id,
                    "data": data.get("data")
                })
    except WebSocketDisconnect:
        manager.disconnect(session_id)


@app.get("/api/questions/types")
async def get_question_types():
    """사용 가능한 시험 타입 조회"""
    types = []
    for exam_type in ["A", "B", "C"]:
        try:
            # 각 타입당 5개 세트 지원
            all_questions_count = 0
            for set_num in range(1, 6):
                try:
                    questions = question_loader.load_questions(exam_type, set_num)
                    all_questions_count += len(questions)
                except:
                    pass

            if all_questions_count > 0:
                stats = question_loader.get_exam_stats(exam_type)
                types.append({
                    "type": exam_type,
                    "name": f"Type {exam_type}",
                    "description": _get_type_description(exam_type),
                    "question_count": all_questions_count,
                    "total_weight": stats["total_weight"],
                    "domains": stats["by_domain"],
                    "sets_available": 5
                })
        except Exception as e:
            print(f"Error loading type {exam_type}: {e}")

    return types


def _get_type_description(exam_type: str) -> str:
    descriptions = {
        "A": "기본 - 표준 CKA 문제, 기본 개념",
        "B": "고급 - Troubleshooting 및 복잡한 시나리오",
        "C": "실전 - 프로덕션 시나리오 기반",
    }
    return descriptions.get(exam_type, "")


@app.post("/api/exam/start")
async def start_exam(request: ExamStartRequest):
    """시험 시작"""
    try:
        # Prometheus Metric
        exam_start_counter.labels(exam_type=request.exam_type).inc()
        active_exams_gauge.inc()

        # 세션 ID 생성
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.set_number}"

        # 문제 로드 (세트 번호 포함)
        questions = question_loader.load_questions(
            request.exam_type.upper(),
            request.set_number
        )

        # 세션 저장
        session = {
            "session_id": session_id,
            "exam_type": request.exam_type.upper(),
            "practice_mode": request.practice_mode,
            "set_number": request.set_number,
            "questions": questions,
            "start_time": datetime.now(),
        }

        active_sessions[session_id] = session

        return {
            "session_id": session_id,
            "exam_type": session["exam_type"],
            "practice_mode": session["practice_mode"],
            "set_number": request.set_number,
            "question_count": len(questions),
            "questions": questions,
            "start_time": session["start_time"].isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/exam/grade")
async def grade_exam(request: GradeRequest, background_tasks: BackgroundTasks):
    """시험 채점"""
    try:
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

        session = active_sessions[request.session_id]
        session["end_time"] = datetime.now()

        # 채점
        grade_result = grader.grade_exam(request.questions)

        # Prometheus Metrics
        result_label = "passed" if grade_result["passed"] else "failed"
        exam_complete_counter.labels(
            exam_type=session["exam_type"],
            result=result_label
        ).inc()
        exam_score_histogram.observe(grade_result["percentage"])
        active_exams_gauge.dec()

        # Duration
        duration = (session["end_time"] - session["start_time"]).total_seconds()
        exam_duration_histogram.observe(duration)

        # 데이터베이스 저장
        background_tasks.add_task(
            save_exam_session,
            {
                "session_id": request.session_id,
                "exam_type": session["exam_type"],
                "practice_mode": session.get("practice_mode", False),
                "start_time": session["start_time"],
                "end_time": session["end_time"],
                "total_score": grade_result["total_score"],
                "total_weight": grade_result["total_weight"],
                "percentage": grade_result["percentage"],
                "passed": grade_result["passed"],
                "results": grade_result["results"],
            },
        )

        # WebSocket으로 결과 전송
        await manager.send_personal_message(
            {
                "type": "exam_completed",
                "grade_result": grade_result
            },
            request.session_id
        )

        return grade_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/exam/report/pdf/{session_id}")
async def download_pdf_report(session_id: str):
    """PDF 리포트 다운로드"""
    try:
        # 세션 데이터 조회
        sessions = get_exam_sessions(limit=100)
        session_data = next((s for s in sessions if s["session_id"] == session_id), None)

        if not session_data:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

        # PDF 생성
        pdf_path = pdf_generator.generate_report(session_data)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"cka_exam_{session_id}.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/exam/certificate/{session_id}")
async def download_certificate(session_id: str):
    """인증서 다운로드 (합격한 경우에만)"""
    try:
        # 세션 데이터 조회
        sessions = get_exam_sessions(limit=100)
        session_data = next((s for s in sessions if s["session_id"] == session_id), None)

        if not session_data:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

        if not session_data.get("passed"):
            raise HTTPException(status_code=403, detail="합격한 경우에만 인증서를 발급받을 수 있습니다")

        # 인증서 생성
        cert_path = cert_generator.generate_certificate(session_data)

        return FileResponse(
            cert_path,
            media_type="application/pdf",
            filename=f"cka_certificate_{session_id}.pdf"
        )

    except HTTPException:
        raise
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


@app.get("/metrics")
async def metrics():
    """Prometheus Metrics 엔드포인트"""
    return StreamingResponse(
        iter([generate_latest()]),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/api/analysis/weakness")
async def get_weakness_analysis(limit: int = 10):
    """약점 분석 조회 - 최근 시험 결과를 기반으로 약점 분석"""
    try:
        # 최근 시험 세션 조회
        sessions = get_exam_sessions(limit=limit)

        if not sessions:
            return {
                "message": "분석할 시험 기록이 없습니다",
                "analysis": None
            }

        # 약점 분석
        analysis = weakness_analyzer.analyze_performance(sessions)

        return {
            "message": "약점 분석 완료",
            "sessions_analyzed": len(sessions),
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations")
async def get_recommendations(
    count: int = 10,
    target_exam_type: Optional[str] = None,
    session_limit: int = 10
):
    """AI 기반 맞춤 문제 추천

    Args:
        count: 추천할 문제 개수 (기본 10개)
        target_exam_type: 특정 타입 (A/B/C) 문제만 추천 (선택사항)
        session_limit: 분석할 최근 시험 세션 개수 (기본 10개)
    """
    try:
        # 최근 시험 세션 조회
        sessions = get_exam_sessions(limit=session_limit)

        if not sessions:
            # 기록이 없으면 기본 문제 추천
            return {
                "message": "시험 기록이 없어 기본 문제를 추천합니다",
                "recommendations": _get_default_recommendations(count, target_exam_type),
                "analysis": None,
                "learning_path": None
            }

        # AI 기반 추천
        result = question_recommender.recommend_questions(
            sessions,
            count=count,
            target_exam_type=target_exam_type
        )

        return {
            "message": "AI 기반 맞춤 문제 추천 완료",
            "sessions_analyzed": len(sessions),
            "recommendations": result["recommendations"],
            "analysis": result["analysis"],
            "learning_path": result["learning_path"],
            "strategy": result["strategy"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _get_default_recommendations(count: int, target_exam_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """기본 문제 추천 (시험 기록이 없을 때)"""
    recommendations = []
    exam_type = target_exam_type or "A"

    try:
        # Set 1의 문제들을 기본으로 추천
        questions = question_loader.load_questions(exam_type, set_number=1)

        for i, q in enumerate(questions[:count]):
            recommendations.append({
                "question": q,
                "reason": "기본 학습 문제입니다. 기초를 다지는데 도움이 됩니다.",
                "priority": 1.0 - (i * 0.05),  # 순서대로 우선순위 감소
                "difficulty": q.get("difficulty", "medium")
            })

    except Exception as e:
        print(f"Error loading default recommendations: {e}")

    return recommendations


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(active_sessions),
        "websocket_connections": len(manager.active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
