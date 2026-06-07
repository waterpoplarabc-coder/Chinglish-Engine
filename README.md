# Chinglish Engine 🇨🇳↔🇬🇧

> **生成式中式英语引擎** — 用中文思维说英语的 API 服务。

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/waterpoplarabc-coder/Chinglish-Engine)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/waterpoplarabc-coder/Chinglish-Engine)

---

## 它能做什么？

| 用法 | 输入 | L1 | L3 | L5 |
|------|------|----|----|----|
| 时间语序 | "I want to go to China tomorrow." | 原文不变 | "I want **tomorrow** to go to China." | "I want **tomorrow go China**." |
| 因果倒装 | "I stayed home, because it rained." | 原文不变 | "**Because** it rained, **so** I stayed home." | 同上 |
| 词汇替换 | "Please turn on the light." | 原文不变 | 原文不变 | "Please **Open** the light." |
| 地点前置 | "I bought a book at the bookstore yesterday" | 原文不变 | "I **yesterday** at the bookstore bought a book" | 同上 |

---

## 🚀 快速开始

### 本地运行

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端（新终端）
cd web
npm install
npm run dev
```

打开 http://localhost:5173（UI）或 http://localhost:8000/docs（API 文档）。

### Docker 部署

```bash
docker build -t chinglish-engine .
docker run -p 8000:8000 chinglish-engine
```

---

## 📡 API 文档

### `POST /api/rewrite`

将英文重写为中式英语。

**请求体：**

```json
{
  "text": "Please turn on the light.",
  "lang": "en",
  "level": 5,
  "domain": "default",
  "seed": 42,
  "explain": true,
  "force_change": false,
  "discourse_filler": false,
  "skeleton_template": "auto",
  "literal_lexical": true
}
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | string | **必填** | 输入英文文本 |
| `lang` | string | `"en"` | 语言（仅支持 `en`） |
| `level` | integer | `3` | 中式强度 **1-5**：1=几乎不变 → 5=地道中式 |
| `domain` | string | `"default"` | 领域权重（保留扩展） |
| `seed` | integer | `0` | 随机种子。相同 seed 每次结果一致 |
| `explain` | boolean | `true` | 是否返回详细步骤 |
| `force_change` | boolean | `false` | 即使已经中式也强制改写 |
| `discourse_filler` | boolean | `false` | 添加语篇填充词（"So," / "Actually," / "for users"） |
| `skeleton_template` | string | `"auto"` | 骨架模板（`auto`/`a`/`b`/`c`） |
| `literal_lexical` | boolean | `true` | 是否应用词汇替换 |

**Level 详解：**

| Level | 概率 | 描述 | 效果 |
|-------|------|------|------|
| L1 | 0% | 原生英语 | 骨架不变，无词汇替换 |
| L2 | ~15% | 微妙中式 | 骨架不变，少量词汇替换 |
| L3 | ~35% | 明显中式 | 语法骨架重写（时间前置、因为→所以）、词汇替换 |
| L4 | ~60% | 强烈中式 | 骨架+词汇+语篇填充 |
| L5 | ~85% | 纯粹中式 | 全部规则 + 移除不定式/冠词 |

**响应示例（`explain: true`）：**

```json
{
  "output": "I want tomorrow go China.",
  "applied_rules": ["EN_ZH_SKELETON_REORDER_INTENT_TIME"],
  "steps": [
    {
      "rule_id": "EN_ZH_SKELETON_REORDER_INTENT_TIME",
      "before": "I want tomorrow to go to China.",
      "after": "I want tomorrow go China."
    }
  ],
  "skeleton": [
    {"en": "I", "zh": "我", "role": "S"},
    {"en": "want", "zh": "想", "role": "V1"},
    {"en": "tomorrow", "zh": "明天", "role": "T"}
  ],
  "structure_type": "simple",
  "skeleton_template": "a"
}
```

### 测试

```bash
python eval/run_regression.py
```

---

## 🧠 技术架构

```
输入英文 → 归一化 → 骨架重写 → 词汇替换 → 语篇填充 → 输出中式英语
                      ↓
              L0 认知层: 因为→所以, 如果→那么
              L1 句法层: 时间前置, 话题前置
              L2 词汇层: enter→input, turn on→open
              L3+ 形态层: 省略冠词
              L4+ 修辞层: So, / Actually,
              L5 控制层: 移除不定式 to
```

### 规则包

规则以 JSON 格式存放在 `rulepacks/en-zhstyle/`：

- **v0.2** — 结构规则（L0-L2，正则替换 + 前缀/后缀注入）
- **v0.1** — 词汇替换规则（L2，词级替换）
- **legacy-filler** — 语篇填充规则（前缀/后缀）

---

## 💰 赚钱方案

这个项目的代码是 **MIT License**，你可以免费使用、修改、商用。这里是一些变现思路：

| 方案 | 难度 | 预估收益 |
|------|------|----------|
| **API 服务**（RapidAPI / 自建）部署到云上按调用量收费 | ⭐⭐ | 小规模够零花 |
| **Chrome 扩展** — 实时改写你写的英文为中式，帮中文用户学地道表达 | ⭐⭐⭐ | 可能性大 |
| **VS Code 插件** — 写作辅助工具 | ⭐⭐ | 开发者市场 |
| **嵌入 NLP 评测数据集** — 出售给需要测试 MT/LLM 鲁棒性的公司 | ⭐⭐⭐⭐ | 高 |
| **英语学习 SaaS** — 输入英文→生成中式→对照学习 | ⭐⭐⭐ | 长期收入 |

---

## 🛠️ 技术栈

- **后端**：FastAPI + Python 3.12
- **前端**：React + TypeScript + Vite + PWA
- **规则**：JSON 规则包（版本化、可组合）
- **部署**：Vercel（前端）+ Render（后端）/ Docker

---

## 📄 License

MIT — 随便用，随便改，随便赚。

---

**Made with ❤️ for language geeks, NLP researchers, and curious minds worldwide.**
