import type { Metadata } from "next";
import { WorkspaceShell } from "./components/WorkspaceShell";
import { QueryProvider } from "./components/QueryProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "SocialMind AI | مدیریت هوشمند محتوا",
  description: "مدیریت، برنامه‌ریزی و تولید محتوای شبکه‌های اجتماعی",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="fa" dir="rtl" suppressHydrationWarning><body><QueryProvider><WorkspaceShell>{children}</WorkspaceShell></QueryProvider></body></html>;
}
