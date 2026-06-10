export type DemoMetric = {
  id: string;
  label: string;
  value: number;
  suffix?: string;
  tone: "individual" | "opportunity" | "risk" | "society";
};

export type DemoBranch = {
  id: string;
  title: string;
  summary: string;
  consequence: string;
  riskProfile: "low" | "medium" | "high";
};

export type DemoStep = {
  turn: number;
  selected: DemoBranch;
  alternatives: DemoBranch[];
  collapseInsight: string;
};

export type DemoInfluenceEvent = {
  id: string;
  turn: number;
  sourceLabel: string;
  targetLabel: string;
  dimension: string;
  direction: string;
  intensity: number;
  explanation: string;
  tone: "individual" | "society";
};

export type DemoStakeholder = {
  id: string;
  role: string;
  stance: string;
  trust: number;
  resistance: number;
  influence: number;
  note: string;
};

export type DemoAblationRun = {
  mode: string;
  label: string;
  includedEvents: number;
  confidence: number;
  stress: number;
  societyTrust: number;
  resistance: number;
  distance: number;
  takeaway: string;
};

export type DemoReplay = {
  title: string;
  subtitle: string;
  dilemma: string;
  sessionId: string;
  model: string;
  thesis: string;
  steps: DemoStep[];
  individualMetrics: DemoMetric[];
  environmentMetrics: DemoMetric[];
  stakeholders: DemoStakeholder[];
  influenceEvents: DemoInfluenceEvent[];
  ablationRuns: DemoAblationRun[];
  summary: {
    headline: string;
    narrative: string;
    decisionArc: string[];
  };
};

