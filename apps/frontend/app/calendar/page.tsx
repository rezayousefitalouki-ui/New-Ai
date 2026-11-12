"use client";

import { FormEvent,useCallback,useEffect,useMemo,useState } from "react";
import { ChevronLeft,ChevronRight,Filter,Instagram,Facebook,Plus,Trash2,Clock3,Play, X } from "lucide-react";
import { apiRequest } from "../../services/api";

type Workspace={id:string;name:string};
type Account={id:string;platform:"facebook"|"instagram";display_name:string;username:string};
type Target={id:string;platform:string;account_name:string;status:string;error_message:string};
type Post={id:string;caption:string;media_urls:string[];status:string;scheduled_at:string|null;targets:Target[]};
const faDate=new Intl.DateTimeFormat("fa-IR-u-ca-persian-nu-latn",{day:"numeric",month:"numeric",year:"numeric"});
const faMonth=new Intl.DateTimeFormat("fa-IR-u-ca-persian",{month:"long",year:"numeric"});
const weekdays=["شنبه","یکشنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنج‌شنبه","جمعه"];
const statuses:Record<string,string>={draft:"پیش‌نویس",scheduled:"زمان‌بندی‌شده",publishing:"در صف انتشار",published:"منتشرشده",failed:"ناموفق",cancelled:"لغوشده"};
function jalaliPart(date:Date,type:string){return faDate.formatToParts(date).find(p=>p.type===type)?.value??""}
function jalaliStart(date:Date){const local=new Date(date.getFullYear(),date.getMonth(),date.getDate());const day=Number(jalaliPart(local,"day"));local.setDate(local.getDate()-day+1);return local}
function plusDays(date:Date,amount:number){const result=new Date(date);result.setDate(result.getDate()+amount);return result}
function sameJalaliMonth(date:Date,first:Date){const a=faDate.formatToParts(date);const b=faDate.formatToParts(first);return a.find(x=>x.type==="month")?.value===b.find(x=>x.type==="month")?.value&&a.find(x=>x.type==="year")?.value===b.find(x=>x.type==="year")?.value}
function localInput(date:Date){const d=new Date(date.getTime()-date.getTimezoneOffset()*60000);return d.toISOString().slice(0,16)}
function prettyTime(value:string|null){return value?new Intl.DateTimeFormat("fa-IR",{hour:"2-digit",minute:"2-digit"}).format(new Date(value)):"بدون زمان"}

