"""
MathExam AI Agent — Hugging Face Spaces 推送脚本
================================================

自动创建并推送 Gradio 演示到 Hugging Face Spaces。

使用方式：
  1. 设置环境变量 HF_TOKEN
  2. python push_to_hf.py

如果 HF_TOKEN 未设置，脚本会输出部署指引。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# 配置
SPACE_NAME = "math-exam-agent-demo"  # Hugging Face Space 名称
SPACE_TITLE = "MathExam AI Agent"
SDK = "gradio"
HF_TOKEN = os.environ.get("HF_TOKEN", "")

HERE = Path(__file__).parent.resolve()
PROJECT_ROOT = HERE.parent


def check_prerequisites() -> list[str]:
    """检查前置条件，返回缺失项列表。"""
    missing = []

    # 检查 git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("git")

    # 检查 Python
    if sys.version_info < (3, 9):
        missing.append("Python >= 3.9")

    return missing


def check_hf_token() -> bool:
    """检查 HF token 是否可用。"""
    if HF_TOKEN:
        return True

    # 尝试从 huggingface-cli 获取
    try:
        result = subprocess.run(
            ["huggingface-cli", "whoami"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def create_space_using_api() -> bool:
    """使用 huggingface_hub API 创建 Space。"""
    try:
        from huggingface_hub import HfApi, create_repo

        api = HfApi(token=HF_TOKEN if HF_TOKEN else None)

        # 1. 创建 Space
        print(f"正在创建 Hugging Face Space: {SPACE_NAME} ...")
        try:
            create_repo(
                repo_id=SPACE_NAME,
                repo_type="space",
                private=False,
                exist_ok=True,
                space_sdk=SDK,
                token=HF_TOKEN if HF_TOKEN else None,
            )
            print(f"  -> 创建成功: https://huggingface.co/spaces/{api.whoami()['name']}/{SPACE_NAME}")
        except Exception as e:
            if "already exists" in str(e):
                print(f"  -> Space 已存在，将覆盖推送...")
            else:
                print(f"  -> 创建失败: {e}")
                return False

        # 2. 上传文件
        space_files = [
            HERE / "app.py",
            HERE / "requirements-web.txt",
            HERE / "README.md",
        ]

        for file_path in space_files:
            if file_path.exists():
                print(f"  上传: {file_path.name}")
                api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=file_path.name,
                    repo_id=f"{api.whoami()['name']}/{SPACE_NAME}",
                    repo_type="space",
                    token=HF_TOKEN if HF_TOKEN else None,
                )

        # 3. 上传 requirements.txt (HF 需要这个文件名)
        req_src = HERE / "requirements-web.txt"
        if req_src.exists():
            print("  上传: requirements.txt (HuggingFace 标准)")
            api.upload_file(
                path_or_fileobj=str(req_src),
                path_in_repo="requirements.txt",
                repo_id=f"{api.whoami()['name']}/{SPACE_NAME}",
                repo_type="space",
                token=HF_TOKEN if HF_TOKEN else None,
            )

        print(f"\n部署完成！")
        print(f"访问地址: https://huggingface.co/spaces/{api.whoami()['name']}/{SPACE_NAME}")
        return True

    except ImportError:
        print("错误：请先安装 huggingface_hub: pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"错误：API 推送失败: {e}")
        return False


def create_space_using_git() -> bool:
    """使用 git 方式推送 Space。"""
    # 先尝试获取 HF 用户名
    username = ""
    try:
        result = subprocess.run(
            ["huggingface-cli", "whoami"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines:
                username = lines[0].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if not username and HF_TOKEN:
        try:
            from huggingface_hub import HfApi

            api = HfApi(token=HF_TOKEN)
            username_info = api.whoami()
            username = username_info["name"]
        except Exception:
            pass

    if not username:
        print("无法自动获取 Hugging Face 用户名。")
        return False

    space_repo = f"https://huggingface.co/spaces/{username}/{SPACE_NAME}"

    print(f"正在通过 git 推送至: {space_repo}")

    # 在临时目录中操作
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 复制文件到临时目录
        files_to_copy = [
            "app.py",
            "requirements-web.txt",
            "README.md",
        ]
        for fname in files_to_copy:
            src = HERE / fname
            if src.exists():
                shutil.copy2(src, tmp_path / fname)

        # requirements.txt (HF 标准格式)
        if (tmp_path / "requirements-web.txt").exists():
            shutil.copy2(
                tmp_path / "requirements-web.txt",
                tmp_path / "requirements.txt",
            )

        # 创建 README.md (HuggingFace Space 元数据)
        readme_path = tmp_path / "README.md"
        if not readme_path.exists():
            readme_path.write_text(
                f"""---
