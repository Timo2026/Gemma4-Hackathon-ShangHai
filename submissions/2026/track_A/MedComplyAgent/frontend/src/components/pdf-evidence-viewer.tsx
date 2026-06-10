"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import type { PDFDocumentProxy, PDFPageProxy, TextItem } from "pdfjs-dist/types/src/display/api";

type HighlightTarget = {
  id: number;
  query: string;
  label: string;
};

type TextBox = {
  id: string;
  text: string;
  left: number;
  top: number;
  width: number;
  height: number;
};

type HighlightBox = {
  ids: string[];
  left: number;
  top: number;
  width: number;
  height: number;
};

type PageRender = {
  pageNumber: number;
  width: number;
  height: number;
  imageUrl: string;
  textBoxes: TextBox[];
};

type MatchResult = {
  pageNumber: number;
  highlightedBoxIds: Set<string>;
  firstBoxId: string;
  firstBoxTop: number;
  firstBoxHeight: number;
  score: number;
};

type PdfEvidenceViewerProps = {
  pdfUrl: string | null;
  highlightTarget: HighlightTarget | null;
  onLocateResult?: (result: { found: boolean; label: string }) => void;
};

const COMMON_TOKENS = new Set([
  "the",
  "and",
  "for",
  "with",
  "this",
  "that",
  "type",
  "date",
  "service",
  "encounter",
  "reading",
  "taken",
]);

function normalizeForMatch(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9./:]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function queryTokens(query: string): string[] {
  const tokens = normalizeForMatch(query)
    .split(/[^a-z0-9./:-]+/)
    .map((token) => token.trim())
    .filter(Boolean)
    .filter((token) => !COMMON_TOKENS.has(token))
    .filter((token) => token.length >= 3 || /\d/.test(token));

  return Array.from(new Set(tokens)).slice(0, 14);
}

function itemScore(text: string, tokens: string[]): number {
  const normalized = normalizeForMatch(text);
  return tokens.reduce((score, token) => (normalized.includes(token) ? score + 1 : score), 0);
}

function textBoxForItem(pageNumber: number, index: number, page: PDFPageProxy, item: TextItem): TextBox {
  const viewport = page.getViewport({ scale: 1 });
  const [, , c, d, e, f] = item.transform;
  const transform = viewport.transform;
  const x = transform[0] * e + transform[2] * f + transform[4];
  const y = transform[1] * e + transform[3] * f + transform[5];
  const fontHeight = Math.max(8, Math.hypot(c, d));
  const width = Math.max(10, item.width);

  return {
    id: `${pageNumber}-${index}`,
    text: item.str,
    left: x,
    top: y - fontHeight,
    width,
    height: fontHeight * 1.15,
  };
}

function findPageMatch(page: PageRender, query: string, tokens: string[]): MatchResult | null {
  const normalizedQuery = normalizeForMatch(query);
  if (!normalizedQuery) {
    return null;
  }

  const directMatches = page.textBoxes.filter((box) => {
    const normalizedBox = normalizeForMatch(box.text);
    return normalizedBox.length > 0 && (normalizedQuery.includes(normalizedBox) || normalizedBox.includes(normalizedQuery));
  });
  if (directMatches.length > 0) {
    return {
      pageNumber: page.pageNumber,
      highlightedBoxIds: new Set(directMatches.map((box) => box.id)),
      firstBoxId: directMatches[0].id,
      firstBoxTop: directMatches[0].top,
      firstBoxHeight: directMatches[0].height,
      score: 1000 + directMatches.length,
    };
  }

  const pageText = normalizeForMatch(page.textBoxes.map((box) => box.text).join(" "));
  const pageScore = tokens.reduce((score, token) => (pageText.includes(token) ? score + 1 : score), 0);
  if (pageScore === 0) {
    return null;
  }

  const tokenThreshold = Math.min(3, Math.max(1, tokens.length));
  const scoredBoxes = page.textBoxes
    .map((box) => ({ box, score: itemScore(box.text, tokens) }))
    .filter((item) => item.score >= tokenThreshold)
    .sort((a, b) => b.score - a.score || a.box.top - b.box.top);

  if (scoredBoxes.length === 0) {
    return null;
  }

  const bestScore = scoredBoxes[0].score;
  const bestBoxes = scoredBoxes.filter((item) => item.score === bestScore).map((item) => item.box);
  return {
    pageNumber: page.pageNumber,
    highlightedBoxIds: new Set(bestBoxes.map((box) => box.id)),
    firstBoxId: bestBoxes[0].id,
    firstBoxTop: bestBoxes[0].top,
    firstBoxHeight: bestBoxes[0].height,
    score: pageScore * 10 + bestScore,
  };
}

