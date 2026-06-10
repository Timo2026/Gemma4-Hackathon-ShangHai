"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState, type CSSProperties } from "react";

type ToolCallRecordView = {
  id: string;
  provider: string;
  toolName: string;
  arguments: unknown;
  status: string;
  resultSummary: string;
};

type SessionPageData = {
  sessionId: string;
  dilemma: string;
  language?: string;
  theme: string;
  presetScenarioId?: string;
  turn: number;
  maxTurns: number;
  status: string;
  quantumTrace: string[];
  influenceEvents?: Array<{
    id: string;
    turn: number;
    branchId: string;
    sourceType: string;
    sourceId: string;
    targetType: string;
    targetId: string;
    dimension: string;
    direction: string;
    intensity: number;
    explanation: string;
  }>;
  simulationState?: {
    scope: string;
    individual: {
      skills: Record<string, number>;
      confidence: number;
      reputation: number;
      trust: number;
      financialStability: number;
      stress: number;
      riskTolerance: number;
      identity: string[];
    };
    stakeholders: Array<{
      id: string;
      role: string;
      stance: string;
      trust: number;
      resistance: number;
      influence: number;
      currentGoal: string;
    }>;
    environmentMetrics: Record<string, number>;
    updatedAtTurn: number;
  };
  userAuthoredActions: Array<{
    turn: number;
    title: string;
    rawInput: string;
    riskProfile: string;
    anchorBranchId?: string;
  }>;
  toolCalls?: ToolCallRecordView[];
  userContextPack?: {
    userGoal: string;
    currentPosition: string;
    riskPreference: string;
    timeHorizon: string;
    personalConstraints: string[];
    keyStakeholders: string[];
    successCriteria: string[];
  };
  userProvidedData?: {
    sources: Array<{
      id: string;
      kind: string;
      title: string;
      content: string;
    }>;
    factItems: Array<{
      id: string;
      type: string;
      summary: string;
      confidence: number;
      userConfirmed: boolean;
    }>;
    derivedBrief: {
      userIntentSummary?: string;
      keyConstraints: string[];
      keyStakeholders: string[];
      activeOptions: string[];
      decisionPressures: string[];
      openQuestions: string[];
    };
  };
  groundingLog: Array<{
    turn: number;
    selectedBranchId: string;
    selectedBranchTitle: string;
    groundingContext: {
      presetScenarioId: string;
      scenarioTitle: string;
      worldFactsUsed: string[];
      socialTensionsUsed: string[];
      roleCastUsed: Array<{
        role: string;
        relationship: string;
        baselineStance: string;
      }>;
      userContextSummary: {
        userGoal: string;
        currentPosition: string;
        riskPreference: string;
        timeHorizon: string;
        personalConstraints: string[];
        keyStakeholders: string[];
        successCriteria: string[];
      };
      userProvidedDataSummary?: {
        sourceCount: number;
        factCount: number;
        topFacts: Array<{
          type: string;
          summary: string;
        }>;
        derivedBrief: {
          userIntentSummary?: string;
          keyConstraints: string[];
          keyStakeholders: string[];
          activeOptions: string[];
          decisionPressures: string[];
          openQuestions: string[];
        };
      };
      worldContextSummary: {
        setting: string;
        externalConditions: string;
        currentWorldPressure: string;
      };
    };
  }>;
  canonicalPath: Array<{
    turn: number;
    title: string;
    consequence: string;
  }>;
  shadowTimelines: Array<
    Array<{
      turn: number;
      title: string;
      consequence: string;
    }>
  >;
  pendingTurn?: {
    turnNumber: number;
    agentTrace?: {
      provider: string;
      observerState: string;
      environmentPressure: string;
      generativeSteps: string[];
      deterministicSteps: string[];
      humanMovement: string[];
      environmentDynamics: string[];
    };
    branches: Array<{
      id: string;
      title: string;
      summary: string;
      consequence: string;
      riskProfile: string;
    }>;
    branchWorldDeltas: Array<{
      branchId: string;
      activatedConstraints: string[];
      activatedOpportunities: string[];
      pressureShift: string;
    }>;
    branchCommunities: Array<{
      branchId: string;
      agents: Array<{
        role: string;
        stance: string;
        motivation: string;
        influence: number;
        reaction: string;
      }>;
      socialDynamics: string;
      dominantNarrative: string;
    }>;
    influenceEvents: Array<{
      id: string;
      turn: number;
      branchId: string;
      sourceType: string;
      sourceId: string;
      targetType: string;
      targetId: string;
      dimension: string;
      direction: string;
      intensity: number;
      explanation: string;
    }>;
    toolCalls?: ToolCallRecordView[];
    groundingContext?: {
      presetScenarioId: string;
      scenarioTitle: string;
      worldFactsUsed: string[];
      socialTensionsUsed: string[];
      roleCastUsed: Array<{
        role: string;
        relationship: string;
        baselineStance: string;
      }>;
      userContextSummary: {
        userGoal: string;
        currentPosition: string;
        riskPreference: string;
        timeHorizon: string;
        personalConstraints: string[];
        keyStakeholders: string[];
        successCriteria: string[];
      };
      userProvidedDataSummary?: {
        sourceCount: number;
        factCount: number;
        topFacts: Array<{
          type: string;
          summary: string;
        }>;
        derivedBrief: {
          userIntentSummary?: string;
          keyConstraints: string[];
          keyStakeholders: string[];
          activeOptions: string[];
          decisionPressures: string[];
          openQuestions: string[];
        };
      };
      worldContext: {
        setting: string;
        externalConditions: string;
        currentWorldPressure: string;
        constraints: string[];
        opportunities: string[];
        stableRules: string[];
      };
    };
  };
  summary?: {
    narrative: string;
    decisionArc: string[];
    alternateHint?: string;
  };
};

