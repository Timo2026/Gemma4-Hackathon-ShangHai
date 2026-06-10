import Link from "next/link";
import type { CSSProperties } from "react";

import {
  hackathonDemoReplay,
  type DemoAblationRun,
  type DemoBranch,
  type DemoInfluenceEvent,
  type DemoMetric,
  type DemoStep,
  type DemoStakeholder,
} from "../../src/domain/demo-replay";

const pageStyle: CSSProperties = {
  minHeight: "100vh",
  background: "#08111f",
  color: "#eef4ff",
};

const shellStyle: CSSProperties = {
  maxWidth: 1180,
  margin: "0 auto",
  padding: "28px 20px 72px",
};

const navStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 16,
  marginBottom: 28,
};

const linkButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  minHeight: 38,
  padding: "8px 12px",
  borderRadius: 8,
  border: "1px solid #294167",
  color: "#dbeafe",
  textDecoration: "none",
  background: "#0f1b31",
  fontWeight: 700,
};

const primaryButtonStyle: CSSProperties = {
  ...linkButtonStyle,
  background: "#5eead4",
  color: "#062423",
  border: 0,
};

const sectionStyle: CSSProperties = {
  borderTop: "1px solid #223454",
  paddingTop: 26,
  marginTop: 28,
};

const sectionHeaderStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 16,
  alignItems: "end",
  marginBottom: 16,
};

const grid3Style: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
  gap: 14,
};

const grid2Style: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
  gap: 16,
};

const cardStyle: CSSProperties = {
  border: "1px solid #263b60",
  borderRadius: 8,
  background: "#0f1b31",
  padding: 16,
};

const mutedStyle: CSSProperties = {
  color: "#a9bddb",
};

const colorByTone: Record<DemoMetric["tone"], string> = {
  individual: "#60a5fa",
  opportunity: "#5eead4",
  risk: "#fb7185",
  society: "#c084fc",
};

