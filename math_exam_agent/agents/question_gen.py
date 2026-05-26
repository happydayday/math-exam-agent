"""出题 Agent (Generator) — 根据分析结果生成针对性数学题目。"""

from __future__ import annotations

import json
from typing import Any

from math_exam_agent.agents.base import BaseAgent
from math_exam_agent.utils.display import DisplayManager


class QuestionGenAgent(BaseAgent):
    """出题 Agent：根据用户水平生成针对性练习题。"""

    def __init__(self, llm: Any, memory: Any = None) -> None:
        super().__init__("出题 Agent (Generator)", llm, memory)
        self.display = DisplayManager()

    def execute(self, topic: str = "", **kwargs: Any) -> dict[str, Any]:
        """生成题目。

        Args:
            topic: 指定知识点，为空则根据分析自动选择。

        Returns:
            包含题目、解析和答案的字典。
        """
        # 获取薄弱知识点作为上下文
        knowledge = self.memory.get_knowledge_status()
        if not topic:
            # 自动选择掌握度最低的知识点
            sorted_kp = sorted(
                knowledge.items(), key=lambda x: x[1].get("mastery", 0)
            )
            if sorted_kp:
                topic = sorted_kp[0][0]

        context = (
            f"用户薄弱知识点：{topic}\n"
            f"当前掌握度：{knowledge.get(topic, {}).get('mastery', 0) * 100:.0f}%\n"
            f"请生成一道难度适中的考研数学题目。"
        )

        reasoning, conclusion = self.reason(
            task=f"生成{topic}相关的考研数学题目",
            context=context,
        )

        # 尝试解析结论为 JSON
        try:
            question_data = json.loads(conclusion)
        except (json.JSONDecodeError, TypeError):
            question_data = {
                "topic": topic,
                "difficulty": "中等",
                "question": conclusion,
                "steps": "",
                "answer": "",
            }

        # 展示题目
        self.display.show_question(
            topic=question_data.get("topic", topic),
            difficulty=question_data.get("difficulty", "中等"),
            question_text=question_data.get("question", ""),
            steps=question_data.get("steps", ""),
            answer=question_data.get("answer", ""),
        )

        return question_data
