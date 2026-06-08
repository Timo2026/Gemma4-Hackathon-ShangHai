type StatusTone = "slate" | "blue" | "emerald" | "rose" | "amber";

const toneClasses: Record<StatusTone, string> = {
  slate: "border-slate-200 bg-slate-100 text-slate-700",
  blue: "border-blue-200 bg-blue-100 text-blue-800",
  emerald: "border-emerald-200 bg-emerald-100 text-emerald-800",
  rose: "border-rose-200 bg-rose-100 text-rose-800",
  amber: "border-amber-200 bg-amber-100 text-amber-800",
};

export function StatusPill({
  label,
  tone,
}: {
  label: string;
  tone: StatusTone;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold tracking-[0.02em] ${toneClasses[tone]}`}
    >
      {label}
    </span>
  );
}