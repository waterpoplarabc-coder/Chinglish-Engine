import { useMemo, useState, useEffect, useCallback } from "react";

type RewriteResponse = {
  output: string;
  applied_rules: string[];
  warnings: string[];
  steps: { rule_id: string; before: string; after: string }[];
  skeleton: { en: string; zh: string; role: string }[];
  structure_type: string;
  skeleton_template: string;
};

function rewriteEndpoint(): string {
  return "/api/rewrite";
}

const EXAMPLES = [
  { text: "I want to go to China tomorrow.", label: "⏰ Time order" },
  { text: "I stayed home because it rained.", label: "🔗 Because/So" },
  { text: "If you come, I will go.", label: "🔗 If/Then" },
  { text: "Please turn on the light.", label: "💡 Verb choice" },
  { text: "She goes to school every morning.", label: "🏫 Daily routine" },
  { text: "I bought a book at the store yesterday.", label: "🛍️ Shopping" },
  { text: "He reads books every day.", label: "📚 3rd person" },
  { text: "We plan to visit Beijing next week.", label: "✈️ Future plan" },
];

function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowPrompt(true);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setShowPrompt(false);
    }
  };

  if (!showPrompt) return null;

  return (
    <div className="install-prompt">
      <div className="install-content">
        <span>📱 Add to Home Screen for offline access!</span>
        <div className="install-buttons">
          <button onClick={handleInstall} className="install-btn">Install</button>
          <button onClick={() => setShowPrompt(false)} className="dismiss-btn">×</button>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [text, setText] = useState("I want to go to China tomorrow.");
  const [level, setLevel] = useState(3);
  const [domain, setDomain] = useState("default");
  const [seed, setSeed] = useState<string>("");
  const [explain, setExplain] = useState(true);
  const [skeletonTemplate, setSkeletonTemplate] = useState<"auto" | "a" | "b" | "c">("auto");
  const [literalLexical, setLiteralLexical] = useState(true);
  const [legacyFiller, setLegacyFiller] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RewriteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const seedValue = useMemo(() => {
    const s = seed.trim();
    if (!s) return null;
    const n = Number(s);
    if (!Number.isFinite(n)) return null;
    return Math.trunc(n);
  }, [seed]);

  async function onRewrite() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(rewriteEndpoint(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          lang: "en",
          level,
          domain,
          seed: seedValue,
          explain,
          discourse_filler: legacyFiller,
          skeleton_template: skeletonTemplate,
          literal_lexical: literalLexical
        })
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `HTTP ${res.status}`);
      }
      const json = (await res.json()) as RewriteResponse;
      setResult(json);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  const handleCopy = useCallback(async () => {
    if (!result?.output) return;
    await navigator.clipboard.writeText(result.output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [result]);

  return (
    <div className="page">
      <InstallPrompt />
      
      <header className="header">
        <div className="title">Chinglish Generator</div>
        <div className="subtitle">Transform English into Chinese-style English • See how Chinese think in English</div>
      </header>

      <main className="grid">
        <section className="card input-card">
          <div className="cardTitle">📝 Input</div>
          <textarea 
            value={text} 
            onChange={(e) => setText(e.target.value)} 
            rows={6}
            placeholder="Enter English text here..."
          />
          
          {/* Example buttons */}
          <div className="examples">
            <span className="examples-label">🎯 Try examples:</span>
            <div className="example-chips">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex.label}
                  className="example-chip"
                  onClick={() => setText(ex.text)}
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </div>

          <div className="controls">
            <div className="control-row">
              <label className="control-label">
                <span>Intensity</span>
                <select value={level} onChange={(e) => setLevel(Number(e.target.value))}>
                  <option value={1}>L1 — Near-native</option>
                  <option value={2}>L2 — Mild Chinglish</option>
                  <option value={3}>L3 — Typical Chinglish</option>
                  <option value={4}>L4 — Heavy Chinglish</option>
                  <option value={5}>L5 — Pure Chinglish</option>
                </select>
              </label>
              
              <label className="control-label">
                <span>Domain</span>
                <input value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="default" />
              </label>
            </div>

            <div className="control-row">
              <label className="control-label">
                <span>Seed (optional)</span>
                <input 
                  value={seed} 
                  onChange={(e) => setSeed(e.target.value)} 
                  placeholder="For reproducibility" 
                />
              </label>
              
              <label className="control-label">
                <span>Template</span>
                <select value={skeletonTemplate} onChange={(e) => setSkeletonTemplate(e.target.value as any)}>
                  <option value="auto">Auto</option>
                  <option value="a">Pattern A</option>
                  <option value="b">Pattern B</option>
                  <option value="c">Pattern C</option>
                </select>
              </label>
            </div>

            <div className="checkbox-row">
              <label className="check">
                <input type="checkbox" checked={explain} onChange={(e) => setExplain(e.target.checked)} />
                Show explanation
              </label>
              <label className="check">
                <input
                  type="checkbox"
                  checked={literalLexical}
                  onChange={(e) => setLiteralLexical(e.target.checked)}
                />
                Word replacement
              </label>
              <label className="check">
                <input
                  type="checkbox"
                  checked={legacyFiller}
                  onChange={(e) => setLegacyFiller(e.target.checked)}
                />
                Discourse fillers
              </label>
            </div>
            
            <button 
              onClick={onRewrite} 
              disabled={loading || text.trim().length === 0}
              className="generate-btn"
            >
              {loading ? "⏳ Processing..." : "✨ Generate Chinglish"}
            </button>
          </div>
          
          <div className="hint">API: {rewriteEndpoint()}</div>
        </section>

        <section className="card output-card">
          <div className="cardTitle">🎯 Output</div>
          
          {/* Original ↔ Output comparison */}
          {result && (
            <div className="comparison">
              <div className="compare-row">
                <div className="compare-label">Original</div>
                <div className="compare-text">{text.trim()}</div>
              </div>
              <div className="compare-arrow">⬇️</div>
              <div className="compare-row output-row">
                <div className="compare-label">Chinglish</div>
                <div className="compare-text chinglish-text">{result.output}</div>
              </div>
            </div>
          )}
          
          <div className="output-box">
            <pre className="output">{result?.output ?? "Your Chinglish will appear here..."}</pre>
            <div className="output-actions">
              <button 
                className="action-btn"
                onClick={handleCopy}
                disabled={!result?.output}
              >
                {copied ? "✅ Copied" : "📋 Copy"}
              </button>
              <button 
                className="action-btn"
                onClick={() => {
                  if (result?.output) {
                    const shareText = `Original: ${text.trim()}\nChinglish (L${level}): ${result.output}\n\nTry it: https://chinglish-generator.vercel.app`;
                    navigator.clipboard.writeText(shareText).then(() => {
                      setCopied(true);
                      setTimeout(() => setCopied(false), 2000);
                    });
                  }
                }}
                disabled={!result?.output}
              >
                🔗 Share
              </button>
            </div>
          </div>
          
          <div className="meta">
            <span className="pill">Structure: {result?.structure_type ?? "—"}</span>
            <span className="pill">Template: {result?.skeleton_template ?? "—"}</span>
            <span className="pill">Level: L{level}</span>
          </div>
          
          {result?.warnings?.length ? (
            <div className="warn">
              {result.warnings.map((w) => (
                <div key={w}>⚠️ {w}</div>
              ))}
            </div>
          ) : null}
          
          {error ? <div className="error">❌ {error}</div> : null}
          
          {result && result.output === text.trim() ? (
            <div className="warn">ℹ️ Text unchanged. Try a higher level or different input.</div>
          ) : null}

          {explain && result && result.applied_rules.length > 0 && (
            <>
              <div className="cardTitle">📋 Applied Rules</div>
              <div className="rules">
                {result.applied_rules.map((r) => (
                  <span key={r} className="pill rule-pill">{r}</span>
                ))}
              </div>

              {result.skeleton.length > 0 && (
                <>
                  <div className="cardTitle">🏗️ Chinese Skeleton</div>
                  <div className="skeleton">
                    {result.skeleton.map((s, idx) => (
                      <span key={`${s.role}-${idx}`} className="skeletonPill">
                        <strong>{s.role}:</strong> {s.en}
                        {s.zh ? ` → ${s.zh}` : ""}
                      </span>
                    ))}
                  </div>
                </>
              )}

              {result.steps.length > 0 && (
                <>
                  <div className="cardTitle">🔍 Transformation Steps</div>
                  <div className="steps">
                    {result.steps.map((s, idx) => (
                      <details key={`${s.rule_id}-${idx}`} className="step">
                        <summary>
                          {idx + 1}. {s.rule_id}
                        </summary>
                        <div className="stepBody">
                          <div className="stepLabel">Before</div>
                          <pre className="stepText">{s.before}</pre>
                          <div className="stepLabel">After</div>
                          <pre className="stepText">{s.after}</pre>
                        </div>
                      </details>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <div>📱 Install this app for offline access • Share results with friends!</div>
        <div style={{marginTop: '8px', opacity: 0.7}}>
          Made for language learners and curious minds • MIT Licensed • <a href="https://github.com/waterpoplarabc-coder/Chinglish-Engine" target="_blank" rel="noopener">GitHub</a>
        </div>
      </footer>
    </div>
  );
}
