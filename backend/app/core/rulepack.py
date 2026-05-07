from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Rule:
    rule_id: str
    layer: str
    type: str
    min_level: int
    max_level: int
    priority: int
    domain_weight: dict[str, float]
    params: dict[str, Any]


@dataclass(frozen=True)
class RulePack:
    pack_id: str
    version: str
    language: str
    style: str
    rules: list[Rule]


def _as_float(x: Any) -> float:
    if isinstance(x, (int, float)):
        return float(x)
    return 1.0


def load_rulepack(path: Path) -> RulePack:
    data = json.loads(path.read_text(encoding="utf-8"))
    rules: list[Rule] = []
    for raw in data.get("rules", []):
        domain_weight: dict[str, float] = {}
        for k, v in (raw.get("domain_weight") or {}).items():
            domain_weight[str(k)] = _as_float(v)
        params: dict[str, Any] = {}
        for k, v in raw.items():
            if k in {
                "rule_id",
                "layer",
                "type",
                "min_level",
                "max_level",
                "priority",
                "domain_weight",
            }:
                continue
            params[k] = v
        rules.append(
            Rule(
                rule_id=str(raw["rule_id"]),
                layer=str(raw.get("layer", "L2")),
                type=str(raw.get("type", "lexical_substitution")),
                min_level=int(raw.get("min_level", 1)),
                max_level=int(raw.get("max_level", 5)),
                priority=int(raw.get("priority", 0)),
                domain_weight=domain_weight or {"default": 1.0},
                params=params,
            )
        )
    return RulePack(
        pack_id=str(data.get("pack_id", "")),
        version=str(data.get("version", "")),
        language=str(data.get("language", "")),
        style=str(data.get("style", "")),
        rules=rules,
    )
