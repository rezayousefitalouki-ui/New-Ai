import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SocialMind AI | دستیار هوشمند محتوا",
  description: "مدیریت و برنامه‌ریزی محتوای اینستاگرام",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="fa" dir="rtl"><body>{children}</body></html>;
}
