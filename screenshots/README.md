# 截图生成指南

本项目在 mock 模式下无需真实 API Key 即可运行。以下是建议生成截图的流程：

## 截图 1：启动界面 (screenshot-01-start.png)

```bash
python -m math_exam_agent start --mode mock
```

执行以上命令后，截取启动 Banner 和主菜单。

## 截图 2：分析流程 (screenshot-02-analyze.png)

在主菜单中选择 `1`，截取分析 Agent 的完整推理过程和学习情况摘要。

## 截图 3：练习流程 (screenshot-03-practice.png)

在主菜单中选择 `2`，截取出题 Agent 生成的数学题目。输入一个答案后，截取批改 Agent 的评分反馈。

## 截图 4：完整流程 (screenshot-04-full-pipeline.png)

在主菜单中选择 `4`，展示四个 Agent 的完整协作流程：
1. 分析 Agent → 2. 出题 Agent → 3. 批改 Agent → 4. 规划 Agent

## 截图 5：子命令 (screenshot-05-subcommands.png)

分别执行以下命令并截取输出：

```bash
python -m math_exam_agent analyze --mode mock
python -m math_exam_agent practice --mode mock
python -m math_exam_agent plan --mode mock
```

## 生成建议

- 使用终端默认配色即可，rich 库会自动美化输出
- 建议在终端宽度 100 字符以上运行
- Windows 用户可用 `Ctrl+Shift+S`（Windows Terminal）保存截图
- 将截图文件（PNG 格式）放在本目录，文件名与上面对应
