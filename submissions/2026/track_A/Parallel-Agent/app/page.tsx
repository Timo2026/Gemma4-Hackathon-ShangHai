"use client";

import { useRouter } from "next/navigation";
import { useState, type CSSProperties, type FormEvent } from "react";

const presetScenarioOptions = [
  {
    id: "none",
    label: "自由输入",
    description: "从一个自定义困境开始。",
    dilemma: "我应该接受创业公司的 offer，还是留在目前稳定的岗位？",
    theme: "sci-fi",
  },
  {
    id: "ai_future_of_work",
    label: "AI 工作未来",
    description:
      "一个围绕 AI 改变岗位期待、团队动态和长期职业杠杆的 grounded demo。",
    dilemma:
      "AI 正在快速改变我的领域。我应该继续强化当前岗位，转向 AI-native 工作方式，还是在市场定义我之前主动重塑自己的角色？",
    theme: "sci-fi",
  },
] as const;

const pageStyle: CSSProperties = {
  maxWidth: 760,
  margin: "0 auto",
  padding: "48px 20px 80px",
};

const panelStyle: CSSProperties = {
  background: "#121a31",
  border: "1px solid #24304f",
  borderRadius: 16,
  padding: 24,
};

const inputStyle: CSSProperties = {
  width: "100%",
  borderRadius: 12,
  border: "1px solid #314265",
  background: "#0f172a",
  color: "#f3f4f6",
  padding: "12px 14px",
  marginTop: 8,
};

const buttonStyle: CSSProperties = {
  borderRadius: 12,
  border: 0,
  background: "#60a5fa",
  color: "#08111f",
  padding: "12px 16px",
  fontWeight: 700,
  cursor: "pointer",
};

