"use client";

import { type FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { MOCK_AUTH_PASSWORD, MOCK_AUTH_USERNAME, isMockAuthenticated, signInMockUser } from "@/lib/mock-auth";

function nextPathFromLocation(): string {
  if (typeof window === "undefined") {
    return "/";
  }
  const next = new URLSearchParams(window.location.search).get("next");
  return next?.startsWith("/") ? next : "/";
}

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState(MOCK_AUTH_USERNAME);
  const [password, setPassword] = useState(MOCK_AUTH_PASSWORD);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isMockAuthenticated()) {
      router.replace(nextPathFromLocation());
    }
  }, [router]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!signInMockUser(username.trim(), password)) {
      setError("Invalid demo credentials.");
      return;
    }
    router.replace(nextPathFromLocation());
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6 py-10">
      <section className="w-full max-w-md rounded-[28px] border border-white/80 bg-white p-8 shadow-lg shadow-slate-900/8">
        <div className="mb-8">
          <div className="inline-flex w-fit items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-blue-700">
            MedComply Agent
          </div>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950">Demo Sign In</h1>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <label className="flex flex-col gap-2 text-sm font-semibold text-slate-700">
            Username
            <input
              value={username}
              onChange={(event) => {
                setUsername(event.target.value);
                setError("");
              }}
              className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-base text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
            />
          </label>

          <label className="flex flex-col gap-2 text-sm font-semibold text-slate-700">
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setError("");
              }}
              className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-base text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
            />
          </label>

          {error ? <p className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

          <button
            type="submit"
            className="inline-flex w-full items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-base font-semibold text-white shadow-sm shadow-blue-900/20 transition hover:bg-blue-700"
          >
            Sign in
          </button>
        </form>
      </section>
    </main>
  );
}
