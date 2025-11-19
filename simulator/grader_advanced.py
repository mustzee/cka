"""
고급 채점 기능 확장
"""

import subprocess
import json
import re
import os
import tempfile
from typing import Dict, Any, List, Tuple, Optional


class AdvancedGrader:
    """고급 채점 기능을 제공하는 클래스"""

    def __init__(self):
        self.jq_available = self._check_jq_available()

    def _check_jq_available(self) -> bool:
        """jq 사용 가능 여부 확인"""
        try:
            subprocess.run(["jq", "--version"], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run_command(
        self, cmd: List[str], timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """
        명령어 실행

        Args:
            cmd: 명령어 리스트
            timeout: 타임아웃

        Returns:
            (성공 여부, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return (
                result.returncode == 0,
                result.stdout.strip(),
                result.stderr.strip(),
            )
        except subprocess.TimeoutExpired:
            return False, "", "시간 초과"
        except Exception as e:
            return False, "", str(e)

    def check_command_output(
        self,
        command: str,
        expected_output: Optional[str] = None,
        contains: Optional[str] = None,
        regex_pattern: Optional[str] = None,
        exit_code: int = 0,
    ) -> Tuple[bool, str]:
        """
        명령어 출력 검증

        Args:
            command: 실행할 명령어
            expected_output: 정확한 출력값
            contains: 포함해야 할 문자열
            regex_pattern: 정규식 패턴
            exit_code: 예상 종료 코드

        Returns:
            (검증 성공, 메시지)
        """
        # 명령어 실행
        success, stdout, stderr = self.run_command(command.split())

        # 종료 코드 확인
        if (success and exit_code != 0) or (not success and exit_code == 0):
            return False, f"종료 코드 불일치 (예상: {exit_code})"

        output = stdout

        # 정확한 출력 비교
        if expected_output is not None:
            if output == expected_output:
                return True, "출력 일치"
            else:
                return False, f"출력 불일치\n예상: {expected_output}\n실제: {output}"

        # 문자열 포함 확인
        if contains is not None:
            if contains in output:
                return True, f"'{contains}' 포함됨"
            else:
                return False, f"'{contains}' 포함되지 않음"

        # 정규식 매칭
        if regex_pattern is not None:
            if re.search(regex_pattern, output):
                return True, f"패턴 '{regex_pattern}' 매칭됨"
            else:
                return False, f"패턴 '{regex_pattern}' 매칭 안됨"

        return True, "명령어 실행 성공"

    def check_with_jq(
        self, kubectl_command: str, jq_filter: str, expected_value: Any
    ) -> Tuple[bool, str]:
        """
        JQ 필터를 사용한 검증

        Args:
            kubectl_command: kubectl 명령어
            jq_filter: jq 필터 표현식
            expected_value: 기대값

        Returns:
            (검증 성공, 메시지)
        """
        if not self.jq_available:
            return False, "jq가 설치되어 있지 않습니다"

        # kubectl 실행
        success, stdout, stderr = self.run_command(kubectl_command.split())
        if not success:
            return False, f"kubectl 실행 실패: {stderr}"

        # jq 필터 적용
        try:
            jq_process = subprocess.run(
                ["jq", "-r", jq_filter],
                input=stdout,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if jq_process.returncode != 0:
                return False, f"jq 필터 오류: {jq_process.stderr}"

            result = jq_process.stdout.strip()

            # 타입 변환
            if isinstance(expected_value, int):
                result = int(result) if result.isdigit() else result
            elif isinstance(expected_value, bool):
                result = result.lower() == "true"

            if result == expected_value or str(result) == str(expected_value):
                return True, f"JQ 결과 일치: {result}"
            else:
                return False, f"JQ 결과 불일치 (예상: {expected_value}, 실제: {result})"

        except Exception as e:
            return False, f"JQ 처리 오류: {str(e)}"

    def check_custom_script(
        self, script_path: str, script_content: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        커스텀 검증 스크립트 실행

        Args:
            script_path: 스크립트 파일 경로
            script_content: 스크립트 내용 (파일 대신)

        Returns:
            (검증 성공, 메시지)
        """
        # 임시 스크립트 파일 생성
        if script_content:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".sh", delete=False
            ) as f:
                f.write("#!/bin/bash\n")
                f.write(script_content)
                script_path = f.name

            # 실행 권한 부여
            os.chmod(script_path, 0o755)

        try:
            # 스크립트 실행
            result = subprocess.run(
                ["/bin/bash", script_path],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # 종료 코드로 성공/실패 판단
            if result.returncode == 0:
                return True, f"스크립트 검증 성공\n{result.stdout}"
            else:
                return False, f"스크립트 검증 실패\n{result.stderr or result.stdout}"

        except subprocess.TimeoutExpired:
            return False, "스크립트 실행 시간 초과 (60초)"
        except Exception as e:
            return False, f"스크립트 실행 오류: {str(e)}"
        finally:
            # 임시 파일 정리
            if script_content and os.path.exists(script_path):
                os.unlink(script_path)

    def check_json_path(
        self, json_data: str, json_path: str, expected_value: Any
    ) -> Tuple[bool, str]:
        """
        JSON Path를 사용한 검증

        Args:
            json_data: JSON 문자열
            json_path: JSON Path 표현식
            expected_value: 기대값

        Returns:
            (검증 성공, 메시지)
        """
        try:
            data = json.loads(json_data)

            # 간단한 JSON Path 구현 (. 기반)
            current = data
            for key in json_path.strip("$.").split("."):
                if "[" in key:
                    # 배열 인덱스 처리
                    field, rest = key.split("[", 1)
                    index = int(rest.rstrip("]"))
                    current = current[field][index]
                else:
                    current = current[key]

            if current == expected_value or str(current) == str(expected_value):
                return True, f"값 일치: {current}"
            else:
                return False, f"값 불일치 (예상: {expected_value}, 실제: {current})"

        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
            return False, f"JSON Path 오류: {str(e)}"

    def check_yaml_content(
        self, yaml_file: str, yaml_path: str, expected_value: Any
    ) -> Tuple[bool, str]:
        """
        YAML 파일 내용 검증

        Args:
            yaml_file: YAML 파일 경로
            yaml_path: YAML 경로 (점 표기법)
            expected_value: 기대값

        Returns:
            (검증 성공, 메시지)
        """
        try:
            with open(yaml_file, "r") as f:
                data = yaml.safe_load(f)

            # 경로 탐색
            current = data
            for key in yaml_path.split("."):
                if "[" in key:
                    field, rest = key.split("[", 1)
                    index = int(rest.rstrip("]"))
                    current = current[field][index]
                else:
                    current = current[key]

            if current == expected_value or str(current) == str(expected_value):
                return True, f"YAML 값 일치: {current}"
            else:
                return (
                    False,
                    f"YAML 값 불일치 (예상: {expected_value}, 실제: {current})",
                )

        except FileNotFoundError:
            return False, f"파일을 찾을 수 없습니다: {yaml_file}"
        except Exception as e:
            return False, f"YAML 검증 오류: {str(e)}"

    def check_line_count(
        self, command: str, expected_count: int, operator: str = "=="
    ) -> Tuple[bool, str]:
        """
        명령어 출력 라인 수 검증

        Args:
            command: 실행할 명령어
            expected_count: 예상 라인 수
            operator: 비교 연산자 (==, >=, <=, >, <)

        Returns:
            (검증 성공, 메시지)
        """
        success, stdout, stderr = self.run_command(command.split())

        if not success:
            return False, f"명령어 실행 실패: {stderr}"

        lines = stdout.strip().split("\n") if stdout.strip() else []
        actual_count = len(lines)

        # 연산자에 따라 비교
        operators = {
            "==": actual_count == expected_count,
            ">=": actual_count >= expected_count,
            "<=": actual_count <= expected_count,
            ">": actual_count > expected_count,
            "<": actual_count < expected_count,
        }

        if operators.get(operator, False):
            return True, f"라인 수 조건 만족: {actual_count} {operator} {expected_count}"
        else:
            return (
                False,
                f"라인 수 조건 불만족: {actual_count} {operator} {expected_count}",
            )
