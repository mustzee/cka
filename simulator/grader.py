"""
자동 채점 시스템
"""

import subprocess
import json
import re
import os
import tempfile
from typing import Dict, Any, List, Tuple, Optional
import yaml


class AutoGrader:
    """CKA 시험 자동 채점기 (고급 기능 포함)"""

    def __init__(self):
        self.kubectl_cmd = "kubectl"
        self.jq_available = self._check_jq_available()

    def _check_jq_available(self) -> bool:
        """jq 명령어 사용 가능 여부 확인"""
        try:
            subprocess.run(["jq", "--version"], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """
        일반 명령어 실행 (고급 기능)

        Args:
            cmd: 명령어 리스트
            timeout: 타임아웃 (초)

        Returns:
            (성공 여부, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return (
                result.returncode == 0,
                result.stdout.strip(),
                result.stderr.strip(),
            )
        except subprocess.TimeoutExpired:
            return False, "", "명령어 실행 시간 초과"
        except Exception as e:
            return False, "", f"오류: {str(e)}"

    def run_kubectl(self, args: List[str]) -> Tuple[bool, str]:
        """
        kubectl 명령어 실행

        Args:
            args: kubectl 인자 리스트

        Returns:
            (성공 여부, 출력)
        """
        try:
            result = subprocess.run(
                [self.kubectl_cmd] + args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "명령어 실행 시간 초과"
        except Exception as e:
            return False, f"오류: {str(e)}"

    def check_resource_exists(
        self, resource_type: str, name: str, namespace: str = None
    ) -> Tuple[bool, str]:
        """
        리소스 존재 여부 확인

        Args:
            resource_type: 리소스 타입 (pod, deployment, service, 등)
            name: 리소스 이름
            namespace: 네임스페이스 (선택사항)

        Returns:
            (존재 여부, 메시지)
        """
        args = ["get", resource_type, name, "-o", "json"]
        if namespace:
            args.extend(["-n", namespace])

        success, output = self.run_kubectl(args)

        if not success:
            return False, f"{resource_type}/{name} 리소스를 찾을 수 없습니다"

        return True, f"{resource_type}/{name} 리소스 확인됨"

    def check_field_value(
        self,
        resource_type: str,
        name: str,
        field_path: str,
        expected_value: Any,
        namespace: str = None,
    ) -> Tuple[bool, str]:
        """
        리소스의 특정 필드 값 확인

        Args:
            resource_type: 리소스 타입
            name: 리소스 이름
            field_path: 필드 경로 (예: spec.replicas)
            expected_value: 기대값
            namespace: 네임스페이스

        Returns:
            (일치 여부, 메시지)
        """
        args = ["get", resource_type, name, "-o", "json"]
        if namespace:
            args.extend(["-n", namespace])

        success, output = self.run_kubectl(args)

        if not success:
            return False, f"리소스를 조회할 수 없습니다: {output}"

        try:
            resource = json.loads(output)

            # 중첩된 필드 경로 처리
            current = resource
            for part in field_path.split("."):
                # 배열 인덱스 처리 (예: containers[0])
                if "[" in part:
                    key, rest = part.split("[", 1)
                    index = int(rest.rstrip("]"))
                    current = current[key][index]
                else:
                    current = current[part]

            actual_value = current

            # 타입 변환 후 비교
            if isinstance(expected_value, int):
                actual_value = int(actual_value)
            elif isinstance(expected_value, str):
                actual_value = str(actual_value)

            if actual_value == expected_value:
                return True, f"{field_path} = {actual_value} (정답)"
            else:
                return False, f"{field_path} = {actual_value} (기대값: {expected_value})"

        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
            return False, f"필드 확인 실패: {str(e)}"

    def check_pod_ready(
        self, name: str, namespace: str = "default"
    ) -> Tuple[bool, str]:
        """
        Pod Ready 상태 확인

        Args:
            name: Pod 이름
            namespace: 네임스페이스

        Returns:
            (Ready 여부, 메시지)
        """
        args = ["get", "pod", name, "-n", namespace, "-o", "json"]
        success, output = self.run_kubectl(args)

        if not success:
            return False, f"Pod를 찾을 수 없습니다: {name}"

        try:
            pod = json.loads(output)
            conditions = pod.get("status", {}).get("conditions", [])

            for condition in conditions:
                if condition.get("type") == "Ready":
                    if condition.get("status") == "True":
                        return True, f"Pod {name}이 Ready 상태입니다"
                    else:
                        reason = condition.get("reason", "Unknown")
                        return False, f"Pod {name}이 Ready가 아닙니다. 이유: {reason}"

            return False, f"Pod {name}의 Ready 조건을 찾을 수 없습니다"

        except (json.JSONDecodeError, KeyError) as e:
            return False, f"Pod 상태 확인 실패: {str(e)}"

    def check_file_exists(self, filepath: str) -> Tuple[bool, str]:
        """
        파일 존재 여부 확인

        Args:
            filepath: 파일 경로

        Returns:
            (존재 여부, 메시지)
        """
        try:
            result = subprocess.run(
                ["test", "-f", filepath], capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return True, f"파일 존재함: {filepath}"
            else:
                return False, f"파일을 찾을 수 없습니다: {filepath}"
        except Exception as e:
            return False, f"파일 확인 실패: {str(e)}"

    def grade_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        문제 채점

        Args:
            question: 문제 딕셔너리

        Returns:
            채점 결과
        """
        validation = question.get("validation", {})
        checks = validation.get("checks", [])

        results = []
        total_checks = len(checks)
        passed_checks = 0

        for check in checks:
            resource = check.get("resource")
            name = check.get("name")
            namespace = check.get("namespace")

            # 리소스 존재 확인
            exists, msg = self.check_resource_exists(resource, name, namespace)

            if not exists:
                results.append(
                    {"check": f"{resource}/{name}", "passed": False, "message": msg}
                )
                continue

            # 조건 확인
            conditions = check.get("conditions", [])
            all_conditions_passed = True

            if not conditions:
                # 조건이 없으면 존재만 확인
                passed_checks += 1
                results.append(
                    {"check": f"{resource}/{name}", "passed": True, "message": msg}
                )
                continue

            for condition in conditions:
                if "type" in condition:
                    # Pod Ready 상태 확인
                    if resource == "pod" and condition.get("type") == "Ready":
                        ready, ready_msg = self.check_pod_ready(name, namespace)
                        if not ready:
                            all_conditions_passed = False
                            results.append(
                                {
                                    "check": f"{resource}/{name} Ready",
                                    "passed": False,
                                    "message": ready_msg,
                                }
                            )

                elif "field" in condition:
                    # 필드 값 확인
                    field = condition.get("field")
                    expected = condition.get("value")
                    field_ok, field_msg = self.check_field_value(
                        resource, name, field, expected, namespace
                    )

                    if not field_ok:
                        all_conditions_passed = False

                    results.append(
                        {
                            "check": f"{resource}/{name} {field}",
                            "passed": field_ok,
                            "message": field_msg,
                        }
                    )

            if all_conditions_passed:
                passed_checks += 1

        # 점수 계산
        weight = question.get("weight", 1)
        if total_checks > 0:
            score = (passed_checks / total_checks) * weight
        else:
            score = 0

        return {
            "question_id": question.get("id"),
            "title": question.get("title"),
            "weight": weight,
            "score": score,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "passed": passed_checks == total_checks,
            "details": results,
        }

    def grade_exam(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        전체 시험 채점

        Args:
            questions: 문제 리스트

        Returns:
            전체 채점 결과
        """
        results = []
        total_weight = sum(q.get("weight", 0) for q in questions)
        total_score = 0

        for question in questions:
            result = self.grade_question(question)
            results.append(result)
            total_score += result["score"]

        percentage = (total_score / total_weight * 100) if total_weight > 0 else 0
        passed = percentage >= 66  # CKA 합격 기준

        return {
            "total_questions": len(questions),
            "total_weight": total_weight,
            "total_score": total_score,
            "percentage": percentage,
            "passed": passed,
            "results": results,
        }
