import type { Metadata } from "next";
import { Geist_Mono, Inter } from "next/font/google";
import "./globals.css";
import { ToastProvider } from "@/components/ui/toast-provider";

const inter = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MedComply Agent",
  description: "Gemma-powered medical compliance review agent for auditable clinical evidence workflows.",
  icons: {
    icon: "/hedis-ai-review-icon.svg",
    shortcut: "/hedis-ai-review-icon.svg",
    apple: "/hedis-ai-review-icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-800">
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}