type AblationReportData = {
  reportVersion: string;
  sessionId: string;
  turns: number;
  influenceEventCount: number;
  headlineInsights: string[];
  runs: Array<{
    mode: string;
    label: string;
    flags: {
      individualToWorld: boolean;
      worldToIndividual: boolean;
    };
    includedEventCount: number;
    excludedEventCount: number;
    metrics: {
      individual: Record<string, number>;
      society: Record<string, number>;
      environment: Record<string, number>;
    };
    deltaFromFull?: {
      totalDistance: number;
    };
  }>;
};

const pageStyle: CSSProperties = {
  maxWidth: 920,
  margin: "0 auto",
  padding: "32px 20px 80px",
};

const panelStyle: CSSProperties = {
  background: "#121a31",
  border: "1px solid #24304f",
  borderRadius: 16,
  padding: 20,
  marginBottom: 16,
};

const buttonStyle: CSSProperties = {
  borderRadius: 12,
  border: 0,
  background: "#60a5fa",
  color: "#08111f",
  padding: "10px 14px",
  fontWeight: 700,
  cursor: "pointer",
  marginTop: 12,
};

const summaryGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
  gap: 14,
};

const summaryCardStyle: CSSProperties = {
  border: "1px solid #314265",
  borderRadius: 8,
  padding: 14,
  background: "#0f1b31",
};

function formatMetric(value: number): string {
  if (!Number.isFinite(value)) {
    return "n/a";
  }

  return `${Math.round(value * 100)}%`;
}

function summarizeToolArguments(args: unknown): string {
  const serialized = JSON.stringify(args);

  if (!serialized) {
    return "No arguments";
  }

  return serialized.length > 520 ? `${serialized.slice(0, 520)}...` : serialized;
}

