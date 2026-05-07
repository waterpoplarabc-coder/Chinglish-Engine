import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class LexicalRule:
    rule_id: str
    layer: str
    pattern: str
    replacement: str


def _split_variants(text: str) -> list[str]:
    raw = re.split(r"\s*/\s*", text)
    variants: list[str] = []
    for item in raw:
        cleaned = item.strip()
        if not cleaned:
            continue
        variants.append(cleaned)
    return variants


def parse_markdown_pairs(md_text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in md_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if line.startswith("| -"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        left, right = parts[0], parts[1]
        if not left or not right:
            continue
        if left == "中式英语" and right == "地道表达":
            continue
        pairs.append((left, right))
    return pairs


def build_lexical_rules(pairs: Iterable[tuple[str, str]]) -> list[LexicalRule]:
    seen: set[tuple[str, str]] = set()
    rules: list[LexicalRule] = []
    i = 1
    for chinglish, proper in pairs:
        for variant in _split_variants(proper):
            key = (variant.casefold(), chinglish.casefold())
            if key in seen:
                continue
            seen.add(key)
            rules.append(
                LexicalRule(
                    rule_id=f"EN_L2_LEX_{i:04d}",
                    layer="L2",
                    pattern=variant,
                    replacement=chinglish,
                )
            )
            i += 1
    return rules


def build_pack(rules: list[LexicalRule]) -> dict:
    return {
        "pack_id": "en-zhstyle",
        "name": "English Chinese-Style Pack",
        "version": "0.1.0",
        "language": "en",
        "style": "zh-thought",
        "rules": [
            {
                "rule_id": r.rule_id,
                "layer": r.layer,
                "type": "lexical_substitution",
                "pattern": r.pattern,
                "replacement": r.replacement,
                "case_insensitive": True,
                "word_boundary": True,
                "min_level": 2,
                "max_level": 5,
                "domain_weight": {"default": 1.0},
            }
            for r in rules
        ],
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    md_path = root / "中式英语（Chinglish）全量分类清单_整理版.md"
    out_path = root / "rulepacks" / "en-zhstyle" / "v0.1" / "pack.json"
    md_text = md_path.read_text(encoding="utf-8")
    pairs = parse_markdown_pairs(md_text)
    rules = build_lexical_rules(pairs)
    pack = build_pack(rules)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path} with {len(rules)} rules")


if __name__ == "__main__":
    main()

