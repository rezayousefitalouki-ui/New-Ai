"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity, Bell, CalendarDays, ChevronDown, Film, FolderOpen, Inbox,
  LayoutDashboard, LogOut, MessageSquare, Moon, Plus, Search, Settings2, Sparkles, Sun,
} from "lucide-react";
import { apiRequest } from "../../services/api";

type User = { phone: string; first_name: string; last_name: string };
type Workspace = { id: string; name: string; role: string };

const sections = [
  { title: "مدیریت", items: [
    { label: "داشبورد", href: "/", Icon: LayoutDashboard },
    { label: "تقویم محتوا", href: "/calendar", Icon: CalendarDays },
    { label: "اینباکس", href: "/inbox", Icon: Inbox },
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
  const router = useRouter();
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [user, setUser] = useState<User | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspaceId, setWorkspaceId] = useState("");
  const [loading, setLoading] = useState(true);
  const isAuthPage = pathname === "/login" || pathname === "/register";

  useEffect(() => {
    if (window.localStorage.getItem("socialmind-theme") === "light") setTheme("light");
  }, []);

  useEffect(() => {
    if (isAuthPage) { setLoading(false); return; }
    let active = true;
    Promise.all([
      apiRequest<{user: User}>("/api/v1/auth/me/"),
      apiRequest<{workspaces: Workspace[]}>("/api/v1/workspaces/"),
    ]).then(([profile, result]) => {
      if (!active) return;
      setUser(profile.user);
      setWorkspaces(result.workspaces);
      setWorkspaceId((current) => current || result.workspaces[0]?.id || "");
      setLoading(false);
    }).catch(() => { if (active) router.replace("/login"); });
    return () => { active = false; };
  }, [isAuthPage, pathname, router]);

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    window.localStorage.setItem("socialmind-theme", next);
  }
  if (isAuthPage) return <div className="auth-root" data-theme={theme}>{children}</div>;
  if (loading) return <div className="app-loading" dir="rtl">در حال بارگذاری فضای کاری…</div>;

  const activeWorkspace = workspaces.find((workspace) => workspace.id === workspaceId);
  const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.phone || "کاربر";

  return <div className="app-shell" data-theme={theme} dir="rtl">
    <aside className="sidebar">
      <div className="brand-row"><span className="brand-symbol"><Activity size={19}/></span><span className="brand-copy"><b>SocialMind</b><small>فضای کاری من</small></span><ChevronDown className="brand-caret" size={16}/></div>
      <label className="workspace-switch"><span className="workspace-avatar">{activeWorkspace?.name.slice(0, 1) || "س"}</span><span><b>{activeWorkspace?.name || "فضای کاری"}</b><small>{activeWorkspace?.role || "عضو"}</small></span>
        <select aria-label="انتخاب فضای کاری" value={workspaceId} onChange={(event) => setWorkspaceId(event.target.value)}>{workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.name}</option>)}</select><ChevronDown size={15}/>
      </label>
      {sections.map(section => <div className="nav-section" key={section.title}><div className="nav-section-title">{section.title}</div>
        {section.items.map(({label,href,Icon}) => <Link key={label} href={href} className={pathname === href ? "nav-link selected" : "nav-link"}><Icon size={17} strokeWidth={1.8}/><span>{label}</span></Link>)}
      </div>)}
      <div className="sidebar-spacer"/>
      <div className="usage-card"><div><span>اعتبار ماهانه</span><b>—</b></div><div className="usage-track"><span style={{width:"0%"}}/></div><small>پس از فعال‌سازی پلن نمایش داده می‌شود</small></div>
      <Link className="nav-link settings-link" href="/settings/connections"><Settings2 size={17}/><span>اتصال حساب‌ها</span></Link>
      <div className="profile-row"><span className="profile-avatar">{displayName.slice(0, 1)}</span><span><b>{displayName}</b><small>{user?.phone}</small></span>
        <button className="logout-button" title="خروج" aria-label="خروج" onClick={async () => { await apiRequest("/api/v1/auth/logout/", {method:"POST"}); router.replace("/login"); }}><LogOut size={15}/></button>
      </div>
    </aside>
    <main className="main-area"><header className="topbar">
      <div className="breadcrumbs"><span>{activeWorkspace?.name || "فضای کاری"}</span><span className="crumb-divider">/</span><b>{sections.flatMap(s=>s.items).find(i=>i.href===pathname)?.label ?? (pathname==="/settings/connections"?"اتصال شبکه‌ها":"داشبورد")}</b></div>
      <div className="topbar-actions"><label className="search-box"><Search size={16}/><input placeholder="جست‌وجو..." aria-label="جست‌وجو"/><kbd>⌘ K</kbd></label><button className="top-icon" aria-label="اعلان‌ها"><Bell size={18}/></button>
        <Link href="/calendar" className="top-compose"><Plus size={16}/> محتوای جدید</Link><span className="top-separator"/><button className="theme-toggle" aria-label="تغییر حالت نمایش" onClick={toggleTheme}>{theme === "dark" ? <Sun size={16}/> : <Moon size={16}/>}</button><span className="profile-avatar top-avatar">{displayName.slice(0, 1)}</span>
      </div>
    </header><div className="page-area">{children}</div></main>
  </div>;
}
