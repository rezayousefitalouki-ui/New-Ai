"use client";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity } from "lucide-react";
import { apiRequest, ensureCsrf } from "../../services/api";

export default function LoginPage() {
  const router = useRouter();
  const [phone,setPhone] = useState("");
  const [password,setPassword] = useState("");
  const [error,setError] = useState("");
  const [busy,setBusy] = useState(false);
  async function submit(event:FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      await ensureCsrf();
      await apiRequest("/api/v1/auth/login/", {method:"POST",body:JSON.stringify({phone,password})});
      router.replace("/");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "ورود انجام نشد."); }
    finally { setBusy(false); }
  }
  return <main className="auth-page" dir="rtl"><section className="auth-card">
    <div className="auth-brand"><span className="brand-symbol"><Activity size={20}/></span><b>SocialMind AI</b></div>
    <div className="eyebrow">خوش برگشتی</div><h1>ورود به فضای کاری</h1><p>با شماره موبایلی که هنگام ثبت‌نام استفاده کردی وارد شو.</p>
    <form onSubmit={submit} className="auth-form">
      <label>شماره موبایل<input autoComplete="tel" inputMode="tel" required value={phone} onChange={e=>setPhone(e.target.value)} placeholder="0912۱۲۳۴۵۶۷"/></label>
      <label>گذرواژه<input type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)} placeholder="گذرواژه"/></label>
      {error&&<div className="form-error" role="alert">{error}</div>}<button className="button-primary auth-submit" disabled={busy}>{busy?"در حال ورود…":"ورود امن"}</button>
    </form><div className="auth-footer">حساب نداری؟ <Link href="/register">ساخت فضای کاری</Link></div>
  </section></main>;
}
