"use client";

import { useCallback,useEffect,useMemo,useState } from "react";
import { Activity,CalendarDays,RefreshCw,Users,Heart,MessageCircle,Video } from "lucide-react";
import { apiRequest } from "../../services/api";

type Workspace={id:string;name:string};
type Snapshot={id:string;account_id:string;account_name:string;username:string;followers_count:number|null;media_count:number|null;captured_at:string};
type Media={id:string;remote_media_id:string;account_name:string;caption:string;media_type:string;permalink:string;published_at:string|null;like_count:number|null;comments_count:number|null;fetched_at:string};
type Analytics={accounts:{id:string;name:string;username:string;last_error:string}[];latest:Snapshot[];series:Snapshot[];top_media:Media[];days:number;last_updated:string|null};
const n=(value:number|null|undefined)=>value===null||value===undefined?"—":new Intl.NumberFormat("fa-IR").format(value);
const time=(value:string|null)=>value?new Intl.DateTimeFormat("fa-IR",{month:"short",day:"numeric"}).format(new Date(value)):"—";

export default function AnalyticsPage(){
  const [workspaces,setWorkspaces]=useState<Workspace[]>([]);
  const [workspaceId,setWorkspaceId]=useState("");
  const [data,setData]=useState<Analytics|null>(null);
  const [days,setDays]=useState(30);
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const refresh=useCallback(async(id:string,range=days)=>{if(!id)return;const result=await apiRequest<Analytics>(`/api/v1/analytics/?workspace_id=${encodeURIComponent(id)}&days=${range}`);setData(result);},[days]);
  useEffect(()=>{apiRequest<{workspaces:Workspace[]}>("/api/v1/workspaces/").then(async r=>{setWorkspaces(r.workspaces);const id=r.workspaces[0]?.id??"";setWorkspaceId(id);if(id)await refresh(id);}).catch(e=>setError(e instanceof Error?e.message:"گزارش دریافت نشد."));},[refresh]);
  useEffect(()=>{if(workspaceId)refresh(workspaceId,days).catch(e=>setError(e instanceof Error?e.message:"گزارش دریافت نشد."));},[workspaceId,days,refresh]);
  const latest=data?.latest?.[data.latest.length-1];
  const interaction=useMemo(()=>data?.top_media.reduce((sum,m)=>sum+(m.like_count??0)+(m.comments_count??0),0)??null,[data]);
  const points=useMemo(()=>{const rows=data?.series??[];if(rows.length<2)return "";const values=rows.map(x=>x.followers_count).filter((x):x is number=>x!==null);if(values.length<2)return "";const min=Math.min(...values),max=Math.max(...values),spread=Math.max(max-min,1);return rows.map((row,i)=>{const value=row.followers_count??min;const x=8+i*(84/(rows.length-1));const y=88-((value-min)/spread)*76;return `${x},${y}`;}).join(" ");},[data]);
  async function sync(){if(!workspaceId)return;setBusy(true);setError("");try{await apiRequest("/api/v1/analytics/",{method:"POST",body:JSON.stringify({workspace_id:workspaceId})});}catch(e){setError(e instanceof Error?e.message:"همگام‌سازی شروع نشد.");}finally{setBusy(false);}}
  return <div className="page-content analytics-page">
    <div className="page-heading"><div><div className="eyebrow">گزارش عملکرد <span className="live-dot"/> دادهٔ ثبت‌شدهٔ Meta</div><h1>تحلیل‌ها</h1><p>مقادیر خالی یعنی داده از Meta دریافت نشده یا برای این حساب در دسترس نیست.</p></div><div className="analytics-actions">{workspaces.length>1&&<select className="connection-select" value={workspaceId} onChange={e=>setWorkspaceId(e.target.value)}>{workspaces.map(w=><option key={w.id} value={w.id}>{w.name}</option>)}</select>}<select className="connection-select" value={days} onChange={e=>setDays(Number(e.target.value))}><option value={7}>۷ روز</option><option value={30}>۳۰ روز</option><option value={90}>۹۰ روز</option></select><button className="button-outline" onClick={sync} disabled={busy}><RefreshCw size={15}/> {busy?"در صف…":"همگام‌سازی Meta"}</button></div></div>
    {error&&<div className="status-banner failure" role="alert">{error}</div>}
    <div className="analytics-cards">
      {[["دنبال‌کنندگان",latest?.followers_count,Users,"mint"],["رسانه‌های حساب",latest?.media_count,Video,"blue"],["تعامل رسانه‌های برتر",interaction,Heart,"violet"],["حساب حرفه‌ای متصل",data?.accounts.length??0,Activity,"amber"]].map(([title,value,Icon,tone])=>{const I=Icon as typeof Users;return <article className="surface metric-card" key={title as string}><div className="metric-head"><span>{title as string}</span><span className={`metric-icon ${tone}`}><I size={17}/></span></div><strong>{n(value as number|null|undefined)}</strong><small>آخرین دادهٔ دریافت‌شده</small></article>})}
    </div>
    <div className="analytics-grid"><section className="surface analytics-chart"><div className="panel-head"><div><h2>روند دنبال‌کنندگان</h2><small>تاریخچهٔ snapshotهای موفق Meta</small></div><span className="select-control"><CalendarDays size={14}/> {days} روز</span></div>
      <div className="analytics-plot"><div className="plot-lines"><i/><i/><i/><i/></div>{points?<svg viewBox="0 0 100 100" preserveAspectRatio="none" className="analytics-line" aria-label="روند دنبال‌کنندگان"><polyline points={points} fill="none" stroke="var(--accent)" strokeWidth="2" vectorEffect="non-scaling-stroke"/></svg>:<div className="plot-empty">برای نمودار، «همگام‌سازی Meta» را بزن و پس از دریافت چند snapshot دوباره مراجعه کن.</div>}<div className="chart-x">{(data?.series??[]).slice(-5).map(row=><span key={row.id}>{time(row.captured_at)}</span>)}</div></div>
      <div className="analytics-foot"><span>{data?.accounts.length??0} حساب Instagram متصل</span><span>آخرین دریافت: {time(data?.last_updated??null)}</span></div>
    </section>
    <section className="surface audience-panel"><div className="panel-head"><div><h2>حساب‌های متصل</h2><small>وضعیت دریافت داده</small></div></div>{data?.accounts.length?data.accounts.map(account=><div className="capacity" key={account.id}><span>@{account.username||account.name}</span><b className={account.last_error?"text-error":"text-success"}>{account.last_error?"نیاز به بررسی":"متصل"}</b></div>):<div className="audience-empty"><span><Users size={21}/></span><b>حساب حرفه‌ای نداریم</b><small>از بخش اتصال‌ها یک Instagram Business یا Creator وصل کن.</small></div>}</section></div>
    <section className="surface top-content-panel"><div className="panel-head"><div><h2>محتوای پربازده</h2><small>مرتب‌شده بر اساس تعداد لایک و دیدگاه دریافت‌شده</small></div></div>{data?.top_media.length?<div className="content-table"><div className="table-head"><span>محتوا</span><span>تاریخ</span><span>پسند</span><span>دیدگاه</span></div>{data.top_media.map(item=><a className="analytics-media-row" href={item.permalink||undefined} target={item.permalink?"_blank":undefined} rel="noreferrer" key={item.id}><span>{item.caption||item.media_type||item.remote_media_id}</span><span>{time(item.published_at)}</span><span><Heart size={13}/>{n(item.like_count)}</span><span><MessageCircle size={13}/>{n(item.comments_count)}</span></a>)}</div>:<div className="table-empty">هنوز دادهٔ رسانه‌ای از Meta دریافت نشده است.</div>}</section>
    <div className="data-note">گزارش شامل فقط فیلدهایی است که Meta برای حساب و مجوزهای فعلی برگردانده است؛ دسترسی به Insights جزئی‌تر می‌تواند به نوع حساب و مجوزهای اپ وابسته باشد.</div>
  </div>;
}
