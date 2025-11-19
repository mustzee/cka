"""
시험 타이머 모듈
"""

import time
from datetime import datetime, timedelta
from typing import Optional


class ExamTimer:
    """CKA 시험 타이머"""

    def __init__(self, duration_minutes: int = 120):
        """
        타이머 초기화

        Args:
            duration_minutes: 시험 시간 (분)
        """
        self.duration = timedelta(minutes=duration_minutes)
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.paused = False
        self.pause_time: Optional[datetime] = None
        self.total_paused_duration = timedelta(0)

    def start(self):
        """타이머 시작"""
        self.start_time = datetime.now()
        self.end_time = self.start_time + self.duration
        self.paused = False

    def pause(self):
        """타이머 일시정지"""
        if not self.paused and self.start_time:
            self.paused = True
            self.pause_time = datetime.now()

    def resume(self):
        """타이머 재개"""
        if self.paused and self.pause_time:
            pause_duration = datetime.now() - self.pause_time
            self.total_paused_duration += pause_duration
            self.end_time += pause_duration
            self.paused = False
            self.pause_time = None

    def get_remaining_time(self) -> timedelta:
        """
        남은 시간 반환

        Returns:
            남은 시간 (timedelta)
        """
        if not self.start_time or not self.end_time:
            return self.duration

        if self.paused and self.pause_time:
            return self.end_time - self.pause_time

        now = datetime.now()
        remaining = self.end_time - now

        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def get_elapsed_time(self) -> timedelta:
        """
        경과 시간 반환 (일시정지 시간 제외)

        Returns:
            경과 시간 (timedelta)
        """
        if not self.start_time:
            return timedelta(0)

        if self.paused and self.pause_time:
            return self.pause_time - self.start_time - self.total_paused_duration

        now = datetime.now()
        return now - self.start_time - self.total_paused_duration

    def is_expired(self) -> bool:
        """
        시간 만료 여부 확인

        Returns:
            만료 여부
        """
        return self.get_remaining_time().total_seconds() <= 0

    def format_time(self, td: timedelta) -> str:
        """
        시간 포맷팅

        Args:
            td: timedelta 객체

        Returns:
            포맷된 시간 문자열 (HH:MM:SS)
        """
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_remaining_formatted(self) -> str:
        """남은 시간을 포맷된 문자열로 반환"""
        return self.format_time(self.get_remaining_time())

    def get_elapsed_formatted(self) -> str:
        """경과 시간을 포맷된 문자열로 반환"""
        return self.format_time(self.get_elapsed_time())

    def get_progress_percentage(self) -> float:
        """
        진행률 반환

        Returns:
            진행률 (0-100)
        """
        if not self.start_time:
            return 0.0

        elapsed = self.get_elapsed_time().total_seconds()
        total = self.duration.total_seconds()
        return min(100.0, (elapsed / total) * 100)
