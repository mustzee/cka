#!/usr/bin/env python3
"""
CKA 시험 시뮬레이터 메인 애플리케이션
"""

import os
import sys
import click
import time
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


console = Console()


class CKASimulator:
    """CKA 시험 시뮬레이터"""

    def __init__(self, exam_type: str = "A", practice_mode: bool = False):
        self.exam_type = exam_type.upper()
        self.practice_mode = practice_mode
        self.loader = QuestionLoader()
        self.grader = AutoGrader()
        self.reporter = ReportGenerator()
        self.timer = ExamTimer(duration_minutes=120 if not practice_mode else 999999)
        self.questions = []
        self.current_question_idx = 0

    def show_welcome(self):
        """환영 메시지 표시"""
        welcome_text = f"""
[bold cyan]Kubernetes CKA 시험 시뮬레이터[/bold cyan]

시험 타입: [bold]{self.exam_type}[/bold]
모드: [bold]{'연습 모드 (타이머 없음)' if self.practice_mode else '실전 모드 (2시간)'}[/bold]

[yellow]실제 CKA 시험과 동일한 환경에서 진행됩니다.[/yellow]

[bold green]준비사항:[/bold green]
✓ Kubernetes 클러스터가 실행 중이어야 합니다
✓ kubectl 명령어를 사용할 수 있어야 합니다
✓ 터미널을 별도로 열어서 작업하세요

[bold red]주의사항:[/bold red]
• 시험 중에는 시뮬레이터를 종료하지 마세요
• 각 문제마다 적절한 context를 사용하세요
• 시간이 종료되면 자동으로 채점됩니다
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

        console.print(f"\n[bold yellow]문제:[/bold yellow]")
        console.print(question.get("description", ""))
        console.print(question.get("task", ""))

        if "hints" in question and question["hints"]:
            console.print(f"\n[bold green]힌트:[/bold green]")
            for hint in question["hints"]:
                console.print(f"  💡 {hint}")

        console.print("\n" + "-" * 80)
        console.print(
            "[bold]별도 터미널에서 작업을 수행하세요. 완료되면 여기로 돌아오세요.[/bold]"
        )
        console.print("-" * 80 + "\n")

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

        if not Confirm.ask("\n시험을 시작하시겠습니까?"):
            console.print("[yellow]시험이 취소되었습니다.[/yellow]")
            return

        # 문제 로드
        self.load_questions()

        # 문제 목록 표시
        self.show_question_list()

        # 타이머 시작
        self.timer.start()
        start_time = datetime.now()

        console.print("[bold green]시험이 시작되었습니다![/bold green]\n")

        # 문제 진행
        while self.current_question_idx < len(self.questions):
            if not self.practice_mode and self.timer.is_expired():
                console.print("\n[bold red]⏰ 시험 시간이 종료되었습니다![/bold red]")
                break

            question = self.questions[self.current_question_idx]
            self.show_question(question)
            self.show_timer()

            # 사용자 입력 대기
            choice = Prompt.ask(
                "\n선택하세요",
                choices=["next", "prev", "list", "skip", "finish", "quit"],
                default="next",
            )

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
                if Confirm.ask("\n시험을 종료하고 채점하시겠습니까?"):
                    break

            elif choice == "quit":
                if Confirm.ask("\n정말로 시험을 중단하시겠습니까? (채점되지 않습니다)"):
                    console.print("[yellow]시험이 중단되었습니다.[/yellow]")
                    return

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
def main(exam_type, practice):
    """
    CKA 시험 시뮬레이터

    실제 CKA 시험과 동일한 환경에서 연습할 수 있습니다.
    """
    try:
        # 결과 디렉토리 생성
        os.makedirs("results", exist_ok=True)

        # 시뮬레이터 실행
        simulator = CKASimulator(exam_type=exam_type, practice_mode=practice)
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
