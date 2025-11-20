"""
AI 기반 약점 분석 및 맞춤 문제 추천 시스템
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import random
import math


class WeaknessAnalyzer:
    """사용자 약점 분석기"""

    def __init__(self):
        self.domain_weights = {
            "Cluster Architecture": 0.25,
            "Workloads & Scheduling": 0.15,
            "Services & Networking": 0.20,
            "Storage": 0.10,
            "Troubleshooting": 0.30,
        }

    def analyze_performance(self, exam_sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        사용자 성적 분석

        Args:
            exam_sessions: 시험 세션 리스트

        Returns:
            분석 결과
        """
        if not exam_sessions:
            return {
                "total_exams": 0,
                "avg_score": 0,
                "weak_domains": [],
                "strong_domains": [],
                "difficulty_analysis": {},
                "learning_trend": "no_data",
            }

        # 도메인별 성적 분석
        domain_stats = defaultdict(lambda: {"total": 0, "correct": 0, "scores": []})

        # 난이도별 성적 분석
        difficulty_stats = defaultdict(lambda: {"total": 0, "correct": 0})

        # 시간대별 점수 (학습 추이)
        time_scores = []

        for session in exam_sessions:
            results = session.get("results", [])
            time_scores.append({
                "date": session.get("created_at", ""),
                "score": session.get("percentage", 0)
            })

            for result in results:
                # 도메인 분석
                domain = self._extract_domain(result)
                domain_stats[domain]["total"] += 1
                if result.get("passed"):
                    domain_stats[domain]["correct"] += 1
                score_ratio = result.get("score", 0) / result.get("weight", 1) * 100
                domain_stats[domain]["scores"].append(score_ratio)

                # 난이도 분석
                difficulty = self._extract_difficulty(result)
                difficulty_stats[difficulty]["total"] += 1
                if result.get("passed"):
                    difficulty_stats[difficulty]["correct"] += 1

        # 약점 도메인 추출 (정답률 낮은 순)
        weak_domains = []
        strong_domains = []

        for domain, stats in domain_stats.items():
            accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
            avg_score = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0

            domain_info = {
                "domain": domain,
                "accuracy": accuracy,
                "avg_score": avg_score,
                "total_attempts": stats["total"],
                "importance": self.domain_weights.get(domain, 0.1),
                "weakness_score": self._calculate_weakness_score(accuracy, stats["total"], domain)
            }

            if accuracy < 70:
                weak_domains.append(domain_info)
            elif accuracy >= 85:
                strong_domains.append(domain_info)

        # 약점 점수로 정렬
        weak_domains.sort(key=lambda x: x["weakness_score"], reverse=True)
        strong_domains.sort(key=lambda x: x["accuracy"], reverse=True)

        # 난이도 분석
        difficulty_analysis = {}
        for difficulty, stats in difficulty_stats.items():
            accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
            difficulty_analysis[difficulty] = {
                "accuracy": accuracy,
                "total": stats["total"],
                "correct": stats["correct"]
            }

        # 학습 추이 분석
        learning_trend = self._analyze_trend(time_scores)

        # 전체 평균 점수
        avg_score = sum(s.get("percentage", 0) for s in exam_sessions) / len(exam_sessions)

        return {
            "total_exams": len(exam_sessions),
            "avg_score": avg_score,
            "weak_domains": weak_domains[:5],  # 상위 5개
            "strong_domains": strong_domains[:5],
            "difficulty_analysis": difficulty_analysis,
            "learning_trend": learning_trend,
            "domain_stats": dict(domain_stats),
        }

    def _extract_domain(self, result: Dict[str, Any]) -> str:
        """결과에서 도메인 추출"""
        # result에 domain이 있으면 사용, 없으면 question에서 추출
        if "domain" in result:
            return result["domain"]

        question = result.get("question", {})
        return question.get("domain", "Unknown")

    def _extract_difficulty(self, result: Dict[str, Any]) -> str:
        """결과에서 난이도 추출"""
        if "difficulty" in result:
            return result["difficulty"]

        question = result.get("question", {})
        return question.get("difficulty", "medium")

    def _calculate_weakness_score(self, accuracy: float, attempts: int, domain: str) -> float:
        """
        약점 점수 계산 (높을수록 더 약함)

        고려 요소:
        1. 정답률 (낮을수록 약함)
        2. 시도 횟수 (많이 틀렸을수록 약함)
        3. 도메인 중요도 (시험 배점 비율)
        """
        # 정답률 점수 (0-100 -> 100-0)
        accuracy_score = 100 - accuracy

        # 시도 횟수 가중치 (많이 풀었는데 틀렸으면 더 심각)
        attempt_weight = min(attempts / 10, 2.0)

        # 도메인 중요도
        importance = self.domain_weights.get(domain, 0.1)

        # 최종 약점 점수
        weakness_score = accuracy_score * attempt_weight * (1 + importance)

        return weakness_score

    def _analyze_trend(self, time_scores: List[Dict[str, Any]]) -> str:
        """
        학습 추이 분석

        Returns:
            "improving": 점수 상승 추세
            "stable": 안정적
            "declining": 하락 추세
            "no_data": 데이터 부족
        """
        if len(time_scores) < 3:
            return "no_data"

        # 최근 5개 세션만 분석
        recent = sorted(time_scores, key=lambda x: x["date"], reverse=True)[:5]
        scores = [s["score"] for s in recent]

        # 선형 회귀 기울기 계산
        n = len(scores)
        x = list(range(n))
        y = scores

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # 기울기로 추세 판단
        if slope > 5:
            return "improving"
        elif slope < -5:
            return "declining"
        else:
            return "stable"