export default function DemoPage() {
  const replay = hackathonDemoReplay;

  return (
    <main style={pageStyle}>
      <style>{`
        .demo-hero {
          display: grid;
          grid-template-columns: minmax(260px, 340px) minmax(0, 1fr);
          gap: 24px;
          align-items: start;
        }

        @media (max-width: 980px) {
          .demo-hero {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
      <div style={shellStyle}>
        <nav style={navStyle}>
          <Link href="/" style={{ color: "#dbeafe", textDecoration: "none" }}>
            Parallel Agent
          </Link>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <Link href="/" style={linkButtonStyle}>
              实时体验
            </Link>
            <Link href={`/session/${replay.sessionId}`} style={primaryButtonStyle}>
              查看原始 Session
            </Link>
          </div>
        </nav>

        <section className="demo-hero">
          <div style={{ minWidth: 0 }}>
            <p style={{ margin: "0 0 10px", color: "#5eead4", fontWeight: 800 }}>
              Gemma 4 Hackathon 固定回放
            </p>
            <h1
              style={{
                margin: 0,
                fontSize: 42,
                lineHeight: 1.08,
              }}
            >
              {replay.title}
            </h1>
            <p style={{ ...mutedStyle, fontSize: 17, lineHeight: 1.6 }}>
              {replay.subtitle}
            </p>
            <div
              style={{
                borderLeft: "4px solid #60a5fa",
                paddingLeft: 14,
                marginTop: 20,
              }}
            >
              <p style={{ margin: "0 0 8px", color: "#93c5fd", fontWeight: 800 }}>
                用户困境
              </p>
              <p style={{ margin: 0, lineHeight: 1.6 }}>{replay.dilemma}</p>
            </div>
            <p style={{ ...mutedStyle, marginTop: 18 }}>
              模型: {replay.model}
              <br />
              数据: 固定 replay fixture，不依赖现场生成
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(2, minmax(120px, 1fr))",
                gap: 10,
                marginTop: 18,
              }}
            >
              <HeroStat value="3" label="轮现实坍缩" tone="individual" />
              <HeroStat value="6" label="条影响事件" tone="society" />
              <HeroStat value="9" label="条未选路径" tone="risk" />
              <HeroStat value="4" label="组消融实验" tone="opportunity" />
            </div>
          </div>

          <div style={{ minWidth: 0 }}>
            <p style={{ margin: "0 0 10px", color: "#c084fc", fontWeight: 800 }}>
              脑图式路径回放
            </p>
            <RealityMindMap steps={replay.steps} events={replay.influenceEvents} />
            <p
              style={{
                margin: "14px 0 0",
                padding: 14,
                borderRadius: 8,
                background: "#10263d",
                border: "1px solid #1e4a73",
                lineHeight: 1.6,
              }}
            >
              {replay.thesis}
            </p>
          </div>
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            title="个人状态与社会状态"
            description="同一条路径下，个人状态、利益相关者反应和环境指标同步演化。"
          />
          <div style={grid2Style}>
            <div>
              <h3 style={{ marginTop: 0 }}>个人状态</h3>
              <div style={{ display: "grid", gap: 12 }}>
                {replay.individualMetrics.map((metric) => (
                  <MetricBar key={metric.id} metric={metric} />
                ))}
              </div>
            </div>
            <div>
              <h3 style={{ marginTop: 0 }}>环境压力</h3>
              <div style={{ display: "grid", gap: 12 }}>
                {replay.environmentMetrics.map((metric) => (
                  <MetricBar key={metric.id} metric={metric} />
                ))}
              </div>
            </div>
          </div>
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            title="个人 ↔ 社会影响链"
            description="影响事件把叙事变成可计算的因果链：谁影响谁、影响什么、强度是多少。"
          />
          <div style={grid2Style}>
            <div>
              <h3 style={{ marginTop: 0 }}>影响链</h3>
              <div style={{ display: "grid", gap: 12 }}>
                {replay.influenceEvents.map((event) => (
                  <InfluenceCard key={event.id} event={event} />
                ))}
              </div>
            </div>
            <div>
              <h3 style={{ marginTop: 0 }}>社会角色</h3>
              <div style={{ display: "grid", gap: 12 }}>
                {replay.stakeholders.map((stakeholder) => (
                  <StakeholderCard
                    key={stakeholder.id}
                    stakeholder={stakeholder}
                  />
                ))}
              </div>
            </div>
          </div>
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            title="从多条未来到一条现实"
            description="脑图给出路径总览；这里保留每一轮候选现实和被坍缩路径的完整证据。"
          />
          <div style={grid3Style}>
            {replay.steps.map((step) => (
              <CollapseStep key={step.turn} step={step} />
            ))}
          </div>
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            title="消融实验：证明双向影响的重要性"
            description="使用同一条已坍缩路径重放，分别关闭个人影响世界、世界影响个人。"
          />
          <AblationTable runs={replay.ablationRuns} />
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            title={replay.summary.headline}
            description={replay.summary.narrative}
          />
          <div style={grid3Style}>
            {replay.summary.decisionArc.map((item, index) => (
              <div key={item} style={cardStyle}>
                <p style={{ margin: "0 0 8px", color: "#5eead4", fontWeight: 800 }}>
                  结论 {index + 1}
                </p>
                <p style={{ margin: 0, lineHeight: 1.55 }}>{item}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

function SectionHeader({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div style={sectionHeaderStyle}>
      <h2 style={{ margin: 0, fontSize: 26 }}>{title}</h2>
      <p style={{ ...mutedStyle, maxWidth: 560, margin: 0, lineHeight: 1.55 }}>
        {description}
      </p>
    </div>
  );
}

function HeroStat({
  value,
  label,
  tone,
}: {
  value: string;
  label: string;
  tone: DemoMetric["tone"];
}) {
  const color = colorByTone[tone];

  return (
    <div
      style={{
        border: `1px solid ${color}`,
        borderRadius: 8,
        padding: "10px 12px",
        background: "#0f1b31",
      }}
    >
      <div style={{ color, fontSize: 28, lineHeight: 1, fontWeight: 900 }}>
        {value}
      </div>
      <div style={{ color: "#cbd5e1", marginTop: 6, fontSize: 13 }}>{label}</div>
    </div>
  );
}

function RealityMindMap({
  steps,
  events,
}: {
  steps: DemoStep[];
  events: DemoInfluenceEvent[];
}) {
  const selectedPositions = [
    { x: 105, y: 170 },
    { x: 276, y: 170 },
    { x: 447, y: 170 },
  ];
  const alternativePositions = [
    [
      { x: 105, y: 46 },
      { x: 105, y: 306 },
    ],
    [
      { x: 276, y: 46 },
      { x: 276, y: 306 },
    ],
    [
      { x: 447, y: 30 },
      { x: 447, y: 92 },
      { x: 447, y: 306 },
    ],
  ];

  return (
    <div
      style={{
        overflowX: "auto",
        border: "1px solid #263b60",
        borderRadius: 10,
        background:
          "linear-gradient(180deg, rgba(15,27,49,0.96), rgba(8,17,31,0.98))",
        padding: 12,
      }}
    >
      <div
        style={{
          position: "relative",
          width: 744,
          height: 430,
        }}
      >
        <svg
          width="744"
          height="430"
          viewBox="0 0 744 430"
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
          }}
        >
          <defs>
            <marker
              id="mind-arrow"
              markerWidth="10"
              markerHeight="10"
              refX="8"
              refY="3"
              orient="auto"
              markerUnits="strokeWidth"
            >
              <path d="M0,0 L0,6 L8,3 z" fill="#5eead4" />
            </marker>
          </defs>
          <line x1="88" y1="214" x2="105" y2="214" stroke="#60a5fa" strokeWidth="3" markerEnd="url(#mind-arrow)" />
          <line x1="255" y1="214" x2="276" y2="214" stroke="#5eead4" strokeWidth="4" markerEnd="url(#mind-arrow)" />
          <line x1="426" y1="214" x2="447" y2="214" stroke="#5eead4" strokeWidth="4" markerEnd="url(#mind-arrow)" />
          <line x1="597" y1="214" x2="652" y2="214" stroke="#5eead4" strokeWidth="3" markerEnd="url(#mind-arrow)" />
          {steps.flatMap((step, stepIndex) =>
            step.alternatives.map((branch, branchIndex) => {
              const selected = selectedPositions[stepIndex]!;
              const alternative = alternativePositions[stepIndex]![branchIndex]!;
              return (
                <line
                  key={`${step.turn}-${branch.id}`}
                  x1={selected.x + 75}
                  y1={selected.y + 43}
                  x2={alternative.x + 62}
                  y2={alternative.y + 32}
                  stroke={riskColor(branch.riskProfile)}
                  strokeWidth="2"
                  strokeDasharray="6 7"
                  opacity="0.72"
                />
              );
            }),
          )}
          <path
            d="M128 398 C250 366, 480 366, 640 398"
            stroke="#c084fc"
            strokeWidth="3"
            strokeDasharray="5 6"
            fill="none"
          />
          <path
            d="M640 398 C525 420, 285 420, 128 398"
            stroke="#60a5fa"
            strokeWidth="3"
            strokeDasharray="5 6"
            fill="none"
          />
        </svg>

        <div
          style={{
            position: "absolute",
            left: 0,
            top: 170,
            width: 88,
          }}
        >
          <MindLabel
            title="用户困境"
            subtitle="AI 浪潮中的职业选择"
            color="#60a5fa"
          />
        </div>

        {steps.map((step, index) => {
          const position = selectedPositions[index]!;
          return (
            <MindNode
              key={step.turn}
              left={position.x}
              top={position.y}
              title={`第 ${step.turn} 轮 · ${step.selected.title}`}
              subtitle={step.collapseInsight}
              color="#5eead4"
              selected
            />
          );
        })}

        {steps.flatMap((step, stepIndex) =>
          step.alternatives.map((branch, branchIndex) => {
            const position = alternativePositions[stepIndex]![branchIndex]!;
            return (
              <MindNode
                key={`${step.turn}-${branch.id}`}
                left={position.x}
                top={position.y}
                title={branch.title}
                subtitle={riskLabel(branch.riskProfile)}
                color={riskColor(branch.riskProfile)}
              />
            );
          }),
        )}

        <div
          style={{
            position: "absolute",
            left: 652,
            top: 170,
            width: 88,
          }}
        >
          <MindLabel
            title="最终现实"
            subtitle="知识桥梁角色"
            color="#5eead4"
          />
        </div>

        <div
          style={{
            position: "absolute",
            left: 98,
            top: 356,
            width: 540,
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: 10,
          }}
        >
          {events.slice(0, 3).map((event) => (
            <div
              key={event.id}
              style={{
                border: `1px solid ${event.tone === "individual" ? "#60a5fa" : "#c084fc"}`,
                borderRadius: 999,
                padding: "8px 10px",
                background: "#101d33",
                textAlign: "center",
                color: "#dbeafe",
                fontSize: 12,
              }}
            >
              {event.sourceLabel} → {event.targetLabel}
            </div>
          ))}
        </div>

        <div
          style={{
            position: "absolute",
            left: 12,
            top: 10,
            color: "#a9bddb",
            fontSize: 13,
            lineHeight: 1.5,
          }}
        >
          <LegendDot color="#5eead4" label="已选择现实" />
          <LegendDot color="#fbbf24" label="中风险未选路径" />
          <LegendDot color="#fb7185" label="高风险未选路径" />
          <LegendDot color="#c084fc" label="社会反馈" />
        </div>
      </div>
    </div>
  );
}

function MindNode({
  left,
  top,
  title,
  subtitle,
  color,
  selected = false,
}: {
  left: number;
  top: number;
  title: string;
  subtitle: string;
  color: string;
  selected?: boolean;
}) {
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: selected ? 150 : 124,
        minHeight: selected ? 86 : 64,
        border: `2px solid ${color}`,
        borderRadius: 12,
        padding: selected ? "11px 12px" : "9px 10px",
        background: selected ? "#0e302f" : "#0b1526",
        boxShadow: selected ? `0 0 0 4px ${color}22` : "none",
      }}
    >
      <strong
        style={{
          display: "-webkit-box",
          WebkitLineClamp: selected ? 2 : 1,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
          lineHeight: 1.35,
          fontSize: selected ? 13 : 12,
          color: selected ? "#f8fffd" : "#e2e8f0",
        }}
      >
        {title}
      </strong>
      <p
        style={{
          ...mutedStyle,
          margin: "7px 0 0",
          display: "-webkit-box",
          WebkitLineClamp: selected ? 2 : 1,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
          fontSize: 12,
          lineHeight: 1.35,
        }}
      >
        {subtitle}
      </p>
    </div>
  );
}

function MindLabel({
  title,
  subtitle,
  color,
}: {
  title: string;
  subtitle: string;
  color: string;
}) {
  return (
    <div
      style={{
        border: `2px solid ${color}`,
        borderRadius: 999,
        width: 88,
        height: 72,
        display: "grid",
        placeItems: "center",
        textAlign: "center",
        padding: 10,
        background: "#101d33",
      }}
    >
      <div>
        <strong style={{ color, fontSize: 13 }}>{title}</strong>
        <p style={{ ...mutedStyle, margin: "4px 0 0", fontSize: 12 }}>{subtitle}</p>
      </div>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
      <span
        style={{
          width: 9,
          height: 9,
          borderRadius: 999,
          background: color,
          display: "inline-block",
        }}
      />
      {label}
    </div>
  );
}

function CollapseStep({ step }: { step: DemoStep }) {
  const allBranches = [step.selected, ...step.alternatives];

  return (
    <div style={cardStyle}>
      <p style={{ margin: "0 0 10px", color: "#93c5fd", fontWeight: 800 }}>
        第 {step.turn} 轮现实选择
      </p>
      <div style={{ display: "grid", gap: 10 }}>
        {allBranches.map((branch) => (
          <BranchOption
            key={branch.id}
            branch={branch}
            selected={branch.id === step.selected.id}
          />
        ))}
      </div>
      <p style={{ margin: "12px 0 0", color: "#5eead4", lineHeight: 1.5 }}>
        坍缩结果: {step.selected.title}
      </p>
    </div>
  );
}

function BranchOption({
  branch,
  selected,
}: {
  branch: DemoBranch;
  selected: boolean;
}) {
  return (
    <div
      style={{
        border: `1px solid ${selected ? "#5eead4" : "#243754"}`,
        borderRadius: 8,
        padding: 10,
        background: selected ? "#0e302f" : "#0b1526",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 10,
          alignItems: "start",
        }}
      >
        <strong style={{ lineHeight: 1.35 }}>{branch.title}</strong>
        <RiskBadge risk={branch.riskProfile} />
      </div>
      <p style={{ ...mutedStyle, margin: "8px 0 0", lineHeight: 1.45 }}>
        {branch.consequence}
      </p>
    </div>
  );
}

function RiskBadge({ risk }: { risk: DemoBranch["riskProfile"] }) {
  const color = risk === "low" ? "#5eead4" : riskColor(risk);
  const label = risk === "high" ? "高风险" : risk === "medium" ? "中风险" : "低风险";

  return (
    <span
      style={{
        color,
        border: `1px solid ${color}`,
        borderRadius: 999,
        padding: "3px 8px",
        fontSize: 12,
        whiteSpace: "nowrap",
      }}
    >
      {label}
    </span>
  );
}

function MetricBar({ metric }: { metric: DemoMetric }) {
  const color = colorByTone[metric.tone];
  const percent = Math.round(metric.value * 100);

  return (
    <div style={cardStyle}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          marginBottom: 10,
        }}
      >
        <strong>{metric.label}</strong>
        <span style={{ color }}>{percent}{metric.suffix ?? "%"}</span>
      </div>
      <div
        style={{
          height: 10,
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
    </div>
  );
}

function InfluenceCard({ event }: { event: DemoInfluenceEvent }) {
  const color = event.tone === "individual" ? "#60a5fa" : "#c084fc";

  return (
    <div style={{ ...cardStyle, borderColor: color }}>
      <p style={{ margin: "0 0 8px", color, fontWeight: 800 }}>
        第 {event.turn} 轮 · {event.sourceLabel} → {event.targetLabel}
      </p>
      <p style={{ margin: "0 0 8px", lineHeight: 1.5 }}>{event.explanation}</p>
      <p style={{ ...mutedStyle, margin: 0 }}>
        {event.dimension} / {event.direction} / 强度 {event.intensity.toFixed(2)}
      </p>
    </div>
  );
}

function StakeholderCard({ stakeholder }: { stakeholder: DemoStakeholder }) {
  return (
    <div style={cardStyle}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          alignItems: "start",
        }}
      >
        <strong>{stakeholder.role}</strong>
        <span style={{ color: "#c084fc" }}>{stanceLabel(stakeholder.stance)}</span>
      </div>
      <p style={{ ...mutedStyle, margin: "8px 0 12px", lineHeight: 1.45 }}>
        {stakeholder.note}
      </p>
      <MiniMetric label="信任" value={stakeholder.trust} color="#60a5fa" />
      <MiniMetric label="阻力" value={stakeholder.resistance} color="#fb7185" />
      <MiniMetric label="影响力" value={stakeholder.influence} color="#c084fc" />
    </div>
  );
}

function MiniMetric({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "64px 1fr 42px", gap: 8 }}>
      <span style={mutedStyle}>{label}</span>
      <div
        style={{
          height: 8,
          borderRadius: 999,
          background: "#182740",
          marginTop: 7,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${Math.round(value * 100)}%`,
            background: color,
          }}
        />
      </div>
      <span style={{ textAlign: "right" }}>{Math.round(value * 100)}%</span>
    </div>
  );
}