export default function CalendarPage(){
  const [workspaces,setWorkspaces]=useState<Workspace[]>([]);
  const [workspaceId,setWorkspaceId]=useState("");
  const [accounts,setAccounts]=useState<Account[]>([]);
  const [posts,setPosts]=useState<Post[]>([]);
  const [monthStart,setMonthStart]=useState(()=>jalaliStart(new Date()));
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const [selectedAccounts,setSelectedAccounts]=useState<string[]>([]);
  const [caption,setCaption]=useState("");
  const [mediaUrl,setMediaUrl]=useState("");
  const [schedule,setSchedule]=useState("");
  const [modal,setModal]=useState(false);
  const refresh=useCallback(async(id:string)=>{if(!id)return;const [p,a]=await Promise.all([
    apiRequest<{posts:Post[]}>(`/api/v1/content/?workspace_id=${encodeURIComponent(id)}`),
    apiRequest<{accounts:Account[]}>(`/api/v1/social-accounts/?workspace_id=${encodeURIComponent(id)}`),
  ]);setPosts(p.posts);setAccounts(a.accounts);},[]);
  useEffect(()=>{apiRequest<{workspaces:Workspace[]}>("/api/v1/workspaces/").then(async r=>{setWorkspaces(r.workspaces);const id=r.workspaces[0]?.id??"";setWorkspaceId(id);if(id)await refresh(id);}).catch(e=>setError(e instanceof Error?e.message:"دریافت تقویم ناموفق بود."));},[refresh]);
  const cells=useMemo(()=>{const offset=(monthStart.getDay()+1)%7;return Array.from({length:42},(_,i)=>plusDays(monthStart,i-offset));},[monthStart]);
  const inMonthPosts=posts.filter(p=>p.scheduled_at&&new Date(p.scheduled_at)>=monthStart&&new Date(p.scheduled_at)<plusDays(monthStart,40));
  const drafts=posts.filter(p=>!p.scheduled_at&&p.status==="draft");
  function openForDate(date?:Date){setError("");setCaption("");setMediaUrl("");setSelectedAccounts([]);setSchedule(date?localInput(new Date(date.getFullYear(),date.getMonth(),date.getDate(),12,0)):"");setModal(true);}
  function toggleAccount(id:string){setSelectedAccounts(ids=>ids.includes(id)?ids.filter(x=>x!==id):[...ids,id]);}
  async function savePost(event:FormEvent<HTMLFormElement>){event.preventDefault();setBusy(true);setError("");try{const body={workspace_id:workspaceId,caption,media_urls:mediaUrl?[mediaUrl]:[],social_account_ids:selectedAccounts,...(schedule?{scheduled_at:new Date(schedule).toISOString()}:{})};await apiRequest("/api/v1/content/",{method:"POST",body:JSON.stringify(body)});setModal(false);await refresh(workspaceId);}catch(e){setError(e instanceof Error?e.message:"ذخیرهٔ محتوا ناموفق بود.");}finally{setBusy(false);}}
  async function action(post:Post,choice:"publish"|"cancel"){setError("");try{await apiRequest(`/api/v1/content/${post.id}/actions/`,{method:"POST",body:JSON.stringify({action:choice})});await refresh(workspaceId);}catch(e){setError(e instanceof Error?e.message:"عملیات انجام نشد.");}}
  async function deletePost(post:Post){if(!window.confirm("این پیش‌نویس حذف شود؟"))return;try{await apiRequest(`/api/v1/content/${post.id}/`,{method:"DELETE"});await refresh(workspaceId);}catch(e){setError(e instanceof Error?e.message:"حذف انجام نشد.");}}
  function changeMonth(delta:number){const target=plusDays(monthStart,delta>0?35:-1);setMonthStart(jalaliStart(target));}
  return <div className="page-content calendar-page">
    <div className="page-heading calendar-heading"><div><div className="eyebrow">انتشار و برنامه‌ریزی <span className="live-dot"/> دادهٔ فضای کاری</div><h1>تقویم محتوا</h1><p>زمان‌ها بر اساس منطقهٔ زمانی مرورگر و ذخیره‌سازی استاندارد UTC هستند.</p></div><button className="button-primary" onClick={()=>openForDate()}><Plus size={17}/> ساخت محتوا</button></div>
    {error&&<div className="status-banner failure" role="alert">{error}</div>}
    <section className="surface calendar-toolbar"><div className="month-nav"><button className="quiet-icon" onClick={()=>changeMonth(-1)} aria-label="ماه قبل"><ChevronRight size={17}/></button><b>{faMonth.format(monthStart)}</b><button className="quiet-icon" onClick={()=>changeMonth(1)} aria-label="ماه بعد"><ChevronLeft size={17}/></button><button className="today-button" onClick={()=>setMonthStart(jalaliStart(new Date()))}>امروز</button></div><div className="calendar-controls"><span className="calendar-real"><Clock3 size={14}/> انتشار واقعی</span>{workspaces.length>1&&<select className="connection-select" value={workspaceId} onChange={async e=>{setWorkspaceId(e.target.value);await refresh(e.target.value);}}>{workspaces.map(w=><option key={w.id} value={w.id}>{w.name}</option>)}</select>}<button className="select-control"><Filter size={14}/> همهٔ کانال‌ها</button></div></section>
    <div className="calendar-layout"><section className="surface month-calendar"><div className="calendar-grid day-header">{weekdays.map(n=><div key={n}>{n}</div>)}</div><div className="calendar-grid month-days">{cells.map((date,i)=>{const current=sameJalaliMonth(date,monthStart);const dayPosts=inMonthPosts.filter(p=>{const d=new Date(p.scheduled_at!);return d.getFullYear()===date.getFullYear()&&d.getMonth()===date.getMonth()&&d.getDate()===date.getDate();});const today=new Date().toDateString()===date.toDateString();return <article key={i} className={today?"day-cell today-cell":current?"day-cell":"day-cell outside"}><div className="day-number">{current?jalaliPart(date,"day"):""}</div>{dayPosts.map(p=><div className={"calendar-post "+(p.targets[0]?.platform??"")} key={p.id}><div className="post-copy"><b>{p.caption||"بدون متن"}</b><small>{prettyTime(p.scheduled_at)} · {statuses[p.status]??p.status}</small></div>{p.targets.map(t=>t.platform==="instagram"?<Instagram key={t.id} size={12}/>:<Facebook key={t.id} size={12}/>)}{(p.status==="draft"||p.status==="failed")&&<button className="calendar-post-action" onClick={()=>action(p,"publish")} title="انتشار فوری" aria-label="انتشار فوری"><Play size={11}/></button>}{p.status==="scheduled"&&<button className="calendar-post-action" onClick={()=>action(p,"cancel")} title="لغو زمان‌بندی" aria-label="لغو زمان‌بندی"><X size={11}/></button>}</div>)}{current&&<button className="add-day" onClick={()=>openForDate(date)} aria-label="ساخت محتوا در این روز"><Plus size={14}/></button>}</article>})}</div></section>
    <aside className="calendar-side"><section className="surface side-card"><div className="panel-head"><div><h2>پیش‌نویس‌ها</h2><small>ذخیره‌شده در فضای کاری</small></div><span className="count-badge">{drafts.length}</span></div>{drafts.length?drafts.slice(0,6).map(p=><div className="draft-row" key={p.id}><span className="draft-thumb"><Instagram size={16}/></span><span><b>{p.caption||"بدون متن"}</b><small>پیش‌نویس · {p.targets.length} حساب</small></span><button className="calendar-post-action" onClick={()=>action(p,"publish")} title="انتشار فوری" aria-label="انتشار فوری"><Play size={12}/></button><button className="remove-member" onClick={()=>deletePost(p)} aria-label="حذف پیش‌نویس"><Trash2 size={14}/></button></div>):<div className="empty-state compact"><b>پیش‌نویسی نداریم</b><small>محتوای ذخیره‌شده اینجا نمایش داده می‌شود.</small></div>}</section>
    <section className="surface side-card"><div className="panel-head"><div><h2>وضعیت انتشار</h2><small>وضعیت محتوای همین ماه</small></div></div>{["scheduled","publishing","published","failed"].map(s=><div className="capacity" key={s}><span>{statuses[s]}</span><b>{inMonthPosts.filter(p=>p.status===s).length}</b></div>)}</section></aside></div>
    {modal&&<div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)setModal(false);}}><section className="surface compose-modal" role="dialog" aria-modal="true" aria-labelledby="compose-title"><div className="panel-head"><div><h2 id="compose-title">ساخت محتوا</h2><small>پیش‌نویس بساز یا برای زمان آینده برنامه‌ریزی کن.</small></div><button className="quiet-icon" onClick={()=>setModal(false)}>×</button></div><form className="compose-form" onSubmit={savePost}>
      <label>متن محتوا<textarea rows={5} maxLength={2200} value={caption} onChange={e=>setCaption(e.target.value)} placeholder="متن پست…"/></label>
      <label>نشانی HTTPS تصویر عمومی<input type="url" value={mediaUrl} onChange={e=>setMediaUrl(e.target.value)} placeholder="https://...jpg"/><small>برای انتشار Instagram فعلاً یک تصویر JPEG لازم است.</small></label>
      <div className="compose-accounts"><b>حساب‌های مقصد</b>{accounts.length?accounts.map(a=><label key={a.id}><input type="checkbox" checked={selectedAccounts.includes(a.id)} onChange={()=>toggleAccount(a.id)}/>{a.platform==="instagram"?<Instagram size={15}/>:<Facebook size={15}/>} {a.display_name||a.platform}</label>):<small>برای انتخاب مقصد ابتدا حساب اجتماعی متصل کن.</small>}</div>
      <label>زمان‌بندی اختیاری<input type="datetime-local" value={schedule} onChange={e=>setSchedule(e.target.value)}/></label>
      <div className="modal-actions"><button className="button-outline" type="button" onClick={()=>setModal(false)}>انصراف</button><button className="button-primary" disabled={busy}>{busy?"در حال ذخیره…":schedule?"زمان‌بندی":"ذخیرهٔ پیش‌نویس"}</button></div>
    </form></section></div>}
  </div>;
}
