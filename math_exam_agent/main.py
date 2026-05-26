"""
MathExam AI Agent — 考研数学多 Agent 智能系统 CLI 入口。

支持子命令：
  python -m math_exam_agent start      启动交互式学习会话
  python -m math_exam_agent analyze    分析学习情况
  python -m math_exam_agent practice   开始做题练习
  python -m math_exam_agent plan       生成学习计划

选项：
  --mode mock|api    切换模式（默认 mock）
"""

from __future__ import annotations

import random
import sys
from typing import NoReturn

import rich

from math_exam_agent import __app_name__, __version__
from math_exam_agent.agents import (
    AnalyzerAgent,
    GraderAgent,
    PlannerAgent,
    QuestionGenAgent,
)
from math_exam_agent.core.llm import create_llm
from math_exam_agent.core.memory import MemoryManager
from math_exam_agent.utils.display import DisplayManager

display = DisplayManager()

# Mock 模式下的知识点列表
TOPICS = [
    "极限与连续",
    "导数与微分",
    "不定积分与定积分",
    "微分中值定理",
    "定积分应用",
]


def parse_args() -> tuple[str, str]:
    """解析命令行参数，返回 (子命令, 模式)。"""
    args = sys.argv[1:]
    command = "start"
    mode = "mock"

    i = 0
    while i < len(args):
        if args[i] == "--mode":
            if i + 1 < len(args):
                mode = args[i + 1]
                i += 2
            else:
                i += 1
        elif args[i].startswith("--mode="):
            mode = args[i].split("=", 1)[1]
            i += 1
        elif not args[i].startswith("--"):
            command = args[i]
            i += 1
        else:
            i += 1

    if mode not in ("mock", "api"):
        print(f"错误：不支持的 mode '{mode}'，请使用 mock 或 api。")
        sys.exit(1)

    return command, mode


def cmd_start(mode: str) -> None:
    """启动交互式学习会话。"""
    display.show_banner()
    display.show_mode_indicator(mode)
    display.print_info(f"欢迎使用 {__app_name__} v{__version__}！")
    display.print_info("输入 0 或 q 随时退出。")

    llm = create_llm(mode)
    memory = MemoryManager.get_instance()

    analyzer = AnalyzerAgent(llm, memory)
    generator = QuestionGenAgent(llm, memory)
    grader = GraderAgent(llm, memory)
    planner = PlannerAgent(llm, memory)

    while True:
        choice = display.show_menu()

        if choice in ("0", "q", "quit", "exit"):
            display.print_success("感谢使用，加油考研！")
            break

        elif choice == "1":
            # 分析
            display.print_info("正在分析学习情况...")
            analyzer.execute()

        elif choice == "2":
            # 练习
            _do_practice(generator, grader, mode)

        elif choice == "3":
            # 计划
            display.print_info("正在生成学习计划...")
            planner.execute()

        elif choice == "4":
            # 完整流程
            display.print_info("▶️  启动完整学习流程（4 Agent 协作）")
            display.print_info("步骤 1/4：分析学习情况...")
            analysis = analyzer.execute()

            display.print_info("步骤 2/4：生成练习题...")
            question_data = generator.execute()

            if question_data.get("question"):
                user_input = display.input(
                    display.print_input_prompt()
                )
                if user_input.lower() in ("q", "quit", "exit"):
                    continue

                display.print_info("步骤 3/4：批改答案...")
                grader.execute(
                    topic=question_data.get("topic", "未知"),
                    question=question_data.get("question", ""),
                    user_answer=user_input,
                    correct_answer=question_data.get("answer", ""),
                    steps=question_data.get("steps", ""),
                )

            display.print_info("步骤 4/4：生成学习计划...")
            planner.execute()

        elif choice == "5":
            # 统计
            summary = memory.get_summary()
            display.show_learning_summary(summary)

        else:
            display.print_error("无效选择，请重新输入。")


def cmd_analyze(mode: str) -> None:
    """分析学习情况。"""
    llm = create_llm(mode)
    memory = MemoryManager.get_instance()
    analyzer = AnalyzerAgent(llm, memory)
    analyzer.execute()


def cmd_practice(mode: str) -> None:
    """开始做题练习。"""
    llm = create_llm(mode)
    memory = MemoryManager.get_instance()
    generator = QuestionGenAgent(llm, memory)
    grader = GraderAgent(llm, memory)
    _do_practice(generator, grader, mode)


def cmd_plan(mode: str) -> None:
    """生成学习计划。"""
    llm = create_llm(mode)
    memory = MemoryManager.get_instance()
    planner = PlannerAgent(llm, memory)
    planner.execute()


def _do_practice(
    generator: QuestionGenAgent,
    grader: GraderAgent,
    mode: str,
) -> None:
    """内部：执行一次练习流程。"""
    # 在 mock 模式下随机选择知识点，api 模式下询问用户
    if mode == "mock":
        topic = random.choice(TOPICS)
        display.print_info(f"选择知识点：{topic}")
    else:
        topic = display.ask_topic(TOPICS)

    question_data = generator.execute(topic=topic)

    if not question_data.get("question"):
        display.print_error("生成题目失败，请重试。")
        return

    # 获取用户答案
    user_input = display.input(
        display.print_input_prompt()
    )
    if user_input.lower() in ("q", "quit", "exit"):
        return

    # 批改
    grader.execute(
        topic=question_data.get("topic", topic),
        question=question_data.get("question", ""),
        user_answer=user_input,
        correct_answer=question_data.get("answer", ""),
        steps=question_data.get("steps", ""),
    )


def main() -> None:
    """主入口函数。"""
    command, mode = parse_args()

    commands = {
        "start": cmd_start,
        "analyze": cmd_analyze,
        "practice": cmd_practice,
        "plan": cmd_plan,
    }

    if command in commands:
        commands[command](mode)
    else:
        print(f"未知命令：{command}")
        print("可用命令：start, analyze, practice, plan")
        sys.exit(1)


if __name__ == "__main__":
    main()
