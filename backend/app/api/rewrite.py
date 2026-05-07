from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.core.engine import RewriteEngine


router = APIRouter(prefix="/api")
_engine = RewriteEngine()


class RewriteRequest(BaseModel):
    text: str = Field(min_length=1)
    lang: str = Field(default="en")
    level: int = Field(default=3, ge=1, le=5)
    domain: str = Field(default="default")
    seed: int | None = None
    explain: bool = Field(default=True)
    force_change: bool | None = None
    mode: str | None = None
    discourse_filler: bool | None = None
    skeleton_template: str | None = None
    literal_lexical: bool | None = None


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
        mode=req.mode,
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