function summaryMetricRow(label: string, value: number, color: string) {
  const percent = Math.round(value * 100);

  return (
    <div
      key={label}
      style={{
        display: "grid",
        gridTemplateColumns: "72px 1fr 44px",
        gap: 8,
        alignItems: "center",
        marginBottom: 8,
      }}
    >
      <span style={{ color: "#cbd5e1" }}>{label}</span>
      <div
        style={{
          height: 8,
          borderRadius: 999,
          background: "#182740",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${percent}%`,
            background: color,
          }}
        />
      </div>
      <span style={{ textAlign: "right" }}>{percent}%</span>
    </div>
  );
}

export default function SessionDetailPage() {
  const params = useParams<{ id: string }>();
  const sessionId = params.id;
  const [session, setSession] = useState<SessionPageData | null>(null);
  const [ablationReport, setAblationReport] =
    useState<AblationReportData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [submittingBranchId, setSubmittingBranchId] = useState<string | null>(null);
  const [customActionInput, setCustomActionInput] = useState("");
  const [customRiskProfile, setCustomRiskProfile] = useState("medium");
  const [customAnchorBranchId, setCustomAnchorBranchId] = useState("");

  useEffect(() => {
    async function loadSession() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/session/${sessionId}`, {
          cache: "no-store",
        });
        const data = (await response.json()) as SessionPageData | { error: string };

        if (!response.ok || !("sessionId" in data)) {
          throw new Error("error" in data ? data.error : "加载 session 失败。");
        }

        setSession(data);
        await loadAblationReport();
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "加载 session 时出现未知错误。",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadSession();
  }, [sessionId]);

  async function loadAblationReport() {
    try {
      const response = await fetch(`/api/session/${sessionId}/ablation`, {
        cache: "no-store",
      });
      const data = (await response.json()) as AblationReportData | { error: string };

      if (!response.ok || !("runs" in data)) {
        setAblationReport(null);
        return;
      }

      setAblationReport(data);
    } catch {
      setAblationReport(null);
    }
  }

  async function chooseBranch(branchId: string) {
    setSubmittingBranchId(branchId);
    setError(null);

    try {
      const response = await fetch("/api/session/choose", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sessionId,
          branchId,
        }),
      });

      const data = (await response.json()) as SessionPageData | { error: string };

      if (!response.ok || !("sessionId" in data)) {
        throw new Error("error" in data ? data.error : "选择分支失败。");
      }

      setSession(data);
      await loadAblationReport();
    } catch (chooseError) {
      setError(
        chooseError instanceof Error
          ? chooseError.message
          : "选择分支时出现未知错误。",
      );
    } finally {
      setSubmittingBranchId(null);
    }
  }

  async function submitCustomAction() {
    const rawInput = customActionInput.trim();

    if (!rawInput) {
      setError("请输入自定义行动。");
      return;
    }

    setSubmittingBranchId("custom");
    setError(null);

    try {
      const response = await fetch("/api/session/choose", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sessionId,
          authoredAction: {
            rawInput,
            riskProfile: customRiskProfile,
            anchorBranchId: customAnchorBranchId || undefined,
          },
        }),
      });

      const data = (await response.json()) as SessionPageData | { error: string };

      if (!response.ok || !("sessionId" in data)) {
        throw new Error(
          "error" in data ? data.error : "提交自定义行动失败。",
        );
      }

      setSession(data);
      await loadAblationReport();
      setCustomActionInput("");
      setCustomRiskProfile("medium");
      setCustomAnchorBranchId("");
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "提交自定义行动时出现未知错误。",
      );
    } finally {
      setSubmittingBranchId(null);
    }
  }

  return (
    <main style={pageStyle}>
      <div style={{ marginBottom: 16 }}>
        <Link href="/">返回首页</Link>
      </div>

      {isLoading ? <p>正在加载 session...</p> : null}
      {error ? <p style={{ color: "#fda4af" }}>{error}</p> : null}

      {session ? (
        <>
          <section style={panelStyle}>
            <p style={{ marginTop: 0, color: "#93c5fd", fontWeight: 700 }}>
              Session {session.sessionId}
            </p>
            <h1 style={{ marginTop: 0 }}>{session.dilemma}</h1>
            <p style={{ color: "#cbd5e1" }}>
              主题: {session.theme}
              {session.presetScenarioId ? ` | 场景: ${session.presetScenarioId}` : ""}
              {" | "}语言: {session.language ?? "zh-CN"}
              {" | "}轮次 {session.turn}/{session.maxTurns} | 状态: {session.status}
            </p>
          </section>

          <section style={panelStyle}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                flexWrap: "wrap",
                alignItems: "center",
              }}
            >
              <div>
                <h2 style={{ margin: 0 }}>展示模式摘要</h2>
                <p style={{ color: "#cbd5e1", marginBottom: 0 }}>
                  先看路径、个人状态和消融结论；下面保留完整调试信息。
                </p>
              </div>
              <Link
                href="/demo"
                style={{
                  ...buttonStyle,
                  display: "inline-flex",
                  textDecoration: "none",
                  marginTop: 0,
                }}
              >
                打开固定回放页
              </Link>
            </div>

            <div style={{ ...summaryGridStyle, marginTop: 16 }}>
              <div style={summaryCardStyle}>
                <h3 style={{ marginTop: 0 }}>已坍缩路径</h3>
                {session.canonicalPath.length === 0 ? (
                  <p style={{ color: "#cbd5e1" }}>还没有做出选择。</p>
                ) : (
                  <ol style={{ paddingLeft: 20, marginBottom: 0 }}>
                    {session.canonicalPath.map((step) => (
                      <li key={`${step.turn}-${step.title}`} style={{ marginBottom: 8 }}>
                        <strong>第 {step.turn} 轮</strong>: {step.title}
                      </li>
                    ))}
                  </ol>
                )}
              </div>

              {session.simulationState ? (
                <div style={summaryCardStyle}>
                  <h3 style={{ marginTop: 0 }}>个人状态</h3>
                  {summaryMetricRow(
                    "信心",
                    session.simulationState.individual.confidence,
                    "#60a5fa",
                  )}
                  {summaryMetricRow(
                    "压力",
                    session.simulationState.individual.stress,
                    "#fb7185",
                  )}
                  {summaryMetricRow(
                    "适应力",
                    session.simulationState.individual.skills.adaptation ?? 0,
                    "#5eead4",
                  )}
                </div>
              ) : null}

              <div style={summaryCardStyle}>
                <h3 style={{ marginTop: 0 }}>消融结论</h3>
                {ablationReport?.headlineInsights.length ? (
                  <ul style={{ paddingLeft: 18, margin: 0 }}>
                    {ablationReport.headlineInsights.slice(0, 2).map((insight) => (
                      <li key={insight} style={{ marginBottom: 8 }}>
                        {insight}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: "#cbd5e1" }}>
                    选择路径后会自动生成消融对比。
                  </p>
                )}
              </div>
            </div>
          </section>

          {session.simulationState ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>模拟状态</h2>
              <p style={{ color: "#cbd5e1" }}>
                范围: {session.simulationState.scope} | 更新至第{" "}
                {session.simulationState.updatedAtTurn}
                {" "}轮
              </p>

              <div
                style={{
                  display: "grid",
                  gap: 16,
                  gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                }}
              >
                <div>
                  <h3>个人</h3>
                  <ul>
                    <li>信心: {formatMetric(session.simulationState.individual.confidence)}</li>
                    <li>声誉: {formatMetric(session.simulationState.individual.reputation)}</li>
                    <li>信任: {formatMetric(session.simulationState.individual.trust)}</li>
                    <li>压力: {formatMetric(session.simulationState.individual.stress)}</li>
                    <li>
                      风险承受度:{" "}
                      {formatMetric(session.simulationState.individual.riskTolerance)}
                    </li>
                  </ul>
                </div>

                <div>
                  <h3>能力</h3>
                  <ul>
                    {Object.entries(session.simulationState.individual.skills).map(
                      ([name, value]) => (
                        <li key={name}>
                          {name}: {formatMetric(value)}
                        </li>
                      ),
                    )}
                  </ul>
                </div>

                <div>
                  <h3>环境</h3>
                  <ul>
                    {Object.entries(session.simulationState.environmentMetrics).map(
                      ([name, value]) => (
                        <li key={name}>
                          {name}: {formatMetric(value)}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              </div>

              <h3>利益相关者</h3>
              <ul>
                {session.simulationState.stakeholders.slice(0, 6).map((stakeholder) => (
                  <li key={stakeholder.id}>
                    {stakeholder.role} ({stakeholder.stance}) | 信任{" "}
                    {formatMetric(stakeholder.trust)} | 阻力{" "}
                    {formatMetric(stakeholder.resistance)} | 影响力{" "}
                    {formatMetric(stakeholder.influence)}
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          {ablationReport ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>消融对比</h2>
              <p style={{ color: "#cbd5e1" }}>
                使用同一条已坍缩路径重放实验，分别关闭个人影响世界、世界影响个人。
                事件数: {ablationReport.influenceEventCount}
              </p>

              <div style={{ overflowX: "auto" }}>
                <table
                  style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    minWidth: 760,
                  }}
                >
                  <thead>
                    <tr>
                      {[
                        "实验",
                        "事件",
                        "信心",
                        "压力",
                        "社会信任",
                        "阻力",
                        "差异距离",
                      ].map((label) => (
                        <th
                          key={label}
                          style={{
                            borderBottom: "1px solid #314265",
                            padding: "10px 8px",
                            textAlign: "left",
                          }}
                        >
                          {label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {ablationReport.runs.map((run) => (
                      <tr key={run.mode}>
                        <td style={{ borderBottom: "1px solid #24304f", padding: 8 }}>
                          <strong>{run.label}</strong>
                        </td>
                        <td style={{ borderBottom: "1px solid #24304f", padding: 8 }}>
                          {run.includedEventCount}/{ablationReport.influenceEventCount}
                        </td>
                        <td style={{ borderBottom: "1px solid #24304f", padding: 8 }}>
                          {formatMetric(run.metrics.individual.confidence ?? 0)}
                        </td>
                        <td style={{ borderBottom: "1px solid #24304f", padding: 8 }}>
                          {formatMetric(run.metrics.individual.stress ?? 0)}
                        </td>
                        <td style={{ borderBottom: "1px solid #24304f", padding: 8 }}>
                          {formatMetric(run.metrics.society.averageTrust ?? 0)}
                        </td>
                        <td style={{ borderBottom: "1px solid #24304f", padding: 8 }}>
                          {formatMetric(run.metrics.society.averageResistance ?? 0)}
                        </td>
                        <td style={{ borderBottom: "1px solid #24304f", padding: 8 }}>
                          {(run.deltaFromFull?.totalDistance ?? 0).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {ablationReport.headlineInsights.length > 0 ? (
                <ul>
                  {ablationReport.headlineInsights.map((insight) => (
                    <li key={insight}>{insight}</li>
                  ))}
                </ul>
              ) : null}
            </section>
          ) : null}

          {session.pendingTurn ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>待选择分支</h2>
              {session.pendingTurn.branches.map((branch) => (
                <div
                  key={branch.id}
                  style={{
                    border: "1px solid #314265",
                    borderRadius: 12,
                    padding: 16,
                    marginBottom: 12,
                  }}
                >
                  <strong>{branch.title}</strong>
                  <p style={{ marginBottom: 8, color: "#cbd5e1" }}>{branch.summary}</p>
                  <p style={{ marginTop: 0 }}>
                    风险: {branch.riskProfile} | {branch.consequence}
                  </p>
                  <button
                    style={buttonStyle}
                    onClick={() => chooseBranch(branch.id)}
                    disabled={submittingBranchId !== null}
                  >
                    {submittingBranchId === branch.id ? "选择中..." : "选择这条分支"}
                  </button>
                </div>
              ))}

              <div
                style={{
                  border: "1px solid #314265",
                  borderRadius: 12,
                  padding: 16,
                  marginTop: 20,
                }}
              >
                <h3 style={{ marginTop: 0 }}>或者输入你自己的行动</h3>
                <p style={{ color: "#cbd5e1" }}>
                  如果候选分支都不准确，可以直接输入你的真实想法、行动或决定。
                </p>
                <textarea
                  value={customActionInput}
                  onChange={(event) => setCustomActionInput(event.target.value)}
                  placeholder="例如：和经理协商 3 个月过渡期，同时周末测试新的 AI-native 工作方向"
                  rows={4}
                  style={{
                    width: "100%",
                    borderRadius: 12,
                    border: "1px solid #314265",
                    background: "#0b1220",
                    color: "#e2e8f0",
                    padding: 12,
                    resize: "vertical",
                  }}
                />
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                    gap: 12,
                    marginTop: 12,
                  }}
                >
                  <label>
                    <span style={{ display: "block", marginBottom: 6 }}>风险画像</span>
                    <select
                      value={customRiskProfile}
                      onChange={(event) => setCustomRiskProfile(event.target.value)}
                      style={{
                        width: "100%",
                        borderRadius: 10,
                        border: "1px solid #314265",
                        background: "#0b1220",
                        color: "#e2e8f0",
                        padding: "10px 12px",
                      }}
                    >
                      <option value="low">低</option>
                      <option value="medium">中</option>
                      <option value="high">高</option>
                    </select>
                  </label>

                  <label>
                    <span style={{ display: "block", marginBottom: 6 }}>
                      关联分支（可选）
                    </span>
                    <select
                      value={customAnchorBranchId}
                      onChange={(event) => setCustomAnchorBranchId(event.target.value)}
                      style={{
                        width: "100%",
                        borderRadius: 10,
                        border: "1px solid #314265",
                        background: "#0b1220",
                        color: "#e2e8f0",
                        padding: "10px 12px",
                      }}
                    >
                      <option value="">无</option>
                      {session.pendingTurn.branches.map((branch) => (
                        <option key={branch.id} value={branch.id}>
                          {branch.title}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <button
                  style={buttonStyle}
                  onClick={() => void submitCustomAction()}
                  disabled={submittingBranchId !== null}
                >
                  {submittingBranchId === "custom"
                    ? "提交中..."
                    : "提交自定义行动"}
                </button>
              </div>
            </section>
          ) : null}

          {session.pendingTurn?.agentTrace ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>运行管线</h2>
              <p style={{ color: "#cbd5e1" }}>
                模型: {session.pendingTurn.agentTrace.provider}
                <br />
                观察者: {session.pendingTurn.agentTrace.observerState}
                <br />
                世界压力: {session.pendingTurn.agentTrace.environmentPressure}
              </p>

              <div
                style={{
                  display: "grid",
                  gap: 16,
                  gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                }}
              >
                <div>
                  <h3>用户路径</h3>
                  <ul>
                    {session.pendingTurn.agentTrace.humanMovement.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3>环境动态</h3>
                  <ul>
                    {session.pendingTurn.agentTrace.environmentDynamics.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div
                style={{
                  display: "grid",
                  gap: 16,
                  gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                  marginTop: 8,
                }}
              >
                <div>
                  <h3>Gemma / LLM 步骤</h3>
                  <ul>
                    {session.pendingTurn.agentTrace.generativeSteps.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3>Parallel Agent 核心步骤</h3>
                  <ul>
                    {session.pendingTurn.agentTrace.deterministicSteps.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>
          ) : null}

          {(session.pendingTurn?.toolCalls?.length ?? 0) > 0 ||
          (session.toolCalls?.length ?? 0) > 0 ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>Gemma Native Function Calling</h2>
              <p style={{ color: "#cbd5e1" }}>
                Gemma 通过原生工具调用返回结构化现实模拟，Parallel Agent
                验证参数后执行本地状态更新。
              </p>

              {(session.pendingTurn?.toolCalls?.length ?? 0) > 0 ? (
                <>
                  <h3>当前待选轮次 tool_calls</h3>
                  <ul>
                    {session.pendingTurn?.toolCalls?.map((toolCall) => (
                      <li key={toolCall.id}>
                        <strong>{toolCall.toolName}</strong> | {toolCall.provider} |{" "}
                        {toolCall.status} | {toolCall.resultSummary}
                        <pre
                          style={{
                            whiteSpace: "pre-wrap",
                            overflowWrap: "anywhere",
                            background: "#0b1220",
                            border: "1px solid #314265",
                            borderRadius: 8,
                            padding: 10,
                          }}
                        >
                          {summarizeToolArguments(toolCall.arguments)}
                        </pre>
                      </li>
                    ))}
                  </ul>
                </>
              ) : null}

              {(session.toolCalls?.length ?? 0) > 0 ? (
                <>
                  <h3>已坍缩并持久化的 tool_calls</h3>
                  <ul>
                    {session.toolCalls?.map((toolCall) => (
                      <li key={toolCall.id}>
                        <strong>{toolCall.toolName}</strong> | {toolCall.provider} |{" "}
                        {toolCall.status} | {toolCall.resultSummary}
                      </li>
                    ))}
                  </ul>
                </>
              ) : null}
            </section>
          ) : null}

          {session.pendingTurn ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>环境预览</h2>
              {session.pendingTurn.branches.map((branch) => {
                const delta = session.pendingTurn?.branchWorldDeltas.find(
                  (item) => item.branchId === branch.id,
                );
                const community = session.pendingTurn?.branchCommunities.find(
                  (item) => item.branchId === branch.id,
                );
                const influenceEvents =
                  session.pendingTurn?.influenceEvents.filter(
                    (item) => item.branchId === branch.id,
                  ) ?? [];

                return (
                  <div
                    key={`environment-${branch.id}`}
                    style={{
                      borderTop: "1px solid #314265",
                      paddingTop: 12,
                      marginTop: 12,
                    }}
                  >
                    <strong>{branch.title}</strong>
                    {delta ? (
                      <p style={{ color: "#cbd5e1" }}>
                        压力变化: {delta.pressureShift}
                        <br />
                        激活约束: {delta.activatedConstraints.join(", ") || "无"}
                        <br />
                        激活机会: {delta.activatedOpportunities.join(", ") || "无"}
                      </p>
                    ) : null}
                    {community ? (
                      <>
                        <p style={{ color: "#cbd5e1" }}>
                          主导叙事: {community.dominantNarrative}
                          <br />
                          社会动态: {community.socialDynamics}
                        </p>
                        <ul>
                          {community.agents.map((agent) => (
                            <li key={`${branch.id}-${agent.role}-${agent.stance}`}>
                              {agent.role} ({agent.stance}): {agent.reaction}
                            </li>
                          ))}
                        </ul>
                      </>
                    ) : null}
                    {influenceEvents.length > 0 ? (
                      <>
                        <p style={{ color: "#93c5fd", fontWeight: 700 }}>
                          影响链
                        </p>
                        <ul>
                          {influenceEvents.map((event) => (
                            <li key={event.id}>
                              {event.sourceType}:{event.sourceId} {"->"}{" "}
                              {event.targetType}:{event.targetId} |{" "}
                              {event.dimension} {event.direction}{" "}
                              {event.intensity.toFixed(2)} - {event.explanation}
                            </li>
                          ))}
                        </ul>
                      </>
                    ) : null}
                  </div>
                );
              })}
            </section>
          ) : null}

          <section style={panelStyle}>
            <h2 style={{ marginTop: 0 }}>量子痕迹</h2>
            {session.quantumTrace.length === 0 ? (
              <p>还没有痕迹。</p>
            ) : (
              <ul>
                {session.quantumTrace.map((entry) => (
                  <li key={entry}>{entry}</li>
                ))}
              </ul>
            )}
          </section>

          <section style={panelStyle}>
            <h2 style={{ marginTop: 0 }}>影响事件</h2>
            {(session.influenceEvents?.length ?? 0) === 0 ? (
              <p>还没有已坍缩的影响事件。</p>
            ) : (
              <ul>
                {session.influenceEvents?.map((event) => (
                  <li key={event.id}>
                    第 {event.turn} 轮: {event.sourceType}:{event.sourceId} {"->"}{" "}
                    {event.targetType}:{event.targetId} | {event.dimension}{" "}
                    {event.direction} {event.intensity.toFixed(2)} -{" "}
                    {event.explanation}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section style={panelStyle}>
            <h2 style={{ marginTop: 0 }}>已选择路径</h2>
            {session.canonicalPath.length === 0 ? (
              <p>还没有做出选择。</p>
            ) : (
              <ul>
                {session.canonicalPath.map((step) => (
                  <li key={`${step.turn}-${step.title}`}>
                    第 {step.turn} 轮: {step.title} {"->"} {step.consequence}
                  </li>
                ))}
              </ul>
            )}
          </section>

          {session.shadowTimelines.length > 0 ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>未选择时间线</h2>
              {session.shadowTimelines.map((branches, index) => (
                <div key={`shadow-${index}`} style={{ marginBottom: 12 }}>
                  <strong>第 {index + 1} 轮未选择路径</strong>
                  <ul>
                    {branches.map((branch) => (
                      <li key={`${branch.turn}-${branch.title}`}>
                        {branch.title} {"->"} {branch.consequence}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </section>
          ) : null}

          {session.userContextPack ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>用户上下文</h2>
              <p>
                目标: {session.userContextPack.userGoal}
                <br />
                当前处境: {session.userContextPack.currentPosition}
                <br />
                风险偏好: {session.userContextPack.riskPreference} | 时间范围:{" "}
                {session.userContextPack.timeHorizon}
              </p>
              <p style={{ color: "#cbd5e1" }}>
                利益相关者: {session.userContextPack.keyStakeholders.join(", ")}
              </p>
            </section>
          ) : null}

          {session.userProvidedData ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>用户补充资料</h2>
              <p style={{ color: "#cbd5e1" }}>
                来源: {session.userProvidedData.sources.length} | 事实:{" "}
                {session.userProvidedData.factItems.length}
              </p>
              {session.userProvidedData.derivedBrief.userIntentSummary ? (
                <p>意图: {session.userProvidedData.derivedBrief.userIntentSummary}</p>
              ) : null}
              <ul>
                {session.userProvidedData.factItems.slice(0, 5).map((fact) => (
                  <li key={fact.id}>
                    [{fact.type}] {fact.summary}
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          {session.pendingTurn?.groundingContext ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>当前 grounding 证据</h2>
              <p>
                场景: {session.pendingTurn.groundingContext.scenarioTitle} (
                {session.pendingTurn.groundingContext.presetScenarioId})
              </p>
              <p style={{ color: "#cbd5e1" }}>
                压力: {session.pendingTurn.groundingContext.worldContext.currentWorldPressure}
              </p>
              <ul>
                {session.pendingTurn.groundingContext.worldFactsUsed.map((fact) => (
                  <li key={fact}>{fact}</li>
                ))}
              </ul>
              {session.pendingTurn.groundingContext.userProvidedDataSummary ? (
                <>
                  <p style={{ color: "#cbd5e1" }}>
                    用户事实:{" "}
                    {session.pendingTurn.groundingContext.userProvidedDataSummary.factCount}
                  </p>
                  <ul>
                    {session.pendingTurn.groundingContext.userProvidedDataSummary.topFacts.map(
                      (fact) => (
                        <li key={`${fact.type}-${fact.summary}`}>
                          [{fact.type}] {fact.summary}
                        </li>
                      ),
                    )}
                  </ul>
                </>
              ) : null}
            </section>
          ) : null}

          {session.groundingLog.length > 0 ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>Grounding 日志</h2>
              <ul>
                {session.groundingLog.map((entry) => (
                  <li key={`${entry.turn}-${entry.selectedBranchId}`}>
                    第 {entry.turn} 轮: {entry.selectedBranchTitle} |{" "}
                    {entry.groundingContext.worldContextSummary.currentWorldPressure}
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          <section style={panelStyle}>
            <h2 style={{ marginTop: 0 }}>用户自定义行动</h2>
            {session.userAuthoredActions.length === 0 ? (
              <p>还没有自定义行动。</p>
            ) : (
              <ul>
                {session.userAuthoredActions.map((action) => (
                  <li key={`${action.turn}-${action.title}-${action.rawInput}`}>
                    第 {action.turn} 轮: {action.title} ({action.riskProfile}) -{" "}
                    {action.rawInput}
                  </li>
                ))}
              </ul>
            )}
          </section>

          {session.summary ? (
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0 }}>总结</h2>
              <p style={{ whiteSpace: "pre-wrap" }}>{session.summary.narrative}</p>
              <ul>
                {session.summary.decisionArc.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
              {session.summary.alternateHint ? (
                <p style={{ color: "#cbd5e1" }}>{session.summary.alternateHint}</p>
              ) : null}
            </section>
          ) : null}
        </>
      ) : null}
    </main>
  );
}
