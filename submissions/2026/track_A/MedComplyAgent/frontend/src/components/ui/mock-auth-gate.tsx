"use client";

import { usePathname, useRouter } from "next/navigation";
import { type ReactNode, useEffect, useState } from "react";

import { isMockAuthenticated, signOutMockUser } from "@/lib/mock-auth";

export function MockAuthGate({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [authenticated] = useState(() => isMockAuthenticated());

  useEffect(() => {
    if (!authenticated) {
      const nextPath = pathname || "/";
      router.replace(`/login?next=${encodeURIComponent(nextPath)}`);
    }
  }, [authenticated, pathname, router]);

  if (!authenticated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
        <p className="text-sm font-medium text-slate-500">Checking demo session...</p>
      </main>
    );
  }

  return <>{children}</>;
}

export function MockLogoutButton() {
  const router = useRouter();

  function handleLogout() {
    signOutMockUser();
    router.push("/login");
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
    >
      Sign out
    </button>
  );
}
