"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";

type ToastTone = "success" | "info" | "error";

type ToastInput = {
  title: string;
  description?: string;
  tone?: ToastTone;
};

type ToastItem = ToastInput & {
  id: number;
};

type ToastContextValue = {
  showToast: (toast: ToastInput) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

const toneStyles: Record<ToastTone, string> = {
  success: "border-emerald-200 bg-white text-slate-800",
  info: "border-blue-200 bg-white text-slate-800",
  error: "border-rose-200 bg-white text-slate-800",
};

function ToastIcon({ tone }: { tone: ToastTone }) {
  if (tone === "error") {
    return (
      <span className="flex h-10 w-10 items-center justify-center rounded-full bg-rose-100 text-rose-700">
        <svg viewBox="0 0 20 20" fill="currentColor" className="h-5 w-5" aria-hidden="true">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm2.78-10.72a.75.75 0 00-1.06-1.06L10 7.94 8.28 6.22a.75.75 0 10-1.06 1.06L8.94 9l-1.72 1.72a.75.75 0 101.06 1.06L10 10.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 9l1.72-1.72z"
            clipRule="evenodd"
          />
        </svg>
      </span>
    );
  }

  return (
    <span className={`flex h-10 w-10 items-center justify-center rounded-full ${tone === "success" ? "bg-emerald-100 text-emerald-700" : "bg-blue-100 text-blue-700"}`}>
      <svg viewBox="0 0 20 20" fill="currentColor" className="h-5 w-5" aria-hidden="true">
        <path
          fillRule="evenodd"
          d="M16.704 5.29a1 1 0 010 1.42l-7.2 7.2a1 1 0 01-1.415 0l-3-3a1 1 0 111.415-1.42l2.293 2.294 6.493-6.494a1 1 0 011.414 0z"
          clipRule="evenodd"
        />
      </svg>
    </span>
  );
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const nextId = useRef(1);

  const showToast = useCallback((toast: ToastInput) => {
    const id = nextId.current++;
    const item: ToastItem = {
      id,
      tone: toast.tone ?? "success",
      title: toast.title,
      description: toast.description,
    };

    setToasts((current) => [...current, item]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((entry) => entry.id !== id));
    }, 4200);
  }, []);

  const contextValue = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <div className="pointer-events-none fixed right-5 top-5 z-[100] flex w-full max-w-sm flex-col gap-3">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto animate-[toast-slide-in_260ms_ease-out] rounded-2xl border p-4 shadow-lg shadow-slate-900/10 backdrop-blur ${toneStyles[toast.tone ?? "success"]}`}
            role="status"
            aria-live="polite"
          >
            <div className="flex items-start gap-3">
              <ToastIcon tone={toast.tone ?? "success"} />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-slate-900">{toast.title}</p>
                {toast.description ? (
                  <p className="mt-1 text-sm leading-6 text-slate-500">{toast.description}</p>
                ) : null}
              </div>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}