"""LLM 接口层 -- 支持 mock 和 OpenAI 兼容 API 两种模式。"""

from __future__ import annotations

import json
import os
import random
from abc import ABC, abstractmethod
from typing import Any


class LLMInterface(ABC):
    """LLM 抽象基类，所有 LLM 实现必须继承此类。"""

    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> str:
        """向 LLM 发送对话并获取回复。"""
        ...

    @abstractmethod
    def reason(self, agent_name: str, task: str, context: str = "") -> tuple[str, str]:
        """执行带推理步骤的调用，返回 (推理过程, 结论)。"""
        ...


# ---------------------------------------------------------------------------
# Mock LLM -- 内置硬编码但真实的数学题目与解析，无需任何 API Key
# 注意：所有文本使用纯 ASCII + 中文字符，避免 Windows GBK 编码问题
# ---------------------------------------------------------------------------

_MOCK_KNOWLEDGE: dict[str, list[dict[str, str]]] = {
    "极限与连续": [
        {
            "question": "求极限：\n\n$$\\lim_{x \\to 0} \\frac{\\sin 3x}{x}$$",
            "answer": "3",
            "steps": (
                "步骤1：观察到当 x->0 时，分子 sin 3x -> 0，分母 x -> 0，是 0/0 型未定式。\n"
                "步骤2：利用重要极限：lim_{u->0} sin u / u = 1。\n"
                "步骤3：将原式变形：lim_{x->0} sin 3x / x = lim_{x->0} 3 * (sin 3x) / (3x)。\n"
                "步骤4：令 u = 3x，当 x->0 时 u->0，所以原式 = 3 * lim_{u->0} sin u / u = 3 * 1 = 3。"
            ),
            "difficulty": "简单",
        },
        {
            "question": "求极限：\n\n$$\\lim_{x \\to 0} \\frac{1 - \\cos x}{x^2}$$",
            "answer": "1/2",
            "steps": (
                "步骤1：当 x->0 时分子 1-cos x -> 0，分母 x^2 -> 0，是 0/0 型未定式。\n"
                "步骤2：使用等价无穷小替换：当 x->0 时，1 - cos x ~ (1/2)x^2。\n"
                "步骤3：因此原式 = lim_{x->0} [(1/2)x^2] / x^2 = 1/2。\n"
                "步骤4：也可使用洛必达法则验证：分子导数为 sin x，分母导数为 2x，\n"
                "     lim_{x->0} sin x / (2x) = 1/2。"
            ),
            "difficulty": "中等",
        },
        {
            "question": "求极限：\n\n$$\\lim_{x \\to 0} \\left(1 + 2x\\right)^{\\frac{1}{x}}$$",
            "answer": "e^2",
            "steps": (
                "步骤1：识别出这是 1^inf 型未定式，使用重要极限 lim_{u->0} (1+u)^{1/u} = e。\n"
                "步骤2：变形：令 u = 2x，则当 x->0 时 u->0，且 x = u/2。\n"
                "步骤3：原式 = lim_{u->0} (1+u)^{2/u} = [lim_{u->0} (1+u)^{1/u}]^2 = e^2。"
            ),
            "difficulty": "中等",
        },
        {
            "question": "求极限：\n\n$$\\lim_{x \\to \\infty} \\frac{x^2 - 3x + 1}{2x^2 + 5x - 7}$$",
            "answer": "1/2",
            "steps": (
                "步骤1：当 x->inf 时，分子和分母都是二次多项式，属于 inf/inf 型。\n"
                "步骤2：分子分母同除以 x^2（最高次项）：\n"
                "     原式 = lim_{x->inf} (1 - 3/x + 1/x^2) / (2 + 5/x - 7/x^2)。\n"
                "步骤3：当 x->inf 时，3/x -> 0，1/x^2 -> 0，5/x -> 0，7/x^2 -> 0。\n"
                "步骤4：所以原式 = 1/2。"
            ),
            "difficulty": "简单",
        },
    ],
    "导数与微分": [
        {
            "question": "求导：\n\n$$y = x^3 \\ln x，求 y'$$",
            "answer": "3x^2 ln x + x^2",
            "steps": (
                "步骤1：这是乘积形式，使用乘积法则：(uv)' = u'v + uv'。\n"
                "步骤2：令 u = x^3，v = ln x。\n"
                "步骤3：u' = 3x^2，v' = 1/x。\n"
                "步骤4：y' = 3x^2 * ln x + x^3 * (1/x) = 3x^2 ln x + x^2。"
            ),
            "difficulty": "简单",
        },
        {
            "question": "求导：\n\n$$y = e^{\\sin x}，求 y'$$",
            "answer": "e^{sin x} * cos x",
            "steps": (
                "步骤1：这是复合函数，使用链式法则：dy/dx = dy/du * du/dx。\n"
                "步骤2：令 u = sin x，则 y = e^u。\n"
                "步骤3：dy/du = e^u = e^{sin x}，du/dx = cos x。\n"
                "步骤4：y' = e^{sin x} * cos x。"
            ),
            "difficulty": "简单",
        },
        {
            "question": "求隐函数导数：\n\n$$x^2 + y^2 = 25，求 \\frac{dy}{dx}$$",
            "answer": "-x/y",
            "steps": (
                "步骤1：方程两边同时对 x 求导，注意 y 是 x 的函数。\n"
                "步骤2：d/dx (x^2) + d/dx (y^2) = d/dx (25)。\n"
                "步骤3：2x + 2y * dy/dx = 0。\n"
                "步骤4：解出 dy/dx = -2x / (2y) = -x/y。"
            ),
            "difficulty": "中等",
        },
        {
            "question": "求曲线 y = x^3 - 3x + 2 在点 (1, 0) 处的切线方程。",
            "answer": "y = 0",
            "steps": (
                "步骤1：切线的斜率等于该点处的导数值。\n"
                "步骤2：y' = 3x^2 - 3，在 x=1 处，y'(1) = 3*1^2 - 3 = 0。\n"
                "步骤3：切线斜率为 0，是水平切线。\n"
                "步骤4：切线方程为 y - 0 = 0*(x - 1)，即 y = 0。"
            ),
            "difficulty": "中等",
        },
    ],
    "不定积分与定积分": [
        {
            "question": "求不定积分：\n\n$$\\int (3x^2 + 2x + 1) \\, dx$$",
            "answer": "x^3 + x^2 + x + C",
            "steps": (
                "步骤1：使用幂函数积分公式：int x^n dx = x^{n+1}/(n+1) + C (n != -1)。\n"
                "步骤2：int 3x^2 dx = 3 * x^3/3 = x^3。\n"
                "步骤3：int 2x dx = 2 * x^2/2 = x^2。\n"
                "步骤4：int 1 dx = x。\n"
                "步骤5：因此原式 = x^3 + x^2 + x + C。"
            ),
            "difficulty": "简单",
        },
        {
            "question": "求不定积分：\n\n$$\\int x e^{x} \\, dx$$",
            "answer": "(x - 1)e^x + C",
            "steps": (
                "步骤1：这是乘积形式，使用分部积分法：int u dv = uv - int v du。\n"
                "步骤2：令 u = x，dv = e^x dx。\n"
                "步骤3：则 du = dx，v = e^x。\n"
                "步骤4：int x e^x dx = x e^x - int e^x dx = x e^x - e^x + C = (x-1)e^x + C。"
            ),
            "difficulty": "中等",
        },
        {
            "question": "求定积分：\n\n$$\\int_0^1 x^2 \\, dx$$",
            "answer": "1/3",
            "steps": (
                "步骤1：先求不定积分：int x^2 dx = x^3/3 + C。\n"
                "步骤2：使用牛顿-莱布尼茨公式：int_0^1 x^2 dx = [x^3/3]_0^1。\n"
                "步骤3：代入上下限：= 1^3/3 - 0^3/3 = 1/3。"
            ),
            "difficulty": "简单",
        },
        {
            "question": "求定积分：\n\n$$\\int_0^{\\pi} \\sin x \\, dx$$",
            "answer": "2",
            "steps": (
                "步骤1：先求不定积分：int sin x dx = -cos x + C。\n"
                "步骤2：使用牛顿-莱布尼茨公式：int_0^pi sin x dx = [-cos x]_0^pi。\n"
                "步骤3：代入上下限：= (-cos pi) - (-cos 0) = (-(-1)) - (-1) = 1 + 1 = 2。"
            ),
            "difficulty": "简单",
        },
    ],
}


