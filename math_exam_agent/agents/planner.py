"""规划 Agent (Planner) — 根据历史表现生成个性化学习计划。"""

from __future__ import annotations

from typing import Any

from math_exam_agent.agents.base import BaseAgent
from math_exam_agent.utils.display import DisplayManager


class PlannerAgent(BaseAgent):
    """规划 Agent：基于学习分析生成个性化周学习计划。"""

    def __init__(self, llm: Any, memory: Any = None) -> None:
        super().__init__("规划 Agent (Planner)", llm, memory)
        self.display = DisplayManager()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """生成学习计划。

        Keyword Args:
            analysis: 分析 Agent 的分析结果（可选）

        Returns:
            包含学习计划的字典。
        """
        summary = self.memory.get_summary()
        knowledge = self.memory.get_knowledge_status()

        # 构建上下文
        context_parts = [
            f"### 学习概况\n"
            f"总练习：{summary['total_practiced']} 题，"
            f"正确：{summary['total_correct']} 题，"
            f"总体掌握度：{summary['overall_mastery'] * 100:.1f}%",
            "",
            "### 各知识点掌握度",
        ]
        for kp, data in sorted(
            knowledge.items(), key=lambda x: x[1].get("mastery", 0)
        ):
            context_parts.append(
                f"  - {kp}: {data['mastery'] * 100:.0f}%"
                f" (练习 {data['practiced']} 次)"
            )

        context = "\n".join(context_parts)

        _, conclusion = self.reason(
            task="生成一周的个性化考研数学学习计划",
            context=context,
        )

        # 展示计划
        self.display.show_plan(conclusion)

        return {"plan": conclusion}
