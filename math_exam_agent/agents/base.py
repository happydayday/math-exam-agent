"""Agent 基类 — 所有 Agent 的公共抽象。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from math_exam_agent.core.llm import LLMInterface
from math_exam_agent.core.memory import MemoryManager
from math_exam_agent.utils.display import DisplayManager


class BaseAgent(ABC):
    """所有 Agent 的抽象基类。

    每个 Agent 都持有一个 LLM 接口用于推理，并通过 MemoryManager
    访问持久化的学习记录。
    """

    def __init__(
        self,
        name: str,
        llm: LLMInterface,
        memory: MemoryManager | None = None,
    ) -> None:
        self.name = name
        self.llm = llm
        self.memory = memory or MemoryManager.get_instance()
        self.display = DisplayManager()

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """执行 Agent 的核心任务。"""
        ...

    def reason(self, task: str, context: str = "") -> tuple[str, str]:
        """执行推理并展示过程。

        Returns:
            (推理过程文本, 结论文本)
        """
        reasoning, conclusion = self.llm.reason(self.name, task, context)
        self.display.show_agent_reasoning(self.name, reasoning, conclusion)
        return reasoning, conclusion
