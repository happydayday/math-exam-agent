# MathExam AI Agent — 考研数学多 Agent 智能系统

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> **MiMo Orbit 百万亿 Token 计划申请项目**  
> 展示多 Agent 协作和长链推理能力的 AI 数学学习工具。

---

## 项目介绍

MathExam AI Agent 是一个基于多 Agent 协作架构的考研数学智能学习系统。它通过 **4 个专业化 Agent** 协同工作，为考研学子提供从**能力分析 → 智能出题 → 自动批改 → 学习规划**的一站式学习体验。

本项目是 **小米 MiMo Orbit 百万亿 Token 计划** 的申请证明材料，核心特色：

- **多 Agent 协作**：4 个 Agent 各司其职，形成完整学习闭环
- **长链推理可见**：每个 Agent 的思考步骤完整打印到终端，推理过程透明
- **双模式运行**：`mock` 模式无需 API Key 即可演示；`api` 模式连接真实 LLM
- **学习记录持久化**：自动保存学习进度，支持历史追溯

---

## 架构设计

### 多 Agent 协作流程

```
                    ┌─────────────────────────────────────────┐
                    │            用户 (User)                   │
                    │    CLI 终端界面 (Rich 美化)              │
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
```

### 完整学习闭环

```
  分析 ──→ 出题 ──→ 答题 ──→ 批改 ──→ 规划
   │                                       │
   └─────────────── 反馈循环 ──────────────┘
```

---

## 安装

### 前置要求

- Python 3.11 或更高版本
- pip（Python 包管理器）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/happydayday/math-exam-agent.git
cd math-exam-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证安装
python -m math_exam_agent --help
```

---

## 使用说明

### Mock 模式（无需 API Key，开箱即用）

```bash
# 1. 启动交互式学习会话（推荐）
python -m math_exam_agent start --mode mock

# 2. 直接分析学习情况
python -m math_exam_agent analyze --mode mock

# 3. 直接开始练习
python -m math_exam_agent practice --mode mock

# 4. 生成学习计划
python -m math_exam_agent plan --mode mock
```

### API 模式（连接真实 LLM）

```bash
# 配置环境变量
export LLM_API_KEY="your-api-key"
export LLM_API_BASE="https://api.openai.com/v1"   # 可选，支持兼容 API
export LLM_MODEL="gpt-4o"                          # 可选，默认 gpt-4o

# 运行
python -m math_exam_agent start --mode api
```

---

## Mock 模式演示

Mock 模式下，系统内置了丰富的数学题目和解析数据，覆盖以下知识点：

| 知识点 | 难度 | 示例 |
|--------|------|------|
| 极限与连续 | 简单/中等 | lim sin 3x / x, 1-cos x / x² |
| 导数与微分 | 简单/中等 | x³ ln x 求导, 隐函数求导 |
| 不定积分与定积分 | 简单/中等 | ∫3x²+2x+1 dx, ∫x eˣ dx |

每个 Agent 在 mock 模式下都会展示完整的**长链推理过程**，包括：
- 分步骤思考（如「步骤 1/5：信息收集」）
- 中间决策逻辑
- 最终结论

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| CLI 框架 | 标准库 `argparse` |
| 终端美化 | [Rich](https://github.com/Textualize/rich) |
| HTTP 客户端 | [HTTPX](https://www.python-httpx.org/) |
| LLM 接口 | OpenAI 兼容 API（可插拔） |
| 数据持久化 | JSON 文件存储 |
| 数据建模 | [Pydantic](https://docs.pydantic.dev/) |

---

## 项目结构

```
math-exam-agent/
├── README.md                    # 项目说明
├── requirements.txt             # 依赖清单
├── .gitignore                   # Git 忽略规则
├── math_exam_agent/             # 主包
│   ├── __init__.py              # 包信息
│   ├── __main__.py              # python -m 入口
│   ├── main.py                  # CLI 入口与菜单
│   ├── agents/                  # Agent 实现
│   │   ├── base.py              # Agent 基类
│   │   ├── analyzer.py          # 分析 Agent
│   │   ├── question_gen.py      # 出题 Agent
│   │   ├── grader.py            # 批改 Agent
│   │   └── planner.py           # 规划 Agent
│   ├── core/                    # 核心模块
│   │   ├── llm.py               # LLM 接口（mock + API）
│   │   └── memory.py            # 学习记录管理
│   └── utils/                   # 工具模块
│       └── display.py           # Rich 显示工具
├── examples/                    # 示例数据
│   └── demo_session.json        # 演示用学习记录
└── screenshots/                 # 截图目录
    └── README.md                # 截图生成指南
```

---

## 命令行输出预览

在 mock 模式下运行 `python -m math_exam_agent start`：

```
  __  __       _   _                     __ _    ___
 |  \/  | __ _| |_| |__   ___  _ __     / _| |_ / _ \__ _  ___ ___
 | |\/| |/ _` | __| '_ \ / _ \| '_ \   | |_| __| | | / _` |/ __/ _ \
 | |  | | (_| | |_| | | | (_) | | | |  |  _| |_| |_| | (_| | (_|  __/
 |_|  |_|\__,_|\__|_| |_|\___/|_| |_|  |_|  \__|\___/ \__,_|\___\___|

                        考研数学多 Agent 智能学习系统 | MiMo Orbit 计划

═══════════════════════════════════════════════════════════════════════════
                        当前模式：MOCK（使用内置演示数据）
═══════════════════════════════════════════════════════════════════════════

主菜单
┌─────────────────────────────────────────────────────────────┐
│ [1] 🔍 分析学习情况                                         │
│ [2] ✏️  开始做题练习                                        │
│ [3] 📅 生成学习计划                                          │
│ [4] ▶️  完整学习流程 (分析 → 出题 → 批改 → 规划)          │
│ [5] 📊 查看学习统计                                          │
│ [0] 🚪 退出                                                  │
└─────────────────────────────────────────────────────────────┘

请选择 [0-5]:
```

---

## 许可

本项目基于 MIT 许可证开源。

---

## 关于 MiMo Orbit

MiMo Orbit 是小米公司推出的百万亿 Token 计划，旨在推动大语言模型在长链推理和多 Agent 协作方向的创新应用。

本项目作为申请材料，重点展示了：

1. **长链推理**：每个 Agent 的完整推理步骤可视化
2. **多 Agent 协作**：4 Agent 分工合作完成复杂学习任务
3. **可插拔 LLM 架构**：支持从 Mock 到生产级 API 的无缝切换
