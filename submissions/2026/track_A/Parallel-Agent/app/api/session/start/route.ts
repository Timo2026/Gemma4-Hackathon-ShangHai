import { NextResponse } from "next/server";

import { isPresetScenarioId } from "../../../../src/domain/preset-scenarios";
import { startWebSession } from "../../../../src/interfaces/web/session-service";

function normalizeTheme(theme: unknown):
  | "adventure"
  | "sci-fi"
  | "dream"
  | "hell"
  | "humorous" {
  if (
    theme === "adventure" ||
    theme === "sci-fi" ||
    theme === "dream" ||
    theme === "hell" ||
    theme === "humorous"
  ) {
    return theme;
  }

  return "sci-fi";
}

function normalizeLanguage(language: unknown): "en" | "zh-CN" {
  if (language === "en" || language === "zh-CN") {
    return language;
  }

  return "zh-CN";
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      dilemma?: string;
      theme?: string;
      language?: string;
      maxTurns?: number;
      presetScenarioId?: string;
      userContextPack?: {
        userGoal?: string;
        currentPosition?: string;
        riskPreference?: string;
        timeHorizon?: string;
        availableOptions?: string[];
        personalConstraints?: string[];
        keyStakeholders?: string[];
        successCriteria?: string[];
      };
      userProvidedData?: {
        rawText?: string;
      };
    };

    const dilemma = body.dilemma?.trim();
    const presetScenarioId = isPresetScenarioId(body.presetScenarioId)
      ? body.presetScenarioId
      : undefined;

    if (!dilemma && !presetScenarioId) {
      return NextResponse.json(
        { error: "必须填写困境或选择预设场景。" },
        { status: 400 },
      );
    }

    const session = await startWebSession({
      dilemma,
      theme: normalizeTheme(body.theme),
      language: normalizeLanguage(body.language),
      maxTurns: Math.min(Math.max(Number(body.maxTurns) || 3, 1), 5),
      presetScenarioId,
      userContextPack: body.userContextPack
        ? {
            userGoal: body.userContextPack.userGoal?.trim() || undefined,
            currentPosition: body.userContextPack.currentPosition?.trim() || undefined,
            riskPreference:
              body.userContextPack.riskPreference === "low" ||
              body.userContextPack.riskPreference === "medium" ||
              body.userContextPack.riskPreference === "high"
                ? body.userContextPack.riskPreference
                : undefined,
            timeHorizon: body.userContextPack.timeHorizon?.trim() || undefined,
            availableOptions:
              body.userContextPack.availableOptions?.map((item) => item.trim()).filter(Boolean) ??
              undefined,
            personalConstraints:
              body.userContextPack.personalConstraints
                ?.map((item) => item.trim())
                .filter(Boolean) ?? undefined,
            keyStakeholders:
              body.userContextPack.keyStakeholders
                ?.map((item) => item.trim())
                .filter(Boolean) ?? undefined,
            successCriteria:
              body.userContextPack.successCriteria
                ?.map((item) => item.trim())
                .filter(Boolean) ?? undefined,
          }
        : undefined,
      userProvidedData: body.userProvidedData?.rawText?.trim()
        ? {
            rawText: body.userProvidedData.rawText.trim(),
          }
        : undefined,
    });

    return NextResponse.json(session);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "启动 session 失败。" },
      { status: 500 },
    );
  }
}
