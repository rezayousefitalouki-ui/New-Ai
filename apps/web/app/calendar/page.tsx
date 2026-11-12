import { CalendarDays, ChevronLeft, ChevronRight, Filter, Instagram, Linkedin, MoreHorizontal, Plus } from "lucide-react";

const dayNames=["شنبه","یکشنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنج‌شنبه","جمعه"];
const scheduled:Record<number,{title:string;channel:string;kind:string}[]> = {
  3:[{title:"معرفی محصول تازه",channel:"instagram",kind:"استوری"}],
  7:[{title:"۳ نکته برای انتخاب...",channel:"linkedin",kind:"پست"}],
  11:[{title:"پشت صحنهٔ کارگاه",channel:"instagram",kind:"ریل"}],
  16:[{title:"داستان یک مشتری",channel:"instagram",kind:"پست"}],
  20:[{title:"پرسش این هفته",channel:"linkedin",kind:"پست"}],
  25:[{title:"معرفی مجموعهٔ پاییز",channel:"instagram",kind:"ریل"}],
  29:[{title:"جمع‌بندی ماه",channel:"linkedin",kind:"پست"}],
};
const cells=Array.from({length:42},(_,i)=>i-5);
export default function CalendarPage(){
  return <div className="page-content calendar-page">
    <div className="page-heading calendar-heading"><div><div className="eyebrow">انتشار و برنامه‌ریزی <span className="sample-pill">نمونهٔ نمایشی</span></div><h1>تقویم محتوا</h1><p>تقویم جلالی · منطقهٔ زمانی تهران</p></div><button className="button-primary"><Plus size={17}/> ساخت محتوا</button></div>
    <section className="surface calendar-toolbar"><div className="month-nav"><button className="quiet-icon"><ChevronRight size={17}/></button><b>آبان ۱۴۰۵</b><button className="quiet-icon"><ChevronLeft size={17}/></button><button className="today-button">امروز</button></div><div className="calendar-controls"><div className="segmented"><button className="seg-active">ماه</button><button>هفته</button><button>روز</button><button>فهرست</button></div><button className="select-control"><Filter size={14}/> همهٔ کانال‌ها <ChevronDownMini/></button></div></section>
    <div className="calendar-layout"><section className="surface month-calendar"><div className="calendar-grid day-header">{dayNames.map(n=><div key={n}>{n}</div>)}</div><div className="calendar-grid month-days">{cells.map((day,i)=>{const inMonth=day>0&&day<=30;const post=inMonth?scheduled[day]:undefined;return <article key={i} className={day===21?"day-cell today-cell":inMonth?"day-cell":"day-cell outside"}><div className="day-number">{inMonth?day:""}</div>{post?.map(p=><div className={"calendar-post "+p.channel} key={p.title}><div className="post-image"><span>{p.channel==="instagram"?"S":"SM"}</span><i>{p.channel==="instagram"?<Instagram size={12}/>:<Linkedin size={12}/>}</i></div><div className="post-copy"><b>{p.title}</b><small>{p.kind} · پیش‌نویس</small></div><MoreHorizontal size={14}/></div>)}{inMonth&&!post&&<button className="add-day"><Plus size={14}/></button>}</article>})}</div></section>
    <aside className="calendar-side"><section className="surface side-card"><div className="panel-head"><div><h2>پیش‌نویس‌ها</h2><small>محتوای آمادهٔ برنامه‌ریزی</small></div><span className="count-badge">۳</span></div>{[["معرفی محصول تازه","استوری · اینستاگرام"],["پرسش و پاسخ هفته","ریل · اینستاگرام"],["نکتهٔ آموزشی کوتاه","پست · لینکدین"]].map(([t,d],i)=><div className="draft-row" key={t}><span className={"draft-thumb draft-"+i}><Instagram size={16}/></span><span><b>{t}</b><small>{d}</small></span><MoreHorizontal size={15}/></div>)}<button className="subtle-link">مشاهدهٔ همه ←</button></section><section className="surface side-card"><div className="panel-head"><div><h2>ظرفیت انتشار</h2><small>برای هر روز</small></div><span>ℹ</span></div><div className="capacity"><span>این هفته</span><b>۳ از ۵ پست</b></div><div className="capacity-track"><i/></div><small className="capacity-note">برنامه‌ریزی نمونه است و چیزی منتشر نمی‌شود.</small></section></aside></div>
    <div className="data-note">محتواها نمونه هستند؛ انتشار و drag-and-drop هنوز به سرویس متصل نشده‌اند.</div>
  </div>;
}
function ChevronDownMini(){return <span className="down-mini">⌄</span>}
