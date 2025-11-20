#!/usr/bin/env python3
"""
CKA 시험 시뮬레이터 메인 애플리케이션
"""

import os
import sys
import click
import time
import subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from question_loader import QuestionLoader
from timer import ExamTimer
from grader import AutoGrader
from report_generator import ReportGenerator
from chaos_engineer import ChaosEngineering


console = Console()


class CKASimulator:
    """CKA 시험 시뮬레이터"""

    def __init__(self, exam_type: str = "A", practice_mode: bool = False, show_hints: bool = False, hard_mode: bool = False, ultra_mode: bool = False):
        self.exam_type = exam_type.upper()
        self.practice_mode = practice_mode
        self.show_hints = show_hints  # 힌트 표시 여부
        self.hard_mode = hard_mode  # 실전 모드 (힌트 완전 제거)
        self.ultra_mode = ultra_mode  # 🔥 Ultra 모드 (Chaos Engineering + 실전 난이도)
        self.loader = QuestionLoader()
        self.grader = AutoGrader()
        self.reporter = ReportGenerator()
        self.timer = ExamTimer(duration_minutes=120 if not practice_mode else 999999)
        self.chaos = ChaosEngineering(enabled=ultra_mode)  # Chaos Engineering
        self.questions = []
        self.current_question_idx = 0
        self.auto_yes = False  # 자동 확인 모드
        self.context_errors = 0  # Context 전환 오류 횟수

    def show_welcome(self):
        """환영 메시지 표시"""
        mode_description = '연습 모드 (타이머 없음)' if self.practice_mode else '실전 모드 (2시간)'
        if self.ultra_mode:
            mode_description += ' - 💀 ULTRA MODE (Chaos Engineering + 무작위 장애 + 힌트 없음)'
        elif self.hard_mode:
            mode_description += ' - 🔥 HARD MODE (힌트 없음, 실전 난이도)'
        elif self.show_hints:
            mode_description += ' - 💡 힌트 표시 모드'
        else:
            mode_description += ' - 힌트 숨김 모드'

        welcome_text = f"""
[bold cyan]Kubernetes CKA 시험 시뮬레이터[/bold cyan]

시험 타입: [bold]{self.exam_type}[/bold]
모드: [bold]{mode_description}[/bold]

[yellow]실제 CKA 시험과 동일한 환경에서 진행됩니다.[/yellow]

[bold green]준비사항:[/bold green]
✓ Kubernetes 클러스터가 실행 중이어야 합니다 (멀티 클러스터 권장)
✓ kubectl 명령어를 사용할 수 있어야 합니다
✓ 터미널을 별도로 열어서 작업하세요

[bold red]주의사항:[/bold red]
• 시험 중에는 시뮬레이터를 종료하지 마세요
• [bold red]각 문제마다 올바른 context로 전환하세요 (kubectl config use-context <cluster>)[/bold red]
• Context 전환을 잊으면 0점 처리될 수 있습니다!
• 시간이 종료되면 자동으로 채점됩니다

[dim]💡 힌트가 필요하면 --hints 플래그를 사용하세요
🔥 실전처럼 연습하려면 --hard 플래그를 사용하세요[/dim]
        """

        console.print(Panel(welcome_text, border_style="cyan"))

    def load_questions(self):
        """문제 로드"""
        try:
            with console.status(
                f"[bold green]문제를 로드하는 중...", spinner="dots"
            ):
                self.questions = self.loader.load_questions(self.exam_type)

            if not self.questions:
                console.print(
                    f"[bold red]오류: {self.exam_type} 타입의 문제를 찾을 수 없습니다.[/bold red]"
                )
                sys.exit(1)

            console.print(
                f"[bold green]✓ {len(self.questions)}개의 문제를 로드했습니다.[/bold green]\n"
            )

        except Exception as e:
            console.print(f"[bold red]문제 로드 실패: {str(e)}[/bold red]")
            sys.exit(1)

    def show_question_list(self):
        """문제 목록 표시"""
        table = Table(title="시험 문제 목록", show_header=True, header_style="bold magenta")
        table.add_column("번호", style="cyan", width=6)
        table.add_column("ID", style="green", width=10)
        table.add_column("제목", style="white", width=40)
        table.add_column("도메인", style="yellow", width=25)
        table.add_column("난이도", style="blue", width=10)
        table.add_column("배점", style="red", width=8)

        for idx, question in enumerate(self.questions, 1):
            table.add_row(
                str(idx),
                question.get("id", ""),
                question.get("title", ""),
                question.get("domain", ""),
                question.get("difficulty", ""),
                str(question.get("weight", 0)),
            )

        console.print(table)
        console.print()

    def show_question(self, question: dict):
        """문제 표시"""
        console.print("\n" + "=" * 80)
        console.print(
            f"[bold cyan]문제 {self.current_question_idx + 1}/{len(self.questions)}[/bold cyan]"
        )
        console.print("=" * 80)

        console.print(f"\n[bold]제목:[/bold] {question.get('title', '')}")
        console.print(f"[bold]도메인:[/bold] {question.get('domain', '')}")
        console.print(f"[bold]난이도:[/bold] {question.get('difficulty', '')}")
        console.print(f"[bold]배점:[/bold] {question.get('weight', 0)}점")
        console.print(
            f"[bold]예상 소요 시간:[/bold] {question.get('time_estimate', 0)}분"
        )

        # Context 정보 표시 (있는 경우)
        if "context" in question and question["context"]:
            console.print(f"[bold red]⚠️  Required Context:[/bold red] [bold yellow]{question['context']}[/bold yellow]")
            console.print(f"[dim]→ kubectl config use-context {question['context']}[/dim]")

        console.print(f"\n[bold yellow]문제:[/bold yellow]")
        console.print(question.get("description", ""))
        console.print(question.get("task", ""))

        # 힌트 표시 로직
        if not self.hard_mode and not self.ultra_mode and "hints" in question and question["hints"]:
            if self.show_hints:
                # --hints 플래그가 있으면 힌트 표시
                console.print(f"\n[bold green]💡 힌트:[/bold green]")
                for hint in question["hints"]:
                    console.print(f"  • {hint}")
            else:
                # 기본 모드: 힌트 숨김 (힌트가 있다는 것만 알림)
                console.print(f"\n[dim]💡 힌트가 숨겨져 있습니다. --hints 플래그로 실행하면 볼 수 있습니다.[/dim]")

        console.print("\n" + "-" * 80)
        console.print(
            "[bold]별도 터미널에서 작업을 수행하세요. 완료되면 여기로 돌아오세요.[/bold]"
        )
        console.print("-" * 80 + "\n")

    def check_context(self, question: dict) -> bool:
        """현재 kubectl context가 문제에서 요구하는 context인지 확인"""
        required_context = question.get("context")
        if not required_context:
            # Context가 지정되지 않은 문제는 검사하지 않음
            return True

        try:
            import subprocess
            result = subprocess.run(
                ["kubectl", "config", "current-context"],
                capture_output=True,
                text=True,
                timeout=5
            )
            current_context = result.stdout.strip()

            if current_context != required_context:
                console.print(f"\n[bold red]⚠️  Context 오류![/bold red]")
                console.print(f"  현재 Context: [yellow]{current_context}[/yellow]")
                console.print(f"  필요한 Context: [green]{required_context}[/green]")
                console.print(f"\n  [bold]다음 명령어를 실행하세요:[/bold]")
                console.print(f"  [cyan]kubectl config use-context {required_context}[/cyan]\n")
                self.context_errors += 1
                return False

            return True

        except Exception as e:
            console.print(f"[yellow]⚠️  Context 확인 실패: {str(e)}[/yellow]")
            return True  # 확인 실패 시 진행 허용

    def show_timer(self):
        """타이머 표시"""
        if self.practice_mode:
            return

        remaining = self.timer.get_remaining_formatted()
        elapsed = self.timer.get_elapsed_formatted()
        progress = self.timer.get_progress_percentage()

        if self.timer.is_expired():
            console.print("[bold red]⏰ 시간이 종료되었습니다![/bold red]")
        else:
            console.print(
                f"[bold]⏱️  경과: {elapsed} | 남은 시간: {remaining} | 진행률: {progress:.1f}%[/bold]"
            )

    def run_exam(self):
        """시험 실행"""
        # 환영 메시지
        self.show_welcome()

        # 자동 확인 모드가 아닐 때만 물어봄
        if not self.auto_yes:
            try:
                if not Confirm.ask("\n시험을 시작하시겠습니까?"):
                    console.print("[yellow]시험이 취소되었습니다.[/yellow]")
                    return
            except EOFError:
                # 비대화형 환경에서는 자동으로 시작
                console.print("[yellow]비대화형 모드: 자동으로 시험을 시작합니다...[/yellow]")
        else:
            console.print("[yellow]자동 확인 모드: 시험을 시작합니다...[/yellow]")

        # 문제 로드
        self.load_questions()

        # 문제 목록 표시
        self.show_question_list()

        # 타이머 시작
        self.timer.start()
        start_time = datetime.now()

        # Chaos Engineering 시작 (Ultra Mode)
        if self.ultra_mode:
            self.chaos.inject_random_failures(duration_minutes=120)

        console.print("[bold green]시험이 시작되었습니다![/bold green]\n")

        # 문제 진행
        while self.current_question_idx < len(self.questions):
            if not self.practice_mode and self.timer.is_expired():
                console.print("\n[bold red]⏰ 시험 시간이 종료되었습니다![/bold red]")
                break

            question = self.questions[self.current_question_idx]

            # Context 확인 (실전 모드나 hard/ultra 모드에서)
            if not self.practice_mode or self.hard_mode or self.ultra_mode:
                self.check_context(question)

            self.show_question(question)
            self.show_timer()

            # 사용자 입력 대기
            try:
                choice = Prompt.ask(
                    "\n선택하세요",
                    choices=["next", "prev", "list", "skip", "finish", "quit"],
                    default="next",
                )
            except EOFError:
                # 비대화형 환경에서는 자동으로 다음 문제로
                choice = "next"
                console.print("[dim]비대화형 모드: 자동으로 다음 문제로 진행...[/dim]")

            if choice == "next":
                if self.current_question_idx < len(self.questions) - 1:
                    self.current_question_idx += 1
                else:
                    console.print(
                        "[yellow]마지막 문제입니다. 'finish'를 선택하여 시험을 종료하세요.[/yellow]"
                    )

            elif choice == "prev":
                if self.current_question_idx > 0:
                    self.current_question_idx -= 1
                else:
                    console.print("[yellow]첫 번째 문제입니다.[/yellow]")

            elif choice == "list":
                self.show_question_list()

            elif choice == "skip":
                if self.current_question_idx < len(self.questions) - 1:
                    self.current_question_idx += 1

            elif choice == "finish":
                try:
                    if self.auto_yes or Confirm.ask("\n시험을 종료하고 채점하시겠습니까?"):
                        break
                except EOFError:
                    break

            elif choice == "quit":
                try:
                    if self.auto_yes or Confirm.ask("\n정말로 시험을 중단하시겠습니까? (채점되지 않습니다)"):
                        console.print("[yellow]시험이 중단되었습니다.[/yellow]")
                        return
                except EOFError:
                    console.print("[yellow]시험이 중단되었습니다.[/yellow]")
                    return

        # Chaos Engineering 정리 (Ultra Mode)
        if self.ultra_mode:
            console.print("\n[yellow]Chaos Engineering 리소스 정리 중...[/yellow]")
            self.chaos.cleanup()

        # 채점
        console.print("\n[bold cyan]채점 중...[/bold cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("문제를 채점하는 중...", total=None)
            grade_result = self.grader.grade_exam(self.questions)
            progress.update(task, completed=True)

        # 경과 시간
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        elapsed_str = str(elapsed_time).split(".")[0]

        exam_info = {
            "type": self.exam_type,
            "practice_mode": self.practice_mode,
            "hard_mode": self.hard_mode,
            "ultra_mode": self.ultra_mode,
            "show_hints": self.show_hints,
            "context_errors": self.context_errors,
            "chaos_report": self.chaos.get_failure_report() if self.ultra_mode else None,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "elapsed_time": elapsed_str,
        }

        # 리포트 생성
        console.print("\n[bold cyan]리포트 생성 중...[/bold cyan]\n")

        score_file = self.reporter.generate_score_report(grade_result, exam_info)
        wrong_file = self.reporter.generate_wrong_answers_note(
            grade_result, self.questions, exam_info
        )

        # 요약 출력
        summary = self.reporter.generate_summary_report(
            grade_result, self.questions, exam_info
        )
        console.print(summary)

        console.print(f"[bold green]점수 리포트:[/bold green] {score_file}")
        console.print(f"[bold green]오답노트:[/bold green] {wrong_file}")
        console.print()


@click.command()
@click.option(
    "--type",
    "-t",
    "exam_type",
    default="A",
    type=click.Choice(["A", "B", "C", "a", "b", "c"], case_sensitive=False),
    help="시험 타입 (A: 기본, B: 고급, C: 실전)",
)
@click.option(
    "--practice",
    "-p",
    is_flag=True,
    help="연습 모드 (타이머 없음)",
)
@click.option(
    "--hints",
    is_flag=True,
    help="힌트 표시 모드 (학습용)",
)
@click.option(
    "--hard",
    is_flag=True,
    help="🔥 HARD MODE (힌트 완전 제거, 실전 난이도)",
)
@click.option(
    "--ultra",
    is_flag=True,
    help="💀 ULTRA MODE (Chaos Engineering + 무작위 장애 + 힌트 없음 + 실전 난이도)",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="모든 확인 질문에 자동으로 yes 응답 (비대화형 모드)",
)
@click.option(
    "--list-only",
    "-l",
    is_flag=True,
    help="문제 목록만 표시하고 종료 (클러스터 불필요)",
)
@click.option(
    "--reset",
    "-r",
    is_flag=True,
    help="🔄 시험 환경 리셋 (모든 시험 관련 리소스 삭제)",
)
def main(exam_type, practice, hints, hard, ultra, yes, list_only, reset):
    """
    CKA 시험 시뮬레이터

    실제 CKA 시험과 동일한 환경에서 연습할 수 있습니다.
    """
    try:
        # 결과 디렉토리 생성
        os.makedirs("results", exist_ok=True)
        
        # 리셋 모드
        if reset:
            console.print("[bold yellow]🔄 시험 환경 리셋을 시작합니다...[/bold yellow]\\n")
            
            try:
                if not yes and not Confirm.ask("정말로 모든 시험 관련 리소스를 삭제하시겠습니까? (되돌릴 수 없습니다)"):
                    console.print("[yellow]리셋이 취소되었습니다.[/yellow]")
                    return
            except EOFError:
                console.print("[yellow]비대화형 모드: 자동으로 리셋을 진행합니다...[/yellow]")
                
            # 리셋 스크립트 실행
            reset_script = os.path.join(os.path.dirname(__file__), "..", "scripts", "reset-exam.sh")
            if os.path.exists(reset_script):
                result = subprocess.run(["/bin/bash", reset_script], 
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    console.print("[bold green]✅ 시험 환경 리셋이 완료되었습니다![/bold green]")
                    console.print("[dim]새로운 시험을 시작할 수 있습니다.[/dim]")
                else:
                    console.print(f"[bold red]❌ 리셋 실패:[/bold red] {result.stderr}")
            else:
                console.print("[bold red]❌ 리셋 스크립트를 찾을 수 없습니다.[/bold red]")
            return

        # 모드 충돌 검사
        if ultra and hints:
            console.print("[bold red]❌ --ultra와 --hints는 동시에 사용할 수 없습니다.[/bold red]")
            console.print("[yellow]--ultra: Ultra Mode (Chaos Engineering + 힌트 없음)[/yellow]")
            console.print("[yellow]--hints: 힌트 표시 (학습 모드)[/yellow]")
            sys.exit(1)

        if ultra and hard:
            console.print("[bold red]❌ --ultra와 --hard는 동시에 사용할 수 없습니다.[/bold red]")
            console.print("[yellow]--ultra는 hard 모드를 포함합니다 (더 어려움)[/yellow]")
            sys.exit(1)

        if hard and hints:
            console.print("[bold red]❌ --hard와 --hints는 동시에 사용할 수 없습니다.[/bold red]")
            console.print("[yellow]--hard: 힌트 완전 제거 (실전 모드)[/yellow]")
            console.print("[yellow]--hints: 힌트 표시 (학습 모드)[/yellow]")
            sys.exit(1)

        # 시뮬레이터 생성
        simulator = CKASimulator(
            exam_type=exam_type,
            practice_mode=practice,
            show_hints=hints,
            hard_mode=hard,
            ultra_mode=ultra
        )
        simulator.auto_yes = yes  # 자동 확인 모드 설정

        # 문제 목록만 보기 모드
        if list_only:
            console.print(f"[bold cyan]시험 타입 {exam_type} 문제 목록[/bold cyan]\n")
            simulator.load_questions()
            simulator.show_question_list()

            # 각 문제의 상세 내용도 표시
            console.print("\n[bold]문제 상세 내용:[/bold]\n")
            for idx, question in enumerate(simulator.questions, 1):
                console.print(f"\n{'='*80}")
                console.print(f"[bold cyan]문제 {idx}: {question.get('title', '')}[/bold cyan]")
                console.print(f"[bold]ID:[/bold] {question.get('id', '')}")
                console.print(f"[bold]도메인:[/bold] {question.get('domain', '')}")
                console.print(f"[bold]난이도:[/bold] {question.get('difficulty', '')}")
                console.print(f"[bold]배점:[/bold] {question.get('weight', 0)}점")
                console.print(f"\n{question.get('description', '')}")
                console.print(f"\n{question.get('task', '')}")
                if 'hints' in question and question['hints']:
                    console.print(f"\n[bold green]힌트:[/bold green]")
                    for hint in question['hints']:
                        console.print(f"  💡 {hint}")
            return

        # 일반 시험 모드
        simulator.run_exam()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]시험이 중단되었습니다.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]오류 발생: {str(e)}[/bold red]")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