title: {SPACE_TITLE}
emoji: 🎓
colorFrom: indigo
colorTo: purple
sdk: {SDK}
sdk_version: "5.0.0"
app_file: app.py
pinned: false
---

# {SPACE_TITLE}

考研数学多 Agent 智能学习系统 Web 演示
""",
                encoding="utf-8",
            )

        # git init 并推送
        try:
            subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(
                ["git", "add", "."], cwd=tmp_path, capture_output=True, check=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit: MathExam AI Agent Web Demo"],
                cwd=tmp_path,
                capture_output=True,
                check=True,
            )

            # 添加 remote 并推送
            if HF_TOKEN:
                # 使用 token 认证
                auth_space_repo = space_repo.replace(
                    "https://", f"https://user:{HF_TOKEN}@"
                )
                result = subprocess.run(
                    ["git", "remote", "add", "space", auth_space_repo],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    print(f"  添加 remote 失败: {result.stderr}")
                    return False

                result = subprocess.run(
                    ["git", "push", "--force", "space", "main"],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode == 0:
                    print(f"推送成功！访问地址: {space_repo}")
                    return True
                else:
                    print(f"  推送失败: {result.stderr}")
                    return False
            else:
                # 需要交互式认证
                # 设置 remote (不含认证，用户需要先 login)
                subprocess.run(
                    ["git", "remote", "add", "space", space_repo],
                    cwd=tmp_path,
                    capture_output=True,
                )
                print(f"\n已创建本地仓库，请手动推送：")
                print(f"  cd {tmp_path}")
                print(f"  git push --force space main")
                print(f"\n或者在本地 web_demo/ 目录执行：")
                print(f"  cd {HERE}")
                print(f"  git init")
                print(f"  git add .")
                print(f"  git commit -m 'Initial commit'")
                print(f"  git remote add space {space_repo}")
                print(f"  git push --force space main")
                return False

        except subprocess.TimeoutExpired:
            print("错误：git 推送超时（超过 120 秒）")
            return False
        except subprocess.CalledProcessError as e:
            print(f"错误：git 操作失败: {e}")
            return False


def print_manual_deploy_guide() -> None:
    """输出手动部署指引。"""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║          手动部署到 Hugging Face Spaces 指引                  ║
╚══════════════════════════════════════════════════════════════╝

方式一：网页方式（推荐给新手）
─────────────────────────────────
1. 打开 https://huggingface.co/new-space
2. Space Name: math-exam-agent-demo
3. SDK: Gradio
4. 点击创建
5. 在 Files 页面手动上传以下文件：
   - app.py
   - requirements.txt（将 requirements-web.txt 重命名）
   - README.md
6. Space 会自动部署

方式二：Git 推送
─────────────────────────────────
1. 安装 huggingface_hub: pip install huggingface_hub
2. 登录: huggingface-cli login（需要先创建 HF Token）
3. 创建 Space:
   huggingface-cli repo create math-exam-agent-demo \\
       --type space --sdk gradio
4. 推送:
   cd web_demo
   cp requirements-web.txt requirements.txt  # HF 需要此文件名
   git init
   git add .
   git commit -m "Initial commit"
   git remote add space \\
       https://huggingface.co/spaces/你的用户名/math-exam-agent-demo
   git push --force space main

方式三：直接运行（本地演示）
─────────────────────────────────
   cd web_demo
   pip install gradio
   python app.py
   访问 http://127.0.0.1:7860

HuggingFace Token 获取: https://huggingface.co/settings/tokens
"""
    )


def main() -> None:
    """主入口。"""
    print("=" * 60)
    print("  MathExam AI Agent - Hugging Face Spaces 部署工具")
    print("=" * 60)
    print()

    # 检查前置条件
    missing = check_prerequisites()
    if missing:
        print(f"缺少必要工具: {', '.join(missing)}")
        print("请先安装后重试。")
        print_manual_deploy_guide()
        sys.exit(1)

    # 检查 HF token
    has_token = check_hf_token()

    if has_token:
        print("HuggingFace 认证可用。")
        print()

        # 尝试 API 方式（优先）
        print("[方式 1] 使用 huggingface_hub API...")
        if create_space_using_api():
            return

        # API 失败，尝试 git 方式
        print()
        print("[方式 2] 使用 git 推送...")
        if create_space_using_git():
            return

        print()
        print("自动部署均失败。请按以下指引手动部署。")
    else:
        print("未检测到 HuggingFace 认证信息。")
        print("如需自动部署，请设置环境变量 HF_TOKEN。")
        print()

    print_manual_deploy_guide()


if __name__ == "__main__":
    main()
