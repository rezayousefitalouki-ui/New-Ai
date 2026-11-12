"use client";

import { FormEvent,useCallback,useEffect,useState } from "react";
import { Check,Facebook,Instagram,Linkedin,MessageCircle,MoreHorizontal,Search,Send,RefreshCw } from "lucide-react";
import { apiRequest } from "../../services/api";

type Workspace={id:string;name:string};
type LastMessage={text:string;direction:string;sent_at:string};
type Conversation={id:string;kind:"message"|"comment";participant_id:string;participant_name:string;platform:string;account_name:string;unread_count:number;updated_at:string;last_message:LastMessage|null};
type Message={id:string;sender_name:string;text:string;direction:"incoming"|"outgoing";sent_at:string};
const timeAgo=(value:string)=>new Intl.DateTimeFormat("fa-IR",{hour:"2-digit",minute:"2-digit"}).format(new Date(value));
const platformIcon=(platform:string)=>platform==="instagram"?<Instagram size={13}/>:platform==="facebook"?<Facebook size={13}/>:<Linkedin size={13}/>;

export default function InboxPage(){
  const [workspaces,setWorkspaces]=useState<Workspace[]>([]);
  const [workspaceId,setWorkspaceId]=useState("");
  const [filter,setFilter]=useState<"all"|"message"|"comment">("all");
  const [conversations,setConversations]=useState<Conversation[]>([]);
  const [searchQuery,setSearchQuery]=useState("");
  const [selectedId,setSelectedId]=useState("");
  const [messages,setMessages]=useState<Message[]>([]);
  const [reply,setReply]=useState("");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const refresh=useCallback(async(id:string,kind:string)=>{if(!id)return;const q=kind==="all"?"":`&kind=${kind}`;const result=await apiRequest<{conversations:Conversation[]}>(`/api/v1/inbox/?workspace_id=${encodeURIComponent(id)}${q}`);setConversations(result.conversations);setSelectedId(current=>result.conversations.some(c=>c.id===current)?current:result.conversations[0]?.id??"");},[]);
  const loadDetail=useCallback(async(id:string)=>{if(!id)return;const result=await apiRequest<{messages:Message[]}>(`/api/v1/inbox/${id}/`);setMessages(result.messages);},[]);
  useEffect(()=>{apiRequest<{workspaces:Workspace[]}>("/api/v1/workspaces/").then(async r=>{setWorkspaces(r.workspaces);const id=r.workspaces[0]?.id??"";setWorkspaceId(id);await refresh(id,filter);}).catch(e=>setError(e instanceof Error?e.message:"اینباکس دریافت نشد."));},[refresh]);
  useEffect(()=>{if(workspaceId)refresh(workspaceId,filter).catch(e=>setError(e instanceof Error?e.message:"اینباکس دریافت نشد."));},[workspaceId,filter,refresh]);
  useEffect(()=>{if(selectedId)loadDetail(selectedId).catch(e=>setError(e instanceof Error?e.message:"گفتگو دریافت نشد."));else setMessages([]);},[selectedId,loadDetail]);
  const visibleConversations=conversations.filter(c=>(c.participant_name+" "+(c.last_message?.text??"")).toLocaleLowerCase().includes(searchQuery.toLocaleLowerCase()));
  const active=conversations.find(c=>c.id===selectedId);
  async function sendReply(event:FormEvent<HTMLFormElement>){event.preventDefault();if(!active||!reply.trim())return;setBusy(true);setError("");try{await apiRequest(`/api/v1/inbox/${active.id}/reply/`,{method:"POST",body:JSON.stringify({text:reply.trim()})});setReply("");await loadDetail(active.id);await refresh(workspaceId,filter);}catch(e){setError(e instanceof Error?e.message:"ارسال پاسخ ناموفق بود.");}finally{setBusy(false);}}
  return <div className="page-content inbox-page">
    <div className="page-heading compact-heading"><div><div className="eyebrow">مدیریت ارتباطات <span className="live-dot"/> دریافت از webhook</div><h1>اینباکس</h1><p>پیام‌ها و دیدگاه‌های دریافتی از حساب‌های متصل.</p></div><div className="inbox-controls">{workspaces.length>1&&<select className="connection-select" value={workspaceId} onChange={e=>setWorkspaceId(e.target.value)}>{workspaces.map(w=><option key={w.id} value={w.id}>{w.name}</option>)}</select>}<button className="quiet-icon" onClick={()=>refresh(workspaceId,filter)} aria-label="تازه‌سازی"><RefreshCw size={15}/></button></div></div>
    {error&&<div className="status-banner failure" role="alert">{error}</div>}
    <div className="inbox-workspace">
      <section className="thread-list surface"><div className="thread-toolbar"><div className="segmented"><button className={filter==="all"?"seg-active":""} onClick={()=>setFilter("all")}>همه</button><button className={filter==="comment"?"seg-active":""} onClick={()=>setFilter("comment")}>دیدگاه‌ها</button><button className={filter==="message"?"seg-active":""} onClick={()=>setFilter("message")}>پیام‌ها</button></div></div>
        <div className="thread-search"><Search size={15}/><input placeholder="جست‌وجوی گفتگوها" aria-label="جست‌وجوی گفتگوها" value={searchQuery} onChange={e=>setSearchQuery(e.target.value)}/></div>
        <div className="thread-items">{visibleConversations.map(c=><button className={c.id===selectedId?"thread-row thread-selected":"thread-row"} key={c.id} onClick={()=>setSelectedId(c.id)}><span className="thread-avatar avatar-green">{(c.participant_name||c.platform).slice(0,2)}<i className="presence"/></span><span className="thread-copy"><span className="thread-name">{c.participant_name||"کاربر شبکه"}<i className={"social-mini "+c.platform}>{platformIcon(c.platform)}</i></span><small>{c.last_message?.text??(c.kind==="comment"?"دیدگاه":"پیام")}</small></span><span className="thread-meta"><small>{timeAgo(c.updated_at)}</small>{c.unread_count>0&&<i className="unread-count">{c.unread_count}</i>}</span></button>)}
          {!visibleConversations.length&&<div className="inbox-empty"><MessageCircle size={22}/><b>گفتگویی دریافت نشده</b><small>پس از تنظیم webhook و دریافت پیام یا دیدگاه، گفتگوها اینجا نمایش داده می‌شوند.</small></div>}
        </div><div className="thread-list-footer"><span className="green-dot"/> همگام‌سازی با webhook</div>
      </section>
      <section className="conversation surface">
        {active?<><div className="conversation-head"><div className="conversation-person"><span className="thread-avatar avatar-green">{(active.participant_name||active.platform).slice(0,2)}</span><span><b>{active.participant_name||"کاربر شبکه"}</b><small>{platformIcon(active.platform)} {active.platform} · {active.kind==="comment"?"دیدگاه":"پیام مستقیم"}</small></span></div><div className="conversation-tools"><span className="status-open">دریافتی</span><button className="quiet-icon"><MoreHorizontal size={19}/></button></div></div>
          <div className="message-stream">{messages.map(m=><div className={m.direction==="outgoing"?"message outgoing":"message incoming"} key={m.id}><small>{m.sender_name|| (m.direction==="outgoing"?"شما":active.participant_name)} · {timeAgo(m.sent_at)}</small><p>{m.text}</p></div>)}</div>
          <form className="reply-box" onSubmit={sendReply}><div className="reply-warning"><Check size={14}/> ارسال از طریق حساب متصل انجام می‌شود.</div><textarea value={reply} onChange={e=>setReply(e.target.value)} maxLength={2000} placeholder="پاسخ بنویس…" rows={3}/><div className="reply-actions"><span>{reply.length}/۲۰۰۰</span><button className="button-primary" disabled={busy||!reply.trim()}><Send size={14}/>{busy?"در حال ارسال…":"ارسال پاسخ"}</button></div></form>
        </>:<div className="inbox-empty conversation-empty"><MessageCircle size={26}/><b>یک گفتگو انتخاب کن</b><small>پیام‌ها و دیدگاه‌های واقعی پس از اتصال webhook اینجا قرار می‌گیرند.</small></div>}
      </section>
    </div>
    <div className="data-note">دریافت پیام‌ها نیازمند ثبت callback وب‌هوک Meta و subscription صفحه‌ها در Meta Developer Dashboard است. ارسال فقط برای گفتگوهایی فعال است که webhook آنها را دریافت کرده.</div>
  </div>;
}
