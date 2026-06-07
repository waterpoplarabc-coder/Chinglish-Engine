from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.core.engine import RewriteEngine


router = APIRouter(prefix="/api")
_engine = RewriteEngine()


class RewriteRequest(BaseModel):
    text: str = Field(min_length=1, description="输入英文文本")
    lang: str = Field(default="en", description="语言（仅支持 en）")
    level: int = Field(default=3, ge=1, le=5, description="中式强度 1-5")
    domain: str = Field(default="default", description="领域权重配置")
    seed: int | None = Field(default=None, description="随机种子（默认=0，确定性输出）")
    explain: bool = Field(default=True, description="是否返回详细步骤")
    force_change: bool = Field(default=False, description="即使已中式也强制改写")
    discourse_filler: bool = Field(default=False, description="添加语篇填充词")
    skeleton_template: str = Field(default="auto", description="骨架模板 (auto/a/b/c)")
    literal_lexical: bool = Field(default=True, description="应用词汇替换")


class RewriteResponse(BaseModel):
    output: str
    applied_rules: list[str]
    warnings: list[str]
    steps: list[dict]
    skeleton: list[dict]
    structure_type: str
    skeleton_template: str


@router.post("/rewrite", response_model=RewriteResponse)
def rewrite(req: RewriteRequest) -> RewriteResponse:
    result = _engine.rewrite(
        text=req.text,
        lang=req.lang,
        level=req.level,
        domain=req.domain,
        seed=req.seed,
        explain=req.explain,
        force_change=req.force_change,
        discourse_filler=req.discourse_filler,
        skeleton_template=req.skeleton_template,
        literal_lexical=req.literal_lexical,
    )
    return RewriteResponse(
        output=result.output,
        applied_rules=result.applied_rules,
        warnings=result.warnings,
        steps=[{"rule_id": s.rule_id, "before": s.before, "after": s.after} for s in result.steps],
        skeleton=[{"en": s.en, "zh": s.zh, "role": s.role} for s in result.skeleton],
        structure_type=result.structure_type,
        skeleton_template=result.skeleton_template,
    )
