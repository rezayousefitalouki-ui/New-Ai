"use client";
import { FormEvent,useCallback,useEffect,useState } from "react";
import { UserPlus,Trash2,RefreshCw } from "lucide-react";
import { apiRequest } from "../../../services/api";

type Workspace={id:string;name:string;role:"owner"|"admin"|"editor"|"viewer"};
type Member={id:string;role:"owner"|"admin"|"editor"|"viewer";user:{id:string;phone:string;first_name:string;last_name:string}};
const roleNames={owner:"مالک",admin:"مدیر",editor:"ویرایشگر",viewer:"بیننده"};
export default function TeamPage(){
  const [workspaces,setWorkspaces]=useState<Workspace[]>([]);
  const [workspaceId,setWorkspaceId]=useState("");
  const [members,setMembers]=useState<Member[]>([]);
  const [phone,setPhone]=useState("");
  const [role,setRole]=useState<"admin"|"editor"|"viewer">("editor");
  const [error,setError]=useState("");
  const [notice,setNotice]=useState("");
  const [busy,setBusy]=useState(false);
  const current=workspaces.find(w=>w.id===workspaceId);
  const refresh=useCallback(async(id:string)=>{if(!id)return;const r=await apiRequest<{members:Member[]}>(`/api/v1/workspaces/${id}/members/`);setMembers(r.members);},[]);
  useEffect(()=>{apiRequest<{workspaces:Workspace[]}>("/api/v1/workspaces/").then(async r=>{setWorkspaces(r.workspaces);const id=r.workspaces[0]?.id??"";setWorkspaceId(id);if(id)await refresh(id);}).catch(e=>setError(e instanceof Error?e.message:"دریافت اعضا ناموفق بود."));},[refresh]);
  async function addMember(event:FormEvent<HTMLFormElement>){event.preventDefault();setBusy(true);setError("");setNotice("");try{await apiRequest(`/api/v1/workspaces/${workspaceId}/members/`,{method:"POST",body:JSON.stringify({phone,role})});setPhone("");await refresh(workspaceId);setNotice("عضو به فضای کاری اضافه شد.");}catch(e){setError(e instanceof Error?e.message:"افزودن عضو ناموفق بود.");}finally{setBusy(false);}}
  async function updateMember(member:Member,nextRole:string){setError("");try{await apiRequest(`/api/v1/workspaces/${workspaceId}/members/${member.id}/`,{method:"PATCH",body:JSON.stringify({role:nextRole})});await refresh(workspaceId);}catch(e){setError(e instanceof Error?e.message:"تغییر نقش ناموفق بود.");}}
  async function removeMember(member:Member){setError("");try{await apiRequest(`/api/v1/workspaces/${workspaceId}/members/${member.id}/`,{method:"DELETE"});await refresh(workspaceId);}catch(e){setError(e instanceof Error?e.message:"حذف عضو ناموفق بود.");}}
  const canManage=current?.role==="owner"||current?.role==="admin";
  return <div className="page-content">
    <div className="page-heading"><div><div className="eyebrow">فضای کاری و دسترسی</div><h1>مدیریت اعضا</h1><p>نقش هر عضو مشخص می‌کند چه کسی به مدیریت فضای کاری دسترسی دارد.</p></div>
      {workspaces.length>1&&<select className="connection-select" value={workspaceId} onChange={async e=>{setWorkspaceId(e.target.value);await refresh(e.target.value);}}>{workspaces.map(w=><option key={w.id} value={w.id}>{w.name}</option>)}</select>}
    </div>
    {error&&<div className="status-banner failure" role="alert">{error}</div>}{notice&&<div className="status-banner success">{notice}</div>}
    {canManage&&<section className="surface team-invite"><div><UserPlus size={18}/><div><b>افزودن عضو ثبت‌نام‌شده</b><small>کاربر باید از قبل حساب SocialMind داشته باشد.</small></div></div>
      <form onSubmit={addMember}><input required inputMode="tel" value={phone} onChange={e=>setPhone(e.target.value)} placeholder="شماره موبایل"/><select value={role} onChange={e=>setRole(e.target.value as typeof role)}><option value="editor">ویرایشگر</option><option value="viewer">بیننده</option>{current?.role==="owner"&&<option value="admin">مدیر</option>}</select><button className="button-primary" disabled={busy||!workspaceId}>{busy?"در حال افزودن…":"افزودن"}</button></form>
    </section>}
    <section className="surface team-list"><div className="panel-head"><div><h2>اعضای فضا</h2><small>{members.length} عضو</small></div><button className="quiet-icon" onClick={()=>refresh(workspaceId)} aria-label="تازه‌سازی"><RefreshCw size={15}/></button></div>
      {members.map(member=><div className="team-member" key={member.id}><span className="profile-avatar">{(member.user.first_name||member.user.phone).slice(0,1)}</span><span className="team-member-copy"><b>{[member.user.first_name,member.user.last_name].filter(Boolean).join(" ")||"کاربر"}</b><small>{member.user.phone}</small></span>
        {member.role==="owner"?<span className="role-pill">{roleNames.owner}</span>:canManage?<><select className="role-select" value={member.role} onChange={e=>updateMember(member,e.target.value)} disabled={current?.role==="admin"&&member.role==="admin"}>{current?.role==="owner"&&<option value="admin">مدیر</option>}<option value="editor">ویرایشگر</option><option value="viewer">بیننده</option></select><button className="remove-member" onClick={()=>removeMember(member)} aria-label="حذف عضو"><Trash2 size={15}/></button></>:<span className="role-pill">{roleNames[member.role]}</span>}
      </div>)}
    </section>
    <div className="data-note">در این نسخه افزودن عضو با شمارهٔ کاربر ثبت‌نام‌شده انجام می‌شود؛ دعوت با پیامک یا ایمیل پس از پیکربندی سرویس ارسال پیاده‌سازی می‌شود.</div>
  </div>;
}
