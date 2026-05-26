"""
MathExam AI Agent — Gradio Web 演示应用
=========================================
考研数学多 Agent 智能学习系统的网页版在线演示。
使用 Mock 数据，无需任何 API Key，开箱即用。
"""

from __future__ import annotations

import json
import math
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import gradio as gr

# ===========================================================================
# Mock 数据（直接嵌入，与 math_exam_agent/core/llm.py 保持一致）
# ===========================================================================

MOCK_KNOWLEDGE: dict[str, list[dict[str, str]]] = {
    "极限与连续": [
        {
            "question": r"求极限：\n\n$$\lim_{x \to 0} \frac{\sin 3x}{x}$$",
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
            "question": r"求极限：\n\n$$\lim_{x \to 0} \frac{1 - \cos x}{x^2}$$",
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
            "question": r"求极限：\n\n$$\lim_{x \to 0} \left(1 + 2x\right)^{\frac{1}{x}}$$",
            "answer": "e^2",
            "steps": (
                "步骤1：识别出这是 1^inf 型未定式，使用重要极限 lim_{u->0} (1+u)^{1/u} = e。\n"
                "步骤2：变形：令 u = 2x，则当 x->0 时 u->0，且 x = u/2。\n"
                "步骤3：原式 = lim_{u->0} (1+u)^{2/u} = [lim_{u->0} (1+u)^{1/u}]^2 = e^2。"
            ),
            "difficulty": "中等",
        },
        {
            "question": r"求极限：\n\n$$\lim_{x \to \infty} \frac{x^2 - 3x + 1}{2x^2 + 5x - 7}$$",
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
            "question": r"求导：\n\n$$y = x^3 \ln x，求 y'$$",
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
            "question": r"求导：\n\n$$y = e^{\sin x}，求 y'$$",
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
            "question": r"求隐函数导数：\n\n$$x^2 + y^2 = 25，求 \frac{dy}{dx}$$",
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
            "question": r"求曲线 y = x^3 - 3x + 2 在点 (1, 0) 处的切线方程。",
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
            "question": r"求不定积分：\n\n$$\int (3x^2 + 2x + 1) \, dx$$",
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
            "question": r"求不定积分：\n\n$$\int x e^{x} \, dx$$",
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
            "question": r"求定积分：\n\n$$\int_0^1 x^2 \, dx$$",
            "answer": "1/3",
            "steps": (
                "步骤1：先求不定积分：int x^2 dx = x^3/3 + C。\n"
                "步骤2：使用牛顿-莱布尼茨公式：int_0^1 x^2 dx = [x^3/3]_0^1。\n"
                "步骤3：代入上下限：= 1^3/3 - 0^3/3 = 1/3。"
            ),
            "difficulty": "简单",
        },
        {
            "question": r"求定积分：\n\n$$\int_0^{\pi} \sin x \, dx$$",
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

# 所有知识点列表（含 CLI 中出现的额外知识点）
ALL_TOPICS = ["极限与连续", "导数与微分", "不定积分与定积分", "微分中值定理", "定积分应用"]

# 演示用学习记录（对应 examples/demo_session.json）
DEMO_RECORDS: dict[str, Any] = {
    "user": {"name": "考研学子", "target": "数学一", "exam_date": "2026-12-21"},
    "knowledge_points": {
        "极限与连续": {"practiced": 15, "correct": 12, "mastery": 0.80},
        "导数与微分": {"practiced": 12, "correct": 7, "mastery": 0.58},
        "不定积分与定积分": {"practiced": 10, "correct": 4, "mastery": 0.40},
        "微分中值定理": {"practiced": 5, "correct": 1, "mastery": 0.20},
        "定积分应用": {"practiced": 6, "correct": 3, "mastery": 0.50},
    },
    "history": [
        {"topic": "极限与连续", "question": "求极限：lim_{x→0} sin 3x / x", "user_answer": "3",
         "correct_answer": "3", "score": 100, "timestamp": "2026-05-20 10:30"},
        {"topic": "导数与微分", "question": "y = x^3 ln x，求 y'", "user_answer": "3x^2 ln x",
         "correct_answer": "3x^2 ln x + x^2", "score": 60, "timestamp": "2026-05-21 14:00"},
        {"topic": "不定积分与定积分", "question": "∫ (3x^2 + 2x + 1) dx", "user_answer": "x^3 + x^2 + C",
         "correct_answer": "x^3 + x^2 + x + C", "score": 70, "timestamp": "2026-05-22 09:00"},
        {"topic": "不定积分与定积分", "question": "∫ x e^x dx", "user_answer": "xe^x - e^x + C",
         "correct_answer": "(x-1)e^x + C", "score": 90, "timestamp": "2026-05-23 16:00"},
        {"topic": "微分中值定理", "question": "验证罗尔定理对 f(x)=x^2-4x+3 在 [1,3] 上成立",
         "user_answer": "f(1)=0, f(3)=0, f'(x)=2x-4=0, x=2∈(1,3)",
         "correct_answer": "f(1)=1-4+3=0, f(3)=9-12+3=0, f'(ξ)=2ξ-4=0, ξ=2∈(1,3), 罗尔定理成立",
         "score": 70, "timestamp": "2026-05-24 11:00"},
    ],
    "sessions": 5,
}

# 分析 Agent 推理过程（mock 数据）
ANALYZER_REASONING = """**分析 Agent 推理过程**

**步骤 1/5：信息收集**
- 读取用户学习记录...
- 提取已完成题目数量、正确率、耗时数据
- 获取各知识点掌握程度

**步骤 2/5：知识点覆盖评估**
- 统计各章节已练习题目数
- 计算各知识点正确率分布
- 识别正确率低于 60% 的薄弱知识点

**步骤 3/5：难度适应度分析**
- 评估用户在简单/中等/困难题目上的表现差异
- 分析用户在哪些难度层级出现正确率下降
- 确定用户的最近发展区

**步骤 4/5：学习模式识别**
- 分析用户答题速度与正确率的权衡
- 识别粗心错误 vs 概念不清的模式
- 判断用户是否需要对特定题型加强训练

**步骤 5/5：生成分析报告**
- 综合以上分析形成结构化报告
- 标注需要优先加强的知识点
- 给出针对性学习建议"""

ANALYZER_CONCLUSION = """### 分析结论

| 知识点 | 掌握度 | 状态 |
|:---|:---:|:---:|
| 极限与连续 | 80% | 良好 |
| 导数与微分 | 58% | 一般，需加强 |
| 不定积分与定积分 | 40% | **薄弱，建议优先复习** |
| 微分中值定理 | 20% | **薄弱，建议优先复习** |
| 定积分应用 | 50% | **薄弱，建议优先复习** |

**建议：** 当前阶段重点攻克「不定积分与定积分」和「微分中值定理」，
建议每天 2 小时专项练习。"""

# 规划 Agent 输出（mock 数据）
WEEKLY_PLAN = """### 本周学习计划

| 日期 | 内容 | 时长 |
|:---|:---|---:|
| **周一** | 不定积分基础 | 2h |
| | 复习基本积分公式 | 30min |
| | 练习换元积分法 | 45min |
| | 练习分部积分法 | 45min |
| **周二** | 定积分与应用 | 2h |
| | 牛顿-莱布尼茨公式复习 | 30min |
| | 定积分计算练习 | 45min |
| | 定积分求面积/体积 | 45min |
| **周三** | 微分中值定理 | 2h |
| | 罗尔定理复习 | 30min |
| | 拉格朗日定理复习 | 30min |
| | 综合证明题练习 | 60min |
| **周四** | 导数综合 | 2h |
| | 复合函数求导 | 30min |
| | 隐函数求导 | 30min |
| | 高阶导数 | 30min |
| | 导数应用 | 30min |
| **周五** | 极限专题 | 1.5h |
| | 重要极限复习 | 30min |
| | 等价无穷小替换 | 30min |
| | 洛必达法则 | 30min |
| **周六** | 综合模拟 | 3h |
| | 完整套题练习 | 2h |
| | 错题分析整理 | 1h |
| **周日** | 休息与薄弱点补强 | 1h |
| | 针对本周错题重新练习 | 1h |

> **本周总学习时长：13.5 小时**

---

### 里程碑目标
- 完成不定积分与定积分基础题型全覆盖
- 掌握微分中值定理的三种基本证明方法
- 周测正确率目标：60% → 75%"""

PLANNER_REASONING = """**规划 Agent 推理过程**

**步骤 1/4：综合分析 — 汇总历史表现**
- 读取分析 Agent 输出报告
- 提取各知识点掌握度数据
- 评估总复习进度
- 计算距考试剩余时间

**步骤 2/4：优先级排序 — 确定薄弱环节**
- 按掌握度从低到高排列知识点
- 识别高权重但低掌握的知识点（优先处理）
- 平衡复习轮次与深度

**步骤 3/4：时间分配 — 制定每日计划**
- 根据薄弱程度分配学习时间
- 设置短期（日/周）和长期（月）目标
- 安排定期模拟测试
- 预留复习和调整时间

**步骤 4/4：生成个性化学习计划**
- 输出结构化周计划
- 包含每日学习目标和时长建议
- 设置里程碑检查点"""

# 架构描述文本
ARCHITECTURE_DESC = """
# MathExam AI Agent — 系统架构

## 多 Agent 协作架构

本项目采用 **4 个专业化 Agent 协同工作** 的架构设计，为考研学子提供从**能力分析 → 智能出题 → 自动批改 → 学习规划**的一站式学习体验。

\`\`\`
                    ┌─────────────────────────────────────────┐
                    │            用户 (User)                   │
                    │     Gradio Web / CLI 界面                │
                    └──────────┬──────────────────────┬───────┘
                               │                       │
                    ┌──────────▼──────────┐   ┌───────▼────────┐
                    │   Memory Manager    │   │  LLM Interface │
                    │  (JSON 持久化存储)  │   │ Mock/API 双模式│
                    └─────────────────────┘   └────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Analyzer      │    │ QuestionGen     │    │ Planner         │
│ 分析 Agent    │───▶│ 出题 Agent      │───▶│ 规划 Agent      │
│               │    │                 │    │                 │
│ • 评估掌握度  │    │ • 薄弱点出题    │    │ • 个性化周计划  │
│ • 识别薄弱点  │    │ • 生成解析步骤  │    │ • 时间分配      │
│ • 定位原因    │    │ • 难度自适应    │    │ • 里程碑设置    │
└───────────────┘    └────────┬────────┘    └─────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Grader          │
                     │ 批改 Agent      │
                     │                 │
                     │ • 自动评分      │
                     │ • 逐步骤批改    │
                     │ • 错误分析      │
                     │ • 改进建议      │
                     └─────────────────┘
\`\`\`

## 完整学习闭环

\`\`\`
  分析 ──→ 出题 ──→ 答题 ──→ 批改 ──→ 规划
   │                                       │
   └─────────────── 反馈循环 ──────────────┘
\`\`\`

---

## Agent 职责说明

| Agent | 职责 | 输入 | 输出 |
|:---|:---|:---|:---|
| **Analyzer** (分析) | 评估用户学习状况，识别薄弱知识点 | 学习记录、历史答题数据 | 掌握度分析报告、薄弱点识别 |
| **QuestionGen** (出题) | 根据用户水平生成针对性练习题 | 知识点、掌握度 | 题目、解题步骤、标准答案 |
| **Grader** (批改) | 自动批改用户答案，提供评分和反馈 | 题目、用户答案、标准答案 | 评分、错误分析、改进建议 |
| **Planner** (规划) | 生成个性化周学习计划 | 分析报告、掌握度数据 | 周计划、时间分配、里程碑 |

## 技术栈

| 组件 | 技术 |
|:---|:---|
| 语言 | Python 3.11+ |
| Web 界面 | Gradio |
| CLI 框架 | 标准库 \`argparse\` |
| LLM 接口 | OpenAI 兼容 API（可插拔） |
| Mock 模式 | 内置 12 道数学题 + 演示数据 |
| 数据持久化 | JSON 文件存储 |

## 双模式运行

- **Mock 模式** (默认)：使用内置 12 道数学题 + 演示数据，无需 API Key，开箱即用
- **API 模式**：连接真实 LLM（支持 OpenAI 兼容 API），生成动态题目和个性化反馈

---

*MathExam AI Agent 是小米 MiMo Orbit 百万亿 Token 计划的申请项目。*
"""

# ===========================================================================
# Helper 函数
# ===========================================================================


def _simple_grade(user_answer: str, correct_answer: str) -> dict[str, Any]:
    """简易评分逻辑（复用 Grader Agent 的逻辑）。"""
    ua = user_answer.strip().lower()
    ca = correct_answer.strip().lower()

    if ua == ca:
        score = 100
        feedback = "完全正确！答案与标准答案完全一致。"
    else:
        # 提取数字和关键表达式
        ua_nums = re.findall(r"-?\d+\.?\d*|e²?|π", ua)
        ca_nums = re.findall(r"-?\d+\.?\d*|e²?|π", ca)

        if ua_nums and ca_nums and ua_nums == ca_nums:
            score = 85
            feedback = "基本正确！答案中的数值与标准答案一致，但表达形式有差异。"
        else:
            # 检查关键表达式匹配率
            ca_keywords = re.findall(r"[a-zA-Z一-鿿]+", ca)
            if ca_keywords:
                match_ratio = sum(1 for kw in ca_keywords if kw in ua) / len(ca_keywords)
                if match_ratio > 0.5:
                    score = int(60 + match_ratio * 20)
                    feedback = f"部分正确（匹配度 {match_ratio:.0%}），有一些遗漏或表达不准确的地方。"
                else:
                    score = 40
                    feedback = "答案与标准答案差异较大，建议认真复习相关知识点。"
            else:
                score = 40
                feedback = "答案与标准答案差异较大，建议认真复习相关知识点。"

    return {
        "score": score,
        "feedback": feedback,
        "correct_answer": correct_answer,
    }


def get_knowledge_mastery_color(mastery: float) -> str:
    """根据掌握度返回颜色。"""
    if mastery >= 0.7:
        return "green"
    elif mastery >= 0.4:
        return "orange"
    return "red"


def get_knowledge_status_text(mastery: float) -> str:
    """根据掌握度返回状态文字。"""
    if mastery >= 0.7:
        return "良好"
    elif mastery >= 0.4:
        return "一般"
    return "薄弱"


def get_recommendation(mastery: float) -> str:
    """根据掌握度返回学习建议。"""
    if mastery >= 0.7:
        return "保持练习，挑战更高难度"
    elif mastery >= 0.4:
        return "需要加强，建议每天练习"
    return "优先复习，打好基础"


def pick_question(topic: str, question_idx: int | None = None) -> dict[str, Any]:
    """从 mock 题库中选题。"""
    questions = MOCK_KNOWLEDGE.get(topic, [])
    if not questions:
        # 对于没有题目的知识点，返回通用题目
        return {
            "topic": topic,
            "question": f"【{topic}】请找一个相关的考研数学题目进行练习。",
            "answer": "",
            "steps": "暂无内置题目数据，建议切换到 API 模式生成题目。",
            "difficulty": "中等",
        }
    if question_idx is not None and 0 <= question_idx < len(questions):
        q = questions[question_idx]
    else:
        q = random.choice(questions)
    q["topic"] = topic
    return q


def get_available_questions() -> list[tuple[str, str]]:
    """获取所有可用的题目列表。"""
    result = []
    for topic, questions in MOCK_KNOWLEDGE.items():
        for i, q in enumerate(questions):
            label = f"[{topic}] {q['difficulty']} - {q['question'][:40].replace(chr(10), ' ')}..."
            result.append((f"{topic}||{i}", label))
    return result


def format_question_md(q: dict[str, Any]) -> str:
    """将题目格式化为 Markdown。"""
    return f"""### {q.get('topic', '数学题目')}

**难度：** {q.get('difficulty', '中等')}

---

**题目：**

{q.get('question', '无题目内容')}
"""


def format_steps_md(q: dict[str, Any]) -> str:
    """将解题步骤格式化为 Markdown。"""
    steps_text = q.get("steps", "暂无解题步骤")
    lines = steps_text.split("\n")
    formatted = []
    for line in lines:
        if line.strip().startswith("步骤"):
            formatted.append(f"\n> **{line.strip()}**")
        else:
            formatted.append(f"> {line.strip()}")
    return "\n".join(formatted)


# ===========================================================================
# Gradio UI 构建
# ===========================================================================


def build_analysis_tab() -> None:
    """构建「分析功能」标签页。"""
    records = DEMO_RECORDS
    kp_data = records["knowledge_points"]
    history = records["history"]
    total_practiced = sum(v["practiced"] for v in kp_data.values())
    total_correct = sum(v["correct"] for v in kp_data.values())
    overall = round(total_correct / total_practiced, 2) if total_practiced > 0 else 0

    with gr.Column():
        gr.Markdown("## 学习情况概览")

        # 顶部统计卡片
        with gr.Row():
            with gr.Column(scale=1, min_width=160):
                gr.Markdown(
                    f"""
<div style='text-align:center; padding:16px; background:linear-gradient(135deg,#667eea,#764ba2); border-radius:12px; color:white'>
    <div style='font-size:36px; font-weight:bold'>{total_practiced}</div>
    <div style='font-size:14px; opacity:0.9'>总练习次数</div>
</div>
                """
                )
            with gr.Column(scale=1, min_width=160):
                gr.Markdown(
                    f"""
<div style='text-align:center; padding:16px; background:linear-gradient(135deg,#43e97b,#38f9d7); border-radius:12px; color:white'>
    <div style='font-size:36px; font-weight:bold'>{total_correct}</div>
    <div style='font-size:14px; opacity:0.9'>正确次数</div>
</div>
                """
                )
            with gr.Column(scale=1, min_width=160):
                gr.Markdown(
                    f"""
<div style='text-align:center; padding:16px; background:linear-gradient(135deg,#fa709a,#fee140); border-radius:12px; color:white'>
    <div style='font-size:36px; font-weight:bold'>{overall * 100:.0f}%</div>
    <div style='font-size:14px; opacity:0.9'>总体掌握度</div>
</div>
                """
                )
            with gr.Column(scale=1, min_width=160):
                gr.Markdown(
                    f"""
<div style='text-align:center; padding:16px; background:linear-gradient(135deg,#a18cd1,#fbc2eb); border-radius:12px; color:white'>
    <div style='font-size:36px; font-weight:bold'>{records["sessions"]}</div>
    <div style='font-size:14px; opacity:0.9'>学习会话数</div>
</div>
                """
                )

        gr.Markdown("---")
        gr.Markdown("## 各知识点掌握度")

        # 知识点进度条
        sorted_kp = sorted(kp_data.items(), key=lambda x: x[1]["mastery"], reverse=True)
        for kp_name, kp_info in sorted_kp:
            mastery = kp_info["mastery"]
            color = get_knowledge_mastery_color(mastery)
            status = get_knowledge_status_text(mastery)
            recommend = get_recommendation(mastery)

            html = f"""
<div style='margin: 12px 0; padding: 12px 16px; border-radius: 10px; background: #f8f9fa; border-left: 4px solid {color};'>
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
        <span style='font-weight: bold; font-size: 15px;'>{kp_name}</span>
        <span style='font-size: 14px; color: {color}; font-weight: bold;'>{mastery * 100:.0f}% ({status})</span>
    </div>
    <div style='background: #e9ecef; border-radius: 8px; height: 12px; overflow: hidden;'>
        <div style='width: {mastery * 100:.0f}%; height: 100%; background: {color}; border-radius: 8px; transition: width 0.6s ease;'></div>
    </div>
    <div style='margin-top: 4px; font-size: 12px; color: #6c757d;'>
        练习 {kp_info['practiced']} 次 · 正确 {kp_info['correct']} 次 · {recommend}
    </div>
</div>
"""
            gr.HTML(html)

        # 推理过程
        with gr.Accordion("查看 Agent 推理过程", open=False):
            gr.Markdown(ANALYZER_REASONING)
            gr.Markdown("---")
            gr.Markdown(ANALYZER_CONCLUSION)

        gr.Markdown("---")
        gr.Markdown("## 历史练习记录")

        # 历史记录表格
        history_md = "| 时间 | 知识点 | 题目 | 得分 |\n|:---|:---|:---|---:|\n"
        for h in history:
            score_display = h["score"]
            score_icon = "🟢" if score_display >= 80 else ("🟡" if score_display >= 60 else "🔴")
            history_md += f"| {h['timestamp']} | {h['topic']} | {h['question'][:35]}... | {score_icon} {score_display} |\n"
        gr.Markdown(history_md)


def build_practice_tab() -> None:
    """构建「开始练习」标签页。"""
    with gr.Column():
        gr.Markdown("## 开始做题练习")
        gr.Markdown("选择知识点，系统将生成一道针对性数学题目。完成答题后可提交批改。")

        with gr.Row():
            topic_dropdown = gr.Dropdown(
                choices=ALL_TOPICS,
                value=random.choice(ALL_TOPICS),
                label="选择知识点",
                interactive=True,
            )
            generate_btn = gr.Button("生成题目", variant="primary", scale=0)

        # 题目显示区域
        question_display = gr.Markdown("点击「生成题目」开始练习", label="题目")

        with gr.Accordion("查看解题步骤", open=False):
            steps_display = gr.Markdown("题目生成后显示解题步骤", label="解题步骤")

        with gr.Accordion("查看出题 Agent 推理过程", open=False):
            gr.Markdown("""**出题 Agent 推理过程**

**步骤 1/4：知识点定向 — 选定主题**
- 从分析报告筛选出需要练习的主题
- 确认主题层级：高等数学 -> 一元函数微积分 -> 选定知识点

**步骤 2/4：难度匹配 — 根据用户水平选择合适难度**
- 评估用户当前掌握程度
- 选择略高于当前水平的难度（最近发展区原则）

**步骤 3/4：题目生成**
- 从题库中筛选符合知识点的题目
- 验证题目覆盖核心考点
- 构造解题步骤和评分标准
- 生成完整解析

**步骤 4/4：质量检查**
- 验证题目无歧义
- 确认答案正确性
- 检查步骤完整性""")

        gr.Markdown("---")
        gr.Markdown("### 提交答案")

        with gr.Row():
            answer_input = gr.Textbox(
                label="输入你的答案",
                placeholder="在此输入你的解答...",
                lines=2,
                scale=4,
            )
            submit_btn = gr.Button("提交批改", variant="primary", scale=0)

        # 批改结果显示
        with gr.Row():
            score_display = gr.Markdown("提交答案后显示批改结果", label="批改结果")

        with gr.Accordion("查看批改 Agent 推理过程", open=False):
            gr.Markdown("""**批改 Agent 推理过程**

**步骤 1/4：答案解析**
- 读取待批改题目和标准答案
- 识别题目类型（计算题/证明题/应用题）
- 分解评分要点

**步骤 2/4：用户答案对比**
- 提取用户答案的关键步骤和最终结果
- 与标准答案逐项对比
- 标记正确部分、错误部分和遗漏部分

**步骤 3/4：错误分析**
- 判断错误类型：概念理解错误 / 计算失误 / 方法选择不当
- 追溯错误根源（是知识点欠缺还是粗心）
- 针对性地给出纠正建议

**步骤 4/4：评分与反馈**
- 根据评分标准计算得分
- 生成结构化反馈报告
- 给出改进建议和推荐练习""")

    # ---- 事件绑定（状态管理） ----
    current_question = gr.State({})
    current_topic = gr.State("")

    def on_generate(topic: str) -> tuple[str, str, dict[str, Any]]:
        """生成题目事件处理。"""
        q = pick_question(topic)
        question_md = format_question_md(q)
        steps_md = format_steps_md(q)
        if not steps_md.strip():
            steps_md = "解题步骤生成中..."
        return question_md, steps_md, q

    def on_submit(
        user_answer: str, q: dict[str, Any]
    ) -> str:
        """提交批改事件处理。"""
        if not user_answer or not user_answer.strip():
            return "⚠️ 请先输入你的答案再提交。"
        if not q or not q.get("answer"):
            return "⚠️ 请先生成一道题目。"
        result = _simple_grade(user_answer, q["answer"])
        score = result["score"]
        feedback = result["feedback"]
        correct = result["correct_answer"]

        # 格式化批改结果
        if score >= 80:
            score_icon = "🎉"
            color = "green"
        elif score >= 60:
            score_icon = "👍"
            color = "orange"
        else:
            score_icon = "💪"
            color = "red"

        return f"""
<div style='padding: 20px; border-radius: 12px; background: #f8f9fa; border: 2px solid {color};'>
    <div style='font-size: 24px; text-align: center;'>
        {score_icon} 得分：<span style='color: {color}; font-weight: bold;'>{score}/100</span>
    </div>
    <div style='margin-top: 12px; padding: 12px; background: white; border-radius: 8px;'>
        <p><strong>详细反馈：</strong>{feedback}</p>
        <p><strong>标准答案：</strong><code>{correct}</code></p>
    </div>
    <div style='margin-top: 8px; font-size: 13px; color: #6c757d;'>
        💡 提示：将你的答案与标准答案对比，找出差异点进行针对性学习
    </div>
</div>
"""

    generate_btn.click(
        fn=on_generate,
        inputs=[topic_dropdown],
        outputs=[question_display, steps_display, current_question],
    )

    submit_btn.click(
        fn=on_submit,
        inputs=[answer_input, current_question],
        outputs=[score_display],
    )


def build_plan_tab() -> None:
    """构建「学习计划」标签页。"""
    with gr.Column():
        gr.Markdown("## 个性化学习计划")
        gr.Markdown("基于你的学习情况和薄弱环节，系统为你生成了以下个性化周计划。")

        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown(WEEKLY_PLAN)
            with gr.Column(scale=1):
                # 侧边统计卡片
                records = DEMO_RECORDS
                kp_data = records["knowledge_points"]
                weakest = min(kp_data.items(), key=lambda x: x[1]["mastery"])
                strongest = max(kp_data.items(), key=lambda x: x[1]["mastery"])

                gr.Markdown(
                    f"""
<div style='padding: 16px; border-radius: 12px; background: linear-gradient(135deg, #667eea, #764ba2); color: white;'>
    <h4 style='margin: 0 0 8px 0; color: white;'>学习建议</h4>
    <p style='margin: 4px 0; font-size: 13px;'>最弱知识点：<strong>{weakest[0]}</strong> ({weakest[1]['mastery'] * 100:.0f}%)</p>
    <p style='margin: 4px 0; font-size: 13px;'>最强知识点：<strong>{strongest[0]}</strong> ({strongest[1]['mastery'] * 100:.0f}%)</p>
    <hr style='border-color: rgba(255,255,255,0.3); margin: 10px 0;'>
    <p style='margin: 4px 0; font-size: 12px; opacity: 0.9;'>距考研：约 209 天</p>
    <p style='margin: 4px 0; font-size: 12px; opacity: 0.9;'>目标院校：数学一</p>
</div>
<br>
<div style='padding: 16px; border-radius: 12px; background: #f8f9fa;'>
    <h4 style='margin: 0 0 8px 0;'>本周重点</h4>
    <ul style='padding-left: 20px; margin: 0; font-size: 14px;'>
        <li>不定积分与定积分</li>
        <li>微分中值定理</li>
        <li>导数综合应用</li>
    </ul>
</div>
                """
                )

        with gr.Accordion("查看规划 Agent 推理过程", open=False):
            gr.Markdown(PLANNER_REASONING)


def build_architecture_tab() -> None:
    """构建「系统架构」标签页。"""
    gr.Markdown(ARCHITECTURE_DESC)


# ===========================================================================
# 应用创建
# ===========================================================================

CSS = """
/* 全局样式 */
:root {
    --primary: #667eea;
    --secondary: #764ba2;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
}
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto;
}
/* 标签页样式 */
.tabs {
    border: none;
}
.tab-nav {
    background: transparent;
    border-bottom: 2px solid #e9ecef;
}
.tab-nav button {
    border: none !important;
    background: transparent !important;
    font-weight: 600;
    font-size: 15px;
    padding: 12px 20px;
    color: #6c757d !important;
    transition: all 0.2s;
}
.tab-nav button.selected {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
}
.tab-nav button:hover {
    color: var(--primary) !important;
    background: rgba(102, 126, 234, 0.05) !important;
}
/* Markdown 美化 */
.markdown-text {
    line-height: 1.7;
}
.markdown-text h1 {
    border-bottom: 2px solid var(--primary);
    padding-bottom: 8px;
    margin-top: 24px;
}
.markdown-text h2 {
    color: #333;
    margin-top: 20px;
}
.markdown-text h3 {
    color: #555;
    margin-top: 16px;
}
.markdown-text code {
    background: #f1f3f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
}
.markdown-text pre {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #e9ecef;
}
.markdown-text blockquote {
    border-left: 4px solid var(--primary);
    padding-left: 16px;
    color: #6c757d;
    background: #f8f9fa;
    padding: 8px 16px;
    border-radius: 0 8px 8px 0;
}
.markdown-text table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
}
.markdown-text th {
    background: var(--primary);
    color: white;
    padding: 8px 12px;
    text-align: left;
}
.markdown-text td {
    padding: 8px 12px;
    border-bottom: 1px solid #e9ecef;
}
.markdown-text tr:hover td {
    background: #f1f3f5;
}
/* 按钮样式 */
button.primary {
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 24px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
button.primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
/* 输入框样式 */
input, textarea, select {
    border-radius: 8px !important;
    border: 1px solid #dee2e6 !important;
    padding: 8px 12px !important;
    transition: border-color 0.2s !important;
}
input:focus, textarea:focus, select:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}
/* Accordion 样式 */
.accordion {
    border: 1px solid #e9ecef !important;
    border-radius: 8px !important;
    margin: 8px 0;
}
.accordion > .label {
    background: #f8f9fa !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
/* 滚动条 */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #aaa;
}
"""


def create_app() -> gr.Blocks:
    """创建 Gradio 应用。"""
    with gr.Blocks(
        css=CSS,
        title="MathExam AI Agent",
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="purple",
            font=gr.themes.GoogleFont("Noto Sans SC"),
        ),
    ) as demo:
        # 页头
        gr.Markdown(
            """
<div style='text-align: center; padding: 24px 0 8px 0;'>
    <h1 style='font-size: 32px; background: linear-gradient(135deg, #667eea, #764ba2);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               background-clip: text; margin: 0;'>
        MathExam AI Agent
    </h1>
    <p style='font-size: 16px; color: #6c757d; margin: 4px 0 0 0;'>
        考研数学多 Agent 智能学习系统 | MiMo Orbit 计划
    </p>
    <div style='margin-top: 8px;'>
        <span style='background: #d4edda; color: #155724; padding: 2px 12px; border-radius: 12px;
                     font-size: 13px; font-weight: 600;'>
            MOCK 模式 | 开箱即用，无需 API Key
        </span>
    </div>
</div>
            """
        )

        # 标签页
        with gr.Tabs(elem_classes="tabs"):
            with gr.Tab("分析功能"):
                build_analysis_tab()

            with gr.Tab("开始练习"):
                build_practice_tab()

            with gr.Tab("学习计划"):
                build_plan_tab()

            with gr.Tab("系统架构"):
                build_architecture_tab()

        # 页脚
        gr.Markdown(
            """
<div style='text-align: center; padding: 16px 0; margin-top: 24px; border-top: 1px solid #e9ecef; color: #6c757d; font-size: 13px;'>
    MathExam AI Agent v1.0.0 · 小米 MiMo Orbit 百万亿 Token 计划申请项目<br>
    <a href='https://github.com/happydayday/math-exam-agent' target='_blank' style='color: #667eea; text-decoration: none;'>
        GitHub 仓库
    </a>
</div>
            """
        )

    return demo


# ===========================================================================
# 主入口
# ===========================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MathExam AI Agent Web Demo")
    parser.add_argument(
        "--port", type=int, default=7860, help="服务端口号（默认 7860）"
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="监听地址（默认 127.0.0.1）"
    )
    parser.add_argument(
        "--share", action="store_true", help="创建公开分享链接"
    )
    parser.add_argument(
        "--debug", action="store_true", help="启用调试模式"
    )
    args = parser.parse_args()

    demo = create_app()

    print(f"""
╔══════════════════════════════════════════════════╗
║       MathExam AI Agent Web Demo                 ║
║                                                  ║
║  启动地址: http://{args.host}:{args.port}             ║
║  模式: MOCK（开箱即用，无需 API Key）            ║
║                                                  ║
║  如需公网分享，请添加 --share 参数               ║
╚══════════════════════════════════════════════════╝
    """)

    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        debug=args.debug,
        show_error=True,
    )
else:
    # 供 Hugging Face Spaces 直接导入使用
    demo = create_app()
