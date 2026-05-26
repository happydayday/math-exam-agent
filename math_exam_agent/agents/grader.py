"""批改 Agent (Grader) — 自动批改用户答案，评分并给出解析。"""

from __future__ import annotations

from typing import Any

from math_exam_agent.agents.base import BaseAgent
from math_exam_agent.utils.display import DisplayManager


class GraderAgent(BaseAgent):
    """批改 Agent：批改用户答案，生成评分和详细反馈。"""

    def __init__(self, llm: Any, memory: Any = None) -> None:
        super().__init__("批改 Agent (Grader)", llm, memory)
        self.display = DisplayManager()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """批改用户答案。

        Keyword Args:
            topic: 知识点名称
            question: 题目内容
            user_answer: 用户提交的答案
            correct_answer: 标准答案
            steps: 解题步骤

        Returns:
            包含评分和反馈的字典。
        """
        topic = kwargs.get("topic", "未知")
        question = kwargs.get("question", "")
        user_answer = kwargs.get("user_answer", "")
        correct_answer = kwargs.get("correct_answer", "")
        steps = kwargs.get("steps", "")

        context = (
            f"知识点：{topic}\n"
            f"题目：{question}\n"
            f"标准答案：{correct_answer}\n"
            f"解题步骤：{steps}\n"
            f"用户答案：{user_answer}\n"
        )

        _, conclusion = self.reason(
            task="批改用户答案并给出评分和详细反馈",
            context=context,
        )

        # 简单评分逻辑
        score = self._simple_grade(user_answer, correct_answer)

        # 记录到学习记忆
        self.memory.add_practice_record(
            topic=topic,
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            score=score,
        )

        return {
            "score": score,
            "feedback": conclusion,
            "topic": topic,
        }

    @staticmethod
    def _simple_grade(user_answer: str, correct_answer: str) -> int:
        """简易评分：完全匹配 100，部分匹配 80，完全不匹配 40。"""
        ua = user_answer.strip().lower()
        ca = correct_answer.strip().lower()

        if ua == ca:
            return 100

        # 检查是否是数值答案
        import re
        ua_nums = re.findall(r"-?\d+\.?\d*|e²?|π", ua)
        ca_nums = re.findall(r"-?\d+\.?\d*|e²?|π", ca)

        if ua_nums and ca_nums and ua_nums == ca_nums:
            return 85

        # 检查是否包含关键表达式
        ca_keywords = re.findall(r"[a-zA-Z]+", ca)
        if ca_keywords:
            match_ratio = sum(1 for kw in ca_keywords if kw in ua) / len(ca_keywords)
            if match_ratio > 0.5:
                return int(60 + match_ratio * 20)

        return 40