export default function HomePage() {
  const router = useRouter();
  const [presetScenarioId, setPresetScenarioId] = useState("none");
  const [dilemma, setDilemma] = useState(
    "我应该接受创业公司的 offer，还是留在目前稳定的岗位？",
  );
  const [language, setLanguage] = useState("zh-CN");
  const [theme, setTheme] = useState("sci-fi");
  const [maxTurns, setMaxTurns] = useState(3);
  const [userGoal, setUserGoal] = useState(
    "在保持专业可信度的同时，提高长期职业杠杆。",
  );
  const [currentPosition, setCurrentPosition] = useState(
    "一个能力稳定、但所在领域正在被 AI 重塑的从业者。",
  );
  const [riskPreference, setRiskPreference] = useState("medium");
  const [timeHorizon, setTimeHorizon] = useState("6-12 个月");
  const [personalConstraints, setPersonalConstraints] = useState(
    "当前职责留给实验的时间有限。\n不能承受长时间公开表现出方向混乱。",
  );
  const [keyStakeholders, setKeyStakeholders] = useState(
    "直属经理\n同组工程师\nAI-forward 推动者\n个人支持系统",
  );
  const [userProvidedRawText, setUserProvidedRawText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/session/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dilemma,
          theme,
          language,
          maxTurns,
          presetScenarioId: presetScenarioId === "none" ? undefined : presetScenarioId,
          userContextPack:
            presetScenarioId === "ai_future_of_work"
              ? {
                  userGoal,
                  currentPosition,
                  riskPreference,
                  timeHorizon,
                  personalConstraints: splitLines(personalConstraints),
                  keyStakeholders: splitLines(keyStakeholders),
                }
              : undefined,
          userProvidedData: userProvidedRawText.trim()
            ? {
                rawText: userProvidedRawText.trim(),
              }
            : undefined,
        }),
      });

      const data = (await response.json()) as
        | { sessionId: string }
        | { error: string };

      if (!response.ok || !("sessionId" in data)) {
        throw new Error("error" in data ? data.error : "启动 session 失败。");
      }

      router.push(`/session/${data.sessionId}`);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "启动 session 时出现未知错误。",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main style={pageStyle}>
      <div style={panelStyle}>
        <p style={{ marginTop: 0, color: "#93c5fd", fontWeight: 700 }}>
          Parallel Agent 中文测试界面
        </p>
        <h1 style={{ marginTop: 0 }}>开始一次决策模拟</h1>
        <p style={{ color: "#cbd5e1" }}>
          输入一个真实困境，Gemma 会生成多条未来分支；你选择其中一条后，
          Parallel Agent 会把它坍缩为当前现实，并继续模拟个人、社会和环境的变化。
        </p>

        <form onSubmit={handleSubmit}>
          <label>
            场景
            <select
              style={inputStyle}
              value={presetScenarioId}
              onChange={(event) => {
                const nextId = event.target.value;
                const option =
                  presetScenarioOptions.find((item) => item.id === nextId) ??
                  presetScenarioOptions[0];
                setPresetScenarioId(nextId);
                setDilemma(option.dilemma);
                setTheme(option.theme);
                if (nextId === "ai_future_of_work") {
                  setUserGoal("在保持专业可信度的同时，提高长期职业杠杆。");
                  setCurrentPosition(
                    "一个能力稳定、但所在领域正在被 AI 重塑的从业者。",
                  );
                  setRiskPreference("medium");
                  setTimeHorizon("6-12 个月");
                }
              }}
            >
              {presetScenarioOptions.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <p style={{ color: "#cbd5e1", marginTop: 12 }}>
            {
              (
                presetScenarioOptions.find((option) => option.id === presetScenarioId) ??
                presetScenarioOptions[0]
              ).description
            }
          </p>

          <label>
            你的困境
            <textarea
              rows={4}
              style={inputStyle}
              value={dilemma}
              onChange={(event) => setDilemma(event.target.value)}
            />
          </label>

          <div
            style={{
              display: "grid",
              gap: 16,
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              marginTop: 16,
            }}
          >
            <label>
              输出语言
              <select
                style={inputStyle}
                value={language}
                onChange={(event) => setLanguage(event.target.value)}
              >
                <option value="zh-CN">简体中文</option>
                <option value="en">English</option>
              </select>
            </label>

            <label>
              主题风格
              <select
                style={inputStyle}
                value={theme}
                onChange={(event) => setTheme(event.target.value)}
              >
                <option value="adventure">冒险</option>
                <option value="sci-fi">科幻</option>
                <option value="dream">梦境</option>
                <option value="hell">高压/地狱</option>
                <option value="humorous">幽默</option>
              </select>
            </label>

            <label>
              轮数
              <input
                style={inputStyle}
                type="number"
                min={1}
                max={5}
                value={maxTurns}
                onChange={(event) => setMaxTurns(Number(event.target.value) || 1)}
              />
            </label>
          </div>

          {presetScenarioId === "ai_future_of_work" ? (
            <div style={{ marginTop: 20, display: "grid", gap: 16 }}>
              <label>
                用户目标
                <input
                  style={inputStyle}
                  value={userGoal}
                  onChange={(event) => setUserGoal(event.target.value)}
                />
              </label>

              <label>
                当前处境
                <input
                  style={inputStyle}
                  value={currentPosition}
                  onChange={(event) => setCurrentPosition(event.target.value)}
                />
              </label>

              <div
                style={{
                  display: "grid",
                  gap: 16,
                  gridTemplateColumns: "1fr 1fr",
                }}
              >
                <label>
                  风险偏好
                  <select
                    style={inputStyle}
                    value={riskPreference}
                    onChange={(event) => setRiskPreference(event.target.value)}
                  >
                    <option value="low">低</option>
                    <option value="medium">中</option>
                    <option value="high">高</option>
                  </select>
                </label>

                <label>
                  时间范围
                  <input
                    style={inputStyle}
                    value={timeHorizon}
                    onChange={(event) => setTimeHorizon(event.target.value)}
                  />
                </label>
              </div>

              <label>
                个人约束
                <textarea
                  rows={3}
                  style={inputStyle}
                  value={personalConstraints}
                  onChange={(event) => setPersonalConstraints(event.target.value)}
                />
              </label>

              <label>
                关键利益相关者
                <textarea
                  rows={3}
                  style={inputStyle}
                  value={keyStakeholders}
                  onChange={(event) => setKeyStakeholders(event.target.value)}
                />
              </label>
            </div>
          ) : null}

          <div style={{ marginTop: 20 }}>
            <label>
              补充背景资料
              <textarea
                rows={6}
                style={inputStyle}
                value={userProvidedRawText}
                onChange={(event) => setUserProvidedRawText(event.target.value)}
                placeholder={
                  "粘贴你希望模拟时参考的真实背景。\n例如：我的经理希望本季度看到明确的 AI 采用成果；我有房贷压力；我正在比较内部平台岗和创业公司 offer。"
                }
              />
            </label>
            <p style={{ color: "#94a3b8", marginBottom: 0 }}>
              这些资料会作为 grounding source 保存，并转化为可复用的事实，影响后续分支生成。
            </p>
          </div>

          {error ? <p style={{ color: "#fda4af" }}>{error}</p> : null}

          <div style={{ marginTop: 20 }}>
            <button style={buttonStyle} type="submit" disabled={isLoading}>
              {isLoading ? "正在生成..." : "开始模拟"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}

function splitLines(value: string): string[] {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}