export const hackathonDemoReplay: DemoReplay = {
  title: "Parallel Agent: 多现实决策模拟",
  subtitle: "Gemma 4 生成现实分支，Parallel Agent 坍缩路径并量化个人与社会的双向影响。",
  dilemma:
    "AI 正在快速改变我的领域。我应该继续强化当前岗位，转向 AI-native 工作方式，还是在市场定义我之前主动重塑自己的角色？",
  sessionId: "dc7a1eb3-71f6-4fe2-a33f-f0ea1181bec0",
  model: "Gemma 4 26B A4B / Ollama",
  thesis:
    "同一个选择路径下，社会反馈会显著改变个人压力与行动方式；个人行动也会重新塑造组织对角色价值的判断。",
  steps: [
    {
      turn: 1,
      selected: {
        id: "b2",
        title: "巩固现有岗位，用 AI 提升可靠交付",
        summary:
          "继续在当前擅长领域内工作，把 AI 作为提效工具，先降低焦虑并维持专业可信度。",
        consequence:
          "短期安全感更高，但如果行业转型速度超出预期，角色天花板会变低。",
        riskProfile: "low",
      },
      alternatives: [
        {
          id: "b1",
          title: "跨领域 AI PoC",
          summary: "主导一个可展示的小型 AI 概念验证，建立知识桥梁身份。",
          consequence: "获得创新者形象，但短期工作量和协调成本上升。",
          riskProfile: "medium",
        },
        {
          id: "b3",
          title: "暂停业务系统性重塑",
          summary: "主动降低当前交付投入，集中学习和构建外部 AI portfolio。",
          consequence: "前瞻性增强，但管理层信任和可见度可能下降。",
          riskProfile: "high",
        },
      ],
      collapseInsight: "第一轮选择低风险稳定路径，把现实坍缩到“先守住可信度”。",
    },
    {
      turn: 2,
      selected: {
        id: "b2",
        title: "小范围试点：定义跨职能 AI 工作流",
        summary:
          "在非核心但可见的侧翼项目中引入 AI-native 工作流，把变革过程变成试验田。",
        consequence:
          "成功可获得创新者与架构师标签；失败则会带来投入产出比质疑。",
        riskProfile: "medium",
      },
      alternatives: [
        {
          id: "b1",
          title: "AI 工具局部优化",
          summary: "只解决眼前最痛的交付问题，保持角色定义不变。",
          consequence: "短期绩效反馈好，但可能固化高级执行者身份。",
          riskProfile: "low",
        },
        {
          id: "b3",
          title: "外部咨询/副业探索",
          summary: "把 AI 能力带到外部市场，寻找新的职业资产。",
          consequence: "身份扩展最大，但财务和心理不确定性显著上升。",
          riskProfile: "high",
        },
      ],
      collapseInsight: "第二轮从防守转向试点，现实开始向“角色重塑”移动。",
    },
    {
      turn: 3,
      selected: {
        id: "ua-3-1",
        title: "内部推进 + 外部验证的双线策略",
        summary:
          "公司内部推动 AI 流程会遇到阻力，因此同步保留外部机会，用真实项目补足背景和经验要求。",
        consequence:
          "这条路径保留稳定收入和组织影响力，同时用外部市场验证新身份，最大化职业可选性。",
        riskProfile: "medium",
      },
      alternatives: [
        {
          id: "b1",
          title: "深入现有领域继续巩固",
          summary: "锁定当前业务痛点，用 AI 工具提升可量化交付。",
          consequence: "短期团队信任提升，但长期更依赖现有流程。",
          riskProfile: "low",
        },
        {
          id: "b2",
          title: "主导跨职能 AI 流程试点",
          summary: "超越团队边界，建立架构师与赋能者身份。",
          consequence: "职业杠杆显著提升，但资源分散和政治阻力更高。",
          riskProfile: "medium",
        },
        {
          id: "b3",
          title: "观望并积累 AI 知识",
          summary: "暂时不展示成果，等待更明确的行业信号。",
          consequence: "心理安全感更高，但可能失去主动权。",
          riskProfile: "low",
        },
      ],
      collapseInsight: "第三轮用户主动写入现实：内部组织变革和外部市场验证同步发生。",
    },
  ],
  individualMetrics: [
    { id: "confidence", label: "信心", value: 0.476, tone: "individual" },
    { id: "stress", label: "压力", value: 0.44, tone: "risk" },
    { id: "adaptation", label: "适应力", value: 0.698, tone: "opportunity" },
    { id: "riskTolerance", label: "风险承受度", value: 0.55, tone: "individual" },
  ],
  environmentMetrics: [
    { id: "momentum", label: "转型动能", value: 0.58, tone: "opportunity" },
    { id: "pressure", label: "组织压力", value: 0.62, tone: "risk" },
    { id: "opportunity", label: "外部机会", value: 0.66, tone: "opportunity" },
    { id: "trust", label: "环境信任", value: 0.52, tone: "society" },
  ],
  stakeholders: [
    {
      id: "manager",
      role: "直属经理",
      stance: "neutral",
      trust: 0.46,
      resistance: 0.505,
      influence: 0.891,
      note: "需要看到 AI 试点能转化为可量化业务收益。",
    },
    {
      id: "peer-engineers",
      role: "同组工程师",
      stance: "uncertain",
      trust: 0.45,
      resistance: 0.55,
      influence: 0.64,
      note: "担心 AI adoption 改变团队绩效标准。",
    },
    {
      id: "ai-forward-operator",
      role: "AI-forward 推动者",
      stance: "supportive",
      trust: 0.72,
      resistance: 0.25,
      influence: 0.72,
      note: "支持可见实验，希望看到工作流被真正重构。",
    },
    {
      id: "support-system",
      role: "个人支持系统",
      stance: "supportive",
      trust: 0.72,
      resistance: 0.25,
      influence: 0.58,
      note: "支持持续成长，但希望避免恐慌式重塑。",
    },
  ],
  influenceEvents: [
    {
      id: "ie-1",
      turn: 1,
      sourceLabel: "个人行动",
      targetLabel: "直属经理",
      dimension: "behavior",
      direction: "increase",
      intensity: 0.5,
      explanation: "稳定交付让管理者继续相信用户的专业可靠性。",
      tone: "individual",
    },
    {
      id: "ie-2",
      turn: 1,
      sourceLabel: "组织环境",
      targetLabel: "个人状态",
      dimension: "pressure",
      direction: "increase",
      intensity: 0.5,
      explanation: "未主动进入前沿议题，使用户对行业变化的压力感上升。",
      tone: "society",
    },
    {
      id: "ie-3",
      turn: 2,
      sourceLabel: "个人试点",
      targetLabel: "管理层认知",
      dimension: "opportunity",
      direction: "increase",
      intensity: 0.7,
      explanation: "跨职能试点把用户从执行者重新定位为流程革新推动者。",
      tone: "individual",
    },
    {
      id: "ie-4",
      turn: 2,
      sourceLabel: "试点反馈",
      targetLabel: "个人身份",
      dimension: "behavior",
      direction: "redirect",
      intensity: 0.6,
      explanation: "社会反馈迫使用户从单纯执行转向流程设计。",
      tone: "society",
    },
    {
      id: "ie-5",
      turn: 3,
      sourceLabel: "双线策略",
      targetLabel: "组织期待",
      dimension: "opportunity",
      direction: "redirect",
      intensity: 0.62,
      explanation: "内部推进与外部验证让组织重新评估用户的战略价值。",
      tone: "individual",
    },
    {
      id: "ie-6",
      turn: 3,
      sourceLabel: "组织阻力",
      targetLabel: "个人行动",
      dimension: "behavior",
      direction: "redirect",
      intensity: 0.5,
      explanation: "内部阻力反过来促使用户保留外部机会，避免把未来押在单一组织上。",
      tone: "society",
    },
  ],
  ablationRuns: [
    {
      mode: "full-coupled",
      label: "完整耦合",
      includedEvents: 6,
      confidence: 0.476,
      stress: 0.44,
      societyTrust: 0.544,
      resistance: 0.419,
      distance: 0,
      takeaway: "个人和社会双向影响都保留，呈现最真实的高压混合路径。",
    },
    {
      mode: "no-individual-influence",
      label: "关闭个人影响",
      includedEvents: 3,
      confidence: 0.476,
      stress: 0.44,
      societyTrust: 0.542,
      resistance: 0.425,
      distance: 0.012,
      takeaway: "社会状态变化很小，说明当前样本里组织反馈更强。",
    },
    {
      mode: "no-society-influence",
      label: "关闭社会影响",
      includedEvents: 3,
      confidence: 0.5,
      stress: 0.35,
      societyTrust: 0.544,
      resistance: 0.419,
      distance: 0.312,
      takeaway: "没有社会压力反馈时，个人压力明显降低。",
    },
    {
      mode: "isolated-baseline",
      label: "隔离基线",
      includedEvents: 0,
      confidence: 0.5,
      stress: 0.35,
      societyTrust: 0.542,
      resistance: 0.425,
      distance: 0.324,
      takeaway: "关闭双向影响后，路径失去社会现实感。",
    },
  ],
  summary: {
    headline: "最终角色：连接 AI 技术与业务痛点的知识桥梁",
    narrative:
      "用户没有选择单纯保守或彻底跳出，而是形成内部巩固、外部扩张的混合策略。它保留当前组织中的可信度，同时用外部机会验证 AI-native 身份。",
    decisionArc: [
      "先用 AI 提效守住可信度。",
      "再通过小范围试点改变组织对角色的期待。",
      "最后用内部推进和外部验证同步提高职业可选性。",
    ],
  },
};
