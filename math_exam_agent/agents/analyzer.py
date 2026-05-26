"""分析 Agent (Analyzer) — 分析用户学习水平与薄弱环节。"""

from __future__ import annotations

from typing import Any

from math_exam_agent.agents.base import BaseAgent
from math_exam_agent.utils.display import DisplayManager


class AnalyzerAgent(BaseAgent):
    """分析 Agent：评估用户学习状况，识别薄弱知识点。"""

    def __init__(self, llm: Any, memory: Any = None) -> None:
        super().__init__("分析 Agent (Analyzer)", llm, memory)
        self.display = DisplayManager()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """执行学习情况分析。

        Returns:
            包含分析结果的字典。
        """
        summary = self.memory.get_summary()
        knowledge_status = self.memory.get_knowledge_status()

        # 构建分析上下文
        context_parts = ["当前学习情况摘要："]
        context_parts.append(f"总练习次数：{summary['total_practiced']}")
        context_parts.append(f"总正确次数：{summary['total_correct']}")
        context_parts.append(f"总体掌握度：{summary['overall_mastery'] * 100:.1f}%")
        context_parts.append("")
        context_parts.append("各知识点掌握情况：")
        for kp, data in knowledge_status.items():
            context_parts.append(
                f"  - {kp}：练习 {data['practiced']} 次，"
                f"正确 {data['correct']} 次，"
                f"掌握度 {data['mastery'] * 100:.0f}%"
            )

        context = "\n".join(context_parts)

        # 展示当前概况
        self.display.show_learning_summary(summary)

        # 执行推理
        _, conclusion = self.reason(
            task="分析用户考研数学学习情况，识别薄弱环节",
            context=context,
        )

        return {
            "summary": summary,
            "knowledge_status": knowledge_status,
            "analysis": conclusion,
        }
