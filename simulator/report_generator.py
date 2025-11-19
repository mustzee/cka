"""
시험 리포트 및 오답노트 생성기
"""

import json
from datetime import datetime
from typing import Dict, Any, List


class ReportGenerator:
    """시험 결과 리포트 생성기"""

    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir

    def generate_score_report(
        self, grade_result: Dict[str, Any], exam_info: Dict[str, Any]
    ) -> str:
        """
        점수 리포트 생성

        Args:
            grade_result: 채점 결과
            exam_info: 시험 정보

        Returns:
            리포트 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{self.output_dir}/score_report_{timestamp}.json"

        report = {
            "exam_info": exam_info,
            "timestamp": timestamp,
            "grade": grade_result,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return filepath

    def generate_wrong_answers_note(
        self,
        grade_result: Dict[str, Any],
        questions: List[Dict[str, Any]],
        exam_info: Dict[str, Any],
    ) -> str:
        """
        오답노트 생성

        Args:
            grade_result: 채점 결과
            questions: 문제 리스트
            exam_info: 시험 정보

        Returns:
            오답노트 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{self.output_dir}/wrong_answers_{timestamp}.md"

        # 문제를 ID로 매핑
        question_map = {q["id"]: q for q in questions}

        # 오답 문제만 필터링
        wrong_results = [r for r in grade_result["results"] if not r["passed"]]

        with open(filepath, "w", encoding="utf-8") as f:
            # 헤더
            f.write("# CKA 시험 오답노트\n\n")
            f.write(f"**시험 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**시험 타입**: {exam_info.get('type', 'A')}\n\n")
            f.write(
                f"**총점**: {grade_result['percentage']:.1f}% ({grade_result['total_score']:.1f}/{grade_result['total_weight']})\n\n"
            )
            f.write(f"**오답 수**: {len(wrong_results)}/{grade_result['total_questions']}\n\n")
            f.write("---\n\n")

            # 통계
            f.write("## 📊 오답 통계\n\n")

            if wrong_results:
                # 도메인별 오답
                domain_errors = {}
                for result in wrong_results:
                    q_id = result["question_id"]
                    if q_id in question_map:
                        domain = question_map[q_id].get("domain", "Unknown")
                        domain_errors[domain] = domain_errors.get(domain, 0) + 1

                f.write("### 도메인별 오답 분포\n\n")
                for domain, count in sorted(
                    domain_errors.items(), key=lambda x: x[1], reverse=True
                ):
                    f.write(f"- **{domain}**: {count}개\n")
                f.write("\n")

                # 난이도별 오답
                difficulty_errors = {}
                for result in wrong_results:
                    q_id = result["question_id"]
                    if q_id in question_map:
                        difficulty = question_map[q_id].get("difficulty", "unknown")
                        difficulty_errors[difficulty] = (
                            difficulty_errors.get(difficulty, 0) + 1
                        )

                f.write("### 난이도별 오답 분포\n\n")
                for difficulty, count in sorted(difficulty_errors.items()):
                    f.write(f"- **{difficulty}**: {count}개\n")
                f.write("\n")

            f.write("---\n\n")

            # 오답 문제 상세
            f.write("## ❌ 오답 문제 상세\n\n")

            if not wrong_results:
                f.write("축하합니다! 모든 문제를 맞히셨습니다. 🎉\n\n")
            else:
                for idx, result in enumerate(wrong_results, 1):
                    q_id = result["question_id"]
                    if q_id not in question_map:
                        continue

                    question = question_map[q_id]

                    f.write(f"### {idx}. {question['title']}\n\n")
                    f.write(f"**문제 ID**: {q_id}\n\n")
                    f.write(f"**도메인**: {question.get('domain', 'Unknown')}\n\n")
                    f.write(f"**난이도**: {question.get('difficulty', 'unknown')}\n\n")
                    f.write(f"**배점**: {question.get('weight', 0)}점\n\n")
                    f.write(
                        f"**획득 점수**: {result['score']:.1f}/{result['weight']}\n\n"
                    )

                    # 문제 설명
                    f.write("#### 📝 문제\n\n")
                    f.write(f"{question.get('description', '')}\n\n")
                    f.write(f"{question.get('task', '')}\n\n")

                    # 채점 상세
                    f.write("#### 🔍 채점 결과\n\n")
                    for detail in result.get("details", []):
                        status = "✅" if detail["passed"] else "❌"
                        f.write(f"{status} **{detail['check']}**: {detail['message']}\n\n")

                    # 정답 및 해설
                    f.write("#### ✅ 정답\n\n")
                    f.write("```bash\n")
                    f.write(f"{question.get('solution', '해결 방법이 제공되지 않았습니다.')}\n")
                    f.write("```\n\n")

                    f.write("#### 💡 해설\n\n")
                    f.write(f"{question.get('explanation', '해설이 제공되지 않았습니다.')}\n\n")

                    # 참고 자료
                    if "references" in question and question["references"]:
                        f.write("#### 📚 참고 자료\n\n")
                        for ref in question["references"]:
                            f.write(f"- {ref}\n")
                        f.write("\n")

                    f.write("---\n\n")

            # 맺음말
            f.write("## 📖 학습 제안\n\n")
            if wrong_results:
                f.write("오답 문제를 다시 풀어보고, 참고 자료를 통해 개념을 복습하세요.\n\n")
                f.write("특히 다음 도메인에 집중하세요:\n\n")

                # 오답이 많은 도메인 추천
                domain_errors = {}
                for result in wrong_results:
                    q_id = result["question_id"]
                    if q_id in question_map:
                        domain = question_map[q_id].get("domain", "Unknown")
                        domain_errors[domain] = domain_errors.get(domain, 0) + 1

                for domain, count in sorted(
                    domain_errors.items(), key=lambda x: x[1], reverse=True
                ):
                    f.write(f"- **{domain}** ({count}개 오답)\n")
                f.write("\n")
            else:
                f.write("완벽합니다! 더 어려운 문제로 도전해보세요.\n\n")

            f.write("좋은 학습 되세요! 🚀\n")

        return filepath

    def generate_summary_report(
        self,
        grade_result: Dict[str, Any],
        questions: List[Dict[str, Any]],
        exam_info: Dict[str, Any],
    ) -> str:
        """
        요약 리포트 생성 (터미널 출력용)

        Args:
            grade_result: 채점 결과
            questions: 문제 리스트
            exam_info: 시험 정보

        Returns:
            포맷된 요약 문자열
        """
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("CKA 시험 결과".center(80))
        lines.append("=" * 80)
        lines.append("")

        # 기본 정보
        lines.append(f"시험 타입: {exam_info.get('type', 'A')}")
        lines.append(f"문제 수: {grade_result['total_questions']}")
        lines.append(f"소요 시간: {exam_info.get('elapsed_time', 'N/A')}")
        lines.append("")

        # 점수
        percentage = grade_result["percentage"]
        passed = grade_result["passed"]
        status = "✅ 합격" if passed else "❌ 불합격"

        lines.append(f"총점: {grade_result['total_score']:.1f}/{grade_result['total_weight']}")
        lines.append(f"정답률: {percentage:.1f}%")
        lines.append(f"결과: {status} (합격 기준: 66%)")
        lines.append("")

        # 문제별 결과
        lines.append("-" * 80)
        lines.append("문제별 결과:")
        lines.append("-" * 80)

        for result in grade_result["results"]:
            status = "✅" if result["passed"] else "❌"
            lines.append(
                f"{status} {result['question_id']}: {result['title']} "
                f"({result['score']:.1f}/{result['weight']})"
            )

        lines.append("")
        lines.append("=" * 80)

        # 파일 위치
        lines.append("")
        lines.append("📁 상세 결과는 다음 파일에서 확인하세요:")
        lines.append(f"   - results/score_report_*.json")
        lines.append(f"   - results/wrong_answers_*.md")
        lines.append("")

        return "\n".join(lines)
