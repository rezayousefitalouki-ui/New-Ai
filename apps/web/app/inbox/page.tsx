import { Check, ChevronDown, Instagram, Linkedin, MessageCircle, MoreHorizontal, Search, Send, Twitter } from "lucide-react";

const threads = [
  { initials:"AR",name:"آرمان رضایی",social:"instagram",time:"۲ ساعت پیش",preview:"برای همکاری در کمپین پاییز آماده‌ایم.",unread:true,color:"avatar-lime" },
  { initials:"DN",name:"دانیال نوری",social:"twitter",time:"۶ ساعت پیش",preview:"ممنون از راهنمایی سریع، مشکل حل شد.",color:"avatar-green" },
  { initials:"SM",name:"سارا محمدی",social:"linkedin",time:"۸ ساعت پیش",preview:"مطالعهٔ موردی شما را دیدم و چند سؤال دارم.",unread:true,color:"avatar-coral" },
  { initials:"MN",name:"ماه‌نشان",social:"instagram",time:"۱۰ ساعت پیش",preview:"ممنون، این پیشنهاد خیلی کمک کرد.",color:"avatar-blue" },
  { initials:"TK",name:"تیم کافه‌نو",social:"instagram",time:"دیروز",preview:"قیمت بستهٔ سازمانی را می‌فرستید؟",color:"avatar-violet" },
  { initials:"NR",name:"نیما رستگار",social:"twitter",time:"دیروز",preview:"پست جدیدتان را با تیم به اشتراک گذاشتم.",color:"avatar-yellow" },
];
const socialIcon = (name:string) => name === "instagram" ? <Instagram size={13}/> : name === "linkedin" ? <Linkedin size={13}/> : <Twitter size={13}/>;

export default function InboxPage() {
  return <div className="page-content inbox-page">
    <div className="page-heading compact-heading"><div><div className="eyebrow">مدیریت ارتباطات <span className="sample-pill">نمونهٔ نمایشی</span></div><h1>اینباکس</h1><p>پیام‌ها، دیدگاه‌ها و اشاره‌ها را در یک فضای کاری مرور کن.</p></div><div className="unread-pill">۴ مورد خوانده‌نشده</div></div>
    <div className="inbox-workspace">
      <section className="thread-list surface">
        <div className="thread-toolbar"><div className="segmented"><button className="seg-active">همه</button><button>دیدگاه‌ها</button><button>پیام‌ها</button><button>اشاره‌ها</button></div></div>
        <div className="thread-search"><Search size={15}/><input placeholder="جست‌وجوی گفتگوها" aria-label="جست‌وجوی گفتگوها"/></div>
        <div className="thread-items">{threads.map((t,i)=><button className={i===0?"thread-row thread-selected":"thread-row"} key={t.name}><span className={"thread-avatar "+t.color}>{t.initials}<i className="presence"/></span><span className="thread-copy"><span className="thread-name">{t.name}<i className={"social-mini "+t.social}>{socialIcon(t.social)}</i></span><small>{t.preview}</small></span><span className="thread-meta"><small>{t.time}</small>{t.unread&&<i className="unread-count">۱</i>}</span></button>)}</div>
        <div className="thread-list-footer"><span className="green-dot"/> همگام‌سازی نمایشی</div>
      </section>
      <section className="conversation surface">
        <div className="conversation-head"><div className="conversation-person"><span className="thread-avatar avatar-lime">AR</span><span><b>آرمان رضایی</b><small><Instagram size={13}/> اینستاگرام · پیام مستقیم</small></span></div><div className="conversation-tools"><span className="status-open">باز</span><button className="select-control">تخصیص به <ChevronDown size={14}/></button><button className="quiet-icon"><MoreHorizontal size={19}/></button></div></div>
        <div className="conversation-context"><span className="context-thumb"><Instagram size={15}/></span><span><small>پاسخ به محتوای شما</small><b>معرفی مجموعهٔ پاییزی</b></span><span className="context-label">نمایش پست ↗</span></div>
        <div className="message-stream"><div className="date-divider"><span>امروز، ساعت ۱۰:۲۵</span></div><div className="message incoming"><small>آرمان رضایی · ۱۰:۲۵</small><p>سلام! محصولات جدیدتون رو دیدم، خیلی جذابن. برای همکاری در کمپین پاییز برنامه‌ای دارید؟</p></div><div className="message outgoing"><small>پاسخ پیشنهادی · نیازمند تأیید</small><p>سلام آرمان، ممنون از لطفتون! خوشحال می‌شیم بیشتر دربارهٔ پیشنهادتون بدونیم. اگر جزئیات کمپین رو بفرستید، بررسی می‌کنیم.</p><span className="suggestion-tag"><SparkleMini/> پیشنهاد هوش مصنوعی</span></div><div className="message incoming"><small>آرمان رضایی · ۱۰:۴۲</small><p>عالیه، جزئیات رو تا آخر امروز براتون می‌فرستم.</p></div></div>
        <div className="reply-box"><div className="reply-warning"><Check size={14}/> پاسخ پیشنهادی است؛ پیش از ارسال بررسی کنید.</div><textarea placeholder="پاسخ خود را بنویسید..." aria-label="متن پاسخ"/><div className="reply-actions"><span>پاسخ خودکار خاموش است</span><button className="send-button" disabled>ارسال <Send size={14}/></button></div></div>
      </section>
      <aside className="contact-panel surface"><div className="contact-top"><span className="thread-avatar avatar-lime large-avatar">AR</span><h3>آرمان رضایی</h3><small>@arman.r · مخاطب جدید</small><button className="follow-button">دنبال‌کردن در اینستاگرام ↗</button></div><div className="contact-section"><b>خلاصهٔ تعامل</b><div><span>دیدگاه‌ها</span><strong>۳</strong></div><div><span>پیام‌ها</span><strong>۲</strong></div><div><span>آخرین تعامل</span><strong>امروز</strong></div></div><div className="contact-section"><b>برچسب‌ها</b><span className="tag">همکاری احتمالی</span><span className="tag">مخاطب جدید</span></div><div className="contact-note">نمایش نمونه؛ اتصال واقعی شبکه‌های اجتماعی هنوز فعال نشده است.</div></aside>
    </div>
  </div>;
}
function SparkleMini(){return <span className="sparkle-mini">✦</span>}
