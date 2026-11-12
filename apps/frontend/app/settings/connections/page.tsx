"use client";
import { useCallback,useEffect,useState } from "react";
import { useSearchParams } from "next/navigation";
import { Facebook,Instagram,Linkedin,Youtube,RefreshCw } from "lucide-react";
import { apiRequest } from "../../../services/api";

type Workspace={id:string;name:string;role:string};
type Account={id:string;platform:"facebook"|"instagram";external_id:string;display_name:string;username:string;status:string};
const platforms=[
  {name:"Facebook",detail:"صفحه‌های تحت مدیریت از مسیر Meta",Icon:Facebook,active:true},
  {name:"Instagram",detail:"حساب حرفه‌ای متصل به صفحهٔ Facebook",Icon:Instagram,active:true},
  {name:"LinkedIn",detail:"اتصال رسمی در فاز بعدی",Icon:Linkedin,active:false},
  {name:"YouTube",detail:"اتصال رسمی در فاز بعدی",Icon:Youtube,active:false},
];
export default function ConnectionsPage(){
  const search=useSearchParams();
  const [workspaces,setWorkspaces]=useState<Workspace[]>([]);
  const [workspaceId,setWorkspaceId]=useState("");
  const [accounts,setAccounts]=useState<Account[]>([]);
  const [error,setError]=useState("");
  const [notice,setNotice]=useState("");
  const [loading,setLoading]=useState(true);
  const [connecting,setConnecting]=useState(false);
  const refresh=useCallback(async(id:string)=>{if(!id)return;const r=await apiRequest<{accounts:Account[]}>(`/api/v1/social-accounts/?workspace_id=${encodeURIComponent(id)}`);setAccounts(r.accounts);},[]);
  useEffect(()=>{
    const status=search.get("status");
    if(status==="connected")setNotice("حساب‌ها با موفقیت از Meta دریافت شدند.");
    else if(status)setError("اتصال Meta کامل نشد. تنظیمات برنامه و دسترسی‌های حساب را بررسی کن.");
  },[search]);
  useEffect(()=>{
    apiRequest<{workspaces:Workspace[]}>("/api/v1/workspaces/").then(async r=>{setWorkspaces(r.workspaces);const id=r.workspaces[0]?.id??"";setWorkspaceId(id);if(id)await refresh(id);})
      .catch(reason=>setError(reason instanceof Error?reason.message:"دریافت حساب‌ها ناموفق بود.")).finally(()=>setLoading(false));
  },[refresh]);
  async function connectMeta(){
    setError("");setNotice("");setConnecting(true);
    try{const r=await apiRequest<{authorization_url:string}>("/api/v1/social-accounts/oauth/meta/start/",{method:"POST",body:JSON.stringify({workspace_id:workspaceId})});window.location.assign(r.authorization_url);}
    catch(reason){setError(reason instanceof Error?reason.message:"شروع اتصال انجام نشد.");setConnecting(false);}
  }
  async function changeWorkspace(id:string){setWorkspaceId(id);try{await refresh(id);}catch(reason){setError(reason instanceof Error?reason.message:"دریافت حساب‌ها ناموفق بود.");}}
  return <div className="page-content">
    <div className="page-heading"><div><div className="eyebrow">حساب‌ها و مجوزها</div><h1>اتصال شبکه‌ها</h1><p>اتصال رسمی شبکه‌ها به فضای کاری را مدیریت کن.</p></div><button className="button-outline" onClick={()=>workspaceId&&refresh(workspaceId)}><RefreshCw size={15}/> تازه‌سازی</button></div>
    {workspaces.length>1&&<label className="connection-workspace">فضای کاری<select value={workspaceId} onChange={e=>changeWorkspace(e.target.value)}>{workspaces.map(w=><option key={w.id} value={w.id}>{w.name}</option>)}</select></label>}
    {notice&&<div className="status-banner success">{notice}</div>}{error&&<div className="status-banner failure" role="alert">{error}</div>}
    <section className="connection-grid">{platforms.map(({name,detail,Icon,active})=>{const linked=accounts.filter(a=>a.platform===name.toLowerCase());return <article className="surface connection-card" key={name}>
      <div className="connection-card-head"><span className={"connection-icon "+(active?"enabled":"disabled")}><Icon size={21}/></span><span className="connection-state">{linked.length?`${linked.length} متصل`:active?"قابل اتصال":"به‌زودی"}</span></div>
      <h2>{name}</h2><p>{detail}</p>{linked.length?<ul className="connected-list">{linked.map(a=><li key={a.id}><b>{a.display_name||name}</b><small>{a.username?`@${a.username}`:a.external_id}</small></li>)}</ul>:<div className="connection-empty">هنوز حسابی متصل نشده است.</div>}
      {name==="Facebook"&&<button className="button-primary connection-action" disabled={connecting||!workspaceId||loading} onClick={connectMeta}>{connecting?"در حال انتقال به Meta…":"اتصال Facebook و Instagram"}</button>}
      {!active&&<button className="button-outline connection-action" disabled>اتصال در فاز بعد فعال می‌شود</button>}
    </article>;})}</section>
    <div className="data-note">توکن خام به مرورگر فرستاده نمی‌شود و در پایگاه‌داده به‌صورت رمز‌شده نگه‌داری می‌شود. اتصال به تأیید مجوزهای Meta نیاز دارد.</div>
  </div>;
}
