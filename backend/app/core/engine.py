from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path

from app.core.rulepack import RulePack, load_rulepack, Rule


@dataclass(frozen=True)
class SkeletonItem:
    en: str
    zh: str
    role: str


@dataclass(frozen=True)
class RewriteStep:
    rule_id: str
    before: str
    after: str


@dataclass(frozen=True)
class RewriteResult:
    output: str
    applied_rules: list[str]
    warnings: list[str]
    steps: list[RewriteStep]
    skeleton: list[SkeletonItem]
    structure_type: str
    skeleton_template: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _boundary_regex(pattern: str) -> str:
    escaped = re.escape(pattern)
    return rf"(?<![A-Za-z]){escaped}(?![A-Za-z])"


def _compile_lexical(pattern: str, case_insensitive: bool, word_boundary: bool) -> re.Pattern[str]:
    flags = re.IGNORECASE if case_insensitive else 0
    pat = _boundary_regex(pattern) if word_boundary else re.escape(pattern)
    return re.compile(pat, flags=flags)


def _level_prob(level: int) -> float:
    return {1: 0.0, 2: 0.15, 3: 0.35, 4: 0.6, 5: 0.85}.get(level, 0.35)


def _max_replacements(level: int) -> int:
    return {1: 0, 2: 3, 3: 6, 4: 12, 5: 24}.get(level, 6)

def _layer_rank(layer: str) -> int:
    return {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}.get(layer.upper(), 9)

def _strip_ending_punct(text: str) -> tuple[str, str]:
    m = re.match(r"^(.*?)([.!?])$", text.strip())
    if not m:
        return text.strip(), ""
    return m.group(1).strip(), m.group(2)


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+", text))


def _gloss(word: str) -> str:
    w = word.lower()
    table = {
        "i": "我",
        "we": "我们",
        "you": "你",
        "he": "他",
        "she": "她",
        "they": "他们",
        "want": "想",
        "plan": "打算",
        "planning": "打算",
        "hope": "希望",
        "hoping": "希望",
        "prepare": "准备",
        "preparing": "准备",
        "decide": "决定",
        "deciding": "决定",
        "go": "去",
        "today": "今天",
        "tomorrow": "明天",
        "yesterday": "昨天",
        "china": "中国",
        "beijing": "北京",
        "morning": "早上",
        "good": "好",
        "night": "晚上",
        "thank": "谢",
    }
    return table.get(w, "")


def _is_phrase(text: str) -> bool:
    core, _ = _strip_ending_punct(text)
    return bool(re.fullmatch(r"[A-Za-z]+(?:\s+[A-Za-z]+){0,2}", core)) and _word_count(core) <= 3


def _expand_contractions(text: str) -> str:
    table: list[tuple[str, str]] = [
        (r"\bI'm\b", "I am"),
        (r"\bI’m\b", "I am"),
        (r"\bYou're\b", "You are"),
        (r"\bYou’re\b", "You are"),
        (r"\bWe're\b", "We are"),
        (r"\bWe’re\b", "We are"),
        (r"\bThey're\b", "They are"),
        (r"\bThey’re\b", "They are"),
        (r"\bHe's\b", "He is"),
        (r"\bHe’s\b", "He is"),
        (r"\bShe's\b", "She is"),
        (r"\bShe’s\b", "She is"),
        (r"\bit's\b", "it is"),
        (r"\bit’s\b", "it is"),
    ]
    out = text
    for pat, rep in table:
        out = re.sub(pat, rep, out)
    return out