function findBestMatch(pages: PageRender[], query: string, tokens: string[]): MatchResult | null {
  const matches = pages
    .map((page) => findPageMatch(page, query, tokens))
    .filter((match): match is MatchResult => match !== null);
  if (matches.length === 0) {
    return null;
  }
  return matches.reduce((best, match) => (match.score > best.score ? match : best), matches[0]);
}

function mergeHighlightedBoxes(page: PageRender, highlightedBoxIds: Set<string>): HighlightBox[] {
  const boxes = page.textBoxes
    .filter((box) => highlightedBoxIds.has(box.id))
    .sort((a, b) => a.top - b.top || a.left - b.left);
  const lines: TextBox[][] = [];

  boxes.forEach((box) => {
    const boxCenter = box.top + box.height / 2;
    const line = lines.find((items) => {
      const first = items[0];
      const lineCenter = first.top + first.height / 2;
      return Math.abs(boxCenter - lineCenter) <= Math.max(box.height, first.height) * 0.65;
    });

    if (line) {
      line.push(box);
    } else {
      lines.push([box]);
    }
  });

  return lines.flatMap((line) => {
    const sortedLine = line.sort((a, b) => a.left - b.left);
    const merged: HighlightBox[] = [];

    sortedLine.forEach((box) => {
      const previous = merged[merged.length - 1];
      const gap = previous ? box.left - (previous.left + previous.width) : Number.POSITIVE_INFINITY;
      const maxJoinGap = Math.max(box.height * 1.25, 10);

      if (previous && gap <= maxJoinGap) {
        const right = Math.max(previous.left + previous.width, box.left + box.width);
        const bottom = Math.max(previous.top + previous.height, box.top + box.height);
        previous.ids.push(box.id);
        previous.left = Math.min(previous.left, box.left);
        previous.top = Math.min(previous.top, box.top);
        previous.width = right - previous.left;
        previous.height = bottom - previous.top;
      } else {
        merged.push({
          ids: [box.id],
          left: box.left,
          top: box.top,
          width: box.width,
          height: box.height,
        });
      }
    });

    return merged;
  });
}

async function renderPdfPages(pdf: PDFDocumentProxy): Promise<PageRender[]> {
  const pageCount = pdf.numPages;
  const renders: PageRender[] = [];

  for (let pageNumber = 1; pageNumber <= pageCount; pageNumber += 1) {
    const page = await pdf.getPage(pageNumber);
    const viewport = page.getViewport({ scale: 1 });
    const renderScale = Math.max(2, Math.min(window.devicePixelRatio || 1, 3));
    const renderViewport = page.getViewport({ scale: renderScale });
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    if (!context) {
      continue;
    }

    canvas.width = Math.ceil(renderViewport.width);
    canvas.height = Math.ceil(renderViewport.height);
    await page.render({ canvas, canvasContext: context, viewport: renderViewport }).promise;

    const textContent = await page.getTextContent();
    const textItems = textContent.items.filter((item): item is TextItem => "str" in item && typeof item.str === "string");
    const textBoxes = textItems
      .filter((item) => item.str.trim())
      .map((item, index) => textBoxForItem(pageNumber, index, page, item));

    renders.push({
      pageNumber,
      width: viewport.width,
      height: viewport.height,
      imageUrl: canvas.toDataURL("image/png"),
      textBoxes,
    });
  }

  return renders;
}

