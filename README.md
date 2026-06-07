# Chinglish Engine 🇨🇳↔🇬🇧

> **把你的英文变成中式英语。可控制强度、可解释、可部署。**

一个可配置、规则驱动的引擎，将英文按照**中文思维习惯**系统性地重写成中式英语（Chinglish）。 5 级强度可控，内置 28+ 条语言规则，支持详细拆解每一步的改写过程。

---

## 🚀 快速体验

```bash
# 后端
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# 前端（新终端）
cd web && npm install && npm run dev
```

打开 http://localhost:5173（界面）或 http://localhost:8000/docs（API 文档）。

---

## 📡 API 文档

### `POST /api/rewrite`

```json
{
  "text": "I want to go to China tomorrow.",
  "lang": "en",
  "level": 5,
  "seed": 42,
  "explain": true
}
```

#### 请求参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `text` | string | **必填** | 输入英文文本 |
| `lang` | string | `"en"` | 语言（目前仅支持 `en`） |
| `level` | int | `3` | 中式强度 **1~5** |
| `seed` | int | `0` | 随机种子。不传=确定性输出（相同输入=相同输出） |
| `explain` | bool | `true` | 是否返回详细改写步骤 |
| `domain` | string | `"default"` | 领域权重 |
| `force_change` | bool | `false` | 即使已中式也追加改写 |
| `discourse_filler` | bool | `false` | 添加语篇填充词（"Actually, ..."、"for users" 等） |
| `skeleton_template` | string | `"auto"` | 骨架模板：`auto` / `a` / `b` / `c` |

#### 响应

```json
{
  "output": "I want tomorrow go China.",
  "applied_rules": ["EN_ZH_SKELETON_REORDER_INTENT_TIME"],
  "warnings": [],
  "steps": [
    {
      "rule_id": "EN_ZH_SKELETON_REORDER_INTENT_TIME",
      "before": "I want to go to China tomorrow.",
      "after": "I want tomorrow go China."
    }
  ],
  "skeleton": [
    {"en": "I", "zh": "我", "role": "S"},
    {"en": "want", "zh": "想", "role": "V1"},
    {"en": "tomorrow", "zh": "明天", "role": "T"},
    {"en": "go", "zh": "去", "role": "V2"}
  ],
  "structure_type": "simple",
  "skeleton_template": "a"
}
```

#### 强度级别示例

| 级别 | 输入 → 输出 |
|------|-------------|
| **L1** | `I want to go to China tomorrow.` → *不变（接近地道英语）* |
| **L2** | `I want to go to China tomorrow.` → *不变（极小概率触发词汇替换）* |
| **L3** | `I want to go to China tomorrow.` → `I want tomorrow to go to China.` |
| **L4** | `I want to go to China tomorrow.` → `I want tomorrow to go to China.` |
| **L5** | `I want to go to China tomorrow.` → `I want tomorrow go China.` |

#### cURL 示例

```bash
curl -X POST https://your-domain.com/api/rewrite \
  -H "Content-Type: application/json" \
  -d '{"text":"Please turn on the light.","lang":"en","level":5,"explain":true}'
```

---

## 🧪 回归测试

```bash
cd eval && python run_regression.py
# 输出: 23 PASS, 0 FAIL
```

---

## 🧠 7 类核心重写规则

| # | 规则 | 例 |
|---|------|-----|
| 1 | **固定短语倒装** | `Good morning` → `morning good` |
| 2 | **因果句重排** | `I stayed home, because it rained.` → `Because it rained, so I stayed home.` |
| 3 | **条件句重排** | `If you come, I will help.` → `If you come, then I will help.` |
| 4 | **意图+时间前置** | `I want to go to China tomorrow.` → `I want tomorrow go China.` |
| 5 | **主谓宾+时间+地点重排** | `I bought a book at the bookstore yesterday.` → `I yesterday at the bookstore bought a book.` |
| 6 | **词汇替换（中式表达）** | `turn on the light` → `Open the light`, `huge crowds` → `People mountain people sea` |
| 7 | **语篇填充** | 添加 `Actually,` / `In my opinion,` / ` for users` |

> 共 **28 条规则**，组织为 6 层架构：认知层(L0) → 句法层(L1) → 词汇层(L2) → 形态层(L3) → 修辞层(L4) → 控制层(L5)。

---

## ⚙️ 架构

```
Input Text → [Normalize] → [Skeleton Rewrite] → [Lexical Rules] → [Fillers] → Output
                │                │                      │
            展开缩写        固定短语/句式          中式词汇替换
                            / 意图+时间            Open the light
                           / 因果/条件             People mountain people sea
```

**规则包** (`rulepacks/en-zhstyle/`):
- `v0.2/pack.json` — 结构规则（L0-L2，16 条）
- `v0.1/pack.json` — 词汇替换规则（L2，~20+ 条）
- `legacy-filler/v0.1/pack.json` — 语篇填充（8 条）

---

## 💰 变现方式

这个引擎可以这样赚钱：

| 方式 | 说明 | 难度 |
|------|------|------|
| 🚀 **API as a Service** | 部署到 Vercel/Render/Docker，按调用量收费 | ⭐ |
| 🌐 **Chrome 扩展** | 实时改写你在网页上写的英文 | ⭐⭐ |
| 🖥️ **VS Code 插件** | 写代码注释/文档时自动转中式英语（测试） | ⭐⭐ |
| 📚 **SaaS 写作平台** | 面向 ESL 学习者的"看看你的英语有多中式"工具 | ⭐⭐⭐ |

> **推荐第一步：** 部署 API + 搭配 Stripe/RapidAPI 收费，零运维成本。

---

## 🔧 部署

### Vercel（前端）

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/waterpoplarabc-coder/Chinglish-Engine)

### Docker（完整部署）

```bash
docker build -t chinglish-engine .
docker run -p 8000:8000 chinglish-engine
```

### Docker Compose（推荐）

```bash
docker-compose up -d
# 访问 http://localhost:8000
```

---

## 📄 许可证

MIT License — 自由使用、修改、商用。

---

> **Made with ❤️ for 语言极客、NLP 研究者和全世界的好奇大脑。**
