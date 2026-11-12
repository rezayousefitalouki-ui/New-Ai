"use client";

import { FormEvent,useCallback,useEffect,useState } from "react";
import { BookOpenCheck,History,Save,Sparkles } from "lucide-react";
import { apiRequest } from "../../services/api";

type Workspace={id:string;name:string};
type Brand={id:string;business_name:string;industry:string;products:string;audience:string;voice:string;preferred_topics:string[];forbidden_terms:string[];updated_at:string};
type Generation={id:string;kind:string;brief:string;status:string;result:Record<string,unknown>|null;provider_model:string;usage_tokens:number|null;error_message:string;created_at:string};
const kinds=[["ideas","ایده محتوا"],["script","سناریو"],["caption","کپشن"],["strategy","استراتژی"]];
const voices=[["friendly","دوستانه"],["professional","حرفه‌ای"],["educational","آموزشی"],["promotional","تبلیغاتی"],["humorous","شوخ"],["technical","تخصصی"]];
const statuses:Record<string,string>={queued:"در صف",running:"در حال تولید",succeeded:"آماده",failed:"ناموفق"};
function resultLines(result:Record<string,unknown>){const items=(result.items??result.scenes??result.pillars) as Record<string,unknown>[]|undefined;if(Array.isArray(items))return items;return [result];}