function AblationTable({ runs }: { runs: DemoAblationRun[] }) {
  const maxDistance = Math.max(...runs.map((run) => run.distance), 0.01);

  return (
    <div style={{ overflowX: "auto" }}>
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          minWidth: 860,
        }}
      >
        <thead>
          <tr>
            {["实验", "事件", "信心", "压力", "社会信任", "阻力", "差异距离", "结论"].map(
              (label) => (
                <th
                  key={label}
                  style={{
                    textAlign: "left",
                    padding: "12px 10px",
                    borderBottom: "1px solid #294167",
                    color: "#a9bddb",
                  }}
                >
                  {label}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.mode}>
              <td style={tableCellStyle}>
                <strong>{run.label}</strong>
              </td>
              <td style={tableCellStyle}>{run.includedEvents}/6</td>
              <td style={tableCellStyle}>{toPercent(run.confidence)}</td>
              <td style={tableCellStyle}>{toPercent(run.stress)}</td>
              <td style={tableCellStyle}>{toPercent(run.societyTrust)}</td>
              <td style={tableCellStyle}>{toPercent(run.resistance)}</td>
              <td style={tableCellStyle}>
                <div
                  style={{
                    width: 140,
                    height: 10,
                    borderRadius: 999,
                    background: "#182740",
                    overflow: "hidden",
                    display: "inline-block",
                    marginRight: 8,
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: `${Math.round((run.distance / maxDistance) * 100)}%`,
                      background: run.distance === 0 ? "#263b60" : "#fb7185",
                    }}
                  />
                </div>
                {run.distance.toFixed(2)}
              </td>
              <td style={{ ...tableCellStyle, maxWidth: 300 }}>{run.takeaway}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const tableCellStyle: CSSProperties = {
  padding: "12px 10px",
  borderBottom: "1px solid #1d2d49",
  verticalAlign: "top",
};

function stanceLabel(stance: string): string {
  if (stance === "supportive") return "支持";
  if (stance === "resistant") return "抵抗";
  if (stance === "neutral") return "中立";
  return "不确定";
}

function riskColor(risk: DemoBranch["riskProfile"]): string {
  if (risk === "high") return "#fb7185";
  if (risk === "medium") return "#fbbf24";
  return "#64748b";
}

function riskLabel(risk: DemoBranch["riskProfile"]): string {
  if (risk === "high") return "高风险未选路径";
  if (risk === "medium") return "中风险未选路径";
  return "低风险未选路径";
}

function toPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}