class QuestionRecommender:
    """AI 기반 문제 추천 시스템"""

    def __init__(self, question_loader):
        self.question_loader = question_loader
        self.analyzer = WeaknessAnalyzer()

    def recommend_questions(
        self,
        exam_sessions: List[Dict[str, Any]],
        count: int = 10,
        target_exam_type: str = None
    ) -> Dict[str, Any]:
        """
        맞춤 문제 추천

        Args:
            exam_sessions: 시험 기록
            count: 추천 문제 수
            target_exam_type: 목표 시험 타입 (None이면 자동 선택)

        Returns:
            추천 문제 및 이유
        """
        # 성적 분석
        analysis = self.analyzer.analyze_performance(exam_sessions)

        # 추천 전략 결정
        strategy = self._determine_strategy(analysis)

        # 문제 풀 로드
        all_questions = self._load_all_questions()

        # 추천 문제 선택
        recommendations = self._select_questions(
            all_questions,
            analysis,
            strategy,
            count,
            target_exam_type
        )

        return {
            "analysis": analysis,
            "strategy": strategy,
            "recommendations": recommendations,
            "learning_path": self._generate_learning_path(analysis, strategy)
        }

    def _determine_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """추천 전략 결정"""
        avg_score = analysis["avg_score"]
        weak_domains = analysis["weak_domains"]
        trend = analysis["learning_trend"]

        # 초보자 (평균 50% 이하)
        if avg_score < 50:
            return {
                "name": "foundation_building",
                "focus": "weak_domains",
                "difficulty_preference": "easy",
                "domain_distribution": "focused",  # 약점 집중
                "description": "기초 다지기 - 약점 도메인 집중 학습"
            }

        # 중급자 (50-70%)
        elif avg_score < 70:
            return {
                "name": "skill_improvement",
                "focus": "weak_and_medium",
                "difficulty_preference": "medium",
                "domain_distribution": "balanced",  # 균형잡힌 학습
                "description": "실력 향상 - 약점 보완 + 전체 도메인 균형"
            }

        # 고급자 (70-85%)
        elif avg_score < 85:
            return {
                "name": "mastery",
                "focus": "challenging",
                "difficulty_preference": "hard",
                "domain_distribution": "comprehensive",  # 종합
                "description": "완성 단계 - 고난이도 문제 도전"
            }

        # 전문가 (85% 이상)
        else:
            return {
                "name": "expert",
                "focus": "advanced",
                "difficulty_preference": "hard",
                "domain_distribution": "comprehensive",
                "description": "전문가 - 실전 시나리오 마스터"
            }

    def _load_all_questions(self) -> List[Dict[str, Any]]:
        """모든 문제 로드"""
        all_questions = []

        for exam_type in ["A", "B", "C"]:
            for set_num in range(1, 6):
                try:
                    questions = self.question_loader.load_questions(exam_type, set_num)
                    for q in questions:
                        q["exam_type"] = exam_type
                        q["set_number"] = set_num
                    all_questions.extend(questions)
                except:
                    pass

        return all_questions

    def _select_questions(
        self,
        all_questions: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        strategy: Dict[str, Any],
        count: int,
        target_exam_type: str = None
    ) -> List[Dict[str, Any]]:
        """문제 선택 알고리즘"""
        recommendations = []
        weak_domains = [d["domain"] for d in analysis["weak_domains"]]

        # 난이도 필터
        difficulty_pref = strategy["difficulty_preference"]
        if difficulty_pref == "easy":
            difficulty_filter = ["easy"]
        elif difficulty_pref == "medium":
            difficulty_filter = ["easy", "medium"]
        else:
            difficulty_filter = ["medium", "hard"]

        # 타입 필터
        if target_exam_type:
            filtered = [q for q in all_questions if q.get("exam_type") == target_exam_type]
        else:
            filtered = all_questions

        # 난이도 필터 적용
        filtered = [q for q in filtered if q.get("difficulty") in difficulty_filter]

        # 도메인 분배에 따라 선택
        if strategy["domain_distribution"] == "focused":
            # 약점 도메인 80%, 나머지 20%
            weak_count = int(count * 0.8)
            other_count = count - weak_count

            weak_questions = [q for q in filtered if q.get("domain") in weak_domains]
            other_questions = [q for q in filtered if q.get("domain") not in weak_domains]

            recommendations.extend(self._random_sample(weak_questions, weak_count))
            recommendations.extend(self._random_sample(other_questions, other_count))

        elif strategy["domain_distribution"] == "balanced":
            # 약점 60%, 나머지 40%
            weak_count = int(count * 0.6)
            other_count = count - weak_count

            weak_questions = [q for q in filtered if q.get("domain") in weak_domains]
            other_questions = [q for q in filtered if q.get("domain") not in weak_domains]

            recommendations.extend(self._random_sample(weak_questions, weak_count))
            recommendations.extend(self._random_sample(other_questions, other_count))

        else:
            # 모든 도메인에서 균등하게
            recommendations = self._random_sample(filtered, count)

        # 각 문제에 추천 이유 추가
        for q in recommendations:
            q["recommendation_reason"] = self._get_recommendation_reason(q, analysis, strategy)

        return recommendations

    def _random_sample(self, questions: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        """랜덤 샘플링"""
        if len(questions) <= count:
            return questions.copy()
        return random.sample(questions, count)

    def _get_recommendation_reason(
        self,
        question: Dict[str, Any],
        analysis: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> str:
        """추천 이유 생성"""
        domain = question.get("domain", "")
        difficulty = question.get("difficulty", "")

        weak_domains = [d["domain"] for d in analysis["weak_domains"]]

        if domain in weak_domains:
            domain_stats = next((d for d in analysis["weak_domains"] if d["domain"] == domain), None)
            if domain_stats:
                accuracy = domain_stats["accuracy"]
                return f"약점 도메인 '{domain}' 보완 (현재 정답률: {accuracy:.1f}%)"

        if difficulty == "hard":
            return f"고난이도 문제로 실력 향상 ({domain})"

        if difficulty == "easy":
            return f"기초 개념 다지기 ({domain})"

        return f"{domain} 도메인 연습"

    def _generate_learning_path(
        self,
        analysis: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """개인화된 학습 경로 생성"""
        path = []

        # 현재 레벨
        avg_score = analysis["avg_score"]
        if avg_score < 50:
            current_level = "초급"
        elif avg_score < 70:
            current_level = "중급"
        elif avg_score < 85:
            current_level = "고급"
        else:
            current_level = "전문가"

        # 단계별 학습 경로
        if avg_score < 50:
            path = [
                {
                    "step": 1,
                    "title": "기초 개념 학습",
                    "description": "Type A 세트 1-2 (연습 모드)",
                    "target": "약점 도메인 집중",
                    "goal": "50% 이상 달성"
                },
                {
                    "step": 2,
                    "title": "반복 학습",
                    "description": "약점 도메인 문제 반복",
                    "target": f"{', '.join([d['domain'] for d in analysis['weak_domains'][:3]])}",
                    "goal": "각 도메인 70% 이상"
                },
                {
                    "step": 3,
                    "title": "전체 복습",
                    "description": "Type A 세트 3-5",
                    "target": "모든 도메인 균형",
                    "goal": "60% 이상 안정적 달성"
                }
            ]
        elif avg_score < 70:
            path = [
                {
                    "step": 1,
                    "title": "약점 보완",
                    "description": "약점 도메인 집중 학습",
                    "target": f"{', '.join([d['domain'] for d in analysis['weak_domains'][:3]])}",
                    "goal": "약점 도메인 75% 이상"
                },
                {
                    "step": 2,
                    "title": "중급 문제 도전",
                    "description": "Type B 세트 1-3",
                    "target": "실전 시나리오",
                    "goal": "65% 이상 달성"
                },
                {
                    "step": 3,
                    "title": "합격선 돌파",
                    "description": "Type A 실전 모드",
                    "target": "2시간 시험",
                    "goal": "70% 이상 안정적 달성"
                }
            ]
        else:
            path = [
                {
                    "step": 1,
                    "title": "고난이도 문제",
                    "description": "Type B, C 모든 세트",
                    "target": "실전 시나리오",
                    "goal": "80% 이상 달성"
                },
                {
                    "step": 2,
                    "title": "실전 연습",
                    "description": "2시간 실전 모드 반복",
                    "target": "시간 관리 + 정확도",
                    "goal": "85% 이상 안정적 달성"
                },
                {
                    "step": 3,
                    "title": "완벽 마스터",
                    "description": "모든 타입 세트 완주",
                    "target": "종합 실력",
                    "goal": "90% 이상 달성"
                }
            ]

        # 현재 레벨 정보 추가
        for item in path:
            item["current_level"] = current_level
            item["current_score"] = avg_score

        return path