export default function AIPage(){
  const [workspaces,setWorkspaces]=useState<Workspace[]>([]);
  const [workspaceId,setWorkspaceId]=useState("");
  const [brand,setBrand]=useState<Brand|null>(null);
  const [generations,setGenerations]=useState<Generation[]>([]);
  const [kind,setKind]=useState("ideas");
  const [brief,setBrief]=useState("");
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const [saved,setSaved]=useState(false);
  const load=useCallback(async(id:string)=>{if(!id)return;const [brandResult,history]=await Promise.all([
    apiRequest<{brand:Brand}>(`/api/v1/ai/brand/?workspace_id=${encodeURIComponent(id)}`),
    apiRequest<{generations:Generation[]}>(`/api/v1/ai/generations/?workspace_id=${encodeURIComponent(id)}`),
  ]);setBrand(brandResult.brand);setGenerations(history.generations);},[]);
  useEffect(()=>{apiRequest<{workspaces:Workspace[]}>("/api/v1/workspaces/").then(async r=>{setWorkspaces(r.workspaces);const id=r.workspaces[0]?.id??"";setWorkspaceId(id);await load(id);}).catch(e=>setError(e instanceof Error?e.message:"فضای کاری بارگذاری نشد."));},[load]);
  useEffect(()=>{if(workspaceId)load(workspaceId).catch(e=>setError(e instanceof Error?e.message:"اطلاعات دریافت نشد."));},[workspaceId,load]);
  useEffect(()=>{if(!workspaceId||!generations.some(g=>g.status==="queued"||g.status==="running"))return;const timer=window.setInterval(()=>load(workspaceId).catch(()=>undefined),2500);return()=>window.clearInterval(timer);},[workspaceId,generations,load]);

  function update<K extends keyof Brand>(key:K,value:Brand[K]){setBrand(current=>current?{...current,[key]:value}:current);}
  async function saveBrand(event:FormEvent<HTMLFormElement>){event.preventDefault();if(!brand)return;setBusy(true);setError("");try{const r=await apiRequest<{brand:Brand}>("/api/v1/ai/brand/",{method:"PATCH",body:JSON.stringify({workspace_id:workspaceId,...brand})});setBrand(r.brand);setSaved(true);}catch(e){setError(e instanceof Error?e.message:"پروفایل ذخیره نشد.");}finally{setBusy(false);}}
  async function generate(event:FormEvent<HTMLFormElement>){event.preventDefault();if(!brief.trim())return;setBusy(true);setError("");try{await apiRequest("/api/v1/ai/generations/",{method:"POST",body:JSON.stringify({workspace_id:workspaceId,kind,brief})});setBrief("");await load(workspaceId);}catch(e){setError(e instanceof Error?e.message:"درخواست تولید ثبت نشد.");}finally{setBusy(false);}}
  return <div className="page-content ai-page">
    <div className="page-heading"><div><div className="eyebrow">دستیار هوشمند <span className="live-dot"/> خروجی provider</div><h1>ایده‌ها و متن‌ها</h1><p>پروفایل برند را بساز، بعد ایده، سناریو، کپشن یا استراتژی درخواست کن.</p></div>{workspaces.length>1&&<select className="connection-select" value={workspaceId} onChange={e=>setWorkspaceId(e.target.value)}>{workspaces.map(w=><option key={w.id} value={w.id}>{w.name}</option>)}</select>}</div>
    {error&&<div className="status-banner failure" role="alert">{error}</div>}
    <div className="ai-studio-layout">
      <section className="surface ai-brand-panel"><div className="panel-head"><div><h2><BookOpenCheck size={17}/> حافظهٔ برند</h2><small>محدود به این فضای کاری</small></div></div>
        {brand&&<form className="compose-form" onSubmit={saveBrand}>
          <label>نام کسب‌وکار<input value={brand.business_name} onChange={e=>update("business_name",e.target.value)}/></label>
          <label>حوزهٔ فعالیت<input value={brand.industry} onChange={e=>update("industry",e.target.value)}/></label>
          <label>محصول‌ها و خدمات<textarea rows={3} value={brand.products} onChange={e=>update("products",e.target.value)}/></label>
          <label>مخاطب هدف<textarea rows={3} value={brand.audience} onChange={e=>update("audience",e.target.value)}/></label>
          <label>لحن برند<select value={brand.voice} onChange={e=>update("voice",e.target.value)}>{voices.map(([v,label])=><option value={v} key={v}>{label}</option>)}</select></label>
          <label>موضوع‌های ترجیحی<input value={brand.preferred_topics.join("، ")} onChange={e=>update("preferred_topics",e.target.value.split(/[,،]/).map(x=>x.trim()).filter(Boolean))}/></label>
          <label>عبارت‌های ممنوع<input value={brand.forbidden_terms.join("، ")} onChange={e=>update("forbidden_terms",e.target.value.split(/[,،]/).map(x=>x.trim()).filter(Boolean))}/></label>
          <button className="button-primary" disabled={busy}><Save size={15}/>{saved?"ذخیره شد":"ذخیرهٔ پروفایل"}</button>
        </form>}
      </section>
      <section className="surface ai-generate-panel"><div className="panel-head"><div><h2><Sparkles size={17}/> ساخت محتوای تازه</h2><small>خروجی بعد از اعتبارسنجی provider در تاریخچه می‌ماند</small></div></div>
        <div className="segmented ai-kind-tabs">{kinds.map(([value,label])=><button type="button" className={kind===value?"seg-active":""} onClick={()=>setKind(value)} key={value}>{label}</button>)}</div>
        <form className="compose-form" onSubmit={generate}><label>شرح درخواست<textarea rows={5} maxLength={5000} value={brief} onChange={e=>setBrief(e.target.value)} placeholder="برای چه محصول، مخاطب و هدفی محتوا بسازیم؟"/></label><div className="ai-generate-footer"><small>تولید فقط وقتی فعال است که کلید AI provider در تنظیمات سرور باشد.</small><button className="button-primary" disabled={busy||!brief.trim()}><Sparkles size={15}/>{busy?"در حال ثبت…":"افزودن به صف"}</button></div></form>
        <div className="ai-history"><div className="panel-head"><div><h2><History size={16}/> خروجی‌ها</h2><small>{generations.length} درخواست اخیر</small></div></div>{generations.length?generations.map(g=><article className="ai-result-card" key={g.id}><header><b>{kinds.find(([value])=>value===g.kind)?.[1]??g.kind}</b><span className={"ai-status "+g.status}>{statuses[g.status]??g.status}</span><time>{new Intl.DateTimeFormat("fa-IR",{month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"}).format(new Date(g.created_at))}</time></header><p>{g.brief}</p>{g.status==="failed"?<div className="ai-error">{g.error_message}</div>:g.result&&<div className="ai-result-items">{resultLines(g.result).map((row,index)=><section key={index}><b>{String(row.title??row.name??row.hook??"خروجی")}</b><p>{String(row.hook??row.narration??row.objective??row.visual??"")}</p>{row.cta&&<small>CTA: {String(row.cta)}</small>}</section>)}</div>}{g.status==="succeeded"&&<small>{g.provider_model} · {g.usage_tokens??"—"} tokens</small>}</article>):<div className="empty-state compact">هنوز خروجی‌ای ثبت نشده است.</div>}</div>
      </section>
    </div>
  </div>;
}
