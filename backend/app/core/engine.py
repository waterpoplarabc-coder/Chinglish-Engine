"""
中式英语重写引擎 (Chinglish Rewrite Engine)

将英文按照中文思维习惯重写为中式英语。
核心逻辑：骨架结构重写 + 词汇替换 + 语篇填充。
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path

from app.core.rulepack import load_rulepack, Rule


# ── 数据类型 ─────────────────────────────────────────────

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


# ── 工具函数 ─────────────────────────────────────────────

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+", text))


def _singular_ies(m: re.Match) -> str:
    """将 -ies 结尾名词转为单数：studies → study, carries → carry"""
    return m.group(1) + "y"


def _singular_s(m: re.Match) -> str:
    """将 -s 结尾名词转为单数（跳过原单数和 -ies 已处理的）"""
    w = m.group(0).lower()
    # 跳过短词（is, has, was, his, its 等）
    if len(w) <= 3:
        return m.group(0)
    # 跳过常见非复数英文词
    skip_words = {"this", "thus", "plus", "bus", "yes", "gas", "status",
                  "series", "species", "basis", "crisis", "thesis",
                  "analysis", "emphasis", "diagnosis",
                  "process", "success", "access", "address",
                  "class", "glass", "grass", "stress", "guess"}
    if w in skip_words:
        return m.group(0)
    # 跳过已经以 -ss, -sh, -ch, -x, -o 结尾的（这类+s 是正确复数）
    if re.search(r"[ssshchxo]s$", w, flags=re.IGNORECASE):
        return m.group(0)
    return m.group(0)[:-1]


def _strip_3rd_p(text: str) -> str:
    """去掉第三人称单数动词后缀：goes → go, reads → read, makes → make
    使用启发式：es/s 结尾的动词去掉后缀。
    跳过常见非动词以 s/es 结尾的词。
    """
    skip_3rd = {"this", "its", "his", "thus", "bus", "plus", "yes", "gas",
                "status", "series", "species", "basis", "crisis", "thesis",
                "analysis", "emphasis", "diagnosis",
                "process", "success", "access", "address",
                "class", "glass", "grass", "stress", "guess"}

    def _safe_strip(m: re.Match) -> str:
        w = m.group(0).lower()
        if w in skip_3rd:
            return m.group(0)
        # 跳过 -ss/-sh/-ch/-x/-o 结尾
        if re.search(r"[ssshchxo]s$", w):
            return m.group(0)
        return m.group(1)

    # goes → go, does → do, has → have (特殊处理)
    text = re.sub(r"\bhas\b", "have", text, flags=re.IGNORECASE)
    text = re.sub(r"\bdoes\b", "do", text, flags=re.IGNORECASE)
    text = re.sub(r"\bgoes\b", "go", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsays\b", "say", text, flags=re.IGNORECASE)
    # 通用：匹配 es/s 结尾且单词长度 >= 3
    text = re.sub(r"\b(\w{3,})(?:es|s)\b", _safe_strip, text, flags=re.IGNORECASE)
    return text


def _is_short_phrase(text: str) -> bool:
    """判断是否为短短语（<=3 词），短语不走词汇替换。"""
    core = text.strip().rstrip(".!?")
    return bool(re.fullmatch(r"[A-Za-z]+(?:\s+[A-Za-z]+){0,2}", core)) and _word_count(core) <= 3


def _strip_ending_punct(text: str) -> tuple[str, str]:
    """剥离末尾标点，返回 (正文, 标点)。"""
    m = re.match(r"^(.*?)([.!?])$", text.strip())
    if not m:
        return text.strip(), ""
    return m.group(1).strip(), m.group(2)


def _expand_contractions(text: str) -> str:
    """展开所有英语缩写。"""
    table: list[tuple[str, str]] = [
        (r"\b(I|I’|I')m\b", r"\1 am"),
        (r"\b(You|You’|You')re\b", r"\1 are"),
        (r"\b(We|We’|We')re\b", r"\1 are"),
        (r"\b(They|They’|They')re\b", r"\1 are"),
        (r"\b(He|He’|He')s\b", r"\1 is"),
        (r"\b(She|She’|She')s\b", r"\1 is"),
        (r"\b(It|It’|It')s\b", r"\1 is"),
        (r"\b(T|T’|T')s\b", r"\1 is"),  # edge case: "it's" → "it is"
    ]
    # 更简单的方法：直接替换固定模式
    text = re.sub(r"\bI'm\b", "I am", text, flags=re.IGNORECASE)
    text = re.sub(r"\bI’m\b", "I am", text)
    text = re.sub(r"\bYou're\b", "You are", text, flags=re.IGNORECASE)
    text = re.sub(r"\bYou’re\b", "You are", text)
    text = re.sub(r"\bWe're\b", "We are", text, flags=re.IGNORECASE)
    text = re.sub(r"\bWe’re\b", "We are", text)
    text = re.sub(r"\bThey're\b", "They are", text, flags=re.IGNORECASE)
    text = re.sub(r"\bThey’re\b", "They are", text)
    text = re.sub(r"\bHe's\b", "He is", text, flags=re.IGNORECASE)
    text = re.sub(r"\bHe’s\b", "He is", text)
    text = re.sub(r"\bShe's\b", "She is", text, flags=re.IGNORECASE)
    text = re.sub(r"\bShe’s\b", "She is", text)
    text = re.sub(r"\bIt's\b", "It is", text, flags=re.IGNORECASE)
    text = re.sub(r"\bIt’s\b", "It is", text)
    return text


def _gloss(word: str) -> str:
    """返回英文词对应的中文释义（用于骨架展示）。"""
    table = {
        "i": "我", "we": "我们", "you": "你", "he": "他", "she": "她",
        "they": "他们", "it": "它",
        "want": "想", "plan": "打算", "planning": "打算",
        "hope": "希望", "hoping": "希望",
        "prepare": "准备", "preparing": "准备",
        "decide": "决定", "deciding": "决定",
        "go": "去", "come": "来", "do": "做", "make": "做", "have": "有",
        "is": "是", "are": "是", "am": "是", "be": "是",
        "today": "今天", "tomorrow": "明天", "yesterday": "昨天",
        "china": "中国", "beijing": "北京",
        "morning": "早上", "good": "好", "night": "晚上",
        "thank": "谢",
    }
    return table.get(word.lower(), "")


# ── 主引擎 ─────────────────────────────────────────────

class RewriteEngine:
    """中式英语重写引擎。

    将英文按中文思维习惯重写成 Chinglish，分 5 个强度级别 (L1-L5)。
    使用骨架结构重写 + 可配置的规则包。
    """

    def __init__(self) -> None:
        root = _repo_root() / "rulepacks" / "en-zhstyle"

        # 加载所有规则包
        packs: list[tuple[str, ...]] = [
            ("v0.2", "pack.json"),           # 结构规则 (L0-L2)
            ("v0.1", "pack.json"),           # 词汇替换规则 (L2)
            ("legacy-filler", "v0.1", "pack.json"),  # 语篇填充
        ]
        all_rules: list[Rule] = []
        for parts in packs:
            p = root.joinpath(*parts)
            if p.exists():
                pk = load_rulepack(p)
                all_rules.extend(pk.rules)

        # 排序：按层级 → 优先级 → 规则 ID
        def _layer_rank(layer: str) -> int:
            return {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}.get(layer.upper(), 9)

        self._rules = sorted(
            all_rules,
            key=lambda r: (
                _layer_rank(r.layer),
                -int(r.priority),
                r.rule_id,
            ),
        )

        # 预编译正则
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
                self._compiled_lexical[r.rule_id] = self._compile_word_pattern(
                    pattern=pattern,
                    case_insensitive=bool(r.params.get("case_insensitive", True)),
                    word_boundary=bool(r.params.get("word_boundary", True)),
                )

            if r.type == "regex_substitution":
                pattern = str(r.params.get("pattern", ""))
                if not pattern:
                    continue
                self._compiled_regex[r.rule_id] = re.compile(pattern, flags=re.IGNORECASE)

    # ── 公共接口 ────────────────────────────────────────

    def rewrite(
        self,
        text: str,
        lang: str,
        level: int,
        domain: str = "default",
        seed: int | None = None,
        explain: bool = True,
        force_change: bool = False,
        discourse_filler: bool = False,
        skeleton_template: str = "auto",
        literal_lexical: bool = True,
    ) -> RewriteResult:
        """将英文重写为中式英语。

        参数:
            text: 输入英文文本
            lang: 语言（仅 "en" 支持）
            level: 强度级别 1-5
            domain: 领域权重
            seed: 随机种子（None=使用确定性模式）
            explain: 是否返回详细解释
            force_change: 即使语法已中式也强制改写
            discourse_filler: 是否添加语篇填充词
            skeleton_template: 骨架模板 (auto/a/b/c)
            literal_lexical: 是否应用词汇替换
        """
        warnings: list[str] = []

        # ── 语言检查 ──
        if lang.lower() != "en":
            warnings.append("当前仅支持英文(en)的中式改写；已原样返回")
            return RewriteResult(
                output=text, applied_rules=[], warnings=warnings,
                steps=[], skeleton=[], structure_type="unsupported",
                skeleton_template="auto",
            )

        # ── 默认值 ──
        # 确定性模式：没传 seed 就用 0，使得输出可复现
        if seed is None:
            seed = 0
        rng = random.Random(seed)
        normalized = self._normalize(text)

        # ── 短语检测（短短语不走词汇替换；但 force_change 或 L5 时强制改写） ──
        is_phrase = _is_short_phrase(normalized)
        if is_phrase and (force_change or level >= 5):
            is_phrase = False  # L5 或 force_change 下强制处理短句

        # ── Step 1: 骨架结构重写 ──
        transformed = normalized
        applied: list[str] = []
        steps: list[RewriteStep] = []
        skeleton: list[SkeletonItem] = []
        structure_type = "simple"
        template_used = "auto"

        before_skel = transformed
        transformed, skel_step_id, skeleton, structure_type, template_used = (
            self._apply_skeleton(transformed, level=level, skeleton_template=skeleton_template)
        )
        if transformed != before_skel and skel_step_id:
            if explain:
                steps.append(RewriteStep(rule_id=skel_step_id, before=before_skel, after=transformed))
            applied.append(skel_step_id)

        # ── Step 2: 词汇替换（L2 规则） ──
        if literal_lexical and not is_phrase:
            transformed, lex_steps, lex_applied = self._apply_lexical_rules(
                transformed, level=level, rng=rng, explain=explain,
            )
            steps.extend(lex_steps)
            applied.extend(lex_applied)

        # ── Step 3: 语篇填充 ──
        if discourse_filler and not is_phrase:
            transformed, fill_steps, fill_applied = self._apply_filler_rules(
                transformed, level=level, rng=rng, explain=explain,
            )
            steps.extend(fill_steps)
            applied.extend(fill_applied)

        # ── Step 4: L5 全局剥离（冠词/复数/第三人称/不定式） ──
        if level >= 5 and not is_phrase:
            before_l5 = transformed
            transformed = self._apply_l5_stripping(transformed)
            if transformed != before_l5:
                rid = "EN_L5_GLOBAL_STRIP"
                if explain:
                    steps.append(RewriteStep(rule_id=rid, before=before_l5, after=transformed))
                applied.append(rid)

        # ── Step 5: force_change 兜底 ──
        if force_change and transformed == normalized and level >= 2:
            before_fb = transformed
            transformed = self._fallback(transformed, level)
            if transformed != before_fb:
                rid = "EN_FALLBACK_PREFIX"
                if explain:
                    steps.append(RewriteStep(rule_id=rid, before=before_fb, after=transformed))
                applied.append(rid)

        return RewriteResult(
            output=transformed,
            applied_rules=applied if explain else [],
            warnings=warnings,
            steps=steps if explain else [],
            skeleton=skeleton if explain else [],
            structure_type=structure_type,
            skeleton_template=template_used,
        )

    # ── 文本预处理 ──────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.strip()
        text = _expand_contractions(text)
        text = re.sub(r"\s+", " ", text)
        return text

    # ── L5 全局剥离（冠词/复数/第三人称） ────────────────

    @staticmethod
    def _apply_l5_stripping(text: str) -> str:
        """L5 级别：移除冠词、简化复数、去掉第三人称动词后缀。
        在骨架重写和词汇替换之后全局应用。
        顺序很重要：先处理特殊动词（去es/s），再处理名词复数。
        """
        result = text
        # 移除冠词 the/a/an
        result = re.sub(r"\b(the|a|an)\s+", "", result, flags=re.IGNORECASE)
        # 先处理第三人称动词（含特殊 goes/does/has → go/do/have）
        result = _strip_3rd_p(result)
        # 再处理名词复数（跳过已被动词处理过的词）
        result = re.sub(r"\b(\w+)ies\b", _singular_ies, result, flags=re.IGNORECASE)
        result = re.sub(r"\b(\w+)(?<![s])s\b", _singular_s, result, flags=re.IGNORECASE)
        result = re.sub(r"\s+", " ", result).strip()
        return result

    # ── 骨架重写 ─────────────────────────────────────────

    def _apply_skeleton(
        self,
        text: str,
        level: int,
        skeleton_template: str,
    ) -> tuple[str, str | None, list[SkeletonItem], str, str]:
        """应用句子骨架结构的中式重写。

        处理顺序：固定短语 → 复合句（because/so, if/then）→ 意图+时间重排 → 主谓宾+时间+地点重排。
        """
        core, punct = _strip_ending_punct(text)
        lower = core.lower()

        # ── 固定短语 ──
        if lower == "good morning":
            return "morning good" + punct, "EN_PHRASE_GOOD_MORNING_SWAP", [
                SkeletonItem(en="good", zh=_gloss("good"), role="ADJ"),
                SkeletonItem(en="morning", zh=_gloss("morning"), role="N"),
            ], "phrase", "auto"

        if lower == "good night":
            return "night good" + punct, "EN_PHRASE_GOOD_NIGHT_SWAP", [
                SkeletonItem(en="good", zh=_gloss("good"), role="ADJ"),
                SkeletonItem(en="night", zh=_gloss("night"), role="N"),
            ], "phrase", "auto"

        if lower == "thank you":
            return text, None, [
                SkeletonItem(en="thank", zh=_gloss("thank"), role="V"),
                SkeletonItem(en="you", zh=_gloss("you"), role="O"),
            ], "phrase", "auto"

        # ── 复合句 —— 只在 level >= 3 时改写 ──
        if level >= 3:
            # because → so
            # because 从句（逗号可选："I stayed home because it rained" → "Because it rained, so I stayed home"）
            m_cause = re.match(
                r"^(?P<main>.+?)\s*,?\s*because\s+(?P<cause>.+)$", core, flags=re.IGNORECASE
            )
            if m_cause:
                main = m_cause.group("main").strip()
                cause = m_cause.group("cause").strip()
                out = f"Because {cause}, so {main}".strip() + punct
                return out, "EN_ZH_COMPOUND_BECAUSE_SO", [], "compound_cause", "auto"

            # if → then
            m_if = re.match(
                r"^if\s+(?P<cond>.+?),\s*(?P<main>.+)$", core, flags=re.IGNORECASE
            )
            if m_if:
                cond = m_if.group("cond").strip()
                main = m_if.group("main").strip()
                out = f"If {cond}, then {main}".strip() + punct
                return out, "EN_ZH_COMPOUND_IF_THEN", [], "compound_if", "auto"

        # ── 主语检测（扩展支持第三人称名字） ──
        subj_match = re.match(r"^(?P<subj>[A-Z][a-z]+|[IY]ou|He|She|They|We)\b", core, flags=re.IGNORECASE)
        detected_subj = subj_match.group("subj") if subj_match else None

        # ── 意图+时间重排（I want [to] go to China tomorrow → I want tomorrow go China）──
        out, step_id, sk, template_used = self._try_intent_time_reorder(
            core=core, level=level, skeleton_template=skeleton_template,
        )
        if step_id:
            return out + punct, step_id, sk, "simple", template_used

        # ── 主谓宾+时间+地点重排 ──
        out, step_id, sk, template_used = self._try_svo_time_place_reorder(
            core=core, level=level, skeleton_template=skeleton_template,
        )
        if step_id:
            return out + punct, step_id, sk, "simple", template_used

        return text, None, [], "simple", "auto"

    def _try_intent_time_reorder(
        self, core: str, level: int, skeleton_template: str,
    ) -> tuple[str, str | None, list[SkeletonItem], str]:
        """意图+时间结构重排：I want [to] go to China tomorrow → 中文语序。

        level >= 3 时有效。
        """
        if level < 3:
            return core, None, [], "auto"

        time_words = r"(today|tomorrow|yesterday|tonight|now|(?:every|next|this)(?:\s+day|\s+morning|\s+night|\s+week|\s+month|\s+year))"
        intent_words = r"want|plan|hope|prepare|decide|need|like|wants|plans|hopes|prepares|decides|needs|likes"
        intent_ing = r"planning|hoping|preparing|deciding"

        # 模式一：I want X tomorrow → 重排时间
        # 扩展主语：支持 I/You/He/She/They/We + 大写名字
        subj_pat = r"(?P<subj>I|We|You|He|She|They|[A-Z][a-z]+(?='s|\s|$))"

        m = re.match(
            rf"^{subj_pat}\s+(?P<intent>{intent_words})\s+"
            rf"(?P<rest>.+?)\s+(?P<time>{time_words})$",
            core, flags=re.IGNORECASE,
        )
        subj = None
        rest = None
        time = None
        intent_phrase = None

        if m:
            subj = m.group("subj")
            intent = m.group("intent")
            rest = m.group("rest").strip()
            time = m.group("time")
            intent_phrase = f"{subj} {intent}"
        else:
            # 模式二：I am planning to X tomorrow
            m2 = re.match(
                rf"^{subj_pat}\s+(?P<aux>am|are|is)\s+"
                rf"(?P<intent>{intent_ing})\s+to\s+"
                rf"(?P<vp>.+?)\s+(?P<time>{time_words})$",
                core, flags=re.IGNORECASE,
            )
            if m2:
                subj = m2.group("subj")
                aux = m2.group("aux")
                intent = m2.group("intent")
                rest = "to " + m2.group("vp").strip()
                time = m2.group("time")
                intent_phrase = f"{subj} {aux} {intent}"

        if intent_phrase is None or subj is None or rest is None or time is None:
            return core, None, [], "auto"

        # 如果时间词已经在 rest 里（说明已经中式语序了），不重排
        if re.search(rf"\b{re.escape(time)}\b", rest, flags=re.IGNORECASE):
            return core, None, [], "auto"

        # ── L5 简化：移除不定式 to 和冠词 ──
        rest_stripped = rest
        # L5 简化：移除不定式 to（现在在全局步骤中处理冠词/复数/第三人称）
        if level >= 5:
            # 移除句子开头的 "to"
            rest_stripped = re.sub(r"^to\s+", "", rest_stripped, flags=re.IGNORECASE)
            # "go to X" → "go X"（保留 go）
            rest_stripped = re.sub(r"\bgo\s+to\s+", "go ", rest_stripped, flags=re.IGNORECASE)
            rest_stripped = re.sub(r"\bcome\s+to\s+", "come ", rest_stripped, flags=re.IGNORECASE)
            # 移除剩余的不定式 to（仅在意图动词后）
            rest_stripped = re.sub(
                rf"\bto\s+(?=\w+)", "",
                rest_stripped, flags=re.IGNORECASE,
            )
            rest_stripped = re.sub(r"\s+", " ", rest_stripped).strip()

        # ── 模板应用 ──
        template = skeleton_template.lower() if skeleton_template.lower() in {"a", "b", "c"} else "a"

        if template == "b":
            out = f"{time} {intent_phrase} {rest_stripped}".strip()
        else:
            out = f"{intent_phrase} {time} {rest_stripped}".strip()
        out = re.sub(r"\s+", " ", out).strip()

        # ── 骨架构建（基于最终输出，保证一致） ──
        intent_token = intent_phrase.split()[-1]
        sk: list[SkeletonItem] = [
            SkeletonItem(en=subj, zh=_gloss(subj), role="S"),
            SkeletonItem(en=intent_token, zh=_gloss(intent_token), role="V1"),
            SkeletonItem(en=time, zh=_gloss(time), role="T"),
        ]
        # 检查输出中是否真的有 "go"/"come" 等动词，而非仅检查原文
        if re.search(r"\bgo\b", out, flags=re.IGNORECASE):
            sk.append(SkeletonItem(en="go", zh=_gloss("go"), role="V2"))
        if re.search(r"\bcome\b", out, flags=re.IGNORECASE):
            sk.append(SkeletonItem(en="come", zh=_gloss("come"), role="V2"))

        rid = "EN_ZH_SKELETON_REORDER_INTENT_TIME"
        return out, rid, sk, template

    def _try_svo_time_place_reorder(
        self, core: str, level: int, skeleton_template: str,
    ) -> tuple[str, str | None, list[SkeletonItem], str]:
        """主谓宾+时间+地点重排：I bought a book at the bookstore yesterday → I yesterday at the bookstore bought a book.

        只在 level >= 3 时生效。
        """
        if level < 3:
            return core, None, [], "auto"

        subj_pat = r"(?P<subj>I|We|You|He|She|They|[A-Z][a-z]+(?='s|\s|$))"
        m = re.match(rf"^{subj_pat}\s+(?P<rest>.+)$", core, flags=re.IGNORECASE)
        if not m:
            return core, None, [], "auto"
        subj = m.group("subj")
        rest = m.group("rest").strip()

        # 检查 rest 是否以意图动词开头（走那个专门的 intent_time 重排，不走这里）
        if re.match(r"^(want|plan|hope|prepare|decide|planning|hoping|preparing|deciding)\b", rest, flags=re.IGNORECASE):
            return core, None, [], "auto"

        svot_time_words = r"(today|tomorrow|yesterday|tonight|now|(?:every|next|this)(?:\s+day|\s+morning|\s+night|\s+week|\s+month|\s+year))"
        m_time = re.match(
            rf"^(?P<pre>.+?)\s+(?P<time>{svot_time_words})$", rest, flags=re.IGNORECASE,
        )
        if not m_time:
            return core, None, [], "auto"
        pre = m_time.group("pre").strip()
        time = m_time.group("time")

        # 提取地点短语（仅匹配地点介词 at/in/on，不匹配 to）
        place_phrase = ""
        m_place = re.search(r"\b(at|in|on)\b\s+(.+)$", pre, flags=re.IGNORECASE)
        verb_obj = pre
        if m_place:
            place_phrase = m_place.group(0).strip()
            verb_obj = pre[: m_place.start()].strip()
            if not verb_obj:
                verb_obj = pre

        template = skeleton_template.lower() if skeleton_template.lower() in {"a", "b", "c"} else "a"

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

    # ── 词汇替换规则 ──────────────────────────────────────

    def _apply_lexical_rules(
        self, text: str, level: int, rng: random.Random, explain: bool,
    ) -> tuple[str, list[RewriteStep], list[str]]:
        """应用 L2 词汇替换规则（确定性模式：全部应用；非确定性：概率应用）。"""
        applied: list[str] = []
        steps: list[RewriteStep] = []
        transformed = text
        prob = 1.0  # 默认确定性
        budget = {2: 3, 3: 6, 4: 12, 5: 24}.get(level, 6)

        # 非确定性模式下按 level 计算概率
        level_prob = {1: 0.0, 2: 0.15, 3: 0.35, 4: 0.6, 5: 0.85}.get(level, 0.35)
        if not (rng.getstate()[1][0] == 0 and rng.getstate()[1][1] == 0):  # 不是默认种子
            prob = level_prob

        for rule in self._rules:
            if rule.type not in {"lexical_substitution", "regex_substitution"}:
                continue
            if rule.layer.upper() != "L2":
                continue
            if not (rule.min_level <= level <= rule.max_level):
                continue

            # 概率判定
            domain_w = rule.domain_weight.get("default", 1.0)
            if rng.random() > prob * domain_w:
                continue

            # 触发器检查
            trig = self._compiled_trigger.get(rule.rule_id)
            if trig is not None and not trig.search(transformed):
                continue

            before = transformed
            transformed = self._apply_rule(rule, transformed)
            if transformed != before:
                if explain:
                    steps.append(RewriteStep(rule_id=rule.rule_id, before=before, after=transformed))
                applied.append(rule.rule_id)
                budget -= 1
                if budget <= 0:
                    break

        return transformed, steps, applied

    # ── 语篇填充规则 ──────────────────────────────────────

    def _apply_filler_rules(
        self, text: str, level: int, rng: random.Random, explain: bool,
    ) -> tuple[str, list[RewriteStep], list[str]]:
        """应用语篇填充规则（前缀/后缀注入）。"""
        applied: list[str] = []
        steps: list[RewriteStep] = []
        transformed = text
        prefix_done = False
        suffix_done = False

        for rule in self._rules:
            if rule.type not in {"prefix_injection", "suffix_injection"}:
                continue
            if not (rule.min_level <= level <= rule.max_level):
                continue

            # 每种类型只应用一次
            if rule.type == "prefix_injection" and prefix_done:
                continue
            if rule.type == "suffix_injection" and suffix_done:
                continue

            # 概率判定
            domain_w = rule.domain_weight.get("default", 1.0)
            if rng.random() > domain_w:
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
                    prefix_done = True
                if rule.type == "suffix_injection":
                    suffix_done = True

        return transformed, steps, applied

    # ── 规则应用 ─────────────────────────────────────────

    @staticmethod
    def _compile_word_pattern(pattern: str, case_insensitive: bool, word_boundary: bool) -> re.Pattern[str]:
        """编译词级正则（带词边界）。"""
        flags = re.IGNORECASE if case_insensitive else 0
        if word_boundary:
            escaped = re.escape(pattern)
            pat = rf"(?<![A-Za-z]){escaped}(?![A-Za-z])"
        else:
            pat = re.escape(pattern)
        return re.compile(pat, flags=flags)

    def _apply_rule(self, rule: Rule, text: str) -> str:
        """应用单条规则到文本。"""
        try:
            if rule.type == "lexical_substitution":
                cregex = self._compiled_lexical.get(rule.rule_id)
                if cregex is None:
                    return text
                replacement = str(rule.params.get("replacement", ""))
                out, n = cregex.subn(replacement, text, count=1)
                return out if n > 0 else text

            if rule.type == "regex_substitution":
                cregex = self._compiled_regex.get(rule.rule_id)
                if cregex is None:
                    return text
                replacement = str(rule.params.get("replacement", ""))
                out, n = cregex.subn(replacement, text, count=1)
                return out if n > 0 else text

            if rule.type == "prefix_injection":
                prefix = str(rule.params.get("prefix", "")).rstrip()
                if not prefix:
                    return text
                # 去重：如果已经以该前缀开头，不再重复添加
                if text.lower().lstrip().startswith(prefix.strip().lower()):
                    return text
                # 前缀末尾是字母/逗号/冒号 → 加空格
                if re.match(r"^[A-Za-z]", text.lstrip()) and (
                    prefix[-1].isalnum() or prefix[-1] in ",:"
                ):
                    return prefix + " " + text.lstrip()
                return prefix + text.lstrip()

            if rule.type == "suffix_injection":
                suffix = str(rule.params.get("suffix", ""))
                if not suffix:
                    return text
                # 去重
                if text.rstrip().lower().endswith(suffix.strip().lower()):
                    return text
                # 替换末尾标点
                text_stripped = text.rstrip()
                if text_stripped and text_stripped[-1] in ".!?":
                    return text_stripped[:-1].rstrip() + suffix + text_stripped[-1]
                return text_stripped + suffix

        except Exception:
            # 规则出错时保持原文不变，不炸服务
            pass

        return text

    # ── 兜底 ────────────────────────────────────────────

    @staticmethod
    def _fallback(text: str, level: int) -> str:
        """force_change 兜底：无条件添加前缀。"""
        if level <= 2:
            return "In my opinion, " + text
        if level == 3:
            return "Actually, " + text
        return "First, " + text
