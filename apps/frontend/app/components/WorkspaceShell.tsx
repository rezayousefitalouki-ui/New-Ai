"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import {
  Activity, Bell, CalendarDays, ChevronDown, Film, FolderOpen, Inbox,
  LayoutDashboard, MessageSquare, Moon, Plus, Search, Settings2, Sparkles, Sun,
} from "lucide-react";

const sections = [
  { title: "مدیریت", items: [
    { label: "داشبورد", href: "/", Icon: LayoutDashboard },
    { label: "تقویم محتوا", href: "/calendar", Icon: CalendarDays },
    { label: "اینباکس", href: "/inbox", Icon: Inbox, badge: "۴" },
    { label: "کتابخانه رسانه", href: "#", Icon: FolderOpen },
  ]},
  { title: "ساخت محتوا", items: [
    { label: "استودیوی ویدیو", href: "/studio", Icon: Film },
    { label: "ایده‌ها و متن‌ها", href: "#", Icon: Sparkles },
  ]},
  { title: "تحلیل", items: [
    { label: "نمای کلی", href: "/analytics", Icon: Activity },
    { label: "تعامل مخاطبان", href: "#", Icon: MessageSquare },
  ]},
];

export function WorkspaceShell({ children }: Readonly<{ children: React.ReactNode }>) {
  const pathname = usePathname();
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  useEffect(() => { const stored = window.localStorage.getItem("socialmind-theme"); if (stored === "light") setTheme("light"); }, []);
  function toggleTheme() { const next = theme === "dark" ? "light" : "dark"; setTheme(next); window.localStorage.setItem("socialmind-theme", next); }
  return <div className="app-shell" data-theme={theme} dir="rtl">
    <aside className="sidebar">
      <div className="brand-row">
        <span className="brand-symbol"><Activity size={19}/></span>
        <span className="brand-copy"><b>SocialMind</b><small>فضای کاری من</small></span>
        <ChevronDown className="brand-caret" size={16}/>
      </div>
      <div className="workspace-switch"><span className="workspace-avatar">س</span><span><b>استودیو سبز</b><small>فضای کاری</small></span><ChevronDown size={15}/></div>
      {sections.map(section => <div className="nav-section" key={section.title}>
        <div className="nav-section-title">{section.title}</div>
        {section.items.map(({label,href,Icon,badge}) => <Link key={label} href={href} className={pathname === href ? "nav-link selected" : "nav-link"}>
          <Icon size={17} strokeWidth={1.8}/><span>{label}</span>{badge && <small className="nav-badge">{badge}</small>}
        </Link>)}
      </div>)}
      <div className="sidebar-spacer"/>
      <div className="usage-card"><div><span>اعتبار ماهانه</span><b>۶۸٪</b></div><div className="usage-track"><span/></div><small>۳۴۰ از ۵۰۰ اعتبار باقی‌مانده</small></div>
      <Link className="nav-link settings-link" href="#"><Settings2 size={17}/><span>تنظیمات</span></Link>
      <div className="profile-row"><span className="profile-avatar">ر</span><span><b>رضا یوسفی</b><small>مدیر فضای کاری</small></span><ChevronDown size={15}/></div>
    </aside>
    <main className="main-area">
      <header className="topbar">
        <div className="breadcrumbs"><span>فضای کاری</span><span className="crumb-divider">/</span><b>{sections.flatMap(s=>s.items).find(i=>i.href===pathname)?.label ?? "داشبورد"}</b></div>
        <div className="topbar-actions">
          <label className="search-box"><Search size={16}/><input placeholder="جست‌وجو..." aria-label="جست‌وجو"/><kbd>⌘ K</kbd></label>
          <button className="top-icon" aria-label="اعلان‌ها"><Bell size={18}/><i/></button>
          <button className="top-compose"><Plus size={16}/> محتوای جدید</button>
          <span className="top-separator"/>
          <button className="theme-toggle" aria-label="تغییر حالت نمایش" onClick={toggleTheme}>{theme === "dark" ? <Sun size={16}/> : <Moon size={16}/>}</button>
          <span className="profile-avatar top-avatar">ر</span>
        </div>
      </header>
      <div className="page-area">{children}</div>
    </main>
  </div>;
}
