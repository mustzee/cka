"""
Chaos Engineering 시스템
무작위 장애 주입으로 실전 트러블슈팅 연습
"""

import random
import subprocess
import threading
import time
from typing import List, Dict, Callable
from rich.console import Console

console = Console()


class ChaosEngineering:
    """무작위 장애 주입 시스템 - Ultra Mode용"""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.active_failures: List[Dict] = []
        self.failure_log: List[str] = []

    def inject_random_failures(self, duration_minutes: int = 120):
        """시험 중 무작위 장애 발생"""
        if not self.enabled:
            return

        console.print("\n[bold red]🔥 Chaos Engineering ENABLED[/bold red]")
        console.print("[yellow]시험 중 무작위 장애가 발생할 수 있습니다![/yellow]\n")

        # 시험 시간 동안 2-4회 장애 발생
        num_failures = random.randint(2, 4)
        interval = (duration_minutes * 60) / (num_failures + 1)

        for i in range(num_failures):
            delay = interval * (i + 1) + random.randint(-300, 300)  # ±5분 무작위
            timer = threading.Timer(delay, self._trigger_random_failure)
            timer.daemon = True
            timer.start()

    def _trigger_random_failure(self):
        """무작위 장애 발생"""
        failures = [
            self._cause_node_pressure,
            self._cause_pod_deletion,
            self._cause_dns_failure,
            self._cause_network_latency,
        ]

        failure_func = random.choice(failures)
        try:
            failure_func()
        except Exception as e:
            console.print(f"[yellow]⚠️  Chaos injection failed: {e}[/yellow]")

    def _cause_node_pressure(self):
        """노드 리소스 압박 시뮬레이션"""
        console.print("\n[bold red]💥 CHAOS EVENT: Node Resource Pressure![/bold red]")
        console.print("[yellow]노드에 메모리 압박이 발생했습니다![/yellow]\n")

        # 메모리 압박 Pod 생성
        manifest = """
apiVersion: v1
kind: Pod
metadata:
  name: memory-stress
  namespace: default
spec:
  containers:
  - name: stress
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "512M", "--vm-hang", "1"]
    resources:
      requests:
        memory: "512Mi"
      limits:
        memory: "512Mi"
"""

        try:
            subprocess.run(
                ["kubectl", "apply", "-f", "-"],
                input=manifest.encode(),
                capture_output=True,
                timeout=10
            )
            self.failure_log.append("Node memory pressure injected")
        except Exception as e:
            console.print(f"[dim]Chaos injection warning: {e}[/dim]")

    def _cause_pod_deletion(self):
        """무작위 Pod 삭제"""
        console.print("\n[bold red]💥 CHAOS EVENT: Random Pod Deleted![/bold red]")
        console.print("[yellow]클러스터에서 Pod가 갑자기 삭제되었습니다![/yellow]\n")

        # 삭제할 Pod 찾기 (kube-system 제외)
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-A", "--no-headers"],
                capture_output=True,
                text=True,
                timeout=10
            )

            pods = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split()
                namespace = parts[0]
                pod_name = parts[1]

                # kube-system, kube-public 제외
                if namespace not in ['kube-system', 'kube-public', 'kube-node-lease']:
                    pods.append((namespace, pod_name))

            if pods:
                namespace, pod_name = random.choice(pods)
                subprocess.run(
                    ["kubectl", "delete", "pod", pod_name, "-n", namespace, "--grace-period=0", "--force"],
                    capture_output=True,
                    timeout=10
                )
                self.failure_log.append(f"Deleted pod {pod_name} in {namespace}")
                console.print(f"[red]삭제된 Pod: {namespace}/{pod_name}[/red]\n")

        except Exception as e:
            console.print(f"[dim]Chaos injection warning: {e}[/dim]")

    def _cause_dns_failure(self):
        """DNS 장애 시뮬레이션"""
        console.print("\n[bold red]💥 CHAOS EVENT: DNS Failure![/bold red]")
        console.print("[yellow]CoreDNS에 문제가 발생했습니다![/yellow]\n")

        # CoreDNS Pod 재시작
        try:
            subprocess.run(
                ["kubectl", "rollout", "restart", "deployment/coredns", "-n", "kube-system"],
                capture_output=True,
                timeout=10
            )
            self.failure_log.append("CoreDNS restarted (DNS disruption)")
        except Exception as e:
            console.print(f"[dim]Chaos injection warning: {e}[/dim]")

    def _cause_network_latency(self):
        """네트워크 지연 시뮬레이션"""
        console.print("\n[bold red]💥 CHAOS EVENT: Network Latency![/bold red]")
        console.print("[yellow]클러스터 네트워크에 지연이 발생했습니다![/yellow]\n")

        # 네트워크 지연 시뮬레이션 Pod 생성
        manifest = """
apiVersion: v1
kind: Pod
metadata:
  name: network-chaos
  namespace: default
spec:
  hostNetwork: true
  containers:
  - name: chaos
    image: nicolaka/netshoot
    command: ["/bin/sh"]
    args: ["-c", "sleep 300"]
    securityContext:
      capabilities:
        add: ["NET_ADMIN"]
"""

        try:
            subprocess.run(
                ["kubectl", "apply", "-f", "-"],
                input=manifest.encode(),
                capture_output=True,
                timeout=10
            )

            # tc (traffic control)로 지연 추가 시도
            time.sleep(2)
            subprocess.run(
                ["kubectl", "exec", "network-chaos", "--",
                 "tc", "qdisc", "add", "dev", "eth0", "root", "netem", "delay", "100ms"],
                capture_output=True,
                timeout=10
            )

            self.failure_log.append("Network latency injected (100ms)")
        except Exception as e:
            console.print(f"[dim]Chaos injection warning: {e}[/dim]")

    def cleanup(self):
        """장애 주입 리소스 정리"""
        if not self.enabled:
            return

        console.print("\n[yellow]Cleaning up chaos engineering resources...[/yellow]")

        cleanup_resources = [
            ("pod", "memory-stress", "default"),
            ("pod", "network-chaos", "default"),
        ]

        for resource_type, name, namespace in cleanup_resources:
            try:
                subprocess.run(
                    ["kubectl", "delete", resource_type, name, "-n", namespace,
                     "--ignore-not-found=true", "--grace-period=0", "--force"],
                    capture_output=True,
                    timeout=10
                )
            except Exception:
                pass

    def get_failure_report(self) -> str:
        """장애 발생 리포트"""
        if not self.failure_log:
            return "No chaos events occurred."

        report = "\n=== Chaos Engineering Report ===\n"
        report += f"Total chaos events: {len(self.failure_log)}\n\n"
        for i, event in enumerate(self.failure_log, 1):
            report += f"{i}. {event}\n"

        return report
