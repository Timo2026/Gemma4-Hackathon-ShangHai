import "./globals.css";

import type { ReactNode } from "react";

export const metadata = {
  title: "Parallel Agent",
  description: "Gemma 4 驱动的多现实决策模拟器。",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
