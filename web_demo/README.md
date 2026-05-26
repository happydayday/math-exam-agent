# MathExam AI Agent — Web Demo

考研数学多 Agent 智能学习系统的 **Gradio 网页版** 在线演示。

> 使用 Mock 数据，无需任何 API Key，开箱即用！

---

## 快速启动

```bash
# 1. 安装依赖
pip install gradio

# 2. 启动服务
python app.py

# 3. 打开浏览器访问 http://127.0.0.1:7860
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|:---|:---|---:|
| `--port` | 服务端口号 | 7860 |
| `--host` | 监听地址 | 127.0.0.1 |
| `--share` | 创建公开分享链接（Gradio 临时链接） | 否 |
| `--debug` | 启用调试模式 | 否 |

示例：

```bash
# 指定端口
python app.py --port 8080

# 允许局域网访问
python app.py --host 0.0.0.0

# 创建公开分享链接
python app.py --share
```

---

## 功能标签页

| 标签页 | 功能 |
|:---|:---|
| **分析功能** | 学习情况概览、各知识点掌握度（进度条）、历史练习记录、Agent 推理过程 |
| **开始练习** | 选择知识点、生成题目、查看解题步骤、提交答案、自动批改评分 |
| **学习计划** | 个性化周计划、学习建议、里程碑目标 |
| **系统架构** | 多 Agent 协作架构图（文字描述）、技术栈说明 |

---

## 部署到 Hugging Face Spaces

### 方式一：使用 Python 脚本推送

```bash
python push_to_hf.py
```

需要先设置环境变量 `HF_TOKEN`（从 https://huggingface.co/settings/tokens 获取）。

### 方式二：手动 Git 推送

```bash
# 1. 创建 Hugging Face Space（在 HF 网页上创建 Gradio SDK Space）

# 2. 本地关联并推送
git init
git add .
git commit -m "Initial commit"
git remote add space https://huggingface.co/spaces/你的用户名/你的Space名
git push --force space main
```

### 方式三：使用 Hugging Face CLI

```bash
# 安装
pip install huggingface_hub

# 登录
huggingface-cli login

# 创建 Space
huggingface-cli repo create math-exam-agent-demo --type space --sdk gradio

# 推送
cd web_demo
git init
git add .
git commit -m "Initial commit"
git remote add space https://huggingface.co/spaces/你的用户名/math-exam-agent-demo
git push space main
```

---

## 项目结构

```
web_demo/
├── app.py                  # Gradio 网页应用（主文件）
├── requirements-web.txt     # 依赖清单
├── README.md               # 本文件
└── push_to_hf.py           # HuggingFace Spaces 推送脚本
```

---

## 技术栈

| 组件 | 技术 |
|:---|:---|
| Web 框架 | [Gradio](https://www.gradio.app/) |
| 主题 | Gradio Soft Theme + 自定义 CSS |
| 数据 | Mock 模式（内置 12 道数学题 + 演示数据） |

## 屏幕截图

启动后打开 http://127.0.0.1:7860 即可查看完整界面。包含 4 个标签页：

1. **分析功能** — 统计卡片 + 知识点进度条 + 历史记录
2. **开始练习** — 知识点选择 + 题目显示 + 答案提交 + 自动批改
3. **学习计划** — 周计划表格 + 学习建议卡片
4. **系统架构** — 多 Agent 协作架构图 + 技术栈表格
