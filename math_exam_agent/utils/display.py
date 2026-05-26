"""Rich 显示工具 — 美化 CLI 输出（无 emoji，兼容 Windows GBK）。"""

from __future__ import annotations

import random

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()


class DisplayManager:
    """统一管理 CLI 界面输出。"""

    @staticmethod
    def show_banner() -> None:
        """显示启动 Banner。"""
        banner = Text(
            r"""
   __  __       _   _                     __ _    ___
  |  \/  | __ _| |_| |__   ___  _ __     / _| |_ / _ \__ _  ___ ___
  | |\/| |/ _` | __| '_ \ / _ \| '_ \   | |_| __| | | / _` |/ __/ _ \
  | |  | | (_| | |_| | | | (_) | | | |  |  _| |_| |_| | (_| | (_|  __/
  |_|  |_|\__,_|\__|_| |_|\___/|_| |_|  |_|  \__|\___/ \__,_|\___\___|
            """,
            style="bold cyan",
        )
        console.print(banner)
        console.print(
            Panel(
                "考研数学多 Agent 智能学习系统",
                style="bright_yellow",
                border_style="yellow",
            )
        )
        console.print()

    @staticmethod
    def show_agent_reasoning(agent_name: str, reasoning: str, conclusion: str) -> None:
        """展示 Agent 推理过程和结论。

        Args:
            agent_name: Agent 名称
            reasoning: 推理过程文本
            conclusion: 最终结论文本
        """
        console.print()
        title = Text(f"[AI] {agent_name} 推理过程", style="bold magenta")
        console.print(Panel(reasoning, title=title, border_style="magenta"))

        console.print(
            Panel(
                conclusion,
                title=Text("[结论] 推理结论", style="bold green"),
                border_style="green",
            )
        )

    @staticmethod
    def show_question(
        topic: str, difficulty: str, question_text: str, steps: str, answer: str
    ) -> None:
        """展示题目及解析。"""
        header = Table.grid(padding=1)
        header.add_column()
        header.add_row(f"[bold cyan]知识点：[/bold cyan] {topic}")
        header.add_row(f"[bold cyan]难度：[/bold cyan] {difficulty}")
        console.print(Panel(header, title="[题目] 数学题目", border_style="cyan"))

        console.print()
        console.print(Panel(question_text, title="题目", border_style="blue"))
        console.print()
        console.print(Panel(steps, title="解题步骤", border_style="green"))
        console.print()
        console.print(
            Panel(Text(answer, style="bold yellow"), title="答案", border_style="yellow")
        )

    @staticmethod
    def show_learning_summary(summary: dict) -> None:
        """展示学习摘要。"""
        table = Table(
            title="[统计] 学习情况概览",
            box=box.ROUNDED,
            border_style="cyan",
        )
        table.add_column("指标", style="bold cyan")
        table.add_column("数值", style="yellow")

        table.add_row("总练习次数", str(summary["total_practiced"]))
        table.add_row("正确次数", str(summary["total_correct"]))
        table.add_row("总体掌握度", f"{summary['overall_mastery'] * 100:.1f}%")
        table.add_row("学习会话数", str(summary["sessions"]))

        console.print(table)

        # 各知识点详情
        kp_table = Table(
            title="[知识点] 各知识点掌握度",
            box=box.SIMPLE,
            border_style="blue",
        )
        kp_table.add_column("知识点", style="cyan")
        kp_table.add_column("练习数", justify="right")
        kp_table.add_column("正确数", justify="right")
        kp_table.add_column("掌握度", justify="right")

        for kp, data in summary["knowledge_points"].items():
            mastery = data["mastery"] * 100
            mastery_str = (
                f"[green]{mastery:.0f}%[/green]"
                if mastery >= 70
                else f"[yellow]{mastery:.0f}%[/yellow]"
                if mastery >= 40
                else f"[red]{mastery:.0f}%[/red]"
            )
            kp_table.add_row(kp, str(data["practiced"]), str(data["correct"]), mastery_str)

        console.print(kp_table)

    @staticmethod
    def show_plan(plan_text: str) -> None:
        """展示学习计划。"""
        console.print(
            Panel(
                plan_text,
                title="[计划] 个性化学习计划",
                border_style="green",
            )
        )

    @staticmethod
    def show_menu() -> str:
        """显示主菜单并返回用户选择。"""
        console.print()
        menu = Panel(
            "[1] [分析] 分析学习情况\n"
            "[2] [练习] 开始做题练习\n"
            "[3] [计划] 生成学习计划\n"
            "[4] [执行] 完整学习流程 (分析 -> 出题 -> 批改 -> 规划)\n"
            "[5] [统计] 查看学习统计\n"
            "[0] [退出] 退出",
            title="主菜单",
            border_style="bright_blue",
        )
        console.print(menu)
        return console.input("[bold cyan]请选择 [0-5]: [/bold cyan]").strip()

    @staticmethod
    def show_mode_indicator(mode: str) -> None:
        """显示当前模式。"""
        mode_style = "green" if mode == "mock" else "yellow"
        console.print(
            Panel(
                f"[bold {mode_style}]当前模式：{mode.upper()}[/bold {mode_style}]"
                + (
                    "  (使用内置演示数据)"
                    if mode == "mock"
                    else "  (连接真实 API)"
                ),
                border_style=mode_style,
            )
        )

    @staticmethod
    def ask_topic(topics: list[str]) -> str:
        """让用户选择题目的知识点。"""
        console.print("\n[bold]可选知识点：[/bold]")
        for i, t in enumerate(topics, 1):
            console.print(f"  [{i}] {t}")
        choice = console.input(
            "[bold cyan]请选择知识点 [1-{}]: [/bold cyan]".format(len(topics))
        ).strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(topics):
                return topics[idx]
        except ValueError:
            pass
        return random.choice(topics)

    @staticmethod
    def show_spinner(message: str = "处理中...") -> Progress:
        """显示进度 spinner。"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        )
        progress.add_task(description=message, total=None)
        progress.start()
        return progress

    @staticmethod
    def stop_spinner(progress: Progress) -> None:
        """停止 spinner。"""
        progress.stop()

    @staticmethod
    def input(prompt_text: str = "") -> str:
        """读取用户输入。"""
        return console.input(prompt_text)

    @staticmethod
    def print_input_prompt() -> str:
        """返回输入提示语。"""
        return "[bold cyan]请输入你的答案（输入 q 返回菜单）: [/bold cyan]"

    @staticmethod
    def print_error(msg: str) -> None:
        """打印错误信息。"""
        console.print(f"[bold red]错误：[/bold red] {msg}")

    @staticmethod
    def print_info(msg: str) -> None:
        """打印提示信息。"""
        console.print(f"[bold blue]信息：[/bold blue] {msg}")

    @staticmethod
    def print_success(msg: str) -> None:
        """打印成功信息。"""
        console.print(f"[bold green]成功：[/bold green] {msg}")