class RewriteEngine:
    def __init__(self) -> None:
        root = _repo_root() / "rulepacks" / "en-zhstyle"
        base_path = root / "v0.1" / "pack.json"
        legacy_filler_path = root / "legacy-filler" / "v0.1" / "pack.json"
        base_pack = load_rulepack(base_path)
        legacy_pack = load_rulepack(legacy_filler_path) if legacy_filler_path.exists() else None
        all_rules = list(base_pack.rules) + (list(legacy_pack.rules) if legacy_pack else [])
        self._pack = base_pack
        self._rules = sorted(
            all_rules,
            key=lambda r: (
                _layer_rank(r.layer),
                -int(r.priority),
                -(len(str(r.params.get("pattern", ""))) if r.type == "lexical_substitution" else 0),
                r.rule_id,
            ),
        )
        self._compiled_lexical: dict[str, re.Pattern[str]] = {}
        self._compiled_regex: dict[str, re.Pattern[str]] = {}
        self._compiled_trigger: dict[str, re.Pattern[str]] = {}
        for r in self._rules:
            trigger = r.params.get("trigger_regex")
            if isinstance(trigger, str) and trigger:
                self._compiled_trigger[r.rule_id] = re.compile(trigger, flags=re.IGNORECASE)
            if r.type == "lexical_substitution":
                pattern = str(r.params.get("pattern", ""))
                if not pattern:
                    continue
                self._compiled_lexical[r.rule_id] = _compile_lexical(
                    pattern=pattern,
                    case_insensitive=bool(r.params.get("case_insensitive", True)),
                    word_boundary=bool(r.params.get("word_boundary", True)),
                )
            if r.type == "regex_substitution":
                pattern = str(r.params.get("pattern", ""))
                if not pattern:
                    continue
                self._compiled_regex[r.rule_id] = re.compile(pattern, flags=re.IGNORECASE)

    def rewrite(
        self,
        text: str,
        lang: str,
        level: int,
        domain: str,
        seed: int | None,
        explain: bool,
        force_change: bool | None = None,
        mode: str | None = None,
        discourse_filler: bool | None = None,
        skeleton_template: str | None = None,
        literal_lexical: bool | None = None,
        deterministic: bool = False,
    ) -> RewriteResult:
        warnings: list[str] = []
        if lang.lower() != "en":
            warnings.append("当前仅支持英文(en)的中式改写；已原样返回")
            return RewriteResult(
                output=text,
                applied_rules=[],
                warnings=warnings,
                steps=[],
                skeleton=[],
                structure_type="unsupported",
                skeleton_template="auto",
            )

        if mode is None:
            mode = "zh_skeleton_literal"
        if discourse_filler is None:
            discourse_filler = False
        if force_change is None:
            force_change = False
        if skeleton_template is None:
            skeleton_template = "auto"
        if literal_lexical is None:
            literal_lexical = True

        if deterministic and seed is None:
            seed = 0
        rng = random.Random(seed)
        applied: list[str] = []
        steps: list[RewriteStep] = []
        skeleton: list[SkeletonItem] = []
        normalized = self._normalize(text)
        transformed = normalized

        if mode == "zh_skeleton_literal":
            is_phrase = _is_phrase(transformed)
            before = transformed
            transformed, step_id, skeleton, structure_type, template_used = self._apply_zh_skeleton_literal(
                transformed,
                level=level,
                explain=explain,
                skeleton_template=skeleton_template,
            )
            if transformed != before and step_id:
                if explain:
                    steps.append(RewriteStep(rule_id=step_id, before=before, after=transformed))
                applied.append(step_id)

            if literal_lexical or (discourse_filler and (not is_phrase)):
                transformed, extra_steps, extra_applied = self._apply_rulepack(
                    transformed,
                    level=level,
                    domain=domain,
                    rng=rng,
                    explain=explain,
                    discourse_filler=discourse_filler and (not is_phrase),
                    deterministic=deterministic,
                    literal_lexical=literal_lexical,
                )
                steps.extend(extra_steps)
                applied.extend(extra_applied)
            return RewriteResult(
                output=transformed,
                applied_rules=applied if explain else [],
                warnings=warnings,
                steps=steps,
                skeleton=skeleton if explain else [],
                structure_type=structure_type,
                skeleton_template=template_used,
            )

        budget = _max_replacements(level)
        prob = _level_prob(level)
        if force_change and level >= 4:
            prob = max(prob, 0.9)

        for rule in self._rules:
            if not (rule.min_level <= level <= rule.max_level):
                continue
            domain_w = rule.domain_weight.get(domain, rule.domain_weight.get("default", 1.0))
            if rng.random() > prob * domain_w:
                continue
            trig = self._compiled_trigger.get(rule.rule_id)
            if trig is not None and not trig.search(transformed):
                continue
            before = transformed
            transformed = self._apply_rule(rule, transformed)
            if transformed != before:
                if explain:
                    steps.append(RewriteStep(rule_id=rule.rule_id, before=before, after=transformed))
                applied.append(rule.rule_id)
                if budget > 0 and rule.type in {"lexical_substitution"}:
                    budget -= 1
                if budget <= 0:
                    break

        if force_change and transformed == normalized and level >= 2:
            before = transformed
            transformed = self._fallback(transformed, level)
            if transformed != before:
                rid = "EN_FALLBACK_PREFIX"
                if explain:
                    steps.append(RewriteStep(rule_id=rid, before=before, after=transformed))
                applied.append(rid)

        return RewriteResult(
            output=transformed,
            applied_rules=applied if explain else [],
            warnings=warnings,
            steps=steps,
            skeleton=skeleton if explain else [],
            structure_type="legacy",
            skeleton_template="auto",
        )

    def _normalize(self, text: str) -> str:
        text = text.strip()
        text = _expand_contractions(text)
        text = re.sub(r"\s+", " ", text)
        return text

    def _apply_zh_skeleton_literal(
        self,
        text: str,
        level: int,
        explain: bool,
        skeleton_template: str,
    ) -> tuple[str, str | None, list[SkeletonItem], str, str]:
        core, punct = _strip_ending_punct(text)
        lower = core.lower()

        if lower == "good morning":
            out = "morning good" + punct
            sk = [
                SkeletonItem(en="good", zh=_gloss("good"), role="ADJ"),
                SkeletonItem(en="morning", zh=_gloss("morning"), role="N"),
            ]
            return out, "EN_PHRASE_GOOD_MORNING_SWAP", sk, "phrase", "auto"

        if lower == "good night":
            out = "night good" + punct
            sk = [
                SkeletonItem(en="good", zh=_gloss("good"), role="ADJ"),
                SkeletonItem(en="night", zh=_gloss("night"), role="N"),
            ]
            return out, "EN_PHRASE_GOOD_NIGHT_SWAP", sk, "phrase", "auto"

        if lower == "thank you":
            sk = [
                SkeletonItem(en="thank", zh=_gloss("thank"), role="V"),
                SkeletonItem(en="you", zh=_gloss("you"), role="O"),
            ]
            return text, None, sk, "phrase", "auto"

        m_cause = re.match(r"^(?P<main>.+?),\s*because\s+(?P<cause>.+)$", core, flags=re.IGNORECASE)
        if m_cause:
            main = m_cause.group("main").strip()
            cause = m_cause.group("cause").strip()
            out = f"Because {cause}, so {main}".strip() + punct
            return out, "EN_ZH_COMPOUND_BECAUSE_SO", [], "compound_cause", "auto"

        m_if = re.match(r"^if\s+(?P<cond>.+?),\s*(?P<main>.+)$", core, flags=re.IGNORECASE)
        if m_if:
            cond = m_if.group("cond").strip()
            main = m_if.group("main").strip()
            out = f"If {cond}, then {main}".strip() + punct
            return out, "EN_ZH_COMPOUND_IF_THEN", [], "compound_if", "auto"

        out, step_id, sk, template_used = self._try_intent_time_reorder(
            core=core,
            level=level,
            skeleton_template=skeleton_template,
        )
        if step_id:
            return out + punct, step_id, sk, "simple", template_used

        out, step_id, sk, template_used = self._try_svo_time_place_reorder(
            core=core,
            skeleton_template=skeleton_template,
        )
        if step_id:
            return out + punct, step_id, sk, "simple", template_used

        return text, None, [], "simple", "auto"

    def _try_intent_time_reorder(
        self,
        core: str,
        level: int,
        skeleton_template: str,
    ) -> tuple[str, str | None, list[SkeletonItem], str]:
        time_words = r"(today|tomorrow|yesterday)"

        m = re.match(
            rf"^(?P<subj>I|We|You|He|She|They)\s+(?P<intent>want|plan|hope|prepare|decide)\s+(?P<rest>.+?)\s+(?P<time>{time_words})$",
            core,
            flags=re.IGNORECASE,
        )
        intent_phrase = None
        subj = None
        rest = None
        time = None
        if m:
            subj = m.group("subj")
            intent = m.group("intent")
            rest = m.group("rest").strip()
            time = m.group("time")
            intent_phrase = f"{subj} {intent}"

        if intent_phrase is None:
            m2 = re.match(
                rf"^(?P<subj>I|We|You|He|She|They)\s+(?P<aux>am|are|is)\s+(?P<intent>planning|hoping|preparing|deciding)\s+to\s+(?P<vp>.+?)\s+(?P<time>{time_words})$",
                core,
                flags=re.IGNORECASE,
            )
            if m2:
                subj = m2.group("subj")
                aux = m2.group("aux")
                intent = m2.group("intent")
                rest = ("to " + m2.group("vp").strip()).strip()
                time = m2.group("time")
                intent_phrase = f"{subj} {aux} {intent}"

        if intent_phrase is None or subj is None or rest is None or time is None:
            return core, None, [], "auto"

        if re.search(rf"\b{re.escape(time)}\b", rest, flags=re.IGNORECASE):
            return core, None, [], "auto"

        rest2 = rest
        if level >= 5:
            rest2 = re.sub(r"^to\s+", "", rest2, flags=re.IGNORECASE)
            rest2 = re.sub(r"\bgo\s+to\s+", "go ", rest2, flags=re.IGNORECASE)
            rest2 = re.sub(r"\bto\s+", "", rest2, flags=re.IGNORECASE)
            rest2 = re.sub(r"\b(the|a|an)\s+", "", rest2, flags=re.IGNORECASE)
        rest2 = re.sub(r"\s+", " ", rest2).strip()

        template = skeleton_template.lower()
        if template not in {"auto", "a", "b", "c"}:
            template = "auto"
        if template == "auto":
            template = "a"

        if template == "b":
            out = f"{time} {intent_phrase} {rest2}".strip()
        else:
            out = f"{intent_phrase} {time} {rest2}".strip()
        out = re.sub(r"\s+", " ", out).strip()

        place = ""
        m_place = re.search(r"\bgo(?:\s+to)?\s+([A-Za-z]+)\b", rest, flags=re.IGNORECASE)
        if m_place:
            place = m_place.group(1)

        intent_token = intent_phrase.split()[-1]
        sk: list[SkeletonItem] = [
            SkeletonItem(en=subj, zh=_gloss(subj), role="S"),
            SkeletonItem(en=intent_token, zh=_gloss(intent_token), role="V1"),
            SkeletonItem(en=time, zh=_gloss(time), role="T"),
        ]
        if re.search(r"\bgo\b", rest, flags=re.IGNORECASE):
            sk.append(SkeletonItem(en="go", zh=_gloss("go"), role="V2"))
        if place:
            sk.append(SkeletonItem(en=place, zh=_gloss(place), role="P"))

        rid = "EN_ZH_SKELETON_REORDER_INTENT_TIME"
        return out, rid, sk, template

    def _try_svo_time_place_reorder(
        self,
        core: str,
        skeleton_template: str,
    ) -> tuple[str, str | None, list[SkeletonItem], str]:
        m = re.match(r"^(?P<subj>I|We|You|He|She|They)\s+(?P<rest>.+)$", core, flags=re.IGNORECASE)
        if not m:
            return core, None, [], "auto"
        subj = m.group("subj")
        rest = m.group("rest").strip()

        m_time = re.match(rf"^(?P<pre>.+?)\s+(?P<time>today|tomorrow|yesterday)$", rest, flags=re.IGNORECASE)
        if not m_time:
            return core, None, [], "auto"
        pre = m_time.group("pre").strip()
        time = m_time.group("time")

        place_phrase = ""
        m_place = re.search(r"\b(at|in|on)\b\s+(.+)$", pre, flags=re.IGNORECASE)
        verb_obj = pre
        if m_place:
            place_phrase = m_place.group(0).strip()
            verb_obj = pre[: m_place.start()].strip()
            if not verb_obj:
                verb_obj = pre

        template = skeleton_template.lower()
        if template not in {"auto", "a", "b", "c"}:
            template = "auto"
        if template == "auto":
            template = "a"

        if template == "c" and place_phrase:
            out = f"{place_phrase} {subj} {time} {verb_obj}".strip()
        elif template == "b":
            out = f"{time} {subj} {place_phrase} {verb_obj}".strip()
        else:
            out = f"{subj} {time} {place_phrase} {verb_obj}".strip()
        out = re.sub(r"\s+", " ", out).strip()

        sk: list[SkeletonItem] = [
            SkeletonItem(en=subj, zh=_gloss(subj), role="S"),
            SkeletonItem(en=time, zh=_gloss(time), role="T"),
        ]
        if place_phrase:
            sk.append(SkeletonItem(en=place_phrase, zh="", role="P"))
        return out, "EN_ZH_SKELETON_S_T_P_V_O", sk, template

    def _apply_rulepack(
        self,
        text: str,
        level: int,
        domain: str,
        rng: random.Random,
        explain: bool,
        discourse_filler: bool,
        deterministic: bool,
        literal_lexical: bool,
    ) -> tuple[str, list[RewriteStep], list[str]]:
        applied: list[str] = []
        steps: list[RewriteStep] = []
        transformed = text
        budget = _max_replacements(level)
        prob = 1.0 if deterministic else _level_prob(level)
        prefix_applied = False
        suffix_applied = False

        for rule in self._rules:
            if rule.type in {"lexical_substitution", "regex_substitution"}:
                if not literal_lexical:
                    continue
                if rule.layer.upper() != "L2":
                    continue
            elif rule.type in {"prefix_injection", "suffix_injection"}:
                if not discourse_filler:
                    continue
                if rule.type == "prefix_injection" and prefix_applied:
                    continue
                if rule.type == "suffix_injection" and suffix_applied:
                    continue
            else:
                continue
            if not (rule.min_level <= level <= rule.max_level):
                continue
            domain_w = rule.domain_weight.get(domain, rule.domain_weight.get("default", 1.0))
            if (not deterministic) and rng.random() > prob * domain_w:
                continue
            trig = self._compiled_trigger.get(rule.rule_id)
            if trig is not None and not trig.search(transformed):
                continue
            before = transformed
            transformed = self._apply_rule(rule, transformed)
            if transformed != before:
                if explain:
                    steps.append(RewriteStep(rule_id=rule.rule_id, before=before, after=transformed))
                applied.append(rule.rule_id)
                if rule.type == "prefix_injection":
                    prefix_applied = True
                if rule.type == "suffix_injection":
                    suffix_applied = True
                if budget > 0 and rule.type in {"lexical_substitution"}:
                    budget -= 1
                if budget <= 0:
                    break

        return transformed, steps, applied

    def _apply_rule(self, rule: Rule, text: str) -> str:
        if rule.type == "lexical_substitution":
            cregex = self._compiled_lexical.get(rule.rule_id)
            if cregex is None:
                return text
            replacement = str(rule.params.get("replacement", ""))
            if not replacement:
                return text
            out, n = cregex.subn(replacement, text, count=1)
            return out if n > 0 else text

        if rule.type == "regex_substitution":
            cregex = self._compiled_regex.get(rule.rule_id)
            if cregex is None:
                return text
            replacement = str(rule.params.get("replacement", ""))
            if not replacement:
                return text
            out, n = cregex.subn(replacement, text, count=1)
            return out if n > 0 else text

        if rule.type == "prefix_injection":
            prefix = str(rule.params.get("prefix", "")).rstrip()
            if not prefix:
                return text
            if text.lower().startswith(prefix.strip().lower()):
                return text
            if re.match(r"^[A-Za-z]", text) and prefix and (prefix[-1].isalnum() or prefix[-1] in ",:"):
                return prefix + " " + text
            return prefix + text

        if rule.type == "suffix_injection":
            suffix = str(rule.params.get("suffix", ""))
            if not suffix:
                return text
            if text.lower().endswith(suffix.strip().lower()):
                return text
            if text and text[-1] in ".!?":
                return text[:-1] + suffix + text[-1]
            return text + suffix

        return text

    def _fallback(self, text: str, level: int) -> str:
        if level <= 2:
            return "In my opinion, " + text
        if level == 3:
            return "Actually, " + text
        return "First, " + text
