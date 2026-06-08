import type {
  DerivedUserBrief,
  UserFactItem,
  UserFactItemInput,
  UserFactType,
  UserProvidedDataInput,
  UserProvidedDataPack,
  UserProvidedDataSource,
} from "./types";

export function normalizeUserProvidedDataInput(
  input: UserProvidedDataInput | undefined,
): UserProvidedDataPack | undefined {
  if (!input) {
    return undefined;
  }

  const sources = normalizeSources(input);
  const factItems =
    input.facts && input.facts.length > 0
      ? normalizeFactInputs(input.facts, sources)
      : deriveFactItemsFromSources(sources);

  if (sources.length === 0 && factItems.length === 0) {
    return undefined;
  }

  return {
    sources,
    factItems,
    derivedBrief: buildDerivedUserBrief(factItems),
  };
}

function normalizeSources(input: UserProvidedDataInput): UserProvidedDataSource[] {
  const normalizedSources: UserProvidedDataSource[] = [];
  let sourceIndex = 0;

  if (input.rawText?.trim()) {
    sourceIndex += 1;
    normalizedSources.push({
      id: `source-${sourceIndex}`,
      kind: "note",
      title: "Pasted user note",
      content: input.rawText.trim(),
    });
  }

  for (const source of input.sources ?? []) {
    const content = source.content.trim();

    if (!content) {
      continue;
    }

    sourceIndex += 1;
    normalizedSources.push({
      id: `source-${sourceIndex}`,
      kind: source.kind ?? "text",
      title: source.title?.trim() || `User source ${sourceIndex}`,
      content,
    });
  }

  return normalizedSources;
}

function normalizeFactInputs(
  facts: UserFactItemInput[],
  sources: UserProvidedDataSource[],
): UserFactItem[] {
  const fallbackSourceIds = sources.map((source) => source.id);
  const normalizedFacts: UserFactItem[] = [];

  for (const [index, fact] of facts.entries()) {
    const summary = fact.summary.trim();

    if (!summary) {
      continue;
    }

    normalizedFacts.push({
      id: `fact-${index + 1}`,
      type: fact.type ?? classifyFactType(summary),
      label: fact.label?.trim() || undefined,
      value: fact.value?.trim() || undefined,
      summary,
      tags: cleanList(fact.tags),
      timeScope: fact.timeScope?.trim() || undefined,
      confidence: 0.85,
      sourceRefIds:
        fact.sourceRefIds?.filter((sourceId) =>
          sources.some((source) => source.id === sourceId),
        ) ?? fallbackSourceIds,
      userConfirmed: fact.userConfirmed ?? true,
    });
  }

  return normalizedFacts;
}

function deriveFactItemsFromSources(sources: UserProvidedDataSource[]): UserFactItem[] {
  const factItems: UserFactItem[] = [];

  for (const source of sources) {
    const candidateLines = source.content
      .split("\n")
      .flatMap((line) => line.split(/(?<=[.!?])\s+/))
      .map((line) => line.replace(/^[-*]\s*/, "").trim())
      .filter((line) => line.length >= 12);

    for (const line of candidateLines.slice(0, 12)) {
      factItems.push({
        id: `fact-${factItems.length + 1}`,
        type: classifyFactType(line),
        summary: line,
        tags: inferTags(line),
        confidence: 0.65,
        sourceRefIds: [source.id],
        userConfirmed: false,
      });
    }
  }

  return factItems;
}

function buildDerivedUserBrief(facts: UserFactItem[]): DerivedUserBrief {
  return {
    userIntentSummary: facts.find((fact) => fact.type === "goal")?.summary,
    keyConstraints: collectFactSummaries(facts, "constraint", 4),
    keyStakeholders: collectFactSummaries(facts, "stakeholder", 4),
    activeOptions: collectFactSummaries(facts, "option", 4),
    decisionPressures: collectFactSummaries(facts, "pressure", 4),
    openQuestions: facts
      .filter((fact) => fact.summary.includes("?"))
      .slice(0, 3)
      .map((fact) => fact.summary),
  };
}

function collectFactSummaries(
  facts: UserFactItem[],
  type: UserFactType,
  limit: number,
): string[] {
  return facts
    .filter((fact) => fact.type === type)
    .slice(0, limit)
    .map((fact) => fact.summary);
}

function cleanList(values: string[] | undefined): string[] {
  return values?.map((value) => value.trim()).filter(Boolean) ?? [];
}

function inferTags(line: string): string[] {
  const lowerLine = line.toLowerCase();
  const tags: string[] = [];

  if (/(ai|llm|automation|model)/.test(lowerLine)) {
    tags.push("ai");
  }

  if (/(manager|team|stakeholder|partner|family|founder|executive)/.test(lowerLine)) {
    tags.push("people");
  }

  if (/(risk|salary|income|runway|pressure|deadline)/.test(lowerLine)) {
    tags.push("pressure");
  }

  return tags;
}

function classifyFactType(text: string): UserFactType {
  const lowerText = text.toLowerCase();

  if (/(goal|want to|aim to|trying to|hope to|looking to)/.test(lowerText)) {
    return "goal";
  }

  if (/(constraint|cannot|can't|must|need to|limited|responsibility|family)/.test(lowerText)) {
    return "constraint";
  }

  if (/(manager|team|stakeholder|partner|family|founder|executive|customer)/.test(lowerText)) {
    return "stakeholder";
  }

  if (/(offer|option|path|stay|leave|pivot|move|join|switch)/.test(lowerText)) {
    return "option";
  }

  if (/(risk|uncertain|downside|afraid|fear|exposure)/.test(lowerText)) {
    return "risk";
  }

  if (/(timeline|month|quarter|year|deadline|urgent|soon)/.test(lowerText)) {
    return "timeline";
  }

  if (/(salary|income|mortgage|runway|pressure|cost|financial)/.test(lowerText)) {
    return "pressure";
  }

  if (/(prefer|bias|comfortable|style)/.test(lowerText)) {
    return "preference";
  }

  if (/(experience|background|currently|worked|role|position)/.test(lowerText)) {
    return "background";
  }

  if (/(resource|network|capital|time|skill|advantage|support)/.test(lowerText)) {
    return "resource";
  }

  return "other";
}
