"""
문제 로더 모듈
YAML 파일에서 시험 문제를 로드합니다.
"""

import os
import yaml
from typing import List, Dict, Any
import random


class QuestionLoader:
    """CKA 시험 문제를 로드하는 클래스"""

    def __init__(self, questions_dir: str = "questions"):
        self.questions_dir = questions_dir

    def load_questions(self, exam_type: str = "A", set_number: int = 1) -> List[Dict[str, Any]]:
        """
        지정된 타입의 문제를 로드합니다.

        Args:
            exam_type: 시험 타입 (A, B, C)
            set_number: 세트 번호 (1-5)

        Returns:
            문제 리스트
        """
        # 세트별 디렉토리 확인
        type_dir = os.path.join(self.questions_dir, f"type_{exam_type.lower()}")
        set_dir = os.path.join(type_dir, f"set{set_number}")

        # 세트 디렉토리가 있으면 사용, 없으면 기본 디렉토리
        if os.path.exists(set_dir):
            type_dir = set_dir

        if not os.path.exists(type_dir):
            raise FileNotFoundError(f"문제 디렉토리를 찾을 수 없습니다: {type_dir}")

        questions = []
        for filename in os.listdir(type_dir):
            if filename.endswith(".yaml") and not filename.startswith("_"):
                filepath = os.path.join(type_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    question = yaml.safe_load(f)
                    questions.append(question)

        # ID로 정렬
        questions.sort(key=lambda q: q.get("id", ""))
        return questions

    def get_random_questions(
        self, exam_type: str = "A", count: int = None
    ) -> List[Dict[str, Any]]:
        """
        랜덤으로 문제를 선택합니다.

        Args:
            exam_type: 시험 타입
            count: 선택할 문제 수 (None이면 모든 문제)

        Returns:
            랜덤 문제 리스트
        """
        questions = self.load_questions(exam_type)

        if count is None or count >= len(questions):
            # 순서만 섞기
            random.shuffle(questions)
            return questions

        # 도메인별로 균등하게 선택
        domains = {}
        for q in questions:
            domain = q.get("domain", "Unknown")
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(q)

        selected = []
        domain_list = list(domains.keys())
        random.shuffle(domain_list)

        # 각 도메인에서 균등하게 선택
        per_domain = count // len(domain_list)
        remainder = count % len(domain_list)

        for i, domain in enumerate(domain_list):
            domain_questions = domains[domain]
            random.shuffle(domain_questions)

            # 나머지를 첫 번째 도메인들에 분배
            take = per_domain + (1 if i < remainder else 0)
            selected.extend(domain_questions[:take])

        random.shuffle(selected)
        return selected

    def get_question_by_id(self, question_id: str, exam_type: str = "A") -> Dict[str, Any]:
        """
        ID로 특정 문제를 조회합니다.

        Args:
            question_id: 문제 ID
            exam_type: 시험 타입

        Returns:
            문제 딕셔너리
        """
        questions = self.load_questions(exam_type)
        for q in questions:
            if q.get("id") == question_id:
                return q
        raise ValueError(f"문제를 찾을 수 없습니다: {question_id}")

    def get_exam_stats(self, exam_type: str = "A") -> Dict[str, Any]:
        """
        시험 통계를 반환합니다.

        Args:
            exam_type: 시험 타입

        Returns:
            통계 딕셔너리
        """
        questions = self.load_questions(exam_type)

        stats = {
            "total_questions": len(questions),
            "total_weight": sum(q.get("weight", 0) for q in questions),
            "by_domain": {},
            "by_difficulty": {},
        }

        for q in questions:
            domain = q.get("domain", "Unknown")
            difficulty = q.get("difficulty", "unknown")

            if domain not in stats["by_domain"]:
                stats["by_domain"][domain] = {"count": 0, "weight": 0}
            stats["by_domain"][domain]["count"] += 1
            stats["by_domain"][domain]["weight"] += q.get("weight", 0)

            if difficulty not in stats["by_difficulty"]:
                stats["by_difficulty"][difficulty] = {"count": 0, "weight": 0}
            stats["by_difficulty"][difficulty]["count"] += 1
            stats["by_difficulty"][difficulty]["weight"] += q.get("weight", 0)

        return stats
