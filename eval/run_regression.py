import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Case:
    name: str
    text: str
    lang: str
    level: int
    domain: str
    expected_output: str | None
    expected_rules: list[str]
    force_change: bool | None
    must_change: bool


def load_cases(path: Path) -> list[Case]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    cases: list[Case] = []
    for item in raw:
        cases.append(
            Case(
                name=str(item["name"]),
                text=str(item["text"]),
                lang=str(item["lang"]),
                level=int(item["level"]),
                domain=str(item.get("domain", "default")),
                expected_output=str(item["expected_output"]) if "expected_output" in item else None,
                expected_rules=list(item.get("expected_rules", [])),
                force_change=item.get("force_change"),
                must_change=bool(item.get("must_change", False)),
            )
        )
    return cases


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "backend"))
    from app.core.engine import RewriteEngine

    cases_path = root / "eval" / "en_regression_cases.json"
    cases = load_cases(cases_path)
    engine = RewriteEngine()

    failed = 0
    for c in cases:
        r = engine.rewrite(
            text=c.text,
            lang=c.lang,
            level=c.level,
            domain=c.domain,
            seed=0,
            explain=True,
            force_change=c.force_change,
            deterministic=True,
        )
        ok_out = True if c.expected_output is None else (r.output == c.expected_output)
        ok_rules = all(x in r.applied_rules for x in c.expected_rules)
        ok_change = (r.output != c.text.strip()) if c.must_change else True
        if ok_out and ok_rules and ok_change:
            print(f"PASS {c.name}")
            continue
        failed += 1
        print(f"FAIL {c.name}")
        print(f"  expected_output: {c.expected_output}")
        print(f"  actual_output:   {r.output}")
        print(f"  expected_rules:  {c.expected_rules}")
        print(f"  actual_rules:    {r.applied_rules}")
        if c.must_change:
            print(f"  must_change:     true")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