class MockLLM(LLMInterface):
    """Mock LLM -- 内置示例数据，展示完整 Agent 推理流程。"""

    def __init__(self) -> None:
        self.knowledge = _MOCK_KNOWLEDGE
        self.topics = list(self.knowledge.keys())

    def chat(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> str:
        """模拟 LLM 对话返回。"""
        prompt_lower = user_prompt.lower()

        if "你好" in prompt_lower or "hello" in prompt_lower:
            return "你好！我是 MathExam AI Agent，很高兴帮助你学习考研数学！"
        if "分析" in prompt_lower or "analyze" in prompt_lower:
            return self._mock_analysis(user_prompt)
        if "计划" in prompt_lower or "plan" in prompt_lower:
            return self._mock_plan(user_prompt)
        if "出题" in prompt_lower or "题目" in prompt_lower or "question" in prompt_lower:
            return self._mock_question(user_prompt)
        if "批改" in prompt_lower or "评分" in prompt_lower or "grader" in prompt_lower:
            return self._mock_grade(user_prompt)
        return (
            "收到你的问题。根据你的学习进度，建议先从基础概念入手，"
            "逐步过渡到综合题型。需要我帮你分析薄弱环节或生成练习题吗？"
        )

    def reason(self, agent_name: str, task: str, context: str = "") -> tuple[str, str]:
        """模拟推理过程，返回 (推理过程, 结论)。"""
        if "分析" in task or "analyzer" in agent_name.lower():
            return self._reason_analyze(context)
        elif "出题" in task or "generator" in agent_name.lower() or "question" in agent_name.lower():
            return self._reason_generate(context)
        elif "批改" in task or "grader" in agent_name.lower():
            return self._reason_grade(context)
        elif "规划" in task or "planner" in agent_name.lower():
            return self._reason_plan(context)
        else:
            return ("正在分析任务需求...", "任务已理解，准备执行。")

    def _reason_analyze(self, context: str) -> tuple[str, str]:
        """分析 Agent 的推理过程。"""
        steps = [
            "【分析 Agent 推理开始】",
            "",
            "步骤 1/5：信息收集",
            "   -> 读取用户学习记录...",
            "   -> 提取已完成题目数量、正确率、耗时数据",
            "   -> 获取各知识点掌握程度",
            "",
            "步骤 2/5：知识点覆盖评估",
            "   -> 统计各章节已练习题目数",
            "   -> 计算各知识点正确率分布",
            "   -> 识别正确率低于 60% 的薄弱知识点",
            "",
            "步骤 3/5：难度适应度分析",
            "   -> 评估用户在简单/中等/困难题目上的表现差异",
            "   -> 分析用户在哪些难度层级出现正确率下降",
            "   -> 确定用户的最近发展区",
            "",
            "步骤 4/5：学习模式识别",
            "   -> 分析用户答题速度与正确率的权衡",
            "   -> 识别粗心错误 vs 概念不清的模式",
            "   -> 判断用户是否需要对特定题型加强训练",
            "",
            "步骤 5/5：生成分析报告",
            "   -> 综合以上分析形成结构化报告",
            "   -> 标注需要优先加强的知识点",
            "   -> 给出针对性学习建议",
            "",
            "【分析 Agent 推理结束】",
        ]
        conclusion = (
            "学习情况分析结论：\n"
            "===========================================\n"
            "各知识点掌握度：\n"
            "  * 极限与连续：75% (良好)\n"
            "  * 导数与微分：60% (一般) 需加强\n"
            "  * 不定积分与定积分：45% (薄弱) 建议优先复习\n"
            "  * 微分中值定理：30% (薄弱) 建议优先复习\n"
            "  * 定积分应用：50% (薄弱) 建议优先复习\n"
            "===========================================\n"
            "建议：当前阶段重点攻克「不定积分与定积分」和「微分中值定理」，"
            "建议每天 2 小时专项练习。"
        )
        return "\n".join(steps), conclusion

    def _reason_generate(self, context: str) -> tuple[str, str]:
        """出题 Agent 的推理过程。"""
        topic = "极限与连续"
        if context:
            for t in self.topics:
                if t in context:
                    topic = t
                    break

        questions = self.knowledge.get(topic, self.knowledge[self.topics[0]])
        q = random.choice(questions)

        steps = [
            "【出题 Agent 推理开始】",
            "",
            f"步骤 1/4：知识点定向 -- 选定主题「{topic}」",
            f"   -> 从分析报告筛选出需要练习的主题",
            f"   -> 解析上下文：{context or '(无上下文，使用默认主题)'}",
            f"   -> 确认主题层级：高等数学 -> 一元函数微积分 -> {topic}",
            "",
            f"步骤 2/4：难度匹配 -- 根据用户水平 {q['difficulty']} 级别",
            "   -> 评估用户当前掌握程度",
            "   -> 选择略高于当前水平的难度（最近发展区原则）",
            f"   -> 确定难度等级：{q['difficulty']}",
            "",
            "步骤 3/4：题目生成",
            "   -> 从题库中筛选符合知识点的题目",
            "   -> 验证题目覆盖核心考点",
            "   -> 构造解题步骤和评分标准",
            "   -> 生成完整解析",
            "",
            "步骤 4/4：质量检查",
            "   -> 验证题目无歧义",
            "   -> 确认答案正确性",
            "   -> 检查步骤完整性",
            "   -> 格式化输出",
            "",
            "【出题 Agent 推理结束】",
        ]
        return "\n".join(steps), json.dumps(
            {
                "topic": topic,
                "difficulty": q["difficulty"],
                "question": q["question"],
                "answer": q["answer"],
                "steps": q["steps"],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _reason_grade(self, context: str) -> tuple[str, str]:
        """批改 Agent 的推理过程。"""
        steps = [
            "【批改 Agent 推理开始】",
            "",
            "步骤 1/4：答案解析",
            "   -> 读取待批改题目和标准答案",
            "   -> 识别题目类型（计算题/证明题/应用题）",
            "   -> 分解评分要点",
            "",
            "步骤 2/4：用户答案对比",
            "   -> 提取用户答案的关键步骤和最终结果",
            "   -> 与标准答案逐项对比",
            "   -> 标记正确部分、错误部分和遗漏部分",
            "",
            "步骤 3/4：错误分析",
            "   -> 判断错误类型：概念理解错误/计算失误/方法选择不当",
            "   -> 追溯错误根源（是知识点欠缺还是粗心）",
            "   -> 针对性地给出纠正建议",
            "",
            "步骤 4/4：评分与反馈",
            "   -> 根据评分标准计算得分",
            "   -> 生成结构化反馈报告",
            "   -> 给出改进建议和推荐练习",
            "",
            "【批改 Agent 推理结束】",
        ]
        conclusion = (
            "批改结果：\n"
            "===========================================\n"
            "得分：85/100\n"
            "评级：良好\n\n"
            "详细反馈：\n"
            "  [OK] 解题思路正确（+20）\n"
            "  [OK] 关键步骤完整（+30）\n"
            "  [OK] 最终答案正确（+25）\n"
            "  [!]  中间计算可简化（+10）\n"
            "  [NO] 缺少验算步骤（-10）\n\n"
            "建议：练习使用等价无穷小替换简化计算。"
        )
        return "\n".join(steps), conclusion

    def _reason_plan(self, context: str) -> tuple[str, str]:
        """规划 Agent 的推理过程。"""
        steps = [
            "【规划 Agent 推理开始】",
            "",
            "步骤 1/4：综合分析 -- 汇总历史表现",
            "   -> 读取分析 Agent 输出报告",
            "   -> 提取各知识点掌握度数据",
            "   -> 评估总复习进度",
            "   -> 计算距考试剩余时间",
            "",
            "步骤 2/4：优先级排序 -- 确定薄弱环节",
            "   -> 按掌握度从低到高排列知识点",
            "   -> 识别高权重但低掌握的知识点（优先处理）",
            "   -> 平衡复习轮次与深度",
            "",
            "步骤 3/4：时间分配 -- 制定每日计划",
            "   -> 根据薄弱程度分配学习时间",
            "   -> 设置短期（日/周）和长期（月）目标",
            "   -> 安排定期模拟测试",
            "   -> 预留复习和调整时间",
            "",
            "步骤 4/4：生成个性化学习计划",
            "   -> 输出结构化周计划",
            "   -> 包含每日学习目标和时长建议",
            "   -> 设置里程碑检查点",
            "",
            "【规划 Agent 推理结束】",
        ]
        conclusion = (
            "个性化学习计划：\n"
            "===========================================\n"
            "【本周学习计划】\n\n"
            "[Day 1] 周一：不定积分基础 (2h)\n"
            "  - 复习基本积分公式 (30min)\n"
            "  - 练习换元积分法 (45min)\n"
            "  - 练习分部积分法 (45min)\n\n"
            "[Day 2] 周二：定积分与应用 (2h)\n"
            "  - 牛顿-莱布尼茨公式复习 (30min)\n"
            "  - 定积分计算练习 (45min)\n"
            "  - 定积分求面积/体积 (45min)\n\n"
            "[Day 3] 周三：微分中值定理 (2h)\n"
            "  - 罗尔定理复习 (30min)\n"
            "  - 拉格朗日定理复习 (30min)\n"
            "  - 综合证明题练习 (60min)\n\n"
            "[Day 4] 周四：导数综合 (2h)\n"
            "  - 复合函数求导 (30min)\n"
            "  - 隐函数求导 (30min)\n"
            "  - 高阶导数 (30min)\n"
            "  - 导数应用 (30min)\n\n"
            "[Day 5] 周五：极限专题 (1.5h)\n"
            "  - 重要极限复习 (30min)\n"
            "  - 等价无穷小替换 (30min)\n"
            "  - 洛必达法则 (30min)\n\n"
            "[Day 6] 周六：综合模拟 (3h)\n"
            "  - 完整套题练习 (2h)\n"
            "  - 错题分析整理 (1h)\n\n"
            "[Day 7] 周日：休息与薄弱点补强 (1h)\n"
            "  - 针对本周错题重新练习\n"
            "==========================================="
        )
        return "\n".join(steps), conclusion

    def _mock_analysis(self, prompt: str) -> str:
        return self._reason_analyze("")[1]

    def _mock_plan(self, prompt: str) -> str:
        return self._reason_plan("")[1]

    def _mock_question(self, prompt: str) -> str:
        topic = ""
        for t in self.topics:
            if t in prompt:
                topic = t
                break
        if not topic:
            topic = random.choice(self.topics)
        questions = self.knowledge[topic]
        q = random.choice(questions)
        return (
            f"【题目 - {topic}（{q['difficulty']}）】\n\n"
            f"{q['question']}\n\n"
            f"【解题步骤】\n{q['steps']}\n\n"
            f"【答案】\n{q['answer']}"
        )

    def _mock_grade(self, prompt: str) -> str:
        return self._reason_grade(prompt)[1]


# ---------------------------------------------------------------------------
# API LLM -- 连接真实 OpenAI 兼容 API
# ---------------------------------------------------------------------------


class APILLM(LLMInterface):
    """基于 httpx 调用 OpenAI 兼容 API 的真实 LLM。

    环境变量配置：
      LLM_API_BASE  -- API 地址（默认 https://api.openai.com/v1）
      LLM_API_KEY   -- API Key
      LLM_MODEL     -- 模型名（默认 gpt-4o）
    """

    def __init__(self) -> None:
        self.api_base = os.getenv(
            "LLM_API_BASE", "https://api.openai.com/v1"
        ).rstrip("/")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gpt-4o")

        if not self.api_key:
            raise ValueError(
                "LLM_API_KEY 环境变量未设置。请设置 LLM_API_KEY 或使用 --mode mock。"
            )

    def _call(self, messages: list[dict], **kwargs: Any) -> str:
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            **kwargs,
        }
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def chat(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self._call(messages, **kwargs)

    def reason(self, agent_name: str, task: str, context: str = "") -> tuple[str, str]:
        system = (
            f"你是一个考研数学 {agent_name}。请一步一步推理，"
            "先展示完整的推理过程（用 链式思考 格式），然后给出最终结论。"
        )
        user = f"任务：{task}\n\n上下文信息：\n{context or '无'}"

        full = self._call(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
        )

        # 简单分割推理和结论（API 模式下交由 LLM 自行组织）
        parts = full.split("最终结论", 1)
        if len(parts) == 2:
            return parts[0].strip(), "最终结论" + parts[1].strip()
        return full, full


# ---------------------------------------------------------------------------
# 工厂函数
# ---------------------------------------------------------------------------


def create_llm(mode: str = "mock") -> LLMInterface:
    """创建 LLM 实例。"""
    if mode == "api":
        return APILLM()
    return MockLLM()
