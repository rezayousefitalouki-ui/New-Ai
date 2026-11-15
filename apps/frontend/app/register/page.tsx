"use client";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity } from "lucide-react";
import { apiRequest, ensureCsrf } from "../../services/api";

export default function RegisterPage() {
  const router=useRouter();
  const [phone,setPhone]=useState("");
  const [password,setPassword]=useState("");
  const [workspaceName,setWorkspaceName]=useState("");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  async function submit(event:FormEvent<HTMLFormElement>) {
    event.preventDefault();setBusy(true);setError("");
    try {
      await ensureCsrf();
      await apiRequest("/api/v1/auth/register/",{method:"POST",body:JSON.stringify({phone,password,workspace_name:workspaceName})});
      router.replace("/");
    } catch(reason) {setError(reason instanceof Error?reason.message:"ثبت‌نام انجام نشد.");}
    finally {setBusy(false);}
  }
  return <main className="auth-page" dir="rtl"><section className="auth-card">
    <div className="auth-brand"><span className="brand-symbol"><Activity size={20}/></span><b>SocialMind AI</b></div>
    <div className="eyebrow">شروع رایگان</div><h1>فضای کاری بساز</h1><p>با ساخت حساب، مالک فضای کاری می‌شوی و بعداً می‌توانی اعضا را اضافه کنی.</p>
    <form onSubmit={submit} className="auth-form">
      <label>شماره موبایل<input autoComplete="tel" inputMode="tel" required value={phone} onChange={e=>setPhone(e.target.value)} placeholder="0912۱۲۳۴۵۶۷"/></label>
      <label>نام فضای کاری<input required maxLength={120} value={workspaceName} onChange={e=>setWorkspaceName(e.target.value)} placeholder="مثلاً استودیو سبز"/></label>
      <label>گذرواژه<input type="password" autoComplete="new-password" minLength={8} required value={password} onChange={e=>setPassword(e.target.value)} placeholder="حداقل ۸ نویسه"/></label>
      {error&&<div className="form-error" role="alert">{error}</div>}<button className="button-primary auth-submit" disabled={busy}>{busy?"در حال ساخت…":"ساخت حساب و فضا"}</button>
    </form><div className="auth-footer">حساب داری؟ <Link href="/login">ورود</Link></div>
  </section></main>;
}
