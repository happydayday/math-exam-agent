"""学习记录管理 — 持久化到 JSON 文件。"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryManager:
    """管理用户学习记录的持久化存储。"""

    _instance: MemoryManager | None = None

    def __init__(self, data_dir: str | None = None) -> None:
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.records_file = self.data_dir / "learning_records.json"
        self._records: dict[str, Any] = self._load()

    @classmethod
    def get_instance(cls, data_dir: str | None = None) -> MemoryManager:
        """获取单例实例。"""
        if cls._instance is None:
            cls._instance = cls(data_dir)
        return cls._instance

    def _load(self) -> dict[str, Any]:
        """从 JSON 文件加载学习记录。"""
        if self.records_file.exists():
            try:
                with open(self.records_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return self._default_records()
        return self._default_records()

    def _default_records(self) -> dict[str, Any]:
        """默认学习记录结构。"""
        return {
            "user": {"name": "考研学子", "target": "数学一", "created_at": datetime.now(timezone.utc).isoformat()},
            "knowledge_points": {
                "极限与连续": {"practiced": 0, "correct": 0, "mastery": 0.0},
                "导数与微分": {"practiced": 0, "correct": 0, "mastery": 0.0},
                "不定积分与定积分": {"practiced": 0, "correct": 0, "mastery": 0.0},
                "微分中值定理": {"practiced": 0, "correct": 0, "mastery": 0.0},
                "定积分应用": {"practiced": 0, "correct": 0, "mastery": 0.0},
            },
            "history": [],
            "sessions": 0,
        }

    def save(self) -> None:
        """保存学习记录到 JSON 文件。"""
        with open(self.records_file, "w", encoding="utf-8") as f:
            json.dump(self._records, f, ensure_ascii=False, indent=2)

    @property
    def records(self) -> dict[str, Any]:
        return self._records

    def get_knowledge_status(self) -> dict[str, dict[str, Any]]:
        """获取各知识点掌握状态。"""
        return self._records.get("knowledge_points", {})

    def add_practice_record(
        self,
        topic: str,
        question: str,
        user_answer: str,
        correct_answer: str,
        score: int,
    ) -> None:
        """添加一条练习记录。"""
        kp = self._records.setdefault("knowledge_points", {})
        if topic not in kp:
            kp[topic] = {"practiced": 0, "correct": 0, "mastery": 0.0}

        kp[topic]["practiced"] += 1
        if score >= 60:
            kp[topic]["correct"] += 1

        # 更新掌握度
        practiced = kp[topic]["practiced"]
        correct = kp[topic]["correct"]
        kp[topic]["mastery"] = round(correct / practiced, 2) if practiced > 0 else 0.0

        self._records.setdefault("history", []).append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "topic": topic,
                "question": question,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "score": score,
            }
        )

        self._records["sessions"] = self._records.get("sessions", 0) + 1
        self.save()

    def get_summary(self) -> dict[str, Any]:
        """获取学习摘要。"""
        total_practiced = sum(
            v["practiced"] for v in self._records.get("knowledge_points", {}).values()
        )
        total_correct = sum(
            v["correct"] for v in self._records.get("knowledge_points", {}).values()
        )
        overall_mastery = round(total_correct / total_practiced, 2) if total_practiced > 0 else 0.0

        return {
            "total_practiced": total_practiced,
            "total_correct": total_correct,
            "overall_mastery": overall_mastery,
            "sessions": self._records.get("sessions", 0),
            "knowledge_points": self._records.get("knowledge_points", {}),
        }
