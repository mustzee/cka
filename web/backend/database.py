"""
SQLite 데이터베이스 관리
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

# 데이터베이스 파일 경로
DB_PATH = os.path.join(os.path.dirname(__file__), "../../results/cka_simulator.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# SQLAlchemy 설정
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 모델 정의
class ExamSessionModel(Base):
    """시험 세션 모델"""

    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    exam_type = Column(String)
    practice_mode = Column(Boolean, default=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    total_score = Column(Float)
    total_weight = Column(Float)
    percentage = Column(Float)
    passed = Column(Boolean)
    results_json = Column(String)  # JSON 문자열로 저장
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """데이터베이스 초기화"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """데이터베이스 세션 가져오기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_exam_session(session_data: dict):
    """
    시험 세션 저장

    Args:
        session_data: 세션 데이터 딕셔너리
    """
    db = SessionLocal()
    try:
        exam_session = ExamSessionModel(
            session_id=session_data["session_id"],
            exam_type=session_data["exam_type"],
            practice_mode=session_data.get("practice_mode", False),
            start_time=session_data["start_time"],
            end_time=session_data.get("end_time"),
            total_score=session_data["total_score"],
            total_weight=session_data["total_weight"],
            percentage=session_data["percentage"],
            passed=session_data["passed"],
            results_json=json.dumps(session_data.get("results", []), ensure_ascii=False),
        )

        db.add(exam_session)
        db.commit()
        db.refresh(exam_session)
        return exam_session

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_exam_sessions(limit: int = 10, exam_type: str = None):
    """
    시험 세션 조회

    Args:
        limit: 조회 개수
        exam_type: 시험 타입 필터

    Returns:
        세션 리스트
    """
    db = SessionLocal()
    try:
        query = db.query(ExamSessionModel)

        if exam_type:
            query = query.filter(ExamSessionModel.exam_type == exam_type)

        sessions = (
            query.order_by(ExamSessionModel.created_at.desc()).limit(limit).all()
        )

        result = []
        for session in sessions:
            result.append(
                {
                    "session_id": session.session_id,
                    "exam_type": session.exam_type,
                    "practice_mode": session.practice_mode,
                    "start_time": session.start_time.isoformat() if session.start_time else None,
                    "end_time": session.end_time.isoformat() if session.end_time else None,
                    "total_score": session.total_score,
                    "total_weight": session.total_weight,
                    "percentage": session.percentage,
                    "passed": session.passed,
                    "results": json.loads(session.results_json) if session.results_json else [],
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                }
            )

        return result

    finally:
        db.close()


def get_exam_statistics():
    """
    전체 통계 조회

    Returns:
        통계 데이터
    """
    db = SessionLocal()
    try:
        total_exams = db.query(ExamSessionModel).count()
        passed_exams = db.query(ExamSessionModel).filter(ExamSessionModel.passed == True).count()
        failed_exams = total_exams - passed_exams

        # 평균 점수
        sessions = db.query(ExamSessionModel).all()
        avg_percentage = (
            sum(s.percentage for s in sessions) / len(sessions) if sessions else 0
        )

        # 타입별 통계
        type_stats = {}
        for exam_type in ["A", "B", "C"]:
            type_sessions = [s for s in sessions if s.exam_type == exam_type]
            if type_sessions:
                type_stats[exam_type] = {
                    "total": len(type_sessions),
                    "passed": sum(1 for s in type_sessions if s.passed),
                    "failed": sum(1 for s in type_sessions if not s.passed),
                    "avg_percentage": sum(s.percentage for s in type_sessions)
                    / len(type_sessions),
                }

        return {
            "total_exams": total_exams,
            "passed": passed_exams,
            "failed": failed_exams,
            "pass_rate": (passed_exams / total_exams * 100) if total_exams > 0 else 0,
            "avg_percentage": avg_percentage,
            "by_type": type_stats,
        }

    finally:
        db.close()


def get_user_progress(user_id: str = "default"):
    """
    사용자 진행률 조회

    Args:
        user_id: 사용자 ID

    Returns:
        진행률 데이터
    """
    db = SessionLocal()
    try:
        # 최근 10개 세션
        recent_sessions = (
            db.query(ExamSessionModel)
            .order_by(ExamSessionModel.created_at.desc())
            .limit(10)
            .all()
        )

        # 시간별 점수 추이
        progress = []
        for session in reversed(recent_sessions):
            progress.append(
                {
                    "date": session.created_at.strftime("%Y-%m-%d"),
                    "exam_type": session.exam_type,
                    "percentage": session.percentage,
                    "passed": session.passed,
                }
            )

        # 약점 도메인 분석
        weak_domains = _analyze_weak_domains(recent_sessions)

        return {"progress": progress, "weak_domains": weak_domains}

    finally:
        db.close()


def _analyze_weak_domains(sessions):
    """
    약점 도메인 분석

    Args:
        sessions: 세션 리스트

    Returns:
        도메인별 성적
    """
    domain_scores = {}

    for session in sessions:
        if not session.results_json:
            continue

        results = json.loads(session.results_json)
        for result in results:
            domain = result.get("domain", "Unknown")

            if domain not in domain_scores:
                domain_scores[domain] = {"total": 0, "correct": 0}

            domain_scores[domain]["total"] += 1
            if result.get("passed"):
                domain_scores[domain]["correct"] += 1

    # 정답률 계산 및 정렬
    weak_domains = []
    for domain, scores in domain_scores.items():
        accuracy = (
            scores["correct"] / scores["total"] * 100 if scores["total"] > 0 else 0
        )
        weak_domains.append(
            {"domain": domain, "accuracy": accuracy, "total": scores["total"]}
        )

    # 정답률 낮은 순으로 정렬
    weak_domains.sort(key=lambda x: x["accuracy"])

    return weak_domains[:5]  # 상위 5개