export function PdfEvidenceViewer({ pdfUrl, highlightTarget, onLocateResult }: PdfEvidenceViewerProps) {
  const [pages, setPages] = useState<PageRender[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const pageRefs = useRef<Record<number, HTMLDivElement | null>>({});
  const lastReportedTargetId = useRef<number | null>(null);

  const tokens = useMemo(() => queryTokens(highlightTarget?.query ?? ""), [highlightTarget]);
  const bestMatch = useMemo(
    () => findBestMatch(pages, highlightTarget?.query ?? "", tokens),
    [highlightTarget?.query, pages, tokens],
  );

  useEffect(() => {
    if (!pdfUrl) {
      return;
    }

    let cancelled = false;
    const sourceUrl = pdfUrl;

    async function loadPdf() {
      try {
        setLoading(true);
        setError(null);
        const pdfjs = await import("pdfjs-dist");
        pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.mjs", import.meta.url).toString();
        const response = await fetch(sourceUrl, { cache: "no-store" });
        if (!response.ok) {
          throw new Error("PDF could not be loaded.");
        }
        const data = await response.arrayBuffer();
        const pdf = await pdfjs.getDocument({ data }).promise;
        const renderedPages = await renderPdfPages(pdf);
        if (!cancelled) {
          setPages(renderedPages);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "PDF could not be loaded.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadPdf();

    return () => {
      cancelled = true;
    };
  }, [pdfUrl]);

  useEffect(() => {
    if (!highlightTarget || loading || pages.length === 0 || lastReportedTargetId.current === highlightTarget.id) {
      return;
    }

    lastReportedTargetId.current = highlightTarget.id;
    if (!bestMatch) {
      onLocateResult?.({ found: false, label: highlightTarget.label });
      return;
    }

    const scrollToMatch = () => {
      const container = containerRef.current;
      const page = pages.find((item) => item.pageNumber === bestMatch.pageNumber);
      const pageNode = pageRefs.current[bestMatch.pageNumber];
      if (!container || !page || !pageNode) {
        return;
      }

      const highlightNode = container.querySelector<HTMLElement>(`[data-highlight-id="${bestMatch.firstBoxId}"]`);
      if (highlightNode) {
        const containerRect = container.getBoundingClientRect();
        const highlightRect = highlightNode.getBoundingClientRect();
        const deltaToCenter =
          highlightRect.top + highlightRect.height / 2 - (containerRect.top + containerRect.height / 2);
        container.scrollTo({ top: Math.max(0, container.scrollTop + deltaToCenter), behavior: "smooth" });
        return;
      }

      const scaledTop = (bestMatch.firstBoxTop / page.height) * pageNode.clientHeight;
      const scaledHeight = (bestMatch.firstBoxHeight / page.height) * pageNode.clientHeight;
      const targetCenter = pageNode.offsetTop + scaledTop + scaledHeight / 2;
      const nextTop = targetCenter - container.clientHeight / 2;
      container.scrollTo({ top: Math.max(0, nextTop), behavior: "smooth" });
    };

    requestAnimationFrame(scrollToMatch);
    onLocateResult?.({ found: true, label: highlightTarget.label });
  }, [bestMatch, highlightTarget, loading, onLocateResult, pages]);

  if (!pdfUrl) {
    return <p className="p-4 text-sm text-slate-500">No source PDF found.</p>;
  }

  if (error) {
    return <p className="p-4 text-sm text-rose-600">{error}</p>;
  }

  return (
    <div
      ref={containerRef}
      className="h-full min-h-0 max-h-full overflow-y-auto overscroll-contain bg-slate-200 px-3 py-4"
    >
      {loading ? <p className="text-sm text-slate-600">Loading PDF...</p> : null}
      <div className="mx-auto flex w-full max-w-[1120px] flex-col gap-5">
        {pages.map((page) => {
          const isBestPage = bestMatch?.pageNumber === page.pageNumber;
          const highlightBoxes = isBestPage && bestMatch ? mergeHighlightedBoxes(page, bestMatch.highlightedBoxIds) : [];
          return (
            <div
              key={page.pageNumber}
              ref={(node) => {
                pageRefs.current[page.pageNumber] = node;
              }}
              className="relative mx-auto w-full bg-white shadow-sm ring-1 ring-slate-300"
            >
              <div className="relative" style={{ aspectRatio: `${page.width} / ${page.height}` }}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={page.imageUrl} alt={`PDF page ${page.pageNumber}`} className="h-full w-full object-contain" />
                <div className="pointer-events-none absolute inset-0">
                  {highlightBoxes.length > 0
                    ? highlightBoxes.map((box) => (
                          <span
                            key={box.ids.join("-")}
                            data-highlight-id={box.ids.includes(bestMatch?.firstBoxId ?? "") ? bestMatch?.firstBoxId : undefined}
                            className="absolute rounded-[2px] bg-yellow-300/55 ring-1 ring-yellow-500/70"
                            style={{
                              left: `${(box.left / page.width) * 100}%`,
                              top: `${(box.top / page.height) * 100}%`,
                              width: `${(box.width / page.width) * 100}%`,
                              height: `${(box.height / page.height) * 100}%`,
                            }}
                          />
                        ))
                    : null}
                </div>
              </div>
              <div className="absolute right-2 top-2 rounded bg-slate-950/70 px-2 py-0.5 text-xs font-semibold text-white">
                {page.pageNumber}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
