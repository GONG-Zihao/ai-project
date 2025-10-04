from __future__ import annotations

from pathlib import Path
from typing import Any

PROMPT_DIR = Path(__file__).resolve().parent / "templates"

SUBJECT_PROMPTS = {
    "数学": "你是一名资深的数学老师，请以循序渐进的方式引导学生理解问题。",
    "物理": "你是一名物理老师，请结合公式和原理给出解释。",
    "化学": "你是一名化学老师，强调实验步骤与安全注意事项。",
    "英语": "你是一名英语老师，请关注语法与词汇点。",
    "语文": "你是一名语文老师，注意阅读理解与写作技巧。",
    "其他": "你是一名全科学习顾问，请提供清晰且富有启发的讲解。",
}

BASE_TEMPLATE = """请结合以下材料，为学生提供详细的解析与学习建议。

【学生问题】
{question}

【检索资料】
{context}

【学习者画像】
{user_profile}

请输出：
1. 题目分析
2. 分步解题过程（必要时包含公式）
3. 常见错误及纠正
4. 后续巩固建议
"""


class PromptTemplateRegistry:
    def get_system_prompt(self, *, subject: str | None = None) -> str:
        if subject and subject in SUBJECT_PROMPTS:
            return SUBJECT_PROMPTS[subject]
        return SUBJECT_PROMPTS["其他"]

    def render(self, *, question: str, context: str, user_context: dict[str, Any]) -> str:
        user_profile = user_context or {"level": "未知", "goals": []}
        return BASE_TEMPLATE.format(
            question=question,
            context=context or "暂无相关资料",
            user_profile=user_profile,
        )
